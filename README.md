# ISO Updater

A simple, extensible Python tool to **automatically fetch the latest stable Linux ISO images** based on a human-readable configuration file.

The project is designed to be:

* easy to understand
* easy to extend
* safe (no betas, snapshots, or daily builds)
* deterministic and predictable

It is intended for users who regularly download Linux ISOs and want a repeatable, scriptable way to keep them up to date.

---

## Features

* Update multiple Linux distro ISOs with one command
* Human-readable configuration file (`distros.txt`)
* Clean separation between:

  * distro logic
  * variants (desktop, server, etc.)
  * channels (lts, latest)
* Snapshot-, beta-, and daily-build safe
* `--debug` mode to preview download URLs without downloading
* Easy to add new distros without modifying the core script

---

## Project Structure

```text
iso-updater/
├── update-isos.py
├── distros.txt
├── requirements.txt
├── isos/
└── distros/
    ├── __init__.py
    ├── ubuntu.py
    ├── debian.py
    └── fedora.py
```

* `update-isos.py` — main entry point
* `distros.txt` — defines which ISOs to fetch
* `distros/` — per-distro URL resolution logic
* `isos/` — downloaded ISO files are stored here

---

## Configuration (`distros.txt`)

Each non-empty line defines **one ISO to fetch** using the format:

```text
<distro> <variant> <channel>
```

Lines starting with `#` are ignored.

### Examples

```txt
# Ubuntu
ubuntu desktop lts
ubuntu server lts
ubuntu server latest

# Debian
debian netinst stable

# Fedora
fedora workstation latest
fedora server latest
```

---

## Supported distros

### Ubuntu

Supports Ubuntu server and dektop on channels lts and latest.

### Fedora

Supports Fedora workstation, kde and server on channel latest.

### Debian

Supports Debian on channal stable

---

## How to Use

### Clone the repository

```bash
git clone https://github.com/WoutNerd/iso-updater
cd iso-updater
```

### Install dependencies

It is recommended to use a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install required packages:

```bash
python3 -m pip install -r requirements.txt
```

### Edit `distros.txt`

Add or remove lines to match the ISOs you want to download.

### Download ISOs

```bash
python3 update-isos.py
```

All ISOs will be downloaded into the `isos/` directory.

---

## Debug / Dry-Run Mode

To **print the resolved download URLs without downloading anything**, run:

```bash
python3 update-isos.py --debug
```

Example output:

```text
[DEBUG] https://releases.ubuntu.com/24.04/ubuntu-24.04-desktop-amd64.iso
[DEBUG] https://download.fedoraproject.org/pub/fedora/linux/releases/40/Server/x86_64/iso/Fedora-Server-dvd-x86_64-40-1.14.iso
```

This is useful for:

* verifying logic
* testing new distro handlers
* scripting or logging

---

## Distro Behavior

### Ubuntu

* Uses **GA releases only**
* LTS selection logic:

  * April releases (`.04`)
  * even years only
  * automatically falls back if a future LTS is not GA yet
* Never uses:

  * snapshots
  * betas
  * daily builds
  * `cdimage.ubuntu.com`

Supported entries:

```txt
ubuntu desktop lts
ubuntu server lts
ubuntu desktop latest
ubuntu server latest
```

---

### Debian

* Uses the official `current/` symlink
* Always tracks **stable**
* No version guessing or scraping heuristics

Supported entries:

```txt
debian netinst stable
```

---

### Fedora

* Uses **GA releases only**
* Avoids Rawhide and Branched automatically
* Supports both Workstation (Live ISO) and Server (DVD ISO)

Supported entries:

```txt
fedora workstation latest
fedora server latest
```

---

## Adding a New Distro

1. Create a new Python file in `distros/`, for example `arch.py`
2. Implement a single function:

```pyt
def resolve_urls(args) -> list[str]:
...
```
3. Add a corresponding line to `distros.txt`
The main script automatically loads the new handler.
