<<<<<<< HEAD
=======
<<<<<<< HEAD
# 🛡️ DarkGuard AI – Dark Pattern Detection System

DarkGuard AI is a full-stack AI-powered web application designed to detect **dark patterns** (deceptive UI/UX practices) on websites.  
It analyzes web pages using a hybrid approach combining **Machine Learning + Rule-Based Detection** and generates a **trust score** along with detailed insights.

---

## 🌐 Live Features

- 🔍 Scan any website URL
- 🤖 AI-based dark pattern detection
- ⚙️ Hybrid detection (ML + Rule-based)
- 📊 Trust Score (0–100) with grading
- 📁 Scan history tracking (MongoDB)
- 📋 Detailed findings with severity levels
- 🧠 ML performance evaluation (Precision, Recall, etc.)

---

## 🧠 Problem Statement

Many websites use **dark patterns** to manipulate user behavior, such as:
- Fake urgency ("Only 2 left!")
- Hidden costs
- Forced actions (mandatory sign-ups)
- Misleading UI elements

DarkGuard AI aims to **identify and warn users** about such patterns.

---

## ⚙️ Tech Stack

### 🔹 Backend
- Python (Flask)
- MongoDB (PyMongo)
- Playwright (Web scraping)
- Scikit-learn (ML Model)

### 🔹 Frontend
- HTML, CSS, JavaScript
- Fetch API

### 🔹 Machine Learning
- TF-IDF Vectorization
- Classification Models (Logistic Regression / SVM)
- Confidence-based filtering

---

## 🏗️ System Architecture

1. User inputs URL
2. Playwright scrapes webpage content
3. Text is cleaned and processed
4. Hybrid detection runs:
   - Rule-based keyword detection
   - ML model prediction
5. Findings are aggregated
6. Trust score is calculated
7. Results displayed on UI and stored in MongoDB

---

## 📊 Scoring System

- Initial Score: 100
- Penalty based on severity:
  - Low → -5
  - Medium → -10
  - High → -20
  - Critical → -30
- Score capped between 0–100

---

## 📈 Model Evaluation

The system is evaluated using a realistic dataset.

| Metric     | Value |
|------------|------|
| Precision  | 0.947 |
| Recall     | 0.720 |
| Accuracy   | 0.800 |
| F1 Score   | 0.818 |

### Key Insights:
- High precision ensures minimal false alerts
- Lower recall indicates conservative detection
- Threshold tuned for real-world usability

---

## ⚠️ Limitations

- Cannot detect purely visual dark patterns
- Some websites block scraping (e.g., Amazon, login-based sites)
- Depends on extracted textual content
- Context-based patterns may be missed

---

## 🚀 Future Improvements

- Deep learning-based NLP models (BERT)
- Visual UI analysis (Computer Vision)
- Browser extension integration
- Real-time detection
- Larger training dataset

---

## 🧪 Installation & Setup

### 1. Clone Repository
```bash
git clone <your-repo-link>
cd darkguard
=======
>>>>>>> b5a0df5
# 🛡️ DarkGuard AI: Deceptive UI Pattern Detector

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![JavaScript](https://img.shields.io/badge/JavaScript-ES6%2B-yellow?logo=javascript&logoColor=white)](https://www.javascript.com/)
[![Chrome Extension](https://img.shields.io/badge/Chrome-Extension-orange?logo=google-chrome&logoColor=white)](https://developer.chrome.com/docs/extensions/)
[![Flask](https://img.shields.io/badge/Flask-Web_Framework-lightgrey?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

DarkGuard AI is a powerful, real-time detection system designed to identify and highlight deceptive UI/UX practices—commonly known as **Dark Patterns**—on modern websites. It combines rule-based heuristics, machine learning classification, and semantic AI analysis to protect users from manipulative digital experiences.

---

## 🚀 Key Features

- **Hybrid Detection Engine**: Combines keyword-based rules with a Random Forest NLP classifier.
- **Semantic Analysis**: Integrated with Claude LLM to catch subtle, linguistically manipulative patterns.
- **Robust Web Scraper**: Headless Playwright integration with automatic static HTML fallbacks.
- **Real-time Scoring**: Provides a "Trust Score" (0–100) based on severity and density of patterns.
- **Universal Extension**: A dedicated Chrome extension that analyzes any tab with a single click.

---

## 📂 Project Structure

```bash
DarkGuard_AI/
├── backend/            # Flask API, ML models, and Rule Detection logic
│   ├── app/            # Main application services (Scraper, Detectors, Scoring)
│   ├── ml/             # NLP training scripts and serialized models
│   └── run.py          # Backend entry point (Port 5000)
├── frontend/           # Modern Analytics Dashboard
│   ├── index.html      # Main UI with Chart.js visualization
│   ├── css/            # Premium dark-theme styling
│   └── js/             # Asynchronous dashboard and history logic
├── chrome_extension/   # Browser-integrated scanner
│   ├── manifest.json   # Extension manifest (MV3)
│   ├── popup.html      # User-facing extension interface
│   └── background.js   # API proxy and content messaging
└── README.md           # Project documentation
```

---

## 🛠️ Tech Stack

- **Backend**: Python 3.10+, Flask, MongoDB, Playwright, Scikit-learn, Anthropic API (Claude).
- **Frontend**: HTML5, Vanilla CSS3, JavaScript (ES6), Chart.js.
- **Extension**: Chrome Extensions API (Manifest V3), Fetch API.
- **AI/ML**: TF-IDF Vectorization, Random Forest Classifier, Claude-3.5-Sonnet.

---

## 🎯 Evaluation Metrics (Realism-Verified)

| Metric | Value | Description |
| :--- | :--- | :--- |
| **Precision** | **0.947** | High-fidelity: 95% of alerts are verified dark patterns. |
| **Recall** | **0.720** | Captures 72% of all patterns, prioritizing accuracy over "alert fatigue". |
| **Accuracy** | **0.800** | Overall success rate across a 100-sample balanced dataset. |
| **F1-Score** | **0.818** | Balanced harmonic mean for industrial-grade stability. |

---

## ⚙️ How to Install and Run Locally

### 1. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python run.py
```
*Make sure you have a `MONGO_URI` and optional `CLAUDE_API_KEY` configured in `app/config.py`.*

### 2. Frontend Setup
```bash
cd frontend
# You can use any static server, like live-server or python http.server
npx live-server
```
*Frontend runs by default on `http://127.0.0.1:8080` (ensure backend is on port 5000).*

---

## 🧩 How to Load the Chrome Extension

1. Open Google Chrome and navigate to `chrome://extensions/`.
2. Toggle **Developer mode** on (top-right corner).
3. Click **Load unpacked**.
4. Select the `chrome_extension/` folder from this project directory.
5. Search for "DarkGuard AI" in your toolbar and pin it!

---

## 🔮 Future Improvements

- [ ] **On-page Highlighting**: Visually highlight detected text directly on the website DOM.
- [ ] **Community Reporting**: Allow users to "flag" missed patterns to retrain the ML model.
- [ ] **Cross-Browser Support**: Expand to Firefox (WebExtensions) and Safari.
- [ ] **Privacy Score**: Analyze cookie banners and privacy policies for "forced consent" patterns.

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Developed with ❤️ by the DarkGuard AI Team.
<<<<<<< HEAD
=======
>>>>>>> ba2db0d (Added professional README with high-scale evaluation metrics and setup instructions)
>>>>>>> b5a0df5
