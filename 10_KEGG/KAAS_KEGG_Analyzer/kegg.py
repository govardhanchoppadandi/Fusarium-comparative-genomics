import pickle
import re
import time
from pathlib import Path

import requests


KEGG_URL = "https://rest.kegg.jp/get/"


def load_cache(cache_file):

    cache_file = Path(
        cache_file
    )

    if not cache_file.exists():

        return {}

    try:

        with open(
            cache_file,
            "rb"
        ) as handle:

            return pickle.load(handle)

    except Exception:

        return {}


def save_cache(
    cache,
    cache_file
):

    cache_file = Path(
        cache_file
    )

    temporary = cache_file.with_suffix(
        ".tmp"
    )

    with open(
        temporary,
        "wb"
    ) as handle:

        pickle.dump(
            cache,
            handle,
            protocol=pickle.HIGHEST_PROTOCOL
        )

    temporary.replace(
        cache_file
    )


def parse_record(
    ko,
    text
):

    ko_name = ""

    ec_numbers = []

    pathways = []


    # NAME
    for line in text.splitlines():

        if line.startswith("NAME"):

            ko_name = line[
                12:
            ].strip()

            break


    # EC
    for line in text.splitlines():

        if "EC:" in line:

            part = line.split(
                "EC:",
                1
            )[1]

            found = re.findall(
                r"\d+\.\d+\.\d+\.\d+",
                part
            )

            for ec in found:

                if ec not in ec_numbers:

                    ec_numbers.append(
                        ec
                    )


    # PATHWAY
    for line in text.splitlines():

        if line.startswith(
            "PATHWAY"
        ):

            parts = line.split()

            if len(parts) >= 3:

                pathway_id = parts[1]

                pathway_name = " ".join(
                    parts[2:]
                )

                pathways.append(
                    (
                        pathway_id,
                        pathway_name
                    )
                )


    return {
        "KO": ko,
        "KO_Name": ko_name,
        "EC": "; ".join(
            sorted(
                set(ec_numbers)
            )
        ),
        "Pathways": pathways
    }


def fetch_kegg(
    ko_list,
    cache_file,
    batch_size=10,
    delay=0.5,
    progress_callback=None
):

    cache = load_cache(
        cache_file
    )

    missing = [
        ko
        for ko in ko_list
        if ko not in cache
    ]

    session = requests.Session()

    session.headers.update({
        "User-Agent":
        "KAAS-KEGG-Analyzer/1.0"
    })


    total = len(missing)

    for start in range(
        0,
        total,
        batch_size
    ):

        batch = missing[
            start:
            start + batch_size
        ]

        ids = "+".join(
            f"ko:{ko}"
            for ko in batch
        )

        url = KEGG_URL + ids

        response = session.get(
            url,
            timeout=300
        )

        response.raise_for_status()

        text = response.text


        # KEGG records are separated
        # by ENTRY lines.
        blocks = re.split(
            r"\n(?=ENTRY\s+)",
            text
        )


        for block in blocks:

            match = re.search(
                r"ENTRY\s+(K\d{5})",
                block
            )

            if not match:

                continue

            ko = match.group(1)

            cache[ko] = parse_record(
                ko,
                block
            )


        save_cache(
            cache,
            cache_file
        )


        if progress_callback:

            progress_callback(
                min(
                    start + len(batch),
                    total
                ),
                total
            )


        time.sleep(
            delay
        )


    return cache
