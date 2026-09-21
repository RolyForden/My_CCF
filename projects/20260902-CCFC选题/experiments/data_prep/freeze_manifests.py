from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import Counter
from pathlib import Path
from typing import Iterable, Mapping

from laso_tools import build_query_rows, select_discovery_shapes


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: Iterable[Mapping[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"yes", "true", "1", "include", "included"}:
        return True
    if normalized in {"no", "false", "0", "exclude", "excluded"}:
        return False
    raise ValueError(f"unknown include value: {value!r}")


def load_rules(path: Path | None) -> dict[str, object]:
    defaults: dict[str, object] = {
        "discovery_split": "val",
        "confirmation_split": "test",
        "min_mean_abs_gt_diff": None,
        "max_mask_iou": None,
        "excluded_pair_types": [],
        "notes": "Pair semantics are controlled by pair_review.csv.",
    }
    if path is None:
        return defaults
    supplied = json.loads(path.read_text(encoding="utf-8"))
    unknown = set(supplied) - set(defaults)
    if unknown:
        raise ValueError(f"unknown rule keys: {sorted(unknown)}")
    defaults.update(supplied)
    if defaults["discovery_split"] != "val" or defaults["confirmation_split"] != "test":
        raise ValueError("this experiment uses val discovery and test confirmation")
    return defaults


def apply_rules(rows: list[dict[str, str]], rules: Mapping[str, object]) -> list[dict[str, str]]:
    excluded_types = {str(value) for value in rules["excluded_pair_types"]}
    min_diff = rules["min_mean_abs_gt_diff"]
    max_iou = rules["max_mask_iou"]
    kept: list[dict[str, str]] = []
    for row in rows:
        if row["pair_type"] in excluded_types:
            continue
        if min_diff is not None and float(row["mean_abs_gt_diff"]) < float(min_diff):
            continue
        if max_iou is not None and float(row["mask_iou"]) > float(max_iou):
            continue
        kept.append(row)
    return kept


def main() -> None:
    parser = argparse.ArgumentParser(description="Freeze LASO pair, shape, and query manifests")
    parser.add_argument("--audit-dir", required=True, type=Path)
    parser.add_argument("--pair-review", required=True, type=Path)
    parser.add_argument("--rules", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--fraction", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    if not 0 < args.fraction <= 1:
        raise ValueError("fraction must be in (0, 1]")
    audit_dir = args.audit_dir.resolve()
    review_path = args.pair_review.resolve()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)

    pairs_path = audit_dir / "pairs_all.csv"
    questions_path = audit_dir / "question_inventory.csv"
    for path in (pairs_path, questions_path, review_path):
        if not path.is_file():
            raise FileNotFoundError(path)

    all_pairs = read_csv(pairs_path)
    candidate_pairs = [row for row in all_pairs if row["split"] in {"val", "test"}]
    review_rows = read_csv(review_path)
    review_map: dict[tuple[str, str], dict[str, str]] = {}
    for row in review_rows:
        key = (row.get("class", "").strip(), row.get("pair_type", "").strip())
        if not all(key):
            raise ValueError("pair_review.csv contains an empty class or pair_type")
        if key in review_map:
            raise ValueError(f"duplicate review for {key}")
        review_map[key] = row

    candidate_keys = {(row["class"], row["pair_type"]) for row in candidate_pairs}
    missing_reviews = sorted(candidate_keys - set(review_map))
    extra_reviews = sorted(set(review_map) - candidate_keys)
    if missing_reviews:
        raise ValueError(
            f"pair_review.csv is missing {len(missing_reviews)} class/pair types; first={missing_reviews[0]}"
        )
    if extra_reviews:
        raise ValueError(f"pair_review.csv has unknown class/pair types; first={extra_reviews[0]}")

    reviewed_pairs: list[dict[str, str]] = []
    for pair in candidate_pairs:
        review = review_map[(pair["class"], pair["pair_type"])]
        if parse_bool(review.get("include", "")):
            reviewed_pairs.append({**pair, "review_reason": review.get("reason", "")})

    rules = load_rules(args.rules.resolve() if args.rules else None)
    included_pairs = apply_rules(reviewed_pairs, rules)
    discovery_pairs = [row for row in included_pairs if row["split"] == "val"]
    confirmation_pairs = [row for row in included_pairs if row["split"] == "test"]
    if not discovery_pairs:
        raise ValueError("no val discovery pairs remain")
    if not confirmation_pairs:
        raise ValueError("no test confirmation pairs remain")

    discovery_full_shapes = sorted({row["shape_id"] for row in discovery_pairs})
    confirmation_shapes = sorted({row["shape_id"] for row in confirmation_pairs})
    discovery20_shapes = select_discovery_shapes(discovery_pairs, args.fraction, args.seed)

    inventory = read_csv(questions_path)
    canonical_lookup: dict[tuple[str, str], str] = {}
    for row in inventory:
        if row["question_id"] == "Question0":
            key = (row["object"], row["affordance"])
            if key in canonical_lookup and canonical_lookup[key] != row["question_text"]:
                raise ValueError(f"multiple Question0 values for {key}")
            canonical_lookup[key] = row["question_text"]
    query_rows = build_query_rows(included_pairs, canonical_lookup)

    pair_fields = list(included_pairs[0])
    query_fields = list(query_rows[0])
    write_csv(output / "pair_manifest.csv", included_pairs, pair_fields)
    write_csv(output / "query_manifest.csv", query_rows, query_fields)
    (output / "discovery20_shapes.json").write_text(
        json.dumps(discovery20_shapes, indent=2), encoding="utf-8"
    )
    (output / "discovery_full_shapes.json").write_text(
        json.dumps(discovery_full_shapes, indent=2), encoding="utf-8"
    )
    (output / "confirmation_shapes.json").write_text(
        json.dumps(confirmation_shapes, indent=2), encoding="utf-8"
    )

    frozen = {
        "discovery_split": "val",
        "confirmation_split": "test",
        "discovery_fraction": args.fraction,
        "seed": args.seed,
        "selection": "coverage-aware deterministic shape selection",
        "rules": rules,
        "source_hashes": {
            "pairs_all.csv": sha256(pairs_path),
            "question_inventory.csv": sha256(questions_path),
            "pair_review.csv": sha256(review_path),
            **({"rules.json": sha256(args.rules.resolve())} if args.rules else {}),
        },
        "counts": {
            "candidate_pairs": len(candidate_pairs),
            "human_included_pairs": len(reviewed_pairs),
            "final_pairs": len(included_pairs),
            "discovery_pairs": len(discovery_pairs),
            "confirmation_pairs": len(confirmation_pairs),
            "discovery_full_shapes": len(discovery_full_shapes),
            "discovery20_shapes": len(discovery20_shapes),
            "confirmation_shapes": len(confirmation_shapes),
            "query_rows": len(query_rows),
        },
        "pair_types": dict(Counter(row["pair_type"] for row in included_pairs)),
    }
    (output / "frozen_rules.json").write_text(
        json.dumps(frozen, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps(frozen["counts"], ensure_ascii=False))


if __name__ == "__main__":
    main()
