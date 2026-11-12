import json
import logging
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from django.conf import settings


logger = logging.getLogger(__name__)


def fetch_google_reviews():
    """Fetch current reviews from Google Places when credentials are configured."""
    api_key = getattr(settings, 'GOOGLE_PLACES_API_KEY', '')
    place_id = getattr(settings, 'GOOGLE_PLACE_ID', '')
    if not api_key or not place_id:
        return []

    url = f'https://places.googleapis.com/v1/places/{quote(place_id, safe="")}?languageCode=en'
    request = Request(
        url,
        headers={
            'X-Goog-Api-Key': api_key,
            'X-Goog-FieldMask': (
                'reviews.rating,reviews.text,reviews.authorAttribution,'
                'reviews.publishTime,reviews.relativePublishTimeDescription'
            ),
        },
    )

    try:
        with urlopen(request, timeout=4) as response:
            place = json.load(response)
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as error:
        logger.error('Google Places reviews could not be fetched: %s', error)
        return []

    if not isinstance(place, dict):
        logger.error('Google Places returned an unexpected response for reviews.')
        return []
    if 'error' in place:
        logger.error('Google Places returned an API error for reviews: %s', place['error'])
        return []

    reviews = []
    google_reviews = place.get('reviews', [])
    if not isinstance(google_reviews, list):
        logger.error('Google Places returned an unexpected reviews value.')
        return []
    for review in google_reviews:
        if not isinstance(review, dict):
            continue
        attribution = review.get('authorAttribution') or {}
        review_text = review.get('text') or {}
        text = review_text.get('text', '') if isinstance(review_text, dict) else ''
        rating = review.get('rating')
        if not text or not isinstance(rating, (int, float)):
            continue
        reviews.append({
            'name': attribution.get('displayName') or 'Google reviewer',
            'message': text,
            'rating': max(1, min(5, round(rating))),
            'photo_url': '',
            'source': 'Google review',
            'author_url': attribution.get('uri', ''),
            'relative_date': review.get('relativePublishTimeDescription', ''),
            'sort_date': review.get('publishTime', ''),
        })
    return reviews
