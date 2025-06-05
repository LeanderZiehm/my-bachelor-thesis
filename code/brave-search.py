import os
import time
import requests
import pandas as pd
import dotenv
dotenv.load_dotenv()

# ─── CONFIG ─────────────────────────────────────────────────────────────────────
API_KEY = os.getenv("BRAVE_SEARCH_API_KEY")
if not API_KEY:
    raise ValueError("Please set BRAVE_SEARCH_API_KEY as an environment variable.")

QUERY = "Predicting Customer Lifetime Value"
RESULTS_PER_PAGE = 50     # max allowed by this endpoint
TOTAL_RESULTS = 1000      # total desired results
OUTPUT_CSV = "clv_search_results.csv"

BASE_URL = "https://api.search.brave.com/res/v1/web/search"
HEADERS = {
    "Accept": "application/json",
    "Accept-Encoding": "gzip",
    "X-Subscription-Token": API_KEY
}

# ─── FETCH RESULTS ──────────────────────────────────────────────────────────────
all_hits = []
offset = 0

while offset < TOTAL_RESULTS:
    params = {
        "q": QUERY,
        "count": RESULTS_PER_PAGE,
        "offset": offset
    }

    response = requests.get(BASE_URL, headers=HEADERS, params=params)
    if response.status_code != 200:
        raise RuntimeError(f"Brave API error {response.status_code}: {response.text}")

    data = response.json()
    results = data.get("web", {}).get("results", [])

    if not results:
        print(f"No more results at offset {offset}; stopping.")
        break

    for res in results:
        all_hits.append({
            "title": res.get("title"),
            "url": res.get("url"),
            "description": res.get("description"),
            "source": res.get("source"),
            "published": res.get("published"),
            "type": res.get("type")
        })

    offset += RESULTS_PER_PAGE
    time.sleep(1.0)  # Respect Brave API rate limits (1 req/sec on free plan)

print(f"Fetched {len(all_hits)} results total.")

# ─── SAVE TO CSV ────────────────────────────────────────────────────────────────
df = pd.DataFrame(all_hits)
df.to_csv(OUTPUT_CSV, index=False)
print(f"Saved to {OUTPUT_CSV}")
