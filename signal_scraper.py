import pandas as pd
import requests
import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
from openpyxl.styles import Alignment

# =====================================
# SIGNAL WEIGHTS
# =====================================

SIGNAL_WEIGHTS = {

    # Weak Signals (1 point)
    "ai": 1,
    "artificial intelligence": 1,
    "machine learning": 1,

    # Medium Signals (3 points)
    "mlops": 3,
    "genai": 3,
    "tensorflow": 3,
    "pytorch": 3,
    "llama": 3,
    "deepseek": 3,
    "whisper": 3,
    "flux": 3,

    # Strong Signals (10 points)
    "llm": 10,
    "vllm": 10,
    "tensorrt": 10,
    "rag": 10,
    "fine tuning": 10,
    "inference": 10,
    "model serving": 10
}

# =====================================
# STRONG SIGNALS
# =====================================

STRONG_SIGNALS = {
    "llm",
    "vllm",
    "tensorrt",
    "rag",
    "fine tuning",
    "inference",
    "model serving"
}

# =====================================
# DISCOVERY PATHS
# =====================================

DISCOVERY_PATHS = [

    # Homepage
    "",

    # Careers
    "/careers",
    "/career",
    "/jobs",
    "/job",
    "/join-us",
    "/work-with-us",
    "/openings",
    "/vacancies",
    "/opportunities",
    "/current-openings",
    "/positions",
    "/hiring",

    # Company / Tech Pages
    "/blog",
    "/engineering",
    "/technology",
    "/tech",
    "/platform",
    "/ai",
    "/machine-learning",
    "/ml",
    "/products",
    "/product",
    "/solutions",
    "/solution"
]

# =====================================
# SETTINGS
# =====================================

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

TIMEOUT = 5
MAX_WORKERS = 50
TOP_COMPANIES = 15

# =====================================
# LOAD COMPANIES
# =====================================

df = pd.read_csv("output/companies.csv")

# =====================================
# BUYING INTENT EXPLANATION
# =====================================

def generate_buying_intent_reason(found_signals):

    signals = set(found_signals)

    if {"llm", "rag", "inference"} & signals:

        return (
            "Company appears to be building production-grade LLM "
            "applications involving retrieval and inference workloads, "
            "which aligns strongly with Simply Smart's AI deployment ICP."
        )

    elif {"llm", "vllm", "tensorrt"} & signals:

        return (
            "Company shows evidence of LLM deployment and inference "
            "optimization activities, indicating potential demand for "
            "AI infrastructure and serving solutions."
        )

    elif {"genai", "llama", "deepseek"} & signals:

        return (
            "Company is investing in Generative AI and open-source "
            "foundation models, making it a relevant prospect for "
            "model deployment and scaling platforms."
        )

    elif {"mlops", "tensorflow", "pytorch"} & signals:

        return (
            "Company demonstrates mature machine learning engineering "
            "practices and model lifecycle management, suggesting a "
            "need for scalable AI operations infrastructure."
        )

    elif {"rag", "model serving"} & signals:

        return (
            "Company appears to be deploying AI systems into production "
            "environments, closely matching Simply Smart's target "
            "customer profile."
        )

    elif {"ai", "artificial intelligence", "machine learning"} & signals:

        return (
            "Company shows active AI and machine learning adoption, "
            "which could evolve into demand for AI deployment and "
            "optimization solutions."
        )

    else:

        return (
            "Company exhibits indicators of AI technology adoption "
            "that may create future demand for AI infrastructure "
            "platforms."
        )

# =====================================
# PROCESS ONE COMPANY
# =====================================

def process_company(row):

    company = row["Company Name"]
    website = row["Website"]

    print(f"Checking {company}")

    base_url = "https://" + str(website).strip()

    collected_text = ""
    source_urls = []

    for path in DISCOVERY_PATHS:

        try:

            target_url = urljoin(base_url, path)

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

            if len(text) < 300:
                continue

            collected_text += " " + text

            if target_url not in source_urls:
                source_urls.append(target_url)

        except Exception:
            continue

    if not collected_text:
        return None

    found_signals = []
    score = 0
    strong_signal_count = 0

    for signal, weight in SIGNAL_WEIGHTS.items():

        if signal in collected_text:

            found_signals.append(signal)
            score += weight

            if signal in STRONG_SIGNALS:
                strong_signal_count += 1


    if not found_signals:
        return None

    buying_intent_reason = generate_buying_intent_reason(
            found_signals
        )

    print(
        f"  Match found: {company} | Score = {score}"
    )

    return {
        "Company Name": company,
        "Signal Found": ", ".join(found_signals),
        "Why It Suggests Buying Intent": buying_intent_reason,
        "Score": score,
        "Source URL": " | ".join(source_urls),

        # Internal tie-breaker only
        "_strong_signal_count": strong_signal_count
    }

# =====================================
# PARALLEL EXECUTION
# =====================================

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

        except Exception:
            continue

# =====================================
# CREATE OUTPUT DATAFRAME
# =====================================

output_df = pd.DataFrame(results)

if not output_df.empty:

    # Sort by Score
    # Tie-break using Strong Signal Count

    output_df = output_df.sort_values(
        by=["Score", "_strong_signal_count"],
        ascending=[False, False]
    )

    # Keep only Top 15 companies

    output_df = output_df.head(TOP_COMPANIES)

    # Remove internal tie-breaker column

    output_df = output_df.drop(
        columns=["_strong_signal_count"]
    )


# =====================================
# SAVE OUTPUT
# =====================================

with pd.ExcelWriter(
    "output/icp_signals_output.xlsx",
    engine="openpyxl"
) as writer:

    output_df.to_excel(
        writer,
        index=False,
        sheet_name="Results"
    )

    worksheet = writer.sheets["Results"]

    for column in worksheet.columns:

        max_length = 0
        column_letter = column[0].column_letter

        for cell in column:

            try:
                if cell.value:
                    max_length = max(
                        max_length,
                        len(str(cell.value))
                    )
            except:
                pass

        if column_letter == "C":
            worksheet.column_dimensions["C"].width = 80
        else:
            worksheet.column_dimensions[
                column_letter
            ].width = min(max_length + 5, 100)

    for cell in worksheet[1]:
        cell.font = cell.font.copy(bold=True)

    for row in worksheet.iter_rows():

        for cell in row:

            cell.alignment = Alignment(
                wrap_text=True,
                vertical="top"
            )

# =====================================
# DONE
# =====================================

print("\n==========================")
print("SCRAPING COMPLETE")
print("==========================")

print(
    f"Total Matched Companies: {len(results)}"
)

if not output_df.empty:

    print(
        f"Top Companies Saved: {len(output_df)}"
    )

    print(
        f"Highest Score: {output_df['Score'].max()}"
    )

print(
    "Output saved to: output/icp_signals_output.xlsx"
)

output_file = os.path.abspath(
    "output/icp_signals_output.xlsx"
)

os.startfile(output_file)

