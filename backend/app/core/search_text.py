"""Stable search keys only; original names and descriptions remain untouched."""
import unicodedata

def search_key(value):
    if value is None:return ''
    decomposed=unicodedata.normalize('NFKD',str(value).casefold())
    return ''.join(char for char in decomposed if not unicodedata.combining(char))
