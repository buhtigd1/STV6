import requests
from datetime import datetime

SOURCE_URL = "https://raw.githubusercontent.com/darkbyteprojects/iptv_png/main/provider_1/live_events.json"

M3U_FILE = "stv6.m3u"
LOG_FILE = "stv6.log"


def format_event_date(stream):
    """
    Ambil tanggal/jam event dari field yang tersedia.
    """

    for field in [
        "date",
        "event_date",
        "start_time",
        "kickoff",
        "time",
        "datetime",
    ]:
        value = stream.get(field)

        if not value:
            continue

        try:
            dt = datetime.fromisoformat(
                str(value).replace("Z", "+00:00")
            )
            return dt.strftime("%d-%m-%Y %H:%M")
        except Exception:
            return str(value)

    return ""


def main():
    response = requests.get(SOURCE_URL, timeout=30)
    response.raise_for_status()

    data = response.json()

    m3u_lines = ["#EXTM3U"]
    total_channels = 0

    for provider in data:

        if not provider.get("visible", True):
            continue

        logo = provider.get("logo", "")

        for stream in provider.get("streams", []):

            name = stream.get("name")
            link = stream.get("link")
            key = stream.get("api")

            if not name or not link:
                continue

            # Tambahkan tanggal event ke nama channel
            event_date = format_event_date(stream)

            if event_date:
                display_name = f"{name} [{event_date}]"
            else:
                display_name = name

            # EXTINF
            m3u_lines.append(
                f'#EXTINF:-1 tvg-logo="{logo}",{display_name}'
            )

            # Kodi DRM Properties
            if key and link.lower().endswith(".mpd"):
                m3u_lines.append(
                    "#KODIPROP:inputstream=inputstream.adaptive"
                )
                m3u_lines.append(
                    "#KODIPROP:inputstream.adaptive.manifest_type=mpd"
                )
                m3u_lines.append(
                    "#KODIPROP:inputstream.adaptive.license_type=clearkey"
                )
                m3u_lines.append(
                    f"#KODIPROP:inputstream.adaptive.license_key={key}"
                )

            # Stream URL
            m3u_lines.append(link)

            total_channels += 1

    with open(M3U_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(m3u_lines))

    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write(f"Source: {SOURCE_URL}\n")
        f.write(f"Generated: {datetime.now():%Y-%m-%d %H:%M:%S}\n")
        f.write(f"Channels: {total_channels}\n")

    print(f"Created: {M3U_FILE}")
    print(f"Created: {LOG_FILE}")
    print(f"Channels: {total_channels}")


if __name__ == "__main__":
    main()
