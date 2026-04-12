# PagePersona AI — Landing Page Personalizer

An end-to-end AI system that takes an **ad creative** + **landing page URL** and returns a **CRO-optimized, personalized version** of the landing page — aligned with the ad's message, tone, and audience.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- A **Gemini API key** → [Get one here](https://aistudio.google.com/app/apikey)

---

### 1. Backend Setup (Django)

```bash
cd backend

# Activate virtual environment 
source venv/bin/activate

# Add your Gemini API key
echo "GEMINI_API_KEY=your_actual_key_here" > .env

# Start the server
python manage.py runserver
```

Django runs at: **http://localhost:8000**

---

### 2. Frontend Setup (React + Vite)

```bash
cd frontend

# Install dependencies 
npm install

# Start dev server
npm run dev
```

React runs at: **http://localhost:5173**

---

### 3. Use the App

1. Open **http://localhost:5173**
2. Paste a landing page URL (e.g. `https://stripe.com`)
3. Upload an ad image OR paste an image URL
4. Click **Analyze & Personalize**
5. See side-by-side comparison + change log with reasoning

---

## 🏗️ Architecture

```
User Input (Ad Image + Landing Page URL)
         ↓
React Frontend (Vite) — port 5173
         ↓ POST /api/personalize/
Django Backend — port 8000
         ↓
  Step 1: page_scraper.py    — BeautifulSoup extracts h1, h2, CTA, hero text
  Step 2: ad_analyzer.py     — Gemini vision analyzes ad image (model: GEMINI_MODEL, default gemini-2.5-flash)
  Step 3: cro_personalizer.py — Gemini generates CRO-aligned copy
  Step 4: html_injector.py   — Surgically patches original HTML
         ↓
  Response: { personalized_html, original_html, change_log, ad_analysis }
         ↓
React Results View — side-by-side iframes + change log panel
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health/` | Health check |
| POST | `/api/scrape-page/` | Scrape landing page `{ url }` |
| POST | `/api/analyze-ad/` | Analyze ad image (multipart or `{ image_url }`) |
| POST | `/api/personalize/` | Full pipeline (multipart: `image` + `landing_page_url`) |

---

## 🛡️ Error Handling

| Concern | Approach |
|---------|----------|
| Hallucinations | `validator.py` schema-checks all Gemini output; falls back to original values |
| Broken HTML | `html_injector.py` returns original HTML if BeautifulSoup fails |
| Broken UI | Field-level fallbacks ensure no empty critical fields reach the frontend |
| Random changes | Structured JSON prompt with strict field limits; temperature=0.3 for analysis |
| Scraping failures | Graceful error with clear user-facing message, step-level failure reporting |
| API key missing | Returns clear 422 error before calling Gemini |

---

## 📁 Project Structure

```
PM-INTERN/
├── backend/
│   ├── api/
│   │   ├── page_scraper.py      # Landing page content extraction
│   │   ├── ad_analyzer.py       # Gemini Vision ad analysis
│   │   ├── cro_personalizer.py  # Gemini CRO copy generation
│   │   ├── validator.py         # Output validation & fallbacks
│   │   ├── html_injector.py     # Surgical HTML patching
│   │   ├── views.py             # REST API endpoints
│   │   └── urls.py              # URL routing
│   ├── backend/
│   │   ├── settings.py
│   │   └── urls.py
│   ├── .env                     # Your API key goes here
│   └── requirements.txt
│
└── frontend/
    └── src/
        ├── components/
        │   ├── InputForm.jsx     # Ad upload + URL input
        │   ├── StepProgress.jsx  # 4-step animated progress
        │   ├── PagePreview.jsx   # Sandboxed iframe viewer
        │   ├── ChangeLogPanel.jsx # Changes + reasoning
        │   └── ResultsView.jsx   # Side-by-side results
        ├── App.jsx               # State machine: input→loading→results
        └── index.css             # Design system (glassmorphism)
```
