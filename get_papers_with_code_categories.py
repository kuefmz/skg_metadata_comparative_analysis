import json
import os

DATA_FILE = "data.json"
PWC_FILE = "papers_with_abstracts.json"

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

def find_pwc_paper_by_title(title):
    pwc_data = load_json(PWC_FILE)
    norm_title = normalize(title)
    for entry in pwc_data:
        if normalize(entry.get("title")) == norm_title:
            # print(entry)
            return entry
    return None

def extract_pwc_info(pwc_entry):
    tasks = pwc_entry.get("tasks", []) or []
    methods_raw = pwc_entry.get("methods", []) or []

    method_names = []
    collection_names = []
    collection_areas = []

    for m in methods_raw:
        if not isinstance(m, dict):
            continue
        name = m.get("name")
        if isinstance(name, str) and name.strip():
            method_names.append(name)

        coll = m.get("main_collection", {})
        if isinstance(coll, dict):
            cname = coll.get("name")
            carea = coll.get("area")
            if isinstance(cname, str) and cname.strip():
                collection_names.append(cname)
            if isinstance(carea, str) and carea.strip():
                collection_areas.append(carea)

    return {
        "abstract": pwc_entry.get("abstract") or "",
        "papers with code categories": {
            "tasks": tasks,
            "methods": list(set(method_names)),
            "main_collection_name": list(set(collection_names)),
            "main_collection_area": list(set(collection_areas))
        }
    }

def update_or_add_to_data_json(data, pwc_entry):
    title = pwc_entry.get("title")
    if not isinstance(title, str) or not title.strip():
        return data

    index = find_entry_by_title(data, title)
    info = extract_pwc_info(pwc_entry)

    if index is not None:
        entry = data[index]

        if not entry.get("abstract"):
            entry["abstract"] = info["abstract"]

        if "papers with code categories" not in entry or not entry["papers with code categories"].get("tasks"):
            entry["papers with code categories"] = info["papers with code categories"]

        data[index] = entry
        print(f"🔁 Updated existing entry: {title}")
    else:
        new_entry = {
            "title": title,
            "doi": "",
            "abstract": info["abstract"],
            "orkg categories": {
                "domains": [],
                "methods": [],
                "research problems": [],
                "tasks": []
            },
            "papers with code categories": info["papers with code categories"],
            "openalex categories": {
                "primary topics": [],
                "topics": [],
                "concepts": []
            },
            "openaire categories": {
                "subjects": []
            },
            "crossref categories": {
                "subjects": []
            }
        }
        data.append(new_entry)
        print(f"➕ Added new entry: {title}")

    return data

def main():
    search_title = input("Enter title to search in Papers with Code: ").strip()
    pwc_entry = find_pwc_paper_by_title(search_title)

    if not pwc_entry:
        print("❌ Paper not found in Papers with Code.")
        return

    data = load_json(DATA_FILE)
    updated_data = update_or_add_to_data_json(data, pwc_entry)
    save_json(updated_data, DATA_FILE)

if __name__ == "__main__":
    main()
