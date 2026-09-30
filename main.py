import pdfplumber
import os

# Find PDF inside data folder
data_folder = "data"

pdf_files = [f for f in os.listdir(data_folder) if f.endswith(".pdf")]

if not pdf_files:
    print("No PDF found in data folder")
    exit()

pdf_path = os.path.join(data_folder, pdf_files[0])


all_text = ""

with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        if text:
            all_text += text + "\n"

import pandas as pd

lines = all_text.split("\n")

companies = []

for line in lines:
    line = line.strip()

    if line:
        companies.append(line)

data = []

for line in companies:
    parts = line.rsplit(" ", 1)

    if len(parts) == 2:
        company = parts[0]
        website = parts[1]
    else:
        company = line
        website = ""

    data.append([company, website])

df = pd.DataFrame(data, columns=["Company Name", "Website"])

df.to_csv(
    "output/companies.csv",
    index=False
)

print("Saved companies to output/companies.csv")