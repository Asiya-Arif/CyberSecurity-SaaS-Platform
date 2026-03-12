from duckduckgo_search import DDGS
try:
    results = DDGS().chat("Hello", model="gpt-4o-mini")
    print(f"Success: {results}")
except Exception as e:
    print(f"Error: {e}")
