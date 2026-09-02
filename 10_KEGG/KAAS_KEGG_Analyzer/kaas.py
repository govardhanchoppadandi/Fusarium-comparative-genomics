import re
import requests
from pathlib import Path


def download_kaas_result(url, output_file):
    """
    Download the KAAS query.ko result.

    Accepts:
      - KAAS result page URL
      - direct query.ko URL

    Returns:
      local query.ko path
    """

    session = requests.Session()

    session.headers.update({
        "User-Agent": "KAAS-KEGG-Analyzer/1.0"
    })

    response = session.get(
        url,
        timeout=180
    )

    response.raise_for_status()

    html = response.text

    # Direct query.ko
    if "query.ko" in url:

        Path(output_file).write_text(
            html,
            encoding="utf-8"
        )

        return Path(output_file)

    # Search KAAS HTML for query.ko
    patterns = [
        r'href="([^"]*query\.ko)"',
        r"href='([^']*query\.ko)'",
        r'(/tools/kaas/files/dl/[^"\']+/query\.ko)'
    ]

    query_url = None

    for pattern in patterns:

        match = re.search(
            pattern,
            html,
            flags=re.IGNORECASE
        )

        if match:

            query_url = match.group(1)

            break

    if query_url is None:

        raise RuntimeError(
            "query.ko link could not be found in the KAAS result page."
        )

    # Convert relative URL
    if query_url.startswith("/"):

        query_url = (
            "https://www.genome.jp"
            + query_url
        )

    elif not query_url.startswith("http"):

        query_url = (
            "https://www.genome.jp/"
            + query_url.lstrip("/")
        )

    # Download query.ko
    result = session.get(
        query_url,
        timeout=600
    )

    result.raise_for_status()

    Path(output_file).write_text(
        result.text,
        encoding="utf-8"
    )

    return Path(output_file)


def parse_kaas(query_file):

    """
    Convert query.ko into:

    Protein_ID | KO
    """

    records = []

    with open(
        query_file,
        encoding="utf-8",
        errors="replace"
    ) as handle:

        for line in handle:

            line = line.rstrip()

            if not line:

                continue

            protein_id = line.split()[0]

            match = re.search(
                r"\bK\d{5}\b",
                line
            )

            ko = (
                match.group(0)
                if match
                else ""
            )

            records.append(
                {
                    "Protein_ID": protein_id,
                    "KO": ko
                }
            )

    return records
