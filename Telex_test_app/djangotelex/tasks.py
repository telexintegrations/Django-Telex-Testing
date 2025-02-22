import requests
import logging

logger = logging.getLogger(__name__)

def send_to_return_url(return_url, response_data):
    """Sends the processed data to the provided return_url."""
    try:
        response = requests.post(return_url, json=response_data, timeout=5)
        logger.info(f"Return URL response: {response.status_code}, {response.text}")
    except requests.RequestException as e:
        logger.error(f"Failed to send data to return_url: {e}")
