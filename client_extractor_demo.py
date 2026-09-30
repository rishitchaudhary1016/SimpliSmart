import pandas as pd
import requests

from bs4 import BeautifulSoup
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed

# =====================================
# SIGNAL WEIGHTS
# =====================================

SIGNAL_WEIGHTS = {

    # Weak Signals
    "ai": 1,
    "artificial intelligence": 1,
    "machine learning": 1,

    # Medium Signals
    "rag": 3,
    "genai": 3,
    "tensorflow": 3,
    "pytorch": 3,
    "llama": 3,
    "deepseek": 3,

    # Strong Signals
    "llm": 10,
    "vllm": 10,
    "tensorrt": 10,
    "mlops": 10,
    "fine tuning": 10,
    "inference": 10,
    "whisper": 10,
    "flux": 10,
    "model serving": 10
}

# =====================================
# SETTINGS
# =====================================

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

TIMEOUT = 5
MAX_WORKERS = 14

# =====================================
# DISCOVERY PATHS
# =====================================

DISCOVERY_PATHS = [
    "",
    "/careers",
    "/jobs",
    "/blog",
    "/engineering",
    "/technology",
    "/ai",
    "/ml",
    "/platform",
    "/products",
    "/solutions"
]

# =====================================
# LOAD CLIENT CSV
# =====================================

df = pd.read_csv("output/client_companies.csv")
df.columns = df.columns.str.strip()

# =====================================
# PROCESS ONE COMPANY
# =====================================

def process_company(row):

    company = row["Company Name"]
    website = str(row["Website"]).strip()

    print(f"Scanning: {company}")

    collected_text = ""

    for path in DISCOVERY_PATHS:

        try:

            target_url = urljoin(website, path)

            response = requests.get(
                target_url,
                headers=HEADERS,
                timeout=TIMEOUT
            )

            if response.status_code != 200:
                continue

            soup = BeautifulSoup(
                response.text,
                "html.parser"
            )

            text = soup.get_text(
                separator=" ",
                strip=True
            ).lower()

            collected_text += " " + text

        except Exception:
            continue

    found_signals = []

    for signal in SIGNAL_WEIGHTS:

        if signal in collected_text:
            found_signals.append(signal)

    return {
        "company": company,
        "signals": found_signals
    }

# =====================================
# START SCAN
# =====================================

print("\n====================================")
print("CLIENT SIGNAL SCAN")
print("====================================\n")

results = []

with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:

    futures = [
        executor.submit(process_company, row)
        for _, row in df.iterrows()
    ]

    for future in as_completed(futures):

        try:

            result = future.result()

            if result:
                results.append(result)

        except Exception as e:

            print("Error:", e)

# =====================================
# DISPLAY RESULTS
# =====================================

print("\n====================================")
print("RESULTS")
print("====================================")

for result in results:

    print(f"\nCompany: {result['company']}")

    if result["signals"]:

        print("Signals Found:")

        for signal in result["signals"]:
            print(f"  - {signal}")

    else:

        print("Signals Found: None")

    print("-" * 50)

print("\nSCAN COMPLETE")