#!/usr/bin/env python3
"""Quick viewer for pull_request_project.yaml"""
import yaml
from pathlib import Path

def load_project(path: str = "pull_request_project.yaml") -> dict:
    with open(Path(path), "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

if __name__ == "__main__":
    proj = load_project()
    print(f"📂  {proj['project']['name']}")
    for key, plan in proj["plans"].items():
        print(f" ├─ {plan['title']} ({key})  [{plan['status']}]")
        for t in plan["tasks"]:
            print(f" │   • {t['id']}  {t['title']}  → {t['status']}")