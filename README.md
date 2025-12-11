# MindSpace — AI-Powered Social Media Language Analysis

---

<p align="center">
  <img src="screenshots/DarkTheme.png" width="900" alt="MindSpace Dark Report" />
</p>

---

# 📸 Screenshots

### <p align="center">📊 Dark Themed Detailed Report</p>

<p align="center">
  <img src="screenshots/DarkTheme.png" width="700" alt="Dark Theme Report" />
</p>
<p align="center">Dark themed results page showing overall verdict, summaries, and visualizations.</p>

---

### <p align="center">🔎 Detailed Analysis (Posts List)</p>

<p align="center">
  <img src="screenshots/DetailedAna.png" width="700" alt="Detailed Analysis" />
</p>
<p align="center">Per‑post cards with sentiment breakdown, abnormality probability, and metadata.</p>

---

### <p align="center">📈 Graphs & Trends</p>

<p align="center">
  <img src="screenshots/Graphs.png" width="700" alt="Graphs & Trends" />
</p>
<p align="center">Time series for abnormality and sentiment trends and an average sentiment breakdown chart.</p>

---

### <p align="center">🕘 Analysis History</p>

<p align="center">
  <img src="screenshots/History.png" width="700" alt="Analysis History" />
</p>
<p align="center">Saved analysis history with quick summary blocks and downloadable PDF reports.</p>

---

### <p align="center">🔑 Login / Register</p>

<p align="center">
  <img src="screenshots/Login.png" width="700" alt="Login Page" />
</p>
<p align="center">Simple authentication pages for saving and revisiting analysis history.</p>

---

### <p align="center">🏠 Main Landing</p>

<p align="center">
  <img src="screenshots/Main.png" width="700" alt="Main Landing" />
</p>
<p align="center">Start a new analysis or view project details. Platform selection modal available for choosing Reddit / Instagram / Twitter/X.</p>

---

### <p align="center">📄 Generated PDF Report</p>

<p align="center">
  <img src="screenshots/PDFGenerated.png" width="700" alt="PDF Generated" />
</p>
<p align="center">Professionally formatted PDF summary automatically generated from the analysis.</p>

---

### <p align="center">🔎 Platform Selection</p>

<p align="center">
  <img src="screenshots/PlatformSelection.png" width="700" alt="Platform Selection" />
</p>

---

### <p align="center">📝 Register / Username Entry</p>

<p align="center">
  <img src="screenshots/Register.png" width="700" alt="Register Page" />
</p>
<p align="center">
  <img src="screenshots/UsernameExt.png" width="700" alt="Username Entry" />
</p>

---

# MindSpace — Short Description

MindSpace is a full‑stack web application that analyzes public social media posts for abnormality (risk) indicators and sentiment. It uses a dual‑engine approach (custom Naïve Bayes abnormality model + NLTK VADER sentiment scores) to produce interactive charts, per‑post breakdowns, and downloadable PDF reports. Registered users can save and revisit analysis history.

---

# ✅ Key Features

**Platform & Scraping**

```
• Reddit, Instagram, Twitter/X scraping (public posts)  
• Platform selector modal for quick analysis
```

**Analysis & ML**

```
• Custom Naïve Bayes abnormality model (model_nb.pkl)  
• VADER sentiment (neg/pos/neu)  
• Per‑post probability + sentiment tags
```

**UI & Reports**

```
• Interactive time series & bar charts  
• Per‑post cards with sentiment chips  
• Downloadable, printable PDF reports  
• Light + Dark UI themes
```

**User & History**

```
• Registration & login  
• Saved analyses with thumbnails and PDF links  
• Timestamps and platform metadata
```

---

# 💻 Tech Stack

```
Frontend: HTML, Bootstrap, JS (charts via Chart.js / Matplotlib for PDFs)  
Backend: Python (Flask)  
ML: scikit‑learn (Naïve Bayes), NLTK VADER  
DB: PostgreSQL / SQLite  
PDF: Matplotlib + ReportLab  
Scraping: AsyncPRAW, Apify, Playwright (where applicable)
```

---

# ⚙️ Setup & Quick Start

```bash
git clone https://github.com/SanjayMarathi/MindSpace.git
cd MindSpace
python -m venv venv
# activate venv
source venv/bin/activate  # mac/linux
# or .\venv\Scripts\activate  # windows
pip install -r requirements.txt
python app.py  # or `flask run` depending on entrypoint
```

**Environment**: create a `.env` with keys for any third‑party scraping services and DB connection string.

---

# 🧭 Usage

1. Open the app in a browser.
2. Click **Start New Analysis** → choose platform → enter a public username/profile URL.
3. Wait for scraping and model processing — results page shows charts, per‑post cards and a PDF export button.
4. Register / log in to save the analysis to your history.

Example analysis URL:

```
http://127.0.0.1:5000/analyze?platform=reddit&user=example_user
```

---

# 📁 Project Structure

```
MindSpace/
├── app.py
├── requirements.txt
├── models/
│   └── model_nb.pkl
├── static/
├── templates/
│   ├── index.html
│   ├── results.html
│   ├── history.html
│   └── report_pdf.html
├── scrapers/
│   ├── reddit_scraper.py
│   ├── instagram_scraper.py
│   └── twitter_scraper.py
└── utils/
    ├── pdf_utils.py
    └── viz_utils.py
```

---

# 📝 Developer Notes

* Keep screenshots in `screenshots/` for README rendering on GitHub.
* Place ML model files in `models/` and load them from the analysis pipeline.
* When deploying, ensure Matplotlib fonts are available to avoid PDF rendering issues.
* Respect platform scraping policies and rate limits — use official APIs where required.

---

# 🧑‍💻 Author

```
Sanjay Marathi
GitHub: https://github.com/SanjayMarathi
```

---

If you want this converted exactly into the `README.md` file (ready to drop into the repo), or want a shortened landing README and a separate `DEVELOPER.md` with setup and model details, tell me which and I'll produce the file.
