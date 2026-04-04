import os

TMDB_API_KEY = os.getenv('TMDB_API_KEY', '6510a58a97f15e281d23de77c93e42ba')
SECRET_KEY = os.getenv('SECRET_KEY', 'cinematch_2026')
TMDB_IMAGE_BASE = 'https://image.tmdb.org/t/p/w500'
DEBUG = False
PORT = int(os.getenv('PORT', 7860))
