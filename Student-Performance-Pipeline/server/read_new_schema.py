import pandas as pd
from docx import Document
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(base_dir, "data")

xlsx_path = os.path.join(data_path, "ML_Dataset_Massar.xlsx")
docx_path = os.path.join(data_path, "ML_Documentation.docx")
out_path = os.path.join(base_dir, "schema_output.txt")

with open(out_path, "w", encoding="utf-8") as f:
    f.write("--- EXCEL COLUMNS & FIRST ROW ---\n")
    try:
        df = pd.read_excel(xlsx_path)
        f.write("Columns: " + str(list(df.columns)) + "\n\n")
        f.write("First row sample:\n")
        f.write(str(df.head(1).to_dict(orient="records")[0]) + "\n")
    except Exception as e:
        f.write("Error reading Excel: " + str(e) + "\n")

    f.write("\n--- DOCUMENTATION EXTRACTION ---\n")
    try:
        doc = Document(docx_path)
        text = []
        for para in doc.paragraphs:
            if para.text.strip():
                text.append(para.text.strip())
        f.write("\n".join(text[:80]) + "\n")
    except Exception as e:
        f.write("Error reading Docx: " + str(e) + "\n")
