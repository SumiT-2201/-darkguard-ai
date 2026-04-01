import sys
import os
import json

# Add backend to sys.path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.services.hybrid_detector import HybridDetector
from app.services.ml_detector import MLDetector

# Initialize the model
MLDetector.load_model()

# Expanded Balanced Evaluation Dataset (100 samples)
eval_data = [
    # --- POSITIVES (Dark Patterns: 50 Samples) ---
    # URGENCY (10)
    {"text": "Only 3 items left in stock now! Hurry up!", "label": "pattern", "category": "urgency"},
    {"text": "Hurry, limited time offer. Sale ends in 5 minutes.", "label": "pattern", "category": "urgency"},
    {"text": "Get 50% discount if you buy in the next 10 minutes!", "label": "pattern", "category": "urgency"},
    {"text": "Price increases in 02:45. Buy before it's too late.", "label": "pattern", "category": "urgency"},
    {"text": "One-time offer expires soon. Act fast and save!", "label": "pattern", "category": "urgency"},
    {"text": "Last chance to grab the deal at this price today.", "label": "pattern", "category": "urgency"},
    {"text": "Hurry up! This flash sale is about to end.", "label": "pattern", "category": "urgency"},
    {"text": "Don't wait! The countdown is already running out.", "label": "pattern", "category": "urgency"},
    {"text": "Exclusive deal ends tonight. Don't miss your chance.", "label": "pattern", "category": "urgency"},
    {"text": "Your cart will expire in 2 minutes. Checkout now!", "label": "pattern", "category": "urgency"},
    
    # SCARCITY (10)
    {"text": "12 other people have this in their cart right now.", "label": "pattern", "category": "scarcity"},
    {"text": "Limited edition item - only a few left in stock.", "label": "pattern", "category": "scarcity"},
    {"text": "Only 2 rooms left on our site for these dates!", "label": "pattern", "category": "scarcity"},
    {"text": "Wait! Others are looking at this same product right now.", "label": "pattern", "category": "scarcity"},
    {"text": "People in London just bought this same item.", "label": "pattern", "category": "scarcity"},
    {"text": "This item is in high demand and selling fast!", "label": "pattern", "category": "scarcity"},
    {"text": "Popular choice! 500+ people viewed this today.", "label": "pattern", "category": "scarcity"},
    {"text": "Almost sold out! Grab yours before the stock is gone.", "label": "pattern", "category": "scarcity"},
    {"text": "We only have 1 item left at this discounted price.", "label": "pattern", "category": "scarcity"},
    {"text": "Join 10k users who already upgraded their plan.", "label": "pattern", "category": "scarcity"},
    
    # CONFIRMSHAMING (10)
    {"text": "No thanks, I'd rather pay full price for my items.", "label": "pattern", "category": "confirmshaming"},
    {"text": "No, I am not interested in saving money today.", "label": "pattern", "category": "confirmshaming"},
    {"text": "I'll pass. I don't care about my family's safety.", "label": "pattern", "category": "confirmshaming"},
    {"text": "No, I prefer being less productive at work.", "label": "pattern", "category": "confirmshaming"},
    {"text": "No thanks, I don't want to get better at coding.", "label": "pattern", "category": "confirmshaming"},
    {"text": "I'm okay with missing out on this huge discount.", "label": "pattern", "category": "confirmshaming"},
    {"text": "No, I don't want to protect my digital identity.", "label": "pattern", "category": "confirmshaming"},
    {"text": "I like paying more for slower shipping services.", "label": "pattern", "category": "confirmshaming"},
    {"text": "No, I don't need any special offers right now.", "label": "pattern", "category": "confirmshaming"},
    {"text": "Skip this offer and pay the original high price.", "label": "pattern", "category": "confirmshaming"},
    
    # HIDDEN COSTS (10)
    {"text": "A processing fee of $15 will be added at checkout.", "label": "pattern", "category": "hidden_cost"},
    {"text": "Shipping fee of $9.99 will be applied to your order.", "label": "pattern", "category": "hidden_cost"},
    {"text": "Additional service charges and taxes added at the end.", "label": "pattern", "category": "hidden_cost"},
    {"text": "Extra charges of $5 for handling will be included.", "label": "pattern", "category": "hidden_cost"},
    {"text": "Taxes and fees are calculated during final payment.", "label": "pattern", "category": "hidden_cost"},
    {"text": "A small convenience fee is added for digital delivery.", "label": "pattern", "category": "hidden_cost"},
    {"text": "Final total may change based on dynamic pricing fees.", "label": "pattern", "category": "hidden_cost"},
    {"text": "Additional customs duties may apply to your region.", "label": "pattern", "category": "hidden_cost"},
    {"text": "We add a surcharge for credit card processing.", "label": "pattern", "category": "hidden_cost"},
    {"text": "Price excludes hidden administrative costs for verification.", "label": "pattern", "category": "hidden_cost"},

    # SNEAKING/MISDIRECTION (10)
    {"text": "Subscription renewals are automatic and billed monthly.", "label": "pattern", "category": "sneaking"},
    {"text": "Recommended choice for most of our pro users.", "label": "pattern", "category": "misdirection"},
    {"text": "By continuing, you accept our daily marketing emails.", "label": "pattern", "category": "forced-action"},
    {"text": "We added a protection plan to your cart for you.", "label": "pattern", "category": "sneaking"},
    {"text": "Opt-out for a slower and less reliable experience.", "label": "pattern", "category": "misdirection"},
    {"text": "Please share your contacts to view this free offer.", "label": "pattern", "category": "forced-action"},
    {"text": "We selected the best insurance option for your trip.", "label": "pattern", "category": "sneaking"},
    {"text": "Don't uncheck this if you want to stay protected.", "label": "pattern", "category": "misdirection"},
    {"text": "Join our VIP club for automatic premium billing.", "label": "pattern", "category": "sneaking"},
    {"text": "Your data is safe, but we will share it with partners.", "label": "pattern", "category": "misdirection"},
    
    # --- NEGATIVES (Safe UI: 50 Samples) ---
    # GENERIC UI (20)
    {"text": "Login to your account to continue.", "label": "safe", "category": "none"},
    {"text": "Search for products, brands and categories here.", "label": "safe", "category": "none"},
    {"text": "New chat with our intelligent AI Assistant.", "label": "safe", "category": "none"},
    {"text": "Privacy policy and terms of service documentation.", "label": "safe", "category": "none"},
    {"text": "Copyright 2024. All rights reserved by Organization.", "label": "safe", "category": "none"},
    {"text": "Contact our support team for immediate assistance.", "label": "safe", "category": "none"},
    {"text": "Terms and conditions apply to all promotions.", "label": "safe", "category": "none"},
    {"text": "View our help center for common questions.", "label": "safe", "category": "none"},
    {"text": "Reset your password via a secure email link.", "label": "safe", "category": "none"},
    {"text": "Manage your cookie preferences and settings here.", "label": "safe", "category": "none"},
    {"text": "Language selection: English (United States) / Spanish.", "label": "safe", "category": "none"},
    {"text": "Back to top of the page navigation.", "label": "safe", "category": "none"},
    {"text": "Read more about our company mission and values.", "label": "safe", "category": "none"},
    {"text": "View all available products in this category.", "label": "safe", "category": "none"},
    {"text": "Stay logged in on this devices for faster access.", "label": "safe", "category": "none"},
    {"text": "Enter your email address to receive updates.", "label": "safe", "category": "none"},
    {"text": "Follow us on social media for more news.", "label": "safe", "category": "none"},
    {"text": "Site map and accessibility features for easier navigation.", "label": "safe", "category": "none"},
    {"text": "Go to my profile and account settings dashboard.", "label": "safe", "category": "none"},
    {"text": "Notifications: You have no new messages at this time.", "label": "safe", "category": "none"},

    # AMBIGUOUS SAFE UI (20)
    {"text": "Your login session will expire in 5 minutes for safety.", "label": "safe", "category": "none"},
    {"text": "Only 3 spots left for the free webinar registration.", "label": "safe", "category": "none"},
    {"text": "This item is currently out of stock. Notify me.", "label": "safe", "category": "none"},
    {"text": "Hurry, the library closes in twenty minutes from now.", "label": "safe", "category": "none"},
    {"text": "Search results for 'dark pattern detection' query.", "label": "safe", "category": "none"},
    {"text": "Act fast to join our community before we close signups.", "label": "safe", "category": "none"},
    {"text": "Limited space in the classroom for this semester.", "label": "safe", "category": "none"},
    {"text": "Please confirm your email within 24 hours to activate.", "label": "safe", "category": "none"},
    {"text": "Only few seats remaining at the back of the theater.", "label": "safe", "category": "none"},
    {"text": "Don't miss out on our opening ceremony tomorrow.", "label": "safe", "category": "none"},
    {"text": "Wait for the page to load completely before clicking.", "label": "safe", "category": "none"},
    {"text": "Hurry! The ice cream truck is leaving the station.", "label": "safe", "category": "none"},
    {"text": "Sign up for a chance to win a free gift box.", "label": "safe", "category": "none"},
    {"text": "Privacy: We do not sell your personal data to others.", "label": "safe", "category": "none"},
    {"text": "Contact about us to learn more about the team.", "label": "safe", "category": "none"},
    {"text": "Limited time offer for students with valid IDs.", "label": "safe", "category": "none"},
    {"text": "Expires on December 31, 2024. Read the terms.", "label": "safe", "category": "none"},
    {"text": "Checkout our new arrivals and trending collections.", "label": "safe", "category": "none"},
    {"text": "Subscribe to get a weekly digest of our best posts.", "label": "safe", "category": "none"},
    {"text": "Join the waitlist for the next available batch.", "label": "safe", "category": "none"},

    # REAL WORLD FRAGMENTS (10)
    {"text": "Official website for the United Nations organization.", "label": "safe", "category": "none"},
    {"text": "Powered by Google Cloud and optimized for speed.", "label": "safe", "category": "none"},
    {"text": "Facebook and Twitter links are available in the footer.", "label": "safe", "category": "none"},
    {"text": "Visit our home and explore our digital gallery now.", "label": "safe", "category": "none"},
    {"text": "All rights reserved. Unauthorized reproduction is prohibited.", "label": "safe", "category": "none"},
    {"text": "Search for news, articles, and scientific research.", "label": "safe", "category": "none"},
    {"text": "Login with your academic credentials for full access.", "label": "safe", "category": "none"},
    {"text": "New chat is ready for your specific query today.", "label": "safe", "category": "none"},
    {"text": "Accessibility settings can be toggled on the right bar.", "label": "safe", "category": "none"},
    {"text": "Terms of use were updated on August 15, 2024.", "label": "safe", "category": "none"}
]

results = []

for item in eval_data:
    detections = HybridDetector.analyze_and_merge("", item["text"])
    
    is_pattern = len(detections) > 0
    confidence = detections[0].get("confidence", 1.0) if is_pattern else 0.0
    pred_cat = detections[0].get("category", "none") if is_pattern else "none"
    
    results.append({
        "text": item["text"],
        "actual": item["label"],
        "actual_cat": item["category"],
        "pred": "pattern" if is_pattern else "safe",
        "pred_cat": pred_cat,
        "confidence": confidence
    })

# Compute metrics
tp = sum(1 for r in results if r["actual"] == "pattern" and r["pred"] == "pattern")
tn = sum(1 for r in results if r["actual"] == "safe" and r["pred"] == "safe")
fp = sum(1 for r in results if r["actual"] == "safe" and r["pred"] == "pattern")
fn = sum(1 for r in results if r["actual"] == "pattern" and r["pred"] == "safe")

precision = tp / (tp + fp) if (tp + fp) > 0 else 0
recall = tp / (tp + fn) if (tp + fn) > 0 else 0
f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
accuracy = (tp + tn) / len(results)

print("\n--- PERFORMANCE SUMMARY (100 SAMPLES) ---")
print(f"TP: {tp}, TN: {tn}, FP: {fp}, FN: {fn}")
print(f"Precision: {precision:.3f}")
print(f"Recall: {recall:.3f}")
print(f"F1: {f1:.3f}")
print(f"Accuracy: {accuracy:.3f}")

print("\n--- ERROR ANALYSIS: FALSE NEGATIVES (MISSED) ---")
for r in results:
    if r["actual"] == "pattern" and r["pred"] == "safe":
        print(f"FN: {r['text']} (Exp: {r['actual_cat']})")

print("\n--- ERROR ANALYSIS: FALSE POSITIVES (WRONGLY FLAGGED) ---")
for r in results:
    if r["actual"] == "safe" and r["pred"] == "pattern":
        print(f"FP: {r['text']} (Pred: {r['pred_cat']})")
