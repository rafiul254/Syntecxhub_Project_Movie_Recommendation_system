from flask import Flask, render_template, request, session, jsonify
import pickle
import pandas as pd
import requests
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from config import TMDB_API_KEY, SECRET_KEY, TMDB_IMAGE_BASE, DEBUG, PORT

app = Flask(__name__)
app.secret_key = SECRET_KEY

movies = pickle.load(open('models/movies.pkl', 'rb'))
similarity_index = pickle.load(open('models/similarity.pkl', 'rb'))

MOOD_MAP = {
    'happy':       {'genres': ['Comedy', 'Animation', 'Family', 'Music'],             'emoji': '😄', 'color': '#f59e0b'},
    'thrilling':   {'genres': ['Action', 'Thriller', 'Crime', 'Adventure'],            'emoji': '⚡', 'color': '#ef4444'},
    'romantic':    {'genres': ['Romance', 'Drama'],                                    'emoji': '💜', 'color': '#ec4899'},
    'scary':       {'genres': ['Horror', 'Mystery'],                                   'emoji': '👻', 'color': '#6366f1'},
    'thoughtful':  {'genres': ['Drama', 'Documentary', 'History'],                     'emoji': '🎭', 'color': '#0ea5e9'},
    'adventurous': {'genres': ['Adventure', 'Fantasy', 'Science Fiction', 'Western'],  'emoji': '🚀', 'color': '#10b981'},
}


def fetch_poster(movie_id):
    if not TMDB_API_KEY:
        return None
    try:
        url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}'
        r = requests.get(url, timeout=4)
        data = r.json()
        path = data.get('poster_path')
        return TMDB_IMAGE_BASE + path if path else None
    except requests.RequestException:
        return None


def bayesian_rating(vote_avg, vote_count):
    c_val = float(movies['vote_average'].mean())
    m_threshold = float(movies['vote_count'].quantile(0.6))
    return (vote_count / (vote_count + m_threshold)) * vote_avg + (m_threshold / (vote_count + m_threshold)) * c_val


def compute_hybrid_score(sim_score, vote_avg, vote_count, popularity):
    b = bayesian_rating(float(vote_avg), float(vote_count)) / 10.0
    p = min(float(popularity) / 200.0, 1.0)
    return round((0.65 * sim_score + 0.28 * b + 0.07 * p) * 100, 1)


def get_match_reasons(source, rec):
    reasons = []
    shared_genres = list(set(source['genres']) & set(rec['genres']))
    for g in shared_genres[:2]:
        reasons.append({'icon': '🎬', 'label': g, 'type': 'genre'})
    shared_cast = list(set(source['cast']) & set(rec['cast']))
    for c in shared_cast[:1]:
        reasons.append({'icon': '⭐', 'label': c, 'type': 'cast'})
    if source['director'] and source['director'] == rec['director']:
        reasons.append({'icon': '🎥', 'label': source['director'], 'type': 'director'})
    return reasons[:4]


def get_recommendations(movie_title, mood=None, top_n=10):
    title_lower = movie_title.strip().lower()
    exact = movies[movies['title'].str.lower() == title_lower]
    if exact.empty:
        partial = movies[movies['title'].str.lower().str.contains(title_lower, na=False, regex=False)]
        if partial.empty:
            return None, []
        source_idx = partial.index[0]
    else:
        source_idx = exact.index[0]

    source = movies.iloc[source_idx].to_dict()

    if mood and mood in MOOD_MAP:
        mood_genres = MOOD_MAP[mood]['genres']
        mood_mask = movies['genres'].apply(lambda g: any(x in g for x in mood_genres))
        mood_pool = movies[mood_mask].index.tolist()
        if source_idx in mood_pool:
            mood_pool.remove(source_idx)

        if not mood_pool:
            return get_recommendations(movie_title, mood=None, top_n=top_n)

        source_tag = movies.loc[source_idx, 'tags']
        pool_tags = movies.loc[mood_pool, 'tags'].tolist()

        tfidf = TfidfVectorizer(max_features=8000, stop_words='english')
        all_tags = [source_tag] + pool_tags
        tfidf_matrix = tfidf.fit_transform(all_tags)
        sim_scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])[0]

        top_indices = sim_scores.argsort()[::-1][:top_n * 3]
        candidates = [(mood_pool[i], sim_scores[i]) for i in top_indices]
    else:
        candidates = similarity_index.get(source_idx, [])

    results = []
    for rec_idx, sim_score in candidates:
        rec = movies.iloc[rec_idx]
        h_score = compute_hybrid_score(sim_score, rec['vote_average'], rec['vote_count'], rec['popularity'])
        reasons = get_match_reasons(source, rec.to_dict())
        overview_text = rec['overview'] if isinstance(rec['overview'], str) else ''
        short_overview = overview_text[:180] + '...' if len(overview_text) > 180 else overview_text

        results.append({
            'title': rec['title'],
            'movie_id': int(rec['movie_id']),
            'year': rec['year'],
            'vote_average': round(float(rec['vote_average']), 1),
            'genres': rec['genres'][:3],
            'director': rec['director'],
            'cast': rec['cast'][:3],
            'runtime': int(rec['runtime']),
            'overview': short_overview,
            'similarity': round(float(sim_score) * 100, 1),
            'hybrid_score': h_score,
            'match_reasons': reasons,
            'poster': None,
        })

        if len(results) >= top_n:
            break

    results.sort(key=lambda x: x['hybrid_score'], reverse=True)
    return source, results


@app.route('/')
def index():
    popular_titles = movies.nlargest(20, 'popularity')['title'].tolist()
    popular_with_posters = []
    for title in popular_titles:
        match = movies[movies['title'] == title]
        if not match.empty:
            m = match.iloc[0]
            popular_with_posters.append({
                'title': title,
                'poster': fetch_poster(int(m['movie_id'])),
                'year': m['year'],
                'vote_average': round(float(m['vote_average']), 1),
            })
    return render_template('index.html', moods=MOOD_MAP, popular=popular_with_posters)


@app.route('/recommend', methods=['POST'])
def recommend():
    title = request.form.get('movie_title', '').strip()
    mood = request.form.get('mood', '').strip() or None
    popular_titles = movies.nlargest(20, 'popularity')['title'].tolist()
    popular_with_posters = []
    for t in popular_titles:
        match = movies[movies['title'] == t]
        if not match.empty:
            m = match.iloc[0]
            popular_with_posters.append({
                'title': t,
                'poster': fetch_poster(int(m['movie_id'])),
                'year': m['year'],
                'vote_average': round(float(m['vote_average']), 1),
            })

    if not title:
        return render_template('index.html', moods=MOOD_MAP, popular=popular_with_posters,
                               error="Please enter a movie title.")

    source, recs = get_recommendations(title, mood)

    if source is None:
        return render_template('index.html', moods=MOOD_MAP, popular=popular_with_posters,
                               error=f"'{title}' not found. Try a different title.")

    source_poster = fetch_poster(int(source['movie_id']))
    for rec in recs:
        rec['poster'] = fetch_poster(rec['movie_id'])

    user_watchlist = session.get('watchlist', [])
    mood_info = MOOD_MAP.get(mood) if mood else None

    return render_template('results.html',
                           source=source,
                           source_poster=source_poster,
                           recs=recs,
                           mood=mood,
                           mood_info=mood_info,
                           watchlist=user_watchlist,
                           moods=MOOD_MAP)


@app.route('/eda')
def eda():
    genre_counts = {}
    for genres in movies['genres']:
        for g in genres:
            genre_counts[g] = genre_counts.get(g, 0) + 1
    genre_sorted = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:15]

    year_series = movies[movies['year'].str.isdigit()]['year'].astype(int)
    year_filtered = year_series[(year_series >= 1990) & (year_series <= 2022)]
    year_counts = year_filtered.value_counts().sort_index()

    rating_bins = pd.cut(movies['vote_average'], bins=[0, 2, 4, 6, 7, 8, 10],
                         labels=['0-2', '2-4', '4-6', '6-7', '7-8', '8-10'])
    rating_counts = rating_bins.value_counts().sort_index()

    runtime_bins = pd.cut(movies['runtime'], bins=[0, 60, 90, 120, 150, 200, 500],
                          labels=['<60', '60-90', '90-120', '120-150', '150-200', '>200'])
    runtime_counts = runtime_bins.value_counts().sort_index()

    director_counts = movies['director'].value_counts().head(10)

    stats = {
        'total': len(movies),
        'avg_rating': round(float(movies['vote_average'].mean()), 2),
        'avg_runtime': int(movies['runtime'].mean()),
        'total_genres': len(genre_counts),
        'genre_labels': [g[0] for g in genre_sorted],
        'genre_values': [g[1] for g in genre_sorted],
        'year_labels': [str(y) for y in year_counts.index.tolist()],
        'year_values': year_counts.values.tolist(),
        'rating_labels': ['0-2', '2-4', '4-6', '6-7', '7-8', '8-10'],
        'rating_values': [int(v) for v in rating_counts.values.tolist()],
        'runtime_labels': ['<60', '60-90', '90-120', '120-150', '150-200', '>200'],
        'runtime_values': [int(v) for v in runtime_counts.values.tolist()],
        'director_labels': director_counts.index.tolist(),
        'director_values': director_counts.values.tolist(),
    }
    return render_template('eda.html', stats=stats, moods=MOOD_MAP)


@app.route('/watchlist')
def watchlist():
    user_watchlist = session.get('watchlist', [])
    wl_movies = []
    for t in user_watchlist:
        match = movies[movies['title'] == t]
        if not match.empty:
            m = match.iloc[0]
            wl_movies.append({
                'title': m['title'],
                'year': m['year'],
                'vote_average': round(float(m['vote_average']), 1),
                'genres': m['genres'][:3],
                'director': m['director'],
                'runtime': int(m['runtime']),
                'poster': fetch_poster(int(m['movie_id'])),
            })
    return render_template('watchlist.html', wl_movies=wl_movies, moods=MOOD_MAP)


@app.route('/watchlist/toggle', methods=['POST'])
def watchlist_toggle():
    title = request.form.get('title', '')
    wl = list(session.get('watchlist', []))
    if title in wl:
        wl.remove(title)
        action = 'removed'
    else:
        wl.append(title)
        action = 'added'
    session['watchlist'] = wl
    return jsonify({'action': action, 'count': len(wl)})


@app.route('/api/search')
def api_search():
    q = request.args.get('q', '').strip().lower()
    if len(q) < 2:
        return jsonify([])
    results = movies[movies['title'].str.lower().str.contains(q, na=False, regex=False)]['title'].head(8).tolist()
    return jsonify(results)


if __name__ == '__main__':
    app.run(debug=DEBUG, port=PORT)
