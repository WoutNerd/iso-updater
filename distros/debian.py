import requests
from bs4 import BeautifulSoup

BASE_URL = "https://cdimage.debian.org/debian-cd/current/amd64/iso-cd/"

def resolve_urls(args):
    if args != ["netinst", "stable"]:
        raise ValueError("Supported: debian netinst stable")

    r = requests.get(BASE_URL)
    soup = BeautifulSoup(r.text, "html.parser")

    for link in soup.find_all("a"):
        href = link.get("href", "")
        if href.endswith("-netinst.iso"):
            return [BASE_URL + href]

    raise RuntimeError("Debian netinst ISO not found")
