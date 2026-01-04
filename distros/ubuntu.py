import requests
import re
from bs4 import BeautifulSoup

BASE_URL = "https://releases.ubuntu.com/"
GA_RELEASE_RE = re.compile(r"^(\d{2})\.(\d{2})$")

def get_ga_releases():
    r = requests.get(BASE_URL)
    soup = BeautifulSoup(r.text, "html.parser")

    releases = []
    for link in soup.find_all("a"):
        href = link.get("href", "").strip("/")
        match = GA_RELEASE_RE.match(href)
        if match:
            year = int(match.group(1))
            month = int(match.group(2))
            releases.append({
                "version": href,
                "year": year,
                "month": month
            })

    # Newest → oldest
    releases.sort(key=lambda r: r["version"], reverse=True)
    return releases

def find_latest_lts():
    for r in get_ga_releases():
        if r["month"] == 4 and r["year"] % 2 == 0:
            return r["version"]

    raise RuntimeError("No GA LTS release found")

def find_latest_ga():
    return get_ga_releases()[0]["version"]

def resolve_urls(args):
    if len(args) != 2:
        raise ValueError("Usage: ubuntu <variant> <channel>")

    variant, channel = args

    if variant not in ("desktop", "server"):
        raise ValueError("Variant must be desktop or server")

    if channel not in ("lts", "latest"):
        raise ValueError("Channel must be lts or latest")

    if channel == "lts":
        release = find_latest_lts()
    else:
        release = find_latest_ga()

    iso_name = (
        f"ubuntu-{release}-desktop-amd64.iso"
        if variant == "desktop"
        else f"ubuntu-{release}-live-server-amd64.iso"
    )

    return [f"{BASE_URL}{release}/{iso_name}"]
