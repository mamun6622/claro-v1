
import json
import os
import re

import requests
from bs4 import BeautifulSoup


DATABASE_FILE = "database/bic_knowledge.json"


SOURCES = [
    "https://www.tu.ac.kr/ic/index.do",

    # Add your selected BIC pages here.
    #
    # Example:
    "https://www.tu.ac.kr/ic/sub02_10_03.do",
]


def clean_text(text):

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def scrape_page(url):

    print(f"\nScraping:")
    print(url)

    headers = {
        "User-Agent":
            "Mozilla/5.0 CLARO-Campus-Robot"
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=20
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    # Remove things that are not useful
    # campus information.
    for tag in soup([
        "script",
        "style",
        "noscript",
        "svg",
        "header",
        "footer",
        "nav",
        "form"
    ]):
        tag.decompose()

    # Get page title.
    if soup.title:
        title = soup.title.get_text(
            " ",
            strip=True
        )
    else:
        title = url

    # Prefer main content when available.
    main = (
        soup.find("main")
        or soup.find("article")
        or soup.find("body")
    )

    if not main:
        raise RuntimeError(
            "Could not find page content."
        )

    # Extract meaningful blocks.
    blocks = []

    for element in main.find_all(
        ["h1", "h2", "h3", "h4", "p", "li"]
    ):

        text = element.get_text(
            " ",
            strip=True
        )

        text = clean_text(text)

        if len(text) >= 20:
            blocks.append(text)

    # Remove duplicates.
    unique_blocks = []

    for block in blocks:

        if block not in unique_blocks:
            unique_blocks.append(block)

    text = " ".join(unique_blocks)

    return {
        "url": url,
        "title": title,
        "text": text
    }


def main():

    os.makedirs(
        "database",
        exist_ok=True
    )

    knowledge = []

    for url in SOURCES:

        try:

            data = scrape_page(url)

            knowledge.append(data)

            print(
                f"✓ Added: {data['title']}"
            )

            print(
                f"  Characters: "
                f"{len(data['text'])}"
            )

        except Exception as error:

            print(
                f"✗ Failed: {url}"
            )

            print(
                f"  Error: {error}"
            )

    with open(
        DATABASE_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            knowledge,
            file,
            ensure_ascii=False,
            indent=2
        )

    print()
    print(
        f"Saved {len(knowledge)} pages."
    )

    print(
        f"Database: {DATABASE_FILE}"
    )


if __name__ == "__main__":
    main()
