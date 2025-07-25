import json
import os
import urllib.parse
import requests

DATA_FILE = "data.json"

def load_existing_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def get_work_from_title(title):
    query = urllib.parse.quote(title)
    url = f"https://api.openalex.org/works?search={query}&per_page=1"
    response = requests.get(url)
    response.raise_for_status()
    results = response.json().get("results", [])
    return results[0] if results else None

def get_work_from_doi(doi):
    encoded_doi = urllib.parse.quote(doi)
    url = f"https://api.openalex.org/works/doi:{encoded_doi}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

def extract_openalex_categories(work):
    primary_topic = work.get("primary_topic", {}).get("display_name")
    topics = [t["display_name"] for t in work.get("topics", [])]
    concepts = [c["display_name"] for c in work.get("concepts", [])]

    return {
        "primary topics": [primary_topic] if primary_topic else [],
        "topics": topics,
        "concepts": concepts
    }

def find_existing_entry(data, title, doi):
    for i, entry in enumerate(data):
        if entry.get("title", "").strip().lower() == title.strip().lower():
            return i
        if doi and entry.get("doi", "").strip().lower() == doi.strip().lower():
            return i
    return None

def add_or_update_entry(data, title, doi):
    # First try to get OpenAlex data
    work = get_work_from_doi(doi) if doi else get_work_from_title(title)
    if not work:
        print("❌ No work found.")
        return data

    # Try to find existing entry in local data
    index = find_existing_entry(data, title, doi)

    if index is not None:
        entry = data[index]
        if "openalex categories" not in entry or not entry["openalex categories"]:
            print("🔁 Updating missing OpenAlex categories...")
            entry["openalex categories"] = extract_openalex_categories(work)
            data[index] = entry
            print("✅ Categories added to existing entry.")
        else:
            print("✅ Entry already exists with OpenAlex categories.")
    else:
        print("➕ Adding new entry.")
        new_entry = {
            "title": work.get("title"),
            "doi": work.get("doi", "").replace("https://doi.org/", ""),
            "abstract": work.get("abstract", ""),
            "orkg categories": {
                "domains": [],
                "methods": [],
                "research problems": [],
                "tasks": []
            },
            "papers with code categories": {
                "tasks": [],
                "methods": []
            },
            "openalex categories": extract_openalex_categories(work),
            "openaire categories": {
                "subjects": []
            }
        }
        data.append(new_entry)
        print("✅ New entry added.")

    return data

def main():
    title = input("Enter paper title: ").strip()
    doi = input("Enter DOI (optional): ").strip()

    data = load_existing_data()
    updated_data = add_or_update_entry(data, title, doi)
    save_data(updated_data)

if __name__ == "__main__":
    main()
