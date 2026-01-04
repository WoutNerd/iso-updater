import requests
from bs4 import BeautifulSoup

BASE_URL = "https://download.fedoraproject.org/pub/fedora/linux/releases/"

def get_latest_release():
    r = requests.get(BASE_URL)
    soup = BeautifulSoup(r.text, "html.parser")

    versions = []
    for link in soup.find_all("a"):
        href = link.get("href", "")
        if href.strip("/").isdigit():
            versions.append(int(href.strip("/")))

    if not versions:
        raise RuntimeError("No Fedora GA releases found")

    return max(versions)

def find_iso(iso_dir, required_tokens):
    r = requests.get(iso_dir)
    soup = BeautifulSoup(r.text, "html.parser")

    for link in soup.find_all("a"):
        href = link.get("href", "")

        if (
            href.startswith("Fedora-")
            and href.endswith(".iso")
            and all(token in href for token in required_tokens)
        ):
            return iso_dir + href

    raise RuntimeError("ISO not found")

def resolve_urls(args):
    if len(args) != 2:
        raise ValueError("Usage: fedora <variant> <channel>")

    variant, channel = args

    if channel != "latest":
        raise ValueError("Fedora only supports channel: latest")

    release = get_latest_release()

    if variant == "workstation":
        iso_dir = f"{BASE_URL}{release}/Workstation/x86_64/iso/"
        tokens = ["Workstation", "Live", "x86_64"]

    elif variant == "server":
        iso_dir = f"{BASE_URL}{release}/Server/x86_64/iso/"
        tokens = ["Server", "dvd", "x86_64"]

    else:
        raise ValueError("Variant must be workstation or server")

    return [find_iso(iso_dir, tokens)]
