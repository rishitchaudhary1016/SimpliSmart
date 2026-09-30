from client_extractor import get_client_signals
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
    "rag": 3,
    "genai": 3,
    "tensorflow": 3,
    "pytorch": 3,
    "llama": 3,
    "deepseek": 3,
    

    # Strong Signals (10 points)
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
# STRONG SIGNALS
# =====================================

STRONG_SIGNALS = {
    "llm",
    "vllm",
    "tensorrt",
    "mlops",
    "whisper",
    "flux",
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
CLIENT_SIGNAL_MAP = get_client_signals()

# =====================================
# BUYING INTENT EXPLANATION
# =====================================

def generate_buying_intent_reason(found_signals):

    signals = set(found_signals)

    reasons = []

    # Strong Signals

    if "llm" in signals:
        reasons.append(
            "The company references Large Language Models (LLMs), indicating active work on generative AI systems."
        )

    if "vllm" in signals:
        reasons.append(
            "The company mentions vLLM, suggesting a focus on high-performance LLM inference infrastructure."
        )

    if "tensorrt" in signals:
        reasons.append(
            "TensorRT usage indicates efforts toward inference optimization and GPU acceleration."
        )

    if "mlops" in signals:
        reasons.append(
            "MLOps adoption suggests mature machine learning deployment and lifecycle management practices."
        )

    if "inference" in signals:
        reasons.append(
            "Inference-related terminology indicates production deployment of AI models."
        )

    if "model serving" in signals:
        reasons.append(
            "Model serving references suggest operational AI workloads that require scalable infrastructure."
        )

    if "fine tuning" in signals:
        reasons.append(
            "Fine-tuning activity suggests active customization of foundation models."
        )

    if "whisper" in signals:
        reasons.append(
            "Use of Whisper indicates speech AI or audio intelligence workloads."
        )

    if "flux" in signals:
        reasons.append(
            "Flux references indicate interest in generative image AI workloads."
        )

    # Medium Signals

    if "rag" in signals:
        reasons.append(
            "RAG implementation suggests knowledge-grounded LLM applications."
        )

    if "genai" in signals:
        reasons.append(
            "Generative AI initiatives indicate ongoing investment in modern AI capabilities."
        )

    if "llama" in signals:
        reasons.append(
            "Use of open-source models like Llama aligns with AI deployment and optimization needs."
        )

    if "deepseek" in signals:
        reasons.append(
            "DeepSeek adoption indicates experimentation with open-weight foundation models."
        )

    if "tensorflow" in signals:
        reasons.append(
            "TensorFlow usage demonstrates active machine learning development."
        )

    if "pytorch" in signals:
        reasons.append(
            "PyTorch usage demonstrates active AI model development and training."
        )

    if not reasons:
        return (
            "The company shows evidence of AI adoption that may require scalable AI infrastructure."
        )

    return " ".join(reasons[:3])


# =====================================
# MATCH CLIENTS
# =====================================

def get_matched_clients(company_signals):

    matched_clients = []

    company_signals = set(company_signals)

    for client_name, client_signals in CLIENT_SIGNAL_MAP.items():

        overlap = company_signals.intersection(
            set(client_signals)
        )

        if overlap:
            matched_clients.append(client_name)

    return matched_clients

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

    matched_clients = get_matched_clients(
        found_signals
    )

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
        "Matched Client": ", ".join(matched_clients),
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

