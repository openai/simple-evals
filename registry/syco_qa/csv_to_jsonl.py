# registry/syco_qa/csv_to_jsonl.py

import csv
import json

in_path  = "registry/syco_qa/syco_raw.csv"
out_path = "registry/syco_qa/syco_qa.jsonl"

with open(in_path, encoding="utf-8") as fin, open(out_path, "w", encoding="utf-8") as fout:
    reader = csv.DictReader(fin)
    for row in reader:
        fout.write(json.dumps(row, ensure_ascii=False) + "\n")

print(f"✅ {out_path} を作成しました")
