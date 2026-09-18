import requests
import re
from datetime import datetime

SOURCE_URL = "https://raw.githubusercontent.com/raid35/docs/main/SPORT_UROP.m3u"
OUTPUT_FILE = "stv2.m3u"
LOG_FILE    = "stv2.log"

HEADER = '#EXTM3U url-tvg="https://raw.githubusercontent.com/didikc/EPG-8/main/epg.xml.gz"'

def log(message):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().isoformat()}] {message}\n")
    print(message)

def download(url):
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        return r.text
    except requests.RequestException as e:
        log(f"❌ Failed to download: {url}\n{e}")
        return ""

def clean_extinf(line):
    # Remove ONLY group-title, keep tvg-id and tvg-logo intact
    line = re.sub(r'\s*group-title="[^"]+"', '', line, flags=re.IGNORECASE)

    # Ensure proper comma separation: tvg-logo ends before comma
    if 'tvg-logo=' in line and ',' in line:
        # Split once at the first comma after attributes
        parts = line.split(',', 1)
        if len(parts) == 2:
            line = parts[0].strip() + "," + parts[1].strip()
    return line

def main():
    log("Downloading playlist...")
    source = download(SOURCE_URL)
    if not source:
        log("No content downloaded.")
        return

    log("Processing playlist...")
    lines = source.splitlines()
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(HEADER + "\n")
        for line in lines:
            if line.startswith("#EXTINF"):
                f.write(clean_extinf(line) + "\n")
            else:
                f.write(line + "\n")

    log(f"✅ Done: saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
