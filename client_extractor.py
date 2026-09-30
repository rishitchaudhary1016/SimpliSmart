import pandas as pd
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

# =====================================
# SIGNALS TO MATCH
# (MEDIUM + STRONG ONLY)
# =====================================

TARGET_SIGNALS = {

    # Medium Signals
    "rag",
    "genai",
    "tensorflow",
    "pytorch",
    "llama",
    "deepseek",

    # Strong Signals
    "llm",
    "vllm",
    "tensorrt",
    "mlops",
    "fine tuning",
    "inference",
    "whisper",
    "flux",
    "model serving"
}

# =====================================
# CONFIG
# =====================================

CLIENT_CSV = "output/client_companies.csv"
MAX_WORKERS = 14

# =====================================
# SCRAPE ONE WEBSITE
# =====================================

def scrape_client(row):

    company = row["Company Name"]
    website = row["Website"]

    found_signals = []

    try:

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(
            website,
            headers=headers,
            timeout=10
        )

        text = response.text.lower()

        for signal in TARGET_SIGNALS:

            if signal.lower() in text:
                found_signals.append(signal)

    except Exception:
        pass

    return company, found_signals


# =====================================
# MAIN FUNCTION
# =====================================

def get_client_signals():

    df = pd.read_csv(CLIENT_CSV)

    client_signal_map = {}

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:

        futures = [
            executor.submit(scrape_client, row)
            for _, row in df.iterrows()
        ]

        for future in as_completed(futures):

            company, signals = future.result()

            # Keep only companies having
            # medium/strong signals
            if len(signals) > 0:
                client_signal_map[company] = signals

    return client_signal_map


# =====================================
# TEST MODE
# =====================================

if __name__ == "__main__":

    client_signals = get_client_signals()

    print("\nCLIENT SIGNALS")
    print("=" * 60)

    for company, signals in client_signals.items():

        print(f"\n{company}")

        for signal in signals:
            print(f"  - {signal}")