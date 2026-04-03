import os

def download_data():
    if not os.path.exists('data/tmdb_5000_movies.csv'):
        print("Dataset not found. Please download from Kaggle and place in data/ folder.")
        exit(1)

import pandas as pd
import numpy as np
import ast
import pickle
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def parse_names(obj, key='name', limit=None):
    try:
        lst = ast.literal_eval(obj)
        result = [item[key] for item in lst]
        return result[:limit] if limit else result
    except Exception:
        return []


def get_director(crew_str):
    try:
        crew = ast.literal_eval(crew_str)
        for person in crew:
            if person.get('job') == 'Director':
                return person['name']
        return ''
    except Exception:
        return ''


def normalize(name):
    return name.replace(' ', '').lower()


def build_tags(row):
    overview = row['overview'].split() if isinstance(row['overview'], str) else []
    genres = [normalize(g) for g in row['genres']]
    keywords = [normalize(k) for k in row['keywords']]
    cast = [normalize(c) for c in row['cast']]
    director = [normalize(row['director'])] if row['director'] else []
    return ' '.join(overview + genres + keywords + cast + director)


def main():
    print("Loading datasets...")
    movies_df = pd.read_csv('data/tmdb_5000_movies.csv', encoding='utf-8', engine='python')
    credits_df = pd.read_csv('data/tmdb_5000_credits.csv', encoding='utf-8', engine='python')

    credits_df = credits_df.rename(columns={'movie_id': 'id'})
    movies_df = movies_df.merge(credits_df[['id', 'cast', 'crew']], on='id')

    cols = ['id', 'title', 'overview', 'genres', 'keywords', 'cast', 'crew',
            'vote_average', 'vote_count', 'popularity', 'release_date', 'runtime']
    movies_df = movies_df[cols].copy()
    movies_df.dropna(subset=['overview'], inplace=True)
    movies_df.reset_index(drop=True, inplace=True)

    print("Extracting features...")
    movies_df['genres'] = movies_df['genres'].apply(lambda x: parse_names(x))
    movies_df['keywords'] = movies_df['keywords'].apply(lambda x: parse_names(x, limit=10))
    movies_df['cast'] = movies_df['cast'].apply(lambda x: parse_names(x, limit=4))
    movies_df['director'] = movies_df['crew'].apply(get_director)
    movies_df['year'] = movies_df['release_date'].apply(
        lambda x: str(x)[:4] if pd.notna(x) and str(x) != 'nan' else 'N/A'
    )
    movies_df['runtime'] = movies_df['runtime'].fillna(0).astype(int)
    movies_df['tags'] = movies_df.apply(build_tags, axis=1)

    final_df = movies_df[['id', 'title', 'tags', 'overview', 'genres', 'cast',
                           'director', 'vote_average', 'vote_count', 'popularity',
                           'year', 'runtime']].copy()
    final_df = final_df.rename(columns={'id': 'movie_id'})
    final_df.reset_index(drop=True, inplace=True)

    print("Computing TF-IDF vectors (8000 features)...")
    tfidf = TfidfVectorizer(max_features=8000, stop_words='english')
    tfidf_matrix = tfidf.fit_transform(final_df['tags'])

    print("Computing cosine similarity matrix...")
    full_sim = cosine_similarity(tfidf_matrix)

    print("Building top-50 similarity index per movie...")
    similarity_index = {}
    for i in range(len(final_df)):
        sim_scores = list(enumerate(full_sim[i]))
        sim_scores_sorted = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:51]
        similarity_index[i] = sim_scores_sorted

    os.makedirs('models', exist_ok=True)
    pickle.dump(final_df, open('models/movies.pkl', 'wb'))
    pickle.dump(similarity_index, open('models/similarity.pkl', 'wb'))

    print(f"\nDone! {len(final_df)} movies indexed.")
    print("Models saved to /models/")


if __name__ == '__main__':
    main()
