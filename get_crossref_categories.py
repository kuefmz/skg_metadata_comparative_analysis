import requests
import json
import os

DATA_FILE = "data.json"

def load_json(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_json(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def normalize(text):
    if not isinstance(text, str):
        return ""
    return " ".join(text.lower().split())

def find_entry_by_title(data, title):
    norm_title = normalize(title)
    for i, entry in enumerate(data):
        if normalize(entry.get("title")) == norm_title:
            return i
    return None

def find_entry_by_doi(data, doi):
    for i, entry in enumerate(data):
        if entry.get("doi", "").lower() == doi.lower():
            return i
    return None

def fetch_crossref_subjects(doi=None, title=None):
    headers = {"User-Agent": "phd-categorizer/1.0 (mailto:your@email.com)"}
    if doi:
        url = f"https://api.crossref.org/works/{doi}"
    elif title:
        query = requests.utils.quote(title)
        url = f"https://api.crossref.org/works?query.title={query}&rows=1"
    else:
        return []

    print(url)
    try:
        r = requests.get(url, headers=headers, timeout=15)
        r.raise_for_status()
        data = r.json()
        item = data["message"]["items"][0] if "items" in data["message"] else data["message"]
        subjects = item.get("subject", [])
        return subjects
    except Exception as e:
        print(f"⚠️ Failed to fetch Crossref data: {e}")
        return []

def update_or_add_crossref_categories(data, title, doi=""):
    index = find_entry_by_doi(data, doi) if doi else find_entry_by_title(data, title)

    if index is not None:
        entry = data[index]
        if not entry.get("crossref categories", {}).get("subjects"):
            subjects = fetch_crossref_subjects(doi=doi, title=title)
            entry["crossref categories"] = { "subjects": subjects }
            data[index] = entry
            print(f"✅ Updated Crossref categories for: {title}")
        else:
            print(f"✔️ Already has Crossref categories: {title}")
    else:
        subjects = fetch_crossref_subjects(doi=doi, title=title)
        new_entry = {
            "title": title,
            "doi": doi,
            "abstract": "",
            "orkg categories": {
                "domains": [],
                "methods": [],
                "research problems": [],
                "tasks": []
            },
            "papers with code categories": {
                "tasks": [],
                "methods": [],
                "main_collection_name": [],
                "main_collection_area": []
            },
            "openalex categories": {
                "primary topics": [],
                "topics": [],
                "concepts": []
            },
            "openaire categories": {
                "subjects": []
            },
            "crossref categories": {
                "subjects": subjects
            }
        }
        data.append(new_entry)
        print(f"➕ Added new paper with Crossref categories: {title}")

    return data

def main():
    title = input("Enter paper title: ").strip()
    doi = input("Enter DOI (leave empty if unknown): ").strip()

    data = load_json(DATA_FILE)
    updated_data = update_or_add_crossref_categories(data, title, doi)
    save_json(updated_data, DATA_FILE)

if __name__ == "__main__":
    main()
