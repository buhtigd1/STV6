import requests
import logging
import re
from datetime import datetime

SOURCE_URL = "https://raw.githubusercontent.com/shibilvp862/shibilvpm3uplaylist/main/Sports%20Backup.m3u"
OUTPUT_FILE = "stv6.m3u"
LOG_FILE = "stv6.log"

# Configure logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def download(url):
    try:
        logging.info(f"Starting download: {url}")
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        logging.info("Download successful")
        return r.text
    except requests.RequestException as e:
        logging.error(f"Download failed: {e}")
        return ""

def clean_line(line: str) -> str:
    # Remove group-title attribute
    line = re.sub(r'\s*group-title="[^"]+"', '', line, flags=re.IGNORECASE)
    # Remove decorative separator lines (lots of '=' and text in between)
    if re.match(r'^\s*=+\s*.*\s*=+\s*$', line):
        return ""  # drop the line entirely
    return line

def main():
    logging.info("=== Scraper run started ===")
    source = download(SOURCE_URL)

    if not source:
        logging.warning("No content downloaded, exiting.")
        return

    cleaned_lines = ["#EXTM3U"]  # ensure header at the very first line
    for line in source.splitlines():
        if line.startswith("#EXTINF") or re.match(r'^\s*=+', line):
            line = clean_line(line)
        if line.strip():  # skip empty lines after cleaning
            cleaned_lines.append(line)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(cleaned_lines))

    logging.info(f"Playlist saved to {OUTPUT_FILE} with header #EXTM3U")
    logging.info("=== Scraper run finished ===")

if __name__ == "__main__":
    main()
