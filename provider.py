import requests
from datetime import datetime

SOURCE_URL = "https://raw.githubusercontent.com/darkbyteprojects/iptv_png/main/provider_1/channels.json"

M3U_FILE = "stv6.m3u"
LOG_FILE = "stv6.log"


def build_playlist():
    response = requests.get(SOURCE_URL, timeout=30)
    response.raise_for_status()

    data = response.json()

    m3u = ["#EXTM3U"]
    total = 0

    for provider in data:

        if not provider.get("visible", True):
            continue

        group = provider.get("name", "")
        logo = provider.get("logo", "")

        for stream in provider.get("streams", []):

            name = stream.get("name")
            link = stream.get("link")
            key = stream.get("api")

            if not name or not link:
                continue

            # Kodi Properties untuk stream DRM/ClearKey
            if key and str(link).endswith(".mpd"):
                m3u.append(
                    "#KODIPROP:inputstream=inputstream.adaptive"
                )
                m3u.append(
                    "#KODIPROP:inputstream.adaptive.manifest_type=mpd"
                )
                m3u.append(
                    "#KODIPROP:inputstream.adaptive.license_type=org.w3.clearkey"
                )
                m3u.append(
                    f"#KODIPROP:inputstream.adaptive.license_key={key}"
                )

            m3u.append(
                f'#EXTINF:-1 tvg-logo="{logo}" group-title="{group}",{name}'
            )
            m3u.append(link)

            total += 1

    with open(M3U_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(m3u))

    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write(f"Source: {SOURCE_URL}\n")
        f.write(f"Generated: {datetime.now()}\n")
        f.write(f"Channels: {total}\n")

    print(f"Created: {M3U_FILE}")
    print(f"Created: {LOG_FILE}")
    print(f"Total channels: {total}")


if __name__ == "__main__":
    build_playlist()
