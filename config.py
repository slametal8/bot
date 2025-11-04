import os
from dotenv import load_dotenv

load_dotenv()

# API Keys (set these in your .env file)
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
BING_API_KEY = os.getenv('BING_API_KEY')
YANDEX_API_KEY = os.getenv('YANDEX_API_KEY')

# Search Engine Endpoints
SUBMISSION_ENDPOINTS = {
    'google': 'https://indexing.googleapis.com/v3/urlNotifications:publish',
    'bing': 'https://www.bing.com/webmaster/api.svc/json/SubmitUrl',
    'yandex': 'https://webmaster.yandex.com/api/v2',
}

# Rate Limiting
RATE_LIMITS = {
    'google': 200,  # requests per day
    'bing': 100,    # requests per day
    'yandex': 50,   # requests per day
}

# Default Settings
DEFAULT_SETTINGS = {
    'max_workers': 10,
    'batch_size': 50,
    'delay_between_requests': 1,  # seconds
    'delay_between_batches': 30,  # seconds
}
