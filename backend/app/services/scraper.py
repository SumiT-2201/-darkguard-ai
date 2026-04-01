from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import re
import requests
import time
import random

class Scraper:
    def __init__(self, url):
        # 1. Clean and normalize URL
        url = url.strip()
        if not url.startswith(('http://', 'https://')):
            url = f"https://{url}"
        
        # 2. SSRF Protection: Prevent scanning local/private networks
        from urllib.parse import urlparse
        import socket
        
        parsed = urlparse(url)
        hostname = parsed.hostname
        
        # Simple security check for common internal patterns
        if hostname in ['localhost', '127.0.0.1', '0.0.0.0', '::1']:
             raise ValueError("Scanning local/internal addresses is restricted for security.")
             
        self.url = url
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
        ]

    def _parse_html(self, html_content):
        # Parse the HTML content
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 1. Context-Aware Content Extraction
        for discard in soup(['footer', 'nav', 'header', 'aside', 'script', 'style']):
            discard.decompose()

        # 2. Focus on "High Value" areas for dark patterns
        high_value_selectors = [
            'button', 'a.button', '.btn', '.cta', '.banner', '.promo', '.offer',
            'h1', 'h2', 'main', '.content', '.modal', '.popup', '.overlay'
        ]
        
        text_parts = []
        for selector in high_value_selectors:
            for el in soup.select(selector):
                content = el.get_text(strip=True)
                if content and 5 < len(content) < 500:
                    content = re.sub(r'\s+', ' ', content)
                    if content not in text_parts: 
                        text_parts.append(content)

        # Fallback to general content
        if len(text_parts) < 5:
            for el in soup.find_all(['p', 'div']):
                content = el.get_text(strip=True)
                if content and 20 < len(content) < 300:
                    content = re.sub(r'\s+', ' ', content)
                    if content not in text_parts:
                        text_parts.append(content)

        text_content = " | ".join(text_parts)
        
        page_meta = {
            "title": soup.title.string if soup.title else "Unknown Title",
            "char_count": len(text_content),
            "buttons_count": len(soup.find_all(['button', 'input'])),
            "links_count": len(soup.find_all('a', href=True)),
            "forms_count": len(soup.find_all('form')),
            "images_count": len(soup.find_all('img'))
        }
        return text_content, page_meta

    def fetch(self):
        """
        Optimized scraper:
        - Headless Playwright (JavaScript rendering)
        - Fallback: Requests + BeautifulSoup (Static HTML)
        - Max 2 retries
        - Returns partial results on block
        """
        html_content = None
        status_info = {"status": "success", "fallback_used": False}
        max_attempts = 2

        # --- Attempt 1: Playwright (Headless) ---
        for attempt in range(max_attempts):
            try:
                with sync_playwright() as p:
                    # Single browser instance per attempt
                    browser = p.chromium.launch(headless=True)
                    context = browser.new_context(
                        user_agent=random.choice(self.user_agents),
                        viewport={'width': 1920, 'height': 1080}
                    )
                    page = context.new_page()
                    
                    # Random delay
                    time.sleep(random.uniform(0.5, 1.0))
                    
                    try:
                        # Navigate and wait for network activity (JavaScript load)
                        page.goto(self.url, wait_until='load', timeout=20000)
                        # Minimal wait for additional dynamic parts
                        time.sleep(1)
                        html_content = page.content()
                    except Exception as e:
                        print(f"Playwright navigation attempt {attempt+1} failed: {e}")
                    
                    # Absolute Cleanup
                    page.close()
                    context.close()
                    browser.close()
                    
                    if html_content and len(html_content) > 1000:
                        break # Successfully retrieved content
            except Exception as e:
                print(f"Critical Playwright error: {e}")
                time.sleep(1)

        # --- Fallback: Requests (Static HTML) if Playwright failed ---
        if not html_content or len(html_content) < 1000:
            print("Playwright failed or was blocked. Using static fallback.")
            try:
                headers = {'User-Agent': random.choice(self.user_agents)}
                response = requests.get(self.url, headers=headers, timeout=10)
                if response.status_code == 200:
                    html_content = response.text
                    status_info["fallback_used"] = True
                    status_info["message"] = "Advanced rendering failed, using basic static fallback."
                else:
                    status_info["status"] = "partial"
                    status_info["message"] = f"Website blocked scraping (Status: {response.status_code}). Scanning static fragments."
                    status_info["fallback_used"] = True
                    # If we got partial HTML or error page, still try to scan it if possible
                    html_content = response.text
            except Exception as e:
                print(f"Fallback request failed: {e}")
                status_info["status"] = "partial"
                status_info["message"] = "Website blocked all scraping attempts. Results may be incomplete."
                status_info["fallback_used"] = True

        # Ensure we return something even if all failed (Partial results requirement)
        if not html_content:
            return "", "", {}, status_info

        # --- Process results ---
        try:
            text_content, page_meta = self._parse_html(html_content)
            return html_content, text_content, page_meta, status_info
        except Exception as e:
            print(f"Parsing error: {e}")
            return html_content, "", {}, status_info
