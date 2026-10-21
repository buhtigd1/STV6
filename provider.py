import json
from datetime import datetime
import requests

SOURCE_URL = "https://raw.githubusercontent.com/darkbyteprojects/iptv_png/main/provider_1/channels.json"

M3U_FILE = "stv6.m3u"
LOG_FILE = "stv6.log"

data = requests.get(SOURCE_URL, timeout=30).json()

m3u = ["#EXTM3U"]
count = 0

for provider in data:

    group = provider.get("name", "")
    logo = provider.get("logo", "")

    for stream in provider.get("streams", []):

        name = stream.get("name")
        link = stream.get("link")

        if not name or not link:
            continue

        m3u.append(
            f'#EXTINF:-1 tvg-name="{name}" tvg-logo="{logo}" group-title="{group}",{name}'
        )
        m3u.append(link)

        count += 1

with open(M3U_FILE, "w", encoding="utf-8") as f:
    f.write("\n".join(m3u))

with open(LOG_FILE, "w", encoding="utf-8") as f:
    f.write(f"Source : {SOURCE_URL}\n")
    f.write(f"Generated : {datetime.now()}\n")
    f.write(f"Channels : {count}\n")

print(f"Created {M3U_FILE}")
print(f"Created {LOG_FILE}")
print(f"Total channels: {count}")
