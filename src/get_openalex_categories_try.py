import requests
import urllib.parse
import json

def get_work_from_title(title):
    query = urllib.parse.quote(title)
    url = f"https://api.openalex.org/works?search={query}&per_page=1"
    response = requests.get(url)
    response.raise_for_status()
    results = response.json().get("results", [])
    if results:
        return results[0]
    return None

def get_work_from_doi(doi):
    encoded_doi = urllib.parse.quote(doi)
    url = f"https://api.openalex.org/works/doi:{encoded_doi}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

def extract_categories(work):
    # Primary topic
    primary_topic = work.get("primary_topic", {}).get("display_name")

    # Topics list
    topics = [t["display_name"] for t in work.get("topics", [])]

    # Concepts list
    concepts = [c["display_name"] for c in work.get("concepts", [])]

    return {
        "openalex categories": {
            "primary topics": [primary_topic] if primary_topic else [],
            "topics": topics,
            "concepts": concepts
        }
    }

def main():
    identifier = input("Enter DOI or title: ").strip()
    if identifier.lower().startswith("10."):
        work = get_work_from_doi(identifier)
    else:
        work = get_work_from_title(identifier)

    if not work:
        print("❌ No work found for the given input.")
        return

    categories = extract_categories(work)
    print(json.dumps(categories, indent=4))

if __name__ == "__main__":
    main()