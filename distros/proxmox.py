import requests
import re
from bs4 import BeautifulSoup

BASE_URL = "https://enterprise.proxmox.com/iso/"

# Map of products and their file patterns
PRODUCTS = {
    "ve": r"proxmox-ve_(\d+\.\d+)-\d+\.iso",
    "backup-server": r"proxmox-backup-server_(\d+\.\d+)-\d+\.iso",
    "mail-gateway": r"proxmox-mail-gateway_(\d+\.\d+)-\d+\.iso",
    "datacenter-manager": r"proxmox-datacenter-manager_(\d+\.\d+)-\d+\.iso",
}


def get_latest_version(product):
    """Get the latest version for a given product."""
    r = requests.get(BASE_URL)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    
    pattern = re.compile(PRODUCTS[product])
    versions = []
    
    for link in soup.find_all("a"):
        href = link.get("href", "")
        match = pattern.match(href)
        if match:
            version = match.group(1)
            versions.append({
                "version": version,
                "filename": href,
                "major": int(version.split(".")[0]),
                "minor": int(version.split(".")[1])
            })
    
    if not versions:
        raise RuntimeError(f"No versions found for {product}")
    
    # Sort by major, then minor version (newest first)
    versions.sort(key=lambda v: (v["major"], v["minor"]), reverse=True)
    return versions[0]["filename"]


def resolve_urls(args):
    if len(args) != 2:
        raise ValueError(f"Usage: proxmox <product> <channel>\nValid products: {', '.join(sorted(PRODUCTS.keys()))}\nChannels: latest")
    
    product, channel = args
    
    if product not in PRODUCTS:
        raise ValueError(f"Invalid product '{product}'. Valid products: {', '.join(sorted(PRODUCTS.keys()))}")
    
    if channel != "latest":
        raise ValueError("Channel must be 'latest'")
    
    filename = get_latest_version(product)
    
    return [f"{BASE_URL}{filename}"]