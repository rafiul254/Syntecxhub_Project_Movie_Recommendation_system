
# 🎬 CineMatch AI — Intelligent Movie Recommendation Engine

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.3.3-000000?style=for-the-badge&logo=flask&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.5.2-F7931E?style=for-the-badge&logo=scikitlearn&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.2.2-150458?style=for-the-badge&logo=pandas&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge)
![Internship](https://img.shields.io/badge/Syntecxhub-Week%204-8b5cf6?style=for-the-badge)

**A production-grade movie recommendation system built with TF-IDF vectorization, cosine similarity, and a custom hybrid scoring algorithm — deployed as a cinematic Netflix-style Flask web application.**

[🌐 Live Demo](#) · [📊 Analytics Dashboard](#) · [🐛 Report Bug](https://github.com/rafiul254/Syntecxhub_Project_Movie_Recommendation_system/issues)

</div>

---

## ✨ What Makes This Different

Most movie recommenders stop at basic cosine similarity. CineMatch AI goes further with 7 unique features that set it apart:

| Feature | Description |
|---|---|
| 🧬 **Movie DNA Analysis** | Every recommendation shows *why* it was suggested — shared genres, cast members, and director connections displayed as visual tags |
| ⚗️ **Hybrid Scoring Engine** | A custom formula: Content Similarity (65%) + Bayesian Weighted Rating (28%) + Popularity Boost (7%) — better results than raw similarity |
| 🎭 **Mood-Based Discovery** | 6 mood filters (Happy, Thrilling, Romantic, Scary, Thoughtful, Adventurous) dynamically pre-filter the entire dataset by genre clusters before ranking |
| 📊 **Cinematic Analytics Dashboard** | Interactive Chart.js EDA with 5 visualizations: genre distribution, yearly trends, rating spread, runtime analysis, top directors |
| 💜 **Session Watchlist** | Add/remove movies with AJAX toggling — no page reload, persistent across the session |
| 🔍 **Live Autocomplete** | Real-time search suggestions from 5000+ movie titles with 200ms debounce |
| 🖱️ **Clickable Recommendations** | Click any recommended movie to instantly get its own recommendations — chain discovery |

---

## 🏗️ Project Structure

```
Syntecxhub_Movie_Recommender/
│
├── app.py                      # Flask application — all routes & logic
├── train_model.py              # Data processing & model training pipeline
├── config.py                   # API keys & configuration
├── requirements.txt            # Python dependencies
├── render.yaml                 # Render deployment config
├── .gitignore
├── LICENSE
├── README.md
│
├── data/                       # Dataset CSVs 
│   ├── tmdb_5000_movies.csv
│   └── tmdb_5000_credits.csv
│
├── models/                     # Trained model files (not in repo — generated locally)
│   ├── movies.pkl
│   └── similarity.pkl
│
├── static/
│   ├── css/
│   │   └── style.css           # Full dark cinematic UI 
│   └── js/
│       └── main.js             # Autocomplete, watchlist, mood, card click
│
└── templates/
    ├── base.html               # Base layout with navbar, toast, footer
    ├── index.html              # Home — search + mood filters + popular row
    ├── results.html            # Netflix grid with poster cards + DNA tags
    ├── eda.html                # Analytics dashboard with Chart.js
    └── watchlist.html          # Saved movies list
```

---

## ⚙️ Local Setup

### Prerequisites
- Python 3.10 or higher
- pip (latest version)

### Step 1 — Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/Syntecxhub_Movie_Recommender.git
cd Syntecxhub_Movie_Recommender
```

### Step 2 — Create Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### Step 3 — Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4 — Download Dataset
Go to [TMDB 5000 Movie Dataset on Kaggle](https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata) and download:
- `tmdb_5000_movies.csv`
- `tmdb_5000_credits.csv`

Place both files inside the `data/` folder.

### Step 5 — Get TMDB API Key (Free)
1. Register at [themoviedb.org](https://www.themoviedb.org/signup)
2. Go to **Settings → API → Request API Key → Developer**
3. Open `config.py` and paste your key:
```python
TMDB_API_KEY = 'your_api_key_here'
```

### Step 6 — Train the Model
```bash
python train_model.py
```
Wait for: `Done! XXXX movies indexed. Models saved to /models/`

### Step 7 — Run the Application
```bash
python app.py
```
Open [http://localhost:5000](http://localhost:5000)

---

## 🧠 How the Recommendation Engine Works

### Step 1 — Feature Engineering
Text features from each movie are combined into a unified "tags" string:
```
tags = overview + genres + keywords + cast (top 4) + director
```

### Step 2 — TF-IDF Vectorization
An 8000-feature TF-IDF matrix transforms all tags into numerical vectors. Rare but meaningful terms (e.g., a director's name) receive higher weight than common words.

### Step 3 — Cosine Similarity
Pairwise cosine similarity is computed across all movies. The top-50 most similar candidates per movie are pre-indexed for fast retrieval at runtime.

### Step 4 — Hybrid Scoring Formula

```
Score = 0.65 × Cosine Similarity
      + 0.28 × Bayesian Weighted Rating
      + 0.07 × Popularity Boost
```

The Bayesian weighted rating formula:
```
Bayesian = (v / v+m) × R + (m / v+m) × C

Where:
  v = vote count for the movie
  m = minimum votes threshold (60th percentile)
  R = movie's average rating
  C = mean rating across all movies
```

### Step 5 — Mood Filtering
When a mood is selected, the entire dataset is pre-filtered to movies matching the mood's genre cluster. TF-IDF similarity is then computed dynamically within that filtered pool — ensuring mood-relevant results every time.

---

## 🎭 Mood Filter Reference

| Mood | Genres Targeted |
|---|---|
| 😄 Happy | Comedy, Animation, Family, Music |
| ⚡ Thrilling | Action, Thriller, Crime, Adventure |
| 💜 Romantic | Romance, Drama |
| 👻 Scary | Horror, Mystery |
| 🎭 Thoughtful | Drama, Documentary, History |
| 🚀 Adventurous | Adventure, Fantasy, Science Fiction, Western |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.10+, Flask 2.3.3 |
| ML | scikit-learn (TF-IDF, Cosine Similarity), pandas, numpy |
| Frontend | HTML5, CSS3 (600+ lines custom), Vanilla JavaScript |
| Charts | Chart.js 4.4.0 |
| Fonts | Inter, Space Grotesk (Google Fonts) |
| Poster API | TMDB API v3 |
| Dataset | TMDB 5000 Movies (Kaggle) |
| Deployment | Render (free tier) |

---

## 📊 Dataset Info

| Property | Value |
|---|---|
| Source | TMDB 5000 Movies Dataset — Kaggle |
| Movies indexed | ~4800 (after cleaning) |
| Features used | Title, Overview, Genres, Keywords, Cast, Director, Ratings, Popularity |
| Model size | ~50MB (excluded from repo) |

---

## 🌐 Deployment

This project is deployed on **Render** (free tier).

Live URL: `https://cinematch-ai.onrender.com`

### Deploy Steps
1. Push code to GitHub
2. Go to [render.com](https://render.com) → New Web Service
3. Connect GitHub repo
4. Set Build Command: `pip install -r requirements.txt && python train_model.py`
5. Set Start Command: `gunicorn app:app --workers 1 --timeout 120`
6. Add Environment Variables: `TMDB_API_KEY`, `SECRET_KEY`
7. Deploy — takes 5-10 minutes

---

## 📦 Requirements

```
Flask==2.3.3
Werkzeug==2.3.7
scikit-learn==1.5.2
pandas==2.2.2
numpy==1.26.4
requests==2.31.0
gunicorn==21.2.0
```

---

## 👤 Author

**Rafiul Islam**

Currently IoT & Robotics Engineering Student

University of Frontier Technology Bangladesh (UFTB)
Syntecxhub ML Internship

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0077B5?style=flat-square&logo=linkedin)](https://www.linkedin.com/in/rafiul-islam-25sep92004)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-181717?style=flat-square&logo=github)](https://github.com/rafiul254)

---

## 📜 License

This project is licensed under the **MIT License** — see [LICENSE] for details.

---

<div align="center">
Made with ❤️ for Syntecxhub ML Internship 
</div>
