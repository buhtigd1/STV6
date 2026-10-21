#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import requests

SOURCE_URL = "https://raw.githubusercontent.com/darkbyteprojects/iptv_png/main/provider_1/live_events.json"

M3U_FILE = "stv6.m3u"
LOG_FILE = "stv6.log"


def get_json():
    r = requests.get(SOURCE_URL, timeout=30)
    r.raise_for_status()
    return r.json()


def is_drm(stream):
    return bool(stream.get("api"))


def clean_url(url):
    if not url:
        return ""
    return url.replace("&amp;", "&")


def build_m3u(events):
    lines = ["#EXTM3U", ""]

    for event in events:
        if not event.get("visible", True):
            continue

        category = event.get("category", "Live")
        event_name = event.get("eventName", "Unknown Event")
        logo = event.get("eventLogo", "")

        for stream in event.get("streams", []):

            name = stream.get("name", "Unknown")
            url = clean_url(stream.get("link"))

            if not url:
                continue

            lines.append(
                f'#EXTINF:-1 tvg-logo="{logo}",[{category}] {event_name} | {name}'
            )

            if is_drm(stream):
                lines.extend([
                    "#KODIPROP:inputstream=inputstream.adaptive",
                    "#KODIPROP:inputstream.adaptive.manifest_type=mpd",
                    "#KODIPROP:inputstream.adaptive.license_type=clearkey",
                    f'#KODIPROP:inputstream.adaptive.license_key={stream["api"]}'
                ])

            lines.append(url)
            lines.append("")

    return "\n".join(lines)


def build_log(events):
    lines = []

    for event in events:
        if not event.get("visible", True):
            continue

        event_name = event.get("eventName", "Unknown")
        category = event.get("category", "Unknown")

        streams = event.get("streams", [])

        lines.append(f"[INFO] Event: {event_name}")
        lines.append(f"[INFO] Category: {category}")
        lines.append(f"[INFO] Streams Found: {len(streams)}")

        for stream in streams:

            name = stream.get("name", "Unknown")

            if stream.get("api"):
                lines.append(f"[DRM] {name}")

            elif stream.get("tokenApi"):
                token_type = stream["tokenApi"].get("type", "unknown")
                lines.append(f"[TOKEN_API] {name} ({token_type})")

            else:
                lines.append(f"[HLS] {name}")

        lines.append("")

    return "\n".join(lines)


def main():
    print("Downloading source...")

    events = get_json()

    print(f"Loaded {len(events)} events")

    with open(M3U_FILE, "w", encoding="utf-8") as f:
        f.write(build_m3u(events))

    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write(build_log(events))

    print(f"Generated: {M3U_FILE}")
    print(f"Generated: {LOG_FILE}")


if __name__ == "__main__":
    main()
