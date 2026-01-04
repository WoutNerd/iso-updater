import requests
import re
from bs4 import BeautifulSoup

BASE_URL = "https://releases.ubuntu.com/"
CDIMAGE_BASE_URL = "https://cdimage.ubuntu.com/"
GA_RELEASE_RE = re.compile(r"^(\d{2})\.(\d{2})$")

FLAVORS = {
    "ubuntu": {
        "base_url": BASE_URL,
        "desktop_pattern": "ubuntu-{version}-desktop-amd64.iso",
        "server_pattern": "ubuntu-{version}-live-server-amd64.iso",
        "has_server": True
    },
    "kubuntu": {
        "base_url": f"{CDIMAGE_BASE_URL}kubuntu/releases/",
        "desktop_pattern": "kubuntu-{version}-desktop-amd64.iso",
        "has_server": False
    },
    "lubuntu": {
        "base_url": f"{CDIMAGE_BASE_URL}lubuntu/releases/",
        "desktop_pattern": "lubuntu-{version}-desktop-amd64.iso",
        "has_server": False
    },
    "xubuntu": {
        "base_url": f"{CDIMAGE_BASE_URL}xubuntu/releases/",
        "desktop_pattern": "xubuntu-{version}-desktop-amd64.iso",
        "has_server": False
    },
    "ubuntu-budgie": {
        "base_url": f"{CDIMAGE_BASE_URL}ubuntu-budgie/releases/",
        "desktop_pattern": "ubuntu-budgie-{version}-desktop-amd64.iso",
        "has_server": False
    },
    "ubuntu-mate": {
        "base_url": f"{CDIMAGE_BASE_URL}ubuntu-mate/releases/",
        "desktop_pattern": "ubuntu-mate-{version}-desktop-amd64.iso",
        "has_server": False
    },
    "ubuntustudio": {
        "base_url": f"{CDIMAGE_BASE_URL}ubuntustudio/releases/",
        "desktop_pattern": "ubuntustudio-{version}-dvd-amd64.iso",
        "has_server": False
    },
    "ubuntu-unity": {
        "base_url": f"{CDIMAGE_BASE_URL}ubuntu-unity/releases/",
        "desktop_pattern": "ubuntu-unity-{version}-desktop-amd64.iso",
        "has_server": False
    },
    "ubuntucinnamon": {
        "base_url": f"{CDIMAGE_BASE_URL}ubuntucinnamon/releases/",
        "desktop_pattern": "ubuntucinnamon-{version}-desktop-amd64.iso",
        "has_server": False
    },
    "ubuntukylin": {
        "base_url": f"{CDIMAGE_BASE_URL}ubuntukylin/releases/",
        "desktop_pattern": "ubuntukylin-{version}-desktop-amd64.iso",
        "has_server": False
    }
}

def get_ga_releases(flavor="ubuntu"):
    base_url = FLAVORS[flavor]["base_url"]
    r = requests.get(base_url)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    releases = []
    for link in soup.find_all("a"):
        href = link.get("href", "").strip("/")
        match = GA_RELEASE_RE.match(href)
        if not match:
            continue

        year = int(match.group(1))
        month = int(match.group(2))
        is_lts = (month == 4) and (year % 2 == 0)

        releases.append({
            "version": href,
            "year": year,
            "month": month,
            "is_lts": is_lts
        })

    releases.sort(key=lambda r: (r["year"], r["month"]), reverse=True)
    return releases

def find_latest_lts(flavor="ubuntu"):
    for r in get_ga_releases(flavor):
        if r["is_lts"]:
            return r["version"]
    raise RuntimeError("No LTS release found")

def get_release_dir(flavor, release):
    base_url = FLAVORS[flavor]["base_url"]
    if flavor == "ubuntu":
        return f"{base_url}{release}/"
    return f"{base_url}{release}/release/"


def flavor_has_iso(flavor, release, variant):
    url = get_release_dir(flavor, release)
    r = requests.get(url)
    if r.status_code != 200:
        return False

    soup = BeautifulSoup(r.text, "html.parser")

    pattern = (
        FLAVORS[flavor]["server_pattern"]
        if variant == "server"
        else FLAVORS[flavor]["desktop_pattern"]
    )

    base = pattern.replace("{version}", release)
    iso_re = re.compile(
        base.replace(
            f"-{release}-",
            rf"-{re.escape(release)}(?:\.\d+)?-"
        )
    )

    return any(
        iso_re.match(link.get("href", ""))
        for link in soup.find_all("a")
    )

def resolve_lts_release(flavor, variant):
    ubuntu_lts = find_latest_lts("ubuntu")

    if flavor == "ubuntu":
        return ubuntu_lts

    if flavor_has_iso(flavor, ubuntu_lts, variant):
        return ubuntu_lts

    for r in get_ga_releases("ubuntu"):
        if r["is_lts"] and r["version"] != ubuntu_lts:
            if flavor_has_iso(flavor, r["version"], variant):
                return r["version"]

    raise RuntimeError(f"No LTS ISO available for {flavor}")

def resolve_latest_release(flavor, variant):
    if flavor == "ubuntu":
        return find_latest_ga("ubuntu")

    # Iterate Ubuntu releases newest → oldest
    for r in get_ga_releases("ubuntu"):
        if flavor_has_iso(flavor, r["version"], variant):
            return r["version"]

    raise RuntimeError(f"No GA ISO available for {flavor}")


def find_latest_ga(flavor="ubuntu"):
    releases = get_ga_releases(flavor)
    if not releases:
        raise RuntimeError("No GA releases found")
    return releases[0]["version"]

def resolve_urls(args):
    if len(args) not in (2, 3):
        raise ValueError(
            "Usage:\n"
            "  ubuntu <variant> <channel>\n"
            "  ubuntu <flavor> <channel>\n"
            "Examples:\n"
            "  ubuntu desktop lts\n"
            "  ubuntu server latest\n"
            "  ubuntu xubuntu lts"
        )

    channel = args[-1]
    if channel not in ("lts", "latest"):
        raise ValueError("Channel must be lts or latest")

    # Defaults
    flavor = "ubuntu"
    variant = "desktop"

    middle = args[0] if len(args) == 2 else args[1]

    if middle in FLAVORS and middle != "ubuntu":
        # ubuntu xubuntu lts
        flavor = middle
        variant = "desktop"
    else:
        # ubuntu desktop lts OR ubuntu server lts
        variant = middle

    if flavor == "ubuntu":
        if variant not in ("desktop", "server"):
            raise ValueError("Ubuntu variant must be desktop or server")
    else:
        if variant != "desktop":
            raise ValueError("Flavors only support desktop")


    if channel == "lts":
        release = resolve_lts_release(flavor, variant)
    else:
        release = resolve_latest_release(flavor, variant)


    url = get_release_dir(flavor, release)
    r = requests.get(url)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    pattern = (
        FLAVORS[flavor]["server_pattern"]
        if variant == "server"
        else FLAVORS[flavor]["desktop_pattern"]
    )

    base = pattern.replace("{version}", release)
    iso_re = re.compile(
        base.replace(
            f"-{release}-",
            rf"-{re.escape(release)}(?:\.\d+)?-"
        )
    )

    isos = []
    for link in soup.find_all("a"):
        href = link.get("href", "")
        if iso_re.match(href):
            m = re.search(rf"{re.escape(release)}\.(\d+)", href)
            isos.append((href, int(m.group(1)) if m else 0))

    if not isos:
        raise RuntimeError(f"No ISO found for {flavor} {variant} {release}")

    isos.sort(key=lambda x: x[1], reverse=True)
    return [f"{url}{isos[0][0]}"]

