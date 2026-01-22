import re

LEGAL_SUFFIXES = [
    "PVT", "PVT LTD", "PRIVATE LIMITED", "LTD", "LIMITED",
    "INC", "LLC", "LLP", "CORP", "CORPORATION", "GMBH"
]

def normalize_supplier_name(name: str) -> dict:
    cleaned = name.upper()
    cleaned = re.sub(r"[^A-Z0-9 ]", " ", cleaned)

    for suffix in LEGAL_SUFFIXES:
        cleaned = re.sub(rf"\b{suffix}\b", "", cleaned)

    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    return {
        "normalized_name": cleaned,
        "match_key": cleaned.replace(" ", "_")
    }

