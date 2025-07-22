import json
import importlib.util
from pathlib import Path

# --------- Config ---------
DATA_FILE = Path("data.json")
OPENALEX_SCRIPT = "get_openalex_categories.py"
OPENAIRE_SCRIPT = "get_openaire_categories.py"
PWC_SCRIPT = "get_papers_with_code_categories.py"

# --------- Dynamic Module Loader ---------
def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# --------- Load Helper Modules ---------
openalex = load_module("openalex", OPENALEX_SCRIPT)
openaire = load_module("openaire", OPENAIRE_SCRIPT)
pwc = load_module("pwc", PWC_SCRIPT)

# --------- Load Local JSON Data ---------
if DATA_FILE.exists():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
else:
    data = []

# --------- Integration Function ---------
def integrate_sources(title, doi=""):
    global data

    print(f"\n📌 Processing: {title}")

    # --------- OpenAlex ---------
    old_data = json.dumps(data, sort_keys=True)
    data = openalex.add_or_update_entry(data, title, doi)
    if json.dumps(data, sort_keys=True) != old_data:
        print(f"✅ OpenAlex: Updated entry.")
    else:
        print(f"ℹ️ OpenAlex: No new info added.")

    # --------- OpenAIRE ---------
    try:
        old_data = json.dumps(data, sort_keys=True)
        data = openaire.update_entry_with_openaire(data, title, doi)
        if json.dumps(data, sort_keys=True) != old_data:
            print(f"✅ OpenAIRE: Updated entry.")
        else:
            print(f"ℹ️ OpenAIRE: No new info added.")
    except Exception as e:
        print(f"❌ OpenAIRE: Error - {str(e)}")

    # --------- Papers with Code ---------
    try:
        pwc_entry = pwc.find_pwc_paper_by_title(title)
        if not pwc_entry:
            print("❌ Paper not found in Papers with Code.")
        else:
            previous_data = json.dumps(data, sort_keys=True)
            data = pwc.update_or_add_to_data_json(data, pwc_entry)
            if json.dumps(data, sort_keys=True) != previous_data:
                print(f"✅ PwC: Updated entry.")
            else:
                print(f"ℹ️ PwC: No new info added.")
    except Exception as e:
        print(f"❌ PwC: Error - {str(e)}")

    # --------- Save Final Data ---------
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print("💾 Data saved.\n")

# --------- Main Entry Point ---------
if __name__ == "__main__":
    print("📄 Enter the title of the paper:")
    title = input("> ").strip()

    print("🔍 Enter the DOI of the paper (optional, press Enter to skip):")
    doi = input("> ").strip()

    integrate_sources(title, doi)
    print("✅ Integration complete.")
