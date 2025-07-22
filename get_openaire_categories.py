import json
import os
import requests
import urllib.parse
import xml.etree.ElementTree as ET

DATA_FILE = "data.json"

def load_existing_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def normalize(text):
    return " ".join(text.lower().split())

def find_existing_entry(data, title, doi):
    norm_title = normalize(title)
    norm_doi = normalize(doi) if doi else None

    for i, entry in enumerate(data):
        entry_title = normalize(entry.get("title", ""))
        entry_doi = normalize(entry.get("doi", ""))

        if norm_title == entry_title or (norm_doi and norm_doi == entry_doi):
            return i
    return None

def get_openaire_by_doi(doi):
    query = urllib.parse.quote_plus(doi)
    url = f"https://api.openaire.eu/search/publications?format=xml&doi={query}"
    return extract_subjects_and_abstract(url)

def get_openaire_by_title(title):
    query = urllib.parse.quote_plus(title)
    url = f"https://api.openaire.eu/search/publications?format=xml&keywords={query}"
    return extract_subjects_and_abstract(url)

def extract_subjects_and_abstract(url):
    response = requests.get(url)
    if response.status_code != 200:
        print("❌ OpenAIRE request failed.")
        return [], None

    try:
        root = ET.fromstring(response.text)
        subjects = set()
        abstract = None

        for result in root.findall(".//result"):
            for subject in result.findall(".//subject"):
                value = subject.text
                if value:
                    subjects.add(value.strip())

            # Try to extract the first non-empty description as abstract
            for desc in result.findall(".//description"):
                if desc.text and not abstract:
                    abstract = desc.text.strip()

        return list(subjects), abstract
    except ET.ParseError as e:
        print("❌ Failed to parse OpenAIRE XML:", e)
        return [], None

def update_entry_with_openaire(data, title, doi):
    index = find_existing_entry(data, title, doi)
    if index is None:
        print("❌ Entry not found in local JSON.")
        return data

    entry = data[index]
    already_has_subjects = "openaire categories" in entry and entry["openaire categories"].get("subjects")
    already_has_abstract = entry.get("abstract", "").strip() != ""

    if already_has_subjects and already_has_abstract:
        print("✅ OpenAIRE data already exists.")
        return data

    print("🔍 Fetching OpenAIRE metadata...")
    subjects, abstract = get_openaire_by_doi(doi) if doi else get_openaire_by_title(title)

    if subjects and not already_has_subjects:
        entry["openaire categories"] = {"subjects": subjects}
        print("✅ Subjects added.")

    if abstract and not already_has_abstract:
        entry["abstract"] = abstract
        print("✅ Abstract added.")

    data[index] = entry
    return data

def main():
    title = input("Enter paper title: ").strip()
    doi = input("Enter DOI (optional): ").strip()

    data = load_existing_data()
    updated_data = update_entry_with_openaire(data, title, doi)
    save_data(updated_data)

if __name__ == "__main__":
    main()
