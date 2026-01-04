import requests
from bs4 import BeautifulSoup
import re

BASE_URL = "https://github.com/home-assistant/operating-system/releases"

BOARDS = {
    "generic-x86-64": "haos_generic-x86-64-{version}.img.xz",
    "generic-aarch64": "haos_generic-aarch64-{version}.img.xz",
    "rpi3": "haos_rpi3-{version}.img.xz",
    "rpi3-64": "haos_rpi3-64-{version}.img.xz",
    "rpi4": "haos_rpi4-{version}.img.xz",
    "rpi4-64": "haos_rpi4-64-{version}.img.xz",
    "rpi5-64": "haos_rpi5-64-{version}.img.xz",
    "yellow": "haos_yellow-{version}.img.xz",
    "green": "haos_green-{version}.img.xz",
    "odroid-c2": "haos_odroid-c2-{version}.img.xz",
    "odroid-c4": "haos_odroid-c4-{version}.img.xz",
    "odroid-m1": "haos_odroid-m1-{version}.img.xz",
    "odroid-n2": "haos_odroid-n2-{version}.img.xz",
    "odroid-xu4": "haos_odroid-xu4-{version}.img.xz",
    "tinker": "haos_tinker-{version}.img.xz",
    "khadas-vim3": "haos_khadas-vim3-{version}.img.xz",
    "ova": "haos_ova-{version}.qcow2.xz",
}


def get_latest_version():
    """Get the latest stable release version by scraping the releases page."""
    r = requests.get(f"{BASE_URL}/latest")
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    
    for tag in soup.find_all(['h1', 'h2', 'a']):
        text = tag.get_text()
        match = re.search(r'Home Assistant OS (\d+\.\d+)', text)
        if match:
            return match.group(1)
    
    raise RuntimeError("Could not find latest version")


def resolve_urls(args):
    if len(args) != 2:
        raise ValueError(f"Usage: homeassistant <board> <channel>\nValid boards: {', '.join(sorted(BOARDS.keys()))}\nChannels: latest")
    
    board, channel = args
    
    if board not in BOARDS:
        raise ValueError(f"Invalid board '{board}'. Valid boards: {', '.join(sorted(BOARDS.keys()))}")
    
    if channel != "latest":
        raise ValueError("Channel must be 'latest'")
    
    version = get_latest_version()
    filename = BOARDS[board].format(version=version)
    
    return [f"{BASE_URL}/download/{version}/{filename}"]