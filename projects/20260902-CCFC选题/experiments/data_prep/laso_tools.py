from __future__ import annotations

import json
import math
import random
import re
from collections import Counter, defaultdict
from itertools import combinations
from typing import Iterable, Mapping, Sequence

import numpy as np


VIEWPOINTS = (
    "from the rear view",
    "from the left-rear view",
    "from the left side view",
    "from the left-front view",
    "from the front view",
    "from the right-front view",
    "from the right side view",
    "from the right-rear view",
    "from the bottom view",
    "from the lower diagonal view",
    "from the upper diagonal view",
    "from the top view",
)


def _mask(value: object) -> np.ndarray:
    mask = np.asarray(value, dtype=np.float32).reshape(-1)
    if mask.size == 0:
        raise ValueError("mask is empty")
    if not np.isfinite(mask).all():
        raise ValueError("mask contains NaN or Inf")
    return mask


def _binary(mask: np.ndarray) -> np.ndarray:
    return mask > 0


def build_pair_rows(
    annotations: Sequence[Mapping[str, object]],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    """Build one unordered affordance pair per shape and affordance combination."""
    grouped: dict[tuple[str, str], list[Mapping[str, object]]] = defaultdict(list)
    for annotation in annotations:
        grouped[(str(annotation["split"]), str(annotation["shape_id"]))].append(annotation)

    pairs: list[dict[str, object]] = []
    issues: list[dict[str, object]] = []
    for (split, shape_id), shape_rows in sorted(grouped.items()):
        by_affordance: dict[str, list[Mapping[str, object]]] = defaultdict(list)
        for row in shape_rows:
            by_affordance[str(row["affordance"])].append(row)

        duplicates = {key: value for key, value in by_affordance.items() if len(value) != 1}
        if duplicates:
            for affordance, rows in sorted(duplicates.items()):
                issues.append(
                    {
                        "split": split,
                        "shape_id": shape_id,
                        "issue": "duplicate_shape_affordance",
                        "detail": f"{affordance}: {len(rows)} annotations",
                    }
                )
            continue

        for affordance_a, affordance_b in combinations(sorted(by_affordance), 2):
            row_a = by_affordance[affordance_a][0]
            row_b = by_affordance[affordance_b][0]
            try:
                mask_a = _mask(row_a["mask"])
                mask_b = _mask(row_b["mask"])
            except (TypeError, ValueError) as exc:
                issues.append(
                    {
                        "split": split,
                        "shape_id": shape_id,
                        "issue": "invalid_mask",
                        "detail": str(exc),
                    }
                )
                continue
            if mask_a.shape != mask_b.shape:
                issues.append(
                    {
                        "split": split,
                        "shape_id": shape_id,
                        "issue": "mask_length_mismatch",
                        "detail": f"{affordance_a}:{mask_a.size}, {affordance_b}:{mask_b.size}",
                    }
                )
                continue

            binary_a = _binary(mask_a)
            binary_b = _binary(mask_b)
            union = np.logical_or(binary_a, binary_b).sum()
            intersection = np.logical_and(binary_a, binary_b).sum()
            classes = {str(row_a["class"]), str(row_b["class"])}
            pairs.append(
                {
                    "pair_id": f"{split}::{shape_id}::{affordance_a}::{affordance_b}",
                    "pair_type": f"{affordance_a}|{affordance_b}",
                    "split": split,
                    "shape_id": shape_id,
                    "class": str(row_a["class"]) if len(classes) == 1 else "|".join(sorted(classes)),
                    "same_class": len(classes) == 1,
                    "affordance_a": affordance_a,
                    "affordance_b": affordance_b,
                    "annotation_index_a": int(row_a["annotation_index"]),
                    "annotation_index_b": int(row_b["annotation_index"]),
                    "point_count": int(mask_a.size),
                    "mask_iou": float(intersection / union) if union else 1.0,
                    "foreground_fraction_a": float(binary_a.mean()),
                    "foreground_fraction_b": float(binary_b.mean()),
                    "mean_abs_gt_diff": float(np.abs(mask_b - mask_a).mean()),
                    "binary_diff_fraction": float(np.not_equal(binary_a, binary_b).mean()),
                }
            )
    return pairs, issues


def _mentions(text: str, phrase: str) -> bool:
    phrase = phrase.replace("_", " ").strip()
    return bool(phrase) and re.search(rf"\b{re.escape(phrase)}\b", text, flags=re.IGNORECASE) is not None


def _template(text: str, object_name: str, affordance: str) -> str:
    normalized = text.lower().replace("_", " ")
    replacements = sorted(
        ((object_name.replace("_", " "), "{object}"), (affordance.replace("_", " "), "{affordance}")),
        key=lambda item: len(item[0]),
        reverse=True,
    )
    for phrase, marker in replacements:
        if phrase:
            normalized = re.sub(rf"\b{re.escape(phrase.lower())}\b", marker, normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def analyze_questions(
    question_rows: Iterable[Mapping[str, object]],
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    inventory: list[dict[str, object]] = []
    issues: list[dict[str, object]] = []
    template_counts: Counter[tuple[str, str]] = Counter()

    for row_index, row in enumerate(question_rows):
        object_name = str(row.get("Object", "")).strip()
        affordance = str(row.get("Affordance", "")).strip()
        if not object_name or not affordance:
            issues.append(
                {
                    "row_index": row_index,
                    "issue": "missing_object_or_affordance",
                    "detail": f"Object={object_name!r}, Affordance={affordance!r}",
                }
            )
            continue
        question_columns = sorted(
            (key for key in row if re.fullmatch(r"Question\d+", str(key))),
            key=lambda key: int(str(key).replace("Question", "")),
        )
        if not question_columns:
            issues.append(
                {
                    "row_index": row_index,
                    "issue": "missing_question_columns",
                    "detail": f"{object_name}|{affordance}",
                }
            )
        for question_id in question_columns:
            raw_value = row.get(question_id, "")
            text = "" if raw_value is None else str(raw_value).strip()
            if not text or text.lower() == "nan":
                issues.append(
                    {
                        "row_index": row_index,
                        "issue": "empty_question",
                        "detail": f"{object_name}|{affordance}|{question_id}",
                    }
                )
                continue
            normalized_template = _template(text, object_name, affordance)
            inventory.append(
                {
                    "row_index": row_index,
                    "object": object_name,
                    "affordance": affordance,
                    "question_id": str(question_id),
                    "question_text": text,
                    "object_mentioned": _mentions(text, object_name),
                    "affordance_mentioned": _mentions(text, affordance),
                    "character_count": len(text),
                    "word_count": len(text.split()),
                    "normalized_template": normalized_template,
                }
            )
            template_counts[(str(question_id), normalized_template)] += 1

    templates = [
        {"question_id": question_id, "normalized_template": template, "count": count}
        for (question_id, template), count in sorted(template_counts.items())
    ]
    return inventory, templates, issues


def select_discovery_shapes(
    pair_rows: Sequence[Mapping[str, object]], fraction: float, seed: int
) -> list[str]:
    if not 0 < fraction <= 1:
        raise ValueError("fraction must be in (0, 1]")
    shape_types: dict[str, set[str]] = defaultdict(set)
    for row in pair_rows:
        shape_types[str(row["shape_id"])].add(str(row["pair_type"]))
    shapes = sorted(shape_types)
    if not shapes:
        return []

    target = max(1, math.ceil(len(shapes) * fraction))
    rng = random.Random(seed)
    shuffled = shapes.copy()
    rng.shuffle(shuffled)
    tie_rank = {shape_id: index for index, shape_id in enumerate(shuffled)}

    selected: list[str] = []
    uncovered = set().union(*(shape_types[shape_id] for shape_id in shapes))
    remaining = set(shapes)
    while remaining and len(selected) < target:
        candidate = min(
            remaining,
            key=lambda shape_id: (
                -len(shape_types[shape_id] & uncovered),
                tie_rank[shape_id],
                shape_id,
            ),
        )
        selected.append(candidate)
        uncovered -= shape_types[candidate]
        remaining.remove(candidate)
    return sorted(selected)


def _model_questions(object_name: str, base_text: str) -> list[str]:
    return [
        f"This is a depth map of a {object_name} viewed {viewpoint}. {base_text}"
        for viewpoint in VIEWPOINTS
    ]


def build_query_rows(
    pair_rows: Sequence[Mapping[str, object]],
    canonical_lookup: Mapping[tuple[str, str], str],
) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str, str, str], dict[str, object]] = {}
    for pair in pair_rows:
        for suffix in ("a", "b"):
            key = (
                str(pair["split"]),
                str(pair["shape_id"]),
                str(pair["class"]),
                str(pair[f"affordance_{suffix}"]),
            )
            record = grouped.setdefault(
                key,
                {
                    "annotation_index": int(pair[f"annotation_index_{suffix}"]),
                    "pair_ids": [],
                },
            )
            record["pair_ids"].append(str(pair["pair_id"]))

    queries: list[dict[str, object]] = []
    for (split, shape_id, object_name, affordance), record in sorted(grouped.items()):
        canonical = canonical_lookup.get((object_name, affordance))
        if canonical is None:
            raise KeyError(f"missing Question0 for {object_name}|{affordance}")
        conditions = (("Label", affordance.replace("_", " ")), ("Canonical", canonical))
        for condition, base_text in conditions:
            queries.append(
                {
                    "query_id": f"{split}::{shape_id}::{affordance}::{condition}",
                    "split": split,
                    "shape_id": shape_id,
                    "class": object_name,
                    "affordance": affordance,
                    "annotation_index": record["annotation_index"],
                    "query_condition": condition,
                    "base_text": base_text,
                    "model_questions_json": json.dumps(
                        _model_questions(object_name, base_text), ensure_ascii=False
                    ),
                    "pair_ids_json": json.dumps(sorted(set(record["pair_ids"]))),
                }
            )
    return queries
