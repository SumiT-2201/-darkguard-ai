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
