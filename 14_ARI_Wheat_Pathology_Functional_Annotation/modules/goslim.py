#!/usr/bin/env python3

from collections import defaultdict, deque


def load_go_relationships(filename):

    parents = defaultdict(set)

    current_id = None

    with open(
        filename,
        "r",
        encoding="utf-8",
        errors="replace"
    ) as f:

        for line in f:

            line = line.rstrip()

            if line == "[Term]":

                current_id = None

            elif line.startswith("id: GO:"):

                current_id = line.split(
                    "id:",
                    1
                )[1].strip()

            elif (
                current_id
                and line.startswith("is_a:")
            ):

                parent = line.split(
                    "is_a:",
                    1
                )[1].split(
                    "!",
                    1
                )[0].strip()

                parents[current_id].add(
                    parent
                )

            elif (
                current_id
                and line.startswith(
                    "relationship: part_of "
                )
            ):

                parent = line.split()[-1]

                if parent.startswith("GO:"):

                    parents[current_id].add(
                        parent
                    )

    return parents


def load_slim_terms(filename):

    slim = set()

    current_id = None

    with open(
        filename,
        "r",
        encoding="utf-8",
        errors="replace"
    ) as f:

        for line in f:

            line = line.rstrip()

            if line == "[Term]":

                current_id = None

            elif line.startswith("id: GO:"):

                current_id = line.split(
                    "id:",
                    1
                )[1].strip()

                slim.add(current_id)

    return slim


def build_slim_mapping(
    go_terms,
    parents,
    slim_terms
):

    mapping = {}

    for go_id in go_terms:

        found = set()

        queue = deque([go_id])

        visited = set()

        while queue:

            current = queue.popleft()

            if current in visited:
                continue

            visited.add(current)

            if current in slim_terms:

                found.add(current)

            for parent in parents.get(
                current,
                set()
            ):

                if parent not in visited:

                    queue.append(parent)

        mapping[go_id] = found

    return mapping
