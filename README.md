# adscite

Fetch BibTeX citations from the NASA ADS database using a DOI or arXiv ID. The result is printed to the terminal and copied to the clipboard using xclip.

---

## Installation

```bash
git clone https://github.com/navaneethnpk/adscite
cd adscite
pip install -e .
```

## Token Setup

adscite requires a NASA ADS API token.

Get your token from: https://ui.adsabs.harvard.edu/user/settings/token

Save it:

```bash
adscite --set-token 'your_token_here'
```

This saves the token to `~/.config/adscite/config`.

---

## Usage

```bash
# From DOI
adscite 10.1098/rspa.1932.0112

# From DOI URL
adscite https://doi.org/10.1098/rspa.1932.0112

# From arXiv ID
adscite --arxiv 1602.03837

# From arXiv URL
adscite --arxiv https://arxiv.org/abs/1602.03837
```

---

## Requirements

- Python >= 3.8
- [xclip](https://github.com/astrand/xclip) for clipboard support

```bash
sudo apt install xclip
```
