import re

MONTH_MAP = {
    "jan": "01",
    "feb": "02",
    "mar": "03",
    "apr": "04",
    "may": "05",
    "jun": "06",
    "jul": "07",
    "aug": "08",
    "sep": "09",
    "oct": "10",
    "nov": "11",
    "dec": "12",
}


def extract_authors(bibtex: str) -> str:
    """Extract full author field value by counting braces"""

    start = re.search(r"author\s*=\s*\{", bibtex)
    if not start:
        return ""

    depth = 0
    result = []
    for char in bibtex[start.end() :]:
        if char == "{":
            depth += 1
        elif char == "}":
            if depth == 0:
                break
            depth -= 1
        result.append(char)

    return "".join(result)


def clean_name(name: str) -> str:
    """Handles accented letters in the LaTeX"""

    name = re.sub(r'\{\\["\'\^\`~=.]\s*([a-zA-Z])\}', r"\1", name)
    name = re.sub(r"\{\\ss\}", "s", name, flags=re.IGNORECASE)
    name = re.sub(r"\{\\[^}]+\}", "", name)
    return name.replace("{", "").replace("}", "")


def make_citekey(bibtex: str) -> str:
    """Generate AuthorYYMM citekey from BibTeX"""

    author_match = extract_authors(bibtex)
    year_match = re.search(r"year\s*=\s*(\d{4})", bibtex)
    month_match = re.search(r"month\s*=\s*([a-zA-Z]+)", bibtex)

    if not author_match or not year_match or not month_match:
        raise ValueError("Could not parse author/year/month from BibTeX")

    first_author = author_match.split(" and ")[0]
    last_name = clean_name(first_author.split(",")[0])
    last_name = re.sub(r"[^a-zA-Z]", "", last_name)
    year = year_match.group(1)[2:]
    month = MONTH_MAP.get(month_match.group(1).lower()[:3], "")
    return f"{last_name}{year}{month}"


def change_citekey(bibtex: str) -> str:
    """Replace ADS bibcode key with AuthorYYMM citekey"""

    key = make_citekey(bibtex)
    new_bibtex = re.sub(r"(@\w+\{)[^,]+,", rf"\g<1>{key},", bibtex, count=1)
    return new_bibtex
