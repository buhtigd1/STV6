import json
import requests
from datetime import datetime

SOURCE_URL = "https://raw.githubusercontent.com/darkbyteprojects/iptv_png/main/provider_1/channels.json"

M3U_FILE = "stv6.m3u"
LOG_FILE = "stv6.log"

def main():
    r = requests.get(SOURCE_URL, timeout=30)
    r.raise_for_status()

    data = r.json()

    channels = []

    if isinstance(data, list):
        channels = data
    elif isinstance(data, dict):
        if "channels" in data:
            channels = data["channels"]
        else:
            channels = list(data.values())

    m3u_lines = ["#EXTM3U"]
    total = 0

    for ch in channels:
        if not isinstance(ch, dict):
            continue

        name = (
            ch.get("name")
            or ch.get("channel_name")
            or ch.get("title")
            or f"Channel {total+1}"
        )

        url = (
            ch.get("url")
            or ch.get("stream")
            or ch.get("stream_url")
            or ch.get("source")
        )

        logo = ch.get("logo", "")
        group = ch.get("group", "")

        if url:
            extinf = (
                f'#EXTINF:-1 tvg-logo="{logo}" group-title="{group}",{name}'
            )
            m3u_lines.append(extinf)
            m3u_lines.append(url)
            total += 1

    with open(M3U_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(m3u_lines))

    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write(f"Source: {SOURCE_URL}\n")
        f.write(f"Generated: {datetime.now()}\n")
        f.write(f"Channels: {total}\n")

    print(f"Created {M3U_FILE}")
    print(f"Created {LOG_FILE}")
    print(f"Channels: {total}")

if __name__ == "__main__":
    main()
