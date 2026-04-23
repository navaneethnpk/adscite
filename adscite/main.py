import sys
import argparse
import subprocess
import requests


ADS_TOKEN = "zo1GaYNx0AFqk4CQ1dFSONpgbjYXyGTT0LqIJGL7"
ADS_SEARCH = "https://api.adsabs.harvard.edu/v1/search/query"
ADS_EXPORT = "https://api.adsabs.harvard.edu/v1/export/bibtex"
HEADERS = {"Authorization": f"Bearer {ADS_TOKEN}"}


def fetch_bibcode(identifier: str, is_arxiv: bool = False) -> str:
    """Fetch ADS bibcode from DOI or arXiv ID"""

    if is_arxiv:
        query = f"arXiv:{identifier}"
    else:
        query = f"doi:{identifier}"

    params = {"q": query, "fl": "bibcode", "rows": 1}
    response = requests.get(ADS_SEARCH, headers=HEADERS, params=params)
    response.raise_for_status()

    docs = response.json().get("response", {}).get("docs", [])
    if not docs:
        raise ValueError(f"No ADS record found for '{identifier}'")

    return docs[0]["bibcode"]


def fetch_bibtex(bibcode: str) -> str:
    """Fetch BibTeX for a ADS bibcode"""

    params = {"bibcode": [bibcode]}
    response = requests.post(ADS_EXPORT, headers=HEADERS, json=params)
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
    """ """
    parser = argparse.ArgumentParser(
        description="Fetch and copy ADS BibTeX from DOI or arXiv ID"
    )
    parser.add_argument("identifier", help="DOI or arXiv identifier")
    parser.add_argument(
        "--arxiv", action="store_true", help="treat ID as arXiv identifier"
    )
    args = parser.parse_args()

    try:
        bibcode = fetch_bibcode(args.identifier, is_arxiv=args.arxiv)
        bibtex = fetch_bibtex(bibcode)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

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
