#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from urllib.parse import parse_qsl
from datetime import datetime
from zoneinfo import ZoneInfo
import re

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
    Source time assumed UTC.
    Convert to Asia/Jakarta (UTC+7)
    """

    try:
        dt = datetime.strptime(
            f"{date_str} {time_str}",
            "%d/%m/%Y %H:%M:%S"
        )

        dt = dt.replace(
            tzinfo=ZoneInfo("UTC")
        )

        dt = dt.astimezone(
            ZoneInfo("Asia/Jakarta")
        )

        return (
            dt.strftime("%H:%M"),
            dt.strftime("%d/%m/%Y")
        )

    except Exception:
        return (
            time_str[:5],
            date_str
        )


def clean_event_name(name):
    """
    Remove leading category tags:
    [Football]
    [Motorsport]
    [Hockey]
    """

    if not name:
        return "Unknown Event"

    name = re.sub(
        r'^\s*(\[[^\]]+\]\s*)+',
        '',
        name
    )

    return name.strip()


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

    lines = [
        "#EXTM3U",
        ""
    ]

    for event in events:

        if not event.get("visible", True):
            continue

        logo = event.get("eventLogo", "")

        event_name = clean_event_name(
            event.get(
                "eventName",
                "Unknown Event"
            )
        )

        date_str = event.get("date", "")
        time_str = event.get(
            "time",
            "00:00:00"
        )

        channel_time, group_title = (
            to_jakarta_time(
                date_str,
                time_str
            )
        )

        for stream in event.get(
            "streams",
            []
        ):

            stream_name = stream.get(
                "name",
                "Unknown"
            )

            stream_url = stream.get(
                "link"
            )

            if not stream_url:
                continue

            lines.append(
                f'#EXTINF:-1 '
                f'group-title="{group_title}" '
                f'tvg-logo="{logo}",'
                f'{channel_time} - '
                f'{event_name} | {stream_name}'
            )

            if stream.get("api"):

                add_drm(
                    lines,
                    stream["api"]
                )

            kodi_props, clean_url = (
                parse_kodi_headers(
                    stream_url
                )
            )

            lines.extend(
                kodi_props
            )

            lines.append(
                clean_url
            )

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

        event_name = clean_event_name(
            event.get(
                "eventName",
                "Unknown Event"
            )
        )

        jakarta_time, jakarta_date = (
            to_jakarta_time(
                event.get("date", ""),
                event.get(
                    "time",
                    "00:00:00"
                )
            )
        )

        streams = event.get(
            "streams",
            []
        )

        log.append(
            f"[INFO] Event: {event_name}"
        )

        log.append(
            f"[INFO] Date: {jakarta_date}"
        )

        log.append(
            f"[INFO] Time: {jakarta_time}"
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

            elif stream.get(
                "tokenApi"
            ):

                token_type = (
                    stream["tokenApi"]
                    .get(
                        "type",
                        "unknown"
                    )
                )

                log.append(
                    f"[TOKEN_API] "
                    f"{name} "
                    f"({token_type})"
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

    print(
        "Downloading source..."
    )

    events = load_events()

    print(
        f"Loaded {len(events)} events"
    )

    with open(
        OUTPUT_M3U,
        "w",
        encoding="utf-8"
    ) as f:
        f.write(
            build_m3u(events)
        )

    with open(
        OUTPUT_LOG,
        "w",
        encoding="utf-8"
    ) as f:
        f.write(
            build_log(events)
        )

    print(
        f"Saved: {OUTPUT_M3U}"
    )

    print(
        f"Saved: {OUTPUT_LOG}"
    )


if __name__ == "__main__":
    main()
