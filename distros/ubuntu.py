import requests
import re
from bs4 import BeautifulSoup

BASE_URL = "https://releases.ubuntu.com/"
GA_RELEASE_RE = re.compile(r"^(\d{2})\.(\d{2})$")

def get_ga_releases():
    r = requests.get(BASE_URL)
    soup = BeautifulSoup(r.text, "html.parser")
    releases = []
    
    # Find all links on the page
    for link in soup.find_all("a"):
        href = link.get("href", "").strip("/")
        match = GA_RELEASE_RE.match(href)
        if match:
            year = int(match.group(1))
            month = int(match.group(2))
            is_lts = (month == 4) and (year % 2 == 0)
            
            releases.append({
                "version": href,
                "year": year,
                "month": month,
                "is_lts": is_lts
            })
    
    # Sort by version (newest first)
    releases.sort(key=lambda r: (r["year"], r["month"]), reverse=True)
    return releases

def find_latest_lts():
    for r in get_ga_releases():
        if r["is_lts"]:
            return r["version"]
    raise RuntimeError("No LTS release found")

def find_latest_ga():
    releases = get_ga_releases()
    if not releases:
        raise RuntimeError("No GA releases found")
    return releases[0]["version"]

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
    
    # Fetch the release directory page to find the actual ISO filename
    release_url = f"{BASE_URL}{release}/"
    r = requests.get(release_url)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    
    # Look for the ISO file link
    # Pattern: ubuntu-{release}.{point}-desktop-amd64.iso or ubuntu-{release}-desktop-amd64.iso
    if variant == "desktop":
        iso_pattern = re.compile(rf"ubuntu-{re.escape(release)}(\.\d+)?-desktop-amd64\.iso$")
    else:
        iso_pattern = re.compile(rf"ubuntu-{re.escape(release)}(\.\d+)?-live-server-amd64\.iso$")
    
    # Find all matching ISO files
    iso_files = []
    for link in soup.find_all("a"):
        href = link.get("href", "")
        if iso_pattern.match(href):
            # Extract version number for sorting (e.g., "24.04.3" -> (24, 04, 3))
            version_match = re.match(rf"{release}(?:\.(\d+))?", href.replace("ubuntu-", "").replace("-desktop-amd64.iso", "").replace("-live-server-amd64.iso", ""))
            point_release = int(version_match.group(1)) if version_match and version_match.group(1) else 0
            iso_files.append({
                "filename": href,
                "point_release": point_release
            })
    
    if not iso_files:
        raise RuntimeError(f"No ISO file found for {variant} {release}")
    
    # Sort by point release (highest first) and get the latest
    iso_files.sort(key=lambda x: x["point_release"], reverse=True)
    iso_name = iso_files[0]["filename"]
    
    return [f"{BASE_URL}{release}/{iso_name}"]