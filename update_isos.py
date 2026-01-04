import argparse
import importlib
from pathlib import Path
import subprocess

ISO_DIR = Path("isos")
ISO_DIR.mkdir(exist_ok=True)

def parse_line(line):
    parts = line.strip().split()
    if len(parts) < 2:
        raise ValueError("Invalid line format")
    return parts[0], parts[1:]

def download(url):
    filename = url.split("/")[-1]
    output = ISO_DIR / filename
    subprocess.run(["wget", "-c", url, "-O", output], check=True)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true",
                        help="Print URLs instead of downloading")
    args = parser.parse_args()

    with open("distros.txt") as f:
        for line in f:
            if not line.strip() or line.startswith("#"):
                continue

            distro, distro_args = parse_line(line)

            try:
                module = importlib.import_module(f"distros.{distro}")
                urls = module.resolve_urls(distro_args)

                for url in urls:
                    if args.debug:
                        print(f"[DEBUG] {url}")
                    else:
                        print(f"[+] Downloading {url}")
                        download(url)

            except Exception as e:
                print(f"[!] {distro}: {e}")

if __name__ == "__main__":
    main()
