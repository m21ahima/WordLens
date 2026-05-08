"""
dictionary.py - Fetches word definitions from DictionaryAPI.dev (free, no key needed)
Falls back to a secondary source if the first fails.
"""

import requests


API_URL = "https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
TIMEOUT = 5  # seconds


def get_definition(word: str) -> dict:
    """
    Returns a dict:
    {
        "word": str,
        "phonetic": str or "",
        "meanings": [
            {
                "part_of_speech": str,
                "definitions": [str, ...]   # up to 2
            },
            ...                             # up to 2 parts of speech
        ],
        "error": str or None
    }
    """
    try:
        url = API_URL.format(word=word.lower())
        response = requests.get(url, timeout=TIMEOUT)

        if response.status_code == 404:
            return _not_found(word)

        response.raise_for_status()
        data = response.json()

        if not data or not isinstance(data, list):
            return _not_found(word)

        entry = data[0]
        phonetic = _extract_phonetic(entry)
        meanings = _extract_meanings(entry)

        return {
            "word": entry.get("word", word),
            "phonetic": phonetic,
            "meanings": meanings,
            "error": None,
        }

    except requests.exceptions.ConnectionError:
        return _error(word, "No internet connection.")
    except requests.exceptions.Timeout:
        return _error(word, "Request timed out.")
    except Exception as e:
        return _error(word, f"Something went wrong: {e}")


def _extract_phonetic(entry: dict) -> str:
    # Try top-level phonetic first
    phonetic = entry.get("phonetic", "")
    if phonetic:
        return phonetic
    # Try inside phonetics list
    for p in entry.get("phonetics", []):
        if p.get("text"):
            return p["text"]
    return ""


def _extract_meanings(entry: dict) -> list:
    results = []
    for meaning in entry.get("meanings", [])[:2]:  # max 2 parts of speech
        pos = meaning.get("partOfSpeech", "")
        defs = [
            d.get("definition", "")
            for d in meaning.get("definitions", [])[:2]  # max 2 definitions
            if d.get("definition")
        ]
        if pos and defs:
            results.append({"part_of_speech": pos, "definitions": defs})
    return results


def _not_found(word):
    return {
        "word": word,
        "phonetic": "",
        "meanings": [],
        "error": f'No definition found for "{word}".',
    }


def _error(word, msg):
    return {
        "word": word,
        "phonetic": "",
        "meanings": [],
        "error": msg,
    }