#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from urllib.parse import parse_qsl
from datetime import datetime
from zoneinfo import ZoneInfo

SOURCE_URL = (
    "https://raw.githubusercontent.com/"
    "darkbyteprojects/iptv_png/main/provider_1/live_events.json"
)

OUTPUT_M3U = "stv6.m3u"
OUTPUT_LOG = "stv6.log"


def load_events():
    r = requests.get(SOURCE_URL, timeout=60)
    r.raise_for_status()
    return r.json()


def to_jakarta_time(date_str, time_str):
    """
    Source assumed UTC.
    Convert to Asia/Jakarta (UTC+7)

    Returns:
        HH:MM
        DD/MM/YYYY
    """

    try:
        dt = datetime.strptime(
            f"{date_str} {time_str}",
            "%d/%m/%Y %H:%M:%S"
        )

        dt = dt.replace(
            tzinfo=ZoneInfo("UTC")
        )

        dt_jakarta = dt.astimezone(
            ZoneInfo("Asia/Jakarta")
        )

        return (
            dt_jakarta.strftime("%H:%M"),
            dt_jakarta.strftime("%d/%m/%Y")
        )

    except Exception:
        return (
            time_str[:5] if time_str else "00:00",
            date_str
        )


def parse_kodi_headers(url):

    if not url:
        return [], ""

    url = url.replace("&amp;", "&")

    if "|" not in url:
        return [], url

    stream_url, headers = url.split("|", 1)

    props = []

    for key, value in parse_qsl(
        headers,
        keep_blank_values=True
    ):

        key = key.lower()

        if key in ("referer", "referrer"):

            props.append(
                f"#KODIPROP:http-referrer={value}"
            )

        elif key == "user-agent":

            props.append(
                f"#KODIPROP:http-user-agent={value}"
            )

        elif key == "origin":

            props.append(
                f"#KODIPROP:http-origin={value}"
            )

        else:

            props.append(
                f"#KODIPROP:http-{key}={value}"
            )

    return props, stream_url


def add_drm(lines, drm_key):

    lines.append(
        "#KODIPROP:inputstream=inputstream.adaptive"
    )

    lines.append(
        "#KODIPROP:inputstream.adaptive.manifest_type=mpd"
    )

    lines.append(
        "#KODIPROP:inputstream.adaptive.license_type=org.w3.clearkey"
    )

    lines.append(
        f"#KODIPROP:inputstream.adaptive.license_key={drm_key}"
    )


def build_m3u(events):

    lines = ["#EXTM3U", ""]

    for event in events:

        if not event.get("visible", True):
            continue

        category = event.get("category", "Live")
        event_name = event.get("eventName", "Unknown Event")
        logo = event.get("eventLogo", "")

        date_str = event.get("date", "")
        time_str = event.get("time", "00:00:00")

        channel_time, group_title = to_jakarta_time(
            date_str,
            time_str
        )

        for stream in event.get("streams", []):

            stream_name = stream.get(
                "name",
                "Unknown"
            )

            stream_url = stream.get("link")

            if not stream_url:
                continue

            lines.append(
                f'#EXTINF:-1 group-title="{group_title}" '
                f'tvg-logo="{logo}",'
                f'{channel_time} - '
                f'[{category}] {event_name} | {stream_name}'
            )

            if stream.get("api"):
                add_drm(
                    lines,
                    stream["api"]
                )

            kodi_props, clean_url = parse_kodi_headers(
                stream_url
            )

            lines.extend(kodi_props)

            lines.append(clean_url)
            lines.append("")

    return "\n".join(lines)


def build_log(events):

    log = []

    total_events = 0
    total_streams = 0

    for event in events:

        if not event.get("visible", True):
            continue

        total_events += 1

        date_str = event.get("date", "")
        time_str = event.get("time", "00:00:00")

        jakarta_time, jakarta_date = to_jakarta_time(
            date_str,
            time_str
        )

        event_name = event.get(
            "eventName",
            "Unknown"
        )

        category = event.get(
            "category",
            "Unknown"
        )

        streams = event.get(
            "streams",
            []
        )

        log.append(
            f"[INFO] Event: {event_name}"
        )

        log.append(
            f"[INFO] Category: {category}"
        )

        log.append(
            f"[INFO] Jakarta Date: {jakarta_date}"
        )

        log.append(
            f"[INFO] Jakarta Time: {jakarta_time}"
        )

        log.append(
            f"[INFO] Streams Found: {len(streams)}"
        )

        for stream in streams:

            total_streams += 1

            name = stream.get(
                "name",
                "Unknown"
            )

            if stream.get("api"):

                log.append(
                    f"[DRM] {name}"
                )

            elif stream.get("tokenApi"):

                token_type = (
                    stream["tokenApi"]
                    .get("type", "unknown")
                )

                log.append(
                    f"[TOKEN_API] {name} ({token_type})"
                )

            else:

                log.append(
                    f"[HLS] {name}"
                )

        log.append("")

    log.append(
        f"[SUMMARY] Events={total_events}"
    )

    log.append(
        f"[SUMMARY] Streams={total_streams}"
    )

    return "\n".join(log)


def main():

    print("Downloading source...")

    events = load_events()

    print(
        f"Loaded {len(events)} events"
    )

    m3u_content = build_m3u(events)
    log_content = build_log(events)

    with open(
        OUTPUT_M3U,
        "w",
        encoding="utf-8"
    ) as f:
        f.write(m3u_content)

    with open(
        OUTPUT_LOG,
        "w",
        encoding="utf-8"
    ) as f:
        f.write(log_content)

    print(
        f"Saved: {OUTPUT_M3U}"
    )

    print(
        f"Saved: {OUTPUT_LOG}"
    )


if __name__ == "__main__":
    main()
