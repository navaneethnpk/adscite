import argparse
import os
import subprocess
import sys
from pathlib import Path

import requests

from .citekey import change_citekey

CONFIG_DIR = Path(os.getenv("XDG_CONFIG_HOME", Path.home() / ".config")) / "adscite"
CONFIG_FILE = CONFIG_DIR / "config"

ADS_SEARCH = "https://api.adsabs.harvard.edu/v1/search/query"
ADS_EXPORT = "https://api.adsabs.harvard.edu/v1/export/bibtex"


def save_token(token: str):
    """Save ADS API token to config file"""

    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(f"ADS_TOKEN={token}\n")
    CONFIG_FILE.chmod(0o600)
    print(f"Token saved to {CONFIG_FILE}")


def load_token() -> str:
    """Load ADS API token from config file"""

    if CONFIG_FILE.exists():
        for line in CONFIG_FILE.read_text().splitlines():
            if line.startswith("ADS_TOKEN="):
                return line.split("=", 1)[1].strip()
    raise RuntimeError("ADS_TOKEN not set. Run: adscite --set-token 'your_token'")


def clean_identifier(identifier: str, is_arxiv: bool = False) -> str:
    """Strip URLs and prefixes, return clean DOI or arXiv ID"""

    clean_id = identifier.strip()

    if is_arxiv:
        clean_id = clean_id.removeprefix("https://arxiv.org/abs/")
    else:
        clean_id = clean_id.removeprefix("https://doi.org/")

    return clean_id


def fetch_bibcode(identifier: str, headers: dict, is_arxiv: bool = False) -> str:
    """Fetch ADS bibcode from DOI or arXiv ID"""

    identifier = clean_identifier(identifier, is_arxiv)

    if is_arxiv:
        query = f"arXiv:{identifier}"
    else:
        query = f"doi:{identifier}"

    params = {"q": query, "fl": "bibcode", "rows": 1}
    response = requests.get(ADS_SEARCH, headers=headers, params=params)
    response.raise_for_status()

    docs = response.json().get("response", {}).get("docs", [])
    if not docs:
        raise ValueError(f"No ADS record found for '{identifier}'")

    return docs[0]["bibcode"]


def fetch_bibtex(bibcode: str, headers: dict) -> str:
    """Fetch BibTeX for a ADS bibcode"""

    params = {"bibcode": [bibcode]}
    response = requests.post(ADS_EXPORT, headers=headers, json=params)
    response.raise_for_status()

    export = response.json().get("export", "")
    if not export:
        raise ValueError(f"ADS returned empty BibTeX for '{bibcode}'")

    return export.strip()


def run_xclip(bibtex: str):
    """Copy BibTeX to clipboard using xclip"""

    subprocess.run(
        ["xclip", "-selection", "clipboard"],
        input=bibtex.encode(),
        check=True,
    )


def main():
    """CLI entry point"""

    parser = argparse.ArgumentParser(
        description="Fetch and copy ADS BibTeX from DOI or arXiv ID"
    )
    parser.add_argument("identifier", nargs="?", help="DOI or arXiv identifier")
    parser.add_argument(
        "--arxiv", action="store_true", help="treat ID as arXiv identifier"
    )
    parser.add_argument("--set-token", metavar="TOKEN", help="save ADS API token")
    args = parser.parse_args()

    if args.set_token:
        save_token(args.set_token)
        sys.exit(0)

    if not args.identifier:
        parser.print_help()
        sys.exit(1)

    try:
        token = load_token()
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    HEADERS = {"Authorization": f"Bearer {token}"}

    try:
        bibcode = fetch_bibcode(args.identifier, HEADERS, is_arxiv=args.arxiv)
        bibtex = fetch_bibtex(bibcode, HEADERS)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Uncomment to use custom citekey (AuthorYYMM) implimentation
    bibtex = change_citekey(bibtex)

    print(f"ADS Bibcode:\n{bibcode}\n")
    print(f"ADS BibTeX:\n{bibtex}\n")

    try:
        run_xclip(bibtex)
        print("BibTeX Copied to clipboard.")
    except FileNotFoundError:
        print("BibTeX copy failed: xclip not found - install xclip", file=sys.stderr)
    except subprocess.CalledProcessError:
        print("BibTeX copy failed: xclip failed", file=sys.stderr)


if __name__ == "__main__":
    main()
