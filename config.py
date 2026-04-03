import os

TMDB_API_KEY = os.getenv('TMDB_API_KEY', '6510a58a97f15e281d23de77c93e42ba')
SECRET_KEY = os.getenv('SECRET_KEY', 'cinematch_ai_local_dev')
TMDB_IMAGE_BASE = 'https://image.tmdb.org/t/p/w500'
DEBUG = os.getenv('FLASK_ENV') != 'production'
PORT = int(os.getenv('PORT', 5000))
