from __future__ import annotations

import argparse
import csv
import hashlib
import json
import pickle
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable, Mapping

import numpy as np

from laso_tools import analyze_questions, build_pair_rows


SPLITS = ("train", "val", "test")
REQUIRED_ANNOTATION_KEYS = ("shape_id", "class", "affordance", "mask")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_csv(path: Path, rows: Iterable[Mapping[str, object]], fieldnames: list[str]) -> None:
    materialized = list(rows)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(materialized)


def load_pickle(path: Path) -> object:
    with path.open("rb") as handle:
        return pickle.load(handle)


def inspect_split(
    data_root: Path, split: str
) -> tuple[list[dict[str, object]], list[dict[str, object]], dict[str, object], list[dict[str, object]]]:
    annotation_path = data_root / f"anno_{split}.pkl"
    object_path = data_root / f"objects_{split}.pkl"
    raw_annotations = load_pickle(annotation_path)
    objects = load_pickle(object_path)
    if not isinstance(raw_annotations, (list, tuple)):
        raise TypeError(f"{annotation_path.name} must contain a list or tuple")
    if not isinstance(objects, dict):
        raise TypeError(f"{object_path.name} must contain a dict")

    normalized: list[dict[str, object]] = []
    summaries: list[dict[str, object]] = []
    issues: list[dict[str, object]] = []
    classes: Counter[str] = Counter()
    affordances: Counter[str] = Counter()
    shape_classes: dict[str, set[str]] = defaultdict(set)

    for index, raw in enumerate(raw_annotations):
        if not isinstance(raw, dict):
            issues.append(
                {"split": split, "shape_id": "", "issue": "annotation_not_dict", "detail": str(index)}
            )
            continue
        missing = [key for key in REQUIRED_ANNOTATION_KEYS if key not in raw]
        if missing:
            issues.append(
                {
                    "split": split,
                    "shape_id": str(raw.get("shape_id", "")),
                    "issue": "missing_annotation_keys",
                    "detail": ",".join(missing),
                }
            )
            continue

        shape_id = str(raw["shape_id"])
        object_class = str(raw["class"])
        affordance = str(raw["affordance"])
        try:
            mask = np.asarray(raw["mask"], dtype=np.float32).reshape(-1)
        except (TypeError, ValueError) as exc:
            issues.append(
                {"split": split, "shape_id": shape_id, "issue": "invalid_mask", "detail": str(exc)}
            )
            continue
        if mask.size == 0 or not np.isfinite(mask).all():
            issues.append(
                {
                    "split": split,
                    "shape_id": shape_id,
                    "issue": "empty_or_nonfinite_mask",
                    "detail": f"annotation_index={index}",
                }
            )
            continue
        object_points = objects.get(shape_id)
        if object_points is None:
            issues.append(
                {"split": split, "shape_id": shape_id, "issue": "missing_object", "detail": str(index)}
            )
            point_count = ""
        else:
            points = np.asarray(object_points)
            point_count = int(points.shape[0]) if points.ndim >= 1 else 0
            if points.ndim != 2 or points.shape[1] < 3:
                issues.append(
                    {
                        "split": split,
                        "shape_id": shape_id,
                        "issue": "unexpected_object_shape",
                        "detail": str(points.shape),
                    }
                )
            if point_count != mask.size:
                issues.append(
                    {
                        "split": split,
                        "shape_id": shape_id,
                        "issue": "object_mask_length_mismatch",
                        "detail": f"points={point_count}, mask={mask.size}",
                    }
                )

        normalized.append(
            {
                "split": split,
                "annotation_index": index,
                "shape_id": shape_id,
                "class": object_class,
                "affordance": affordance,
                "mask": mask,
            }
        )
        summaries.append(
            {
                "split": split,
                "annotation_index": index,
                "shape_id": shape_id,
                "class": object_class,
                "affordance": affordance,
                "mask_length": int(mask.size),
                "mask_dtype": str(mask.dtype),
                "mask_min": float(mask.min()),
                "mask_max": float(mask.max()),
                "foreground_fraction": float((mask > 0).mean()),
                "object_point_count": point_count,
            }
        )
        classes[object_class] += 1
        affordances[affordance] += 1
        shape_classes[shape_id].add(object_class)

    for shape_id, values in shape_classes.items():
        if len(values) > 1:
            issues.append(
                {
                    "split": split,
                    "shape_id": shape_id,
                    "issue": "shape_has_multiple_classes",
                    "detail": "|".join(sorted(values)),
                }
            )

    schema = {
        "annotation_container": type(raw_annotations).__name__,
        "annotation_keys": sorted({str(key) for row in raw_annotations if isinstance(row, dict) for key in row}),
        "object_container": type(objects).__name__,
        "object_key_type_counts": dict(Counter(type(key).__name__ for key in objects)),
        "object_value_shape_counts": dict(Counter(str(np.asarray(value).shape) for value in objects.values())),
    }
    summary = {
        "annotation_count": len(raw_annotations),
        "valid_annotation_count": len(normalized),
        "shape_count": len({row["shape_id"] for row in normalized}),
        "object_count": len(objects),
        "class_count": len(classes),
        "affordance_count": len(affordances),
        "classes": dict(sorted(classes.items())),
        "affordances": dict(sorted(affordances.items())),
    }
    return normalized, summaries, {"schema": schema, "summary": summary}, issues


def main() -> None:
    parser = argparse.ArgumentParser(description="Read-only LASO data and language analysis")
    parser.add_argument("--data-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    data_root = args.data_root.resolve()
    output = args.output.resolve()
    required = [data_root / "Affordance-Question.csv"]
    for split in SPLITS:
        required.extend((data_root / f"anno_{split}.pkl", data_root / f"objects_{split}.pkl"))
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError("Missing LASO files:\n" + "\n".join(missing))
    output.mkdir(parents=True, exist_ok=True)

    source_manifest = [
        {"file": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)} for path in required
    ]
    (output / "source_manifest.json").write_text(
        json.dumps(source_manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    all_annotations: list[dict[str, object]] = []
    annotation_summaries: list[dict[str, object]] = []
    all_pairs: list[dict[str, object]] = []
    all_issues: list[dict[str, object]] = []
    schema: dict[str, object] = {}
    run_splits: dict[str, object] = {}
    split_shapes: dict[str, set[str]] = {}

    for split in SPLITS:
        annotations, summaries, details, issues = inspect_split(data_root, split)
        pairs, pair_issues = build_pair_rows(annotations)
        all_annotations.extend(annotations)
        annotation_summaries.extend(summaries)
        all_pairs.extend(pairs)
        all_issues.extend(issues)
        all_issues.extend(pair_issues)
        schema[split] = details["schema"]
        split_shapes[split] = {str(row["shape_id"]) for row in annotations}
        split_summary = dict(details["summary"])
        split_summary["pair_count"] = len(pairs)
        split_summary["pair_shape_count"] = len({row["shape_id"] for row in pairs})
        run_splits[split] = split_summary

    for left, right in (("train", "val"), ("train", "test"), ("val", "test")):
        for shape_id in sorted(split_shapes[left] & split_shapes[right]):
            all_issues.append(
                {
                    "split": f"{left}|{right}",
                    "shape_id": shape_id,
                    "issue": "cross_split_shape_overlap",
                    "detail": "same shape_id appears in both splits",
                }
            )

    with (data_root / "Affordance-Question.csv").open(encoding="utf-8-sig", newline="") as handle:
        question_rows = list(csv.DictReader(handle))
    inventory, templates, language_issues = analyze_questions(question_rows)
    for issue in language_issues:
        all_issues.append(
            {
                "split": "language",
                "shape_id": "",
                "issue": issue["issue"],
                "detail": issue["detail"],
            }
        )

    pair_type_counts: dict[tuple[str, str, str], set[str]] = defaultdict(set)
    pair_type_rows: Counter[tuple[str, str, str]] = Counter()
    for pair in all_pairs:
        key = (str(pair["split"]), str(pair["class"]), str(pair["pair_type"]))
        pair_type_rows[key] += 1
        pair_type_counts[key].add(str(pair["shape_id"]))
    pair_type_summary = [
        {
            "split": key[0],
            "class": key[1],
            "pair_type": key[2],
            "pair_count": pair_type_rows[key],
            "shape_count": len(pair_type_counts[key]),
        }
        for key in sorted(pair_type_rows)
    ]

    (output / "schema.json").write_text(json.dumps(schema, indent=2, ensure_ascii=False), encoding="utf-8")
    write_csv(
        output / "split_summary.csv",
        ({"split": split, **run_splits[split]} for split in SPLITS),
        [
            "split",
            "annotation_count",
            "valid_annotation_count",
            "shape_count",
            "object_count",
            "class_count",
            "affordance_count",
            "pair_count",
            "pair_shape_count",
            "classes",
            "affordances",
        ],
    )
    write_csv(
        output / "annotations.csv",
        annotation_summaries,
        [
            "split",
            "annotation_index",
            "shape_id",
            "class",
            "affordance",
            "mask_length",
            "mask_dtype",
            "mask_min",
            "mask_max",
            "foreground_fraction",
            "object_point_count",
        ],
    )
    pair_fields = [
        "pair_id",
        "pair_type",
        "split",
        "shape_id",
        "class",
        "same_class",
        "affordance_a",
        "affordance_b",
        "annotation_index_a",
        "annotation_index_b",
        "point_count",
        "mask_iou",
        "foreground_fraction_a",
        "foreground_fraction_b",
        "mean_abs_gt_diff",
        "binary_diff_fraction",
    ]
    write_csv(output / "pairs_all.csv", all_pairs, pair_fields)
    write_csv(
        output / "pair_type_summary.csv",
        pair_type_summary,
        ["split", "class", "pair_type", "pair_count", "shape_count"],
    )
    review_groups: dict[tuple[str, str], dict[str, object]] = {}
    for row in pair_type_summary:
        if row["split"] not in {"val", "test"}:
            continue
        key = (str(row["class"]), str(row["pair_type"]))
        current = review_groups.setdefault(
            key,
            {
                "class": key[0],
                "pair_type": key[1],
                "val_shapes": 0,
                "test_shapes": 0,
                "include": "",
                "reason": "",
            },
        )
        current[f"{row['split']}_shapes"] = row["shape_count"]
    write_csv(
        output / "pair_review_template.csv",
        (review_groups[key] for key in sorted(review_groups)),
        ["class", "pair_type", "val_shapes", "test_shapes", "include", "reason"],
    )
    write_csv(
        output / "question_inventory.csv",
        inventory,
        [
            "row_index",
            "object",
            "affordance",
            "question_id",
            "question_text",
            "object_mentioned",
            "affordance_mentioned",
            "character_count",
            "word_count",
            "normalized_template",
        ],
    )
    write_csv(
        output / "template_summary.csv",
        templates,
        ["question_id", "normalized_template", "count"],
    )
    write_csv(output / "issues.csv", all_issues, ["split", "shape_id", "issue", "detail"])

    run_summary = {
        "data_root": str(data_root),
        "splits": run_splits,
        "language": {
            "csv_row_count": len(question_rows),
            "question_count": len(inventory),
            "template_count": len({row["normalized_template"] for row in templates}),
            "object_mention_rate": (
                sum(bool(row["object_mentioned"]) for row in inventory) / len(inventory) if inventory else None
            ),
            "affordance_mention_rate": (
                sum(bool(row["affordance_mentioned"]) for row in inventory) / len(inventory)
                if inventory
                else None
            ),
        },
        "issue_count": len(all_issues),
    }
    (output / "run_summary.json").write_text(
        json.dumps(run_summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps(run_summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
