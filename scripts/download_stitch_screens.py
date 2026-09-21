import os
import json
import urllib.request

PROJECT_ID = os.environ.get("STITCH_PROJECT_ID", "10495873035675457844")
API_KEY = os.environ.get("STITCH_API_KEY", "")
OUTPUT_DIR = os.path.abspath("docs/stitch_screens")

SCREENS = [
    {
        "id": "0443a3debfc84ed7a925ff6440dfef58",
        "title": "NORMVAULT Institutional Mark",
        "slug": "01_institutional_mark"
    },
    {
        "id": "d59dfdcfa6c4404aa5e9aeacc38a4d68",
        "title": "NORMVAULT - Specification Analysis Workspace",
        "slug": "02_specification_analysis_workspace"
    },
    {
        "id": "4202c06f5f4642a69f6581e23a9987f9",
        "title": "NORMVAULT - Specification Analysis Workspace (Interactive)",
        "slug": "03_specification_analysis_interactive"
    },
    {
        "id": "c36809cf5f9c4ff38980ebea5423f3be",
        "title": "NORMVAULT Dashboard - Procurement Intelligence",
        "slug": "04_dashboard_procurement_intelligence"
    },
    {
        "id": "8e150ae0cfd04f33b7a5550b7df60b72",
        "title": "NORMVAULT - Indian Standards & Dependencies",
        "slug": "05_standards_and_dependencies"
    },
    {
        "id": "df7f77e236d64c0f83487940c01509b2",
        "title": "NORMVAULT - Procurement Decision Package & Traceability",
        "slug": "06_decision_package_traceability"
    }
]

os.makedirs(OUTPUT_DIR, exist_ok=True)

for item in SCREENS:
    screen_id = item["id"]
    slug = item["slug"]
    print(f"\n=======================================================")
    print(f"Fetching {item['title']} ({screen_id})...")
    url = f"https://stitch.googleapis.com/v1/projects/{PROJECT_ID}/screens/{screen_id}"
    req = urllib.request.Request(url, headers={"X-Goog-Api-Key": API_KEY})
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            
            # Save raw metadata
            meta_path = os.path.join(OUTPUT_DIR, f"{slug}.json")
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            print(f"  Saved metadata to {slug}.json")

            # Download htmlCode content
            html_entry = data.get("htmlCode")
            if isinstance(html_entry, dict) and "downloadUrl" in html_entry:
                html_url = html_entry["downloadUrl"]
                mime = html_entry.get("mimeType", "")
                ext = ".svg" if "svg" in mime else ".html"
                code_path = os.path.join(OUTPUT_DIR, f"{slug}{ext}")
                print(f"  Downloading code ({mime}) from {html_url[:60]}... to {slug}{ext}")
                req_code = urllib.request.Request(html_url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req_code) as c_resp:
                    content = c_resp.read()
                    with open(code_path, "wb") as f:
                        f.write(content)
                print(f"  Saved code to {slug}{ext} ({len(content)} bytes)")
            elif isinstance(html_entry, str):
                code_path = os.path.join(OUTPUT_DIR, f"{slug}.html")
                with open(code_path, "w", encoding="utf-8") as f:
                    f.write(html_entry)
                print(f"  Saved raw html to {slug}.html ({len(html_entry)} chars)")

            # Download screenshot image
            screenshot = data.get("screenshot", {})
            if isinstance(screenshot, dict) and "downloadUrl" in screenshot:
                img_url = screenshot["downloadUrl"]
                img_path = os.path.join(OUTPUT_DIR, f"{slug}.png")
                print(f"  Downloading screenshot to {slug}.png...")
                req_img = urllib.request.Request(img_url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req_img) as i_resp:
                    img_data = i_resp.read()
                    with open(img_path, "wb") as f:
                        f.write(img_data)
                print(f"  Saved screenshot to {slug}.png ({len(img_data)} bytes)")

    except Exception as e:
        print(f"  ERROR fetching {screen_id}: {e}")

print("\nAll screens downloaded successfully!")
