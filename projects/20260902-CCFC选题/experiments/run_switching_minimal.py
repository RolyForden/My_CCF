from __future__ import annotations

import argparse
import csv
import json
import pickle
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def sim(prediction: np.ndarray, target: np.ndarray, eps: float = 1e-12) -> float:
    p = prediction / (prediction.sum() + eps)
    y = target / (target.sum() + eps)
    return float(np.minimum(p, y).sum())


def main() -> None:
    parser = argparse.ArgumentParser(description="Minimal GEAL query-switching screen")
    parser.add_argument("--geal-root", required=True, type=Path)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--query-manifest", required=True, type=Path)
    parser.add_argument("--pair-manifest", required=True, type=Path)
    parser.add_argument("--shape-manifest", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--batch-size", type=int, default=32)
    args = parser.parse_args()

    geal_root = args.geal_root.resolve()
    sys.path.insert(0, str(geal_root))
    import torch
    from dataset.data_utils import normalize_point_cloud
    from model.branch_3d import Branch3D
    from utils.metrics import (
        calculate_batch_iou_auc,
        calculate_batch_mae,
        calculate_batch_sim,
    )
    from utils.utils import read_yaml, seed_torch

    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    cfg = read_yaml(str(args.config.resolve()))
    seed_torch(cfg["seed"])
    selected_shapes = set(json.loads(args.shape_manifest.read_text(encoding="utf-8")))
    query_rows = [
        row
        for row in read_csv(args.query_manifest)
        if row["split"] == "val" and row["shape_id"] in selected_shapes
    ]
    pair_rows = [
        row
        for row in read_csv(args.pair_manifest)
        if row["split"] == "val" and row["shape_id"] in selected_shapes
    ]
    if not query_rows or not pair_rows:
        raise ValueError("selected query or pair set is empty")

    data_root = Path(cfg["data_root"])
    with (data_root / "anno_val.pkl").open("rb") as handle:
        annotations = pickle.load(handle)
    with (data_root / "objects_val.pkl").open("rb") as handle:
        objects = pickle.load(handle)

    device = torch.device("cuda")
    model = Branch3D(cfg["model_3d"])
    checkpoint = torch.load(cfg["ckpt"], map_location=device)
    status = model.load_state_dict(checkpoint["model"], strict=False)
    model.to(device).eval()
    print(json.dumps({"missing_keys": status.missing_keys, "unexpected_keys": status.unexpected_keys}))

    predictions: list[np.ndarray] = []
    ground_truth: list[np.ndarray] = []
    for start in range(0, len(query_rows), args.batch_size):
        batch = query_rows[start : start + args.batch_size]
        points, labels, texts = [], [], []
        for row in batch:
            annotation = annotations[int(row["annotation_index"])]
            expected = (row["shape_id"], row["class"], row["affordance"])
            actual = (
                str(annotation["shape_id"]),
                str(annotation["class"]),
                str(annotation["affordance"]),
            )
            if actual != expected:
                raise ValueError(f"annotation mismatch: expected={expected}, actual={actual}")
            point, _, _ = normalize_point_cloud(objects[str(annotation["shape_id"])])
            points.append(point.T.astype(np.float32))
            labels.append(np.asarray(annotation["mask"], dtype=np.float32))
            texts.append(json.loads(row["model_questions_json"])[0])
        tensor = torch.from_numpy(np.stack(points)).to(device)
        with torch.no_grad():
            prediction = model((texts,), tensor).cpu().numpy().astype(np.float32)
        predictions.extend(prediction)
        ground_truth.extend(labels)
        print(f"infer {min(start + len(batch), len(query_rows))}/{len(query_rows)}", flush=True)

    prediction_array = np.stack(predictions)
    target_array = np.stack(ground_truth)
    if not np.isfinite(prediction_array).all():
        raise ValueError("prediction contains NaN or Inf")
    np.savez_compressed(
        output / "predictions.npz",
        prediction=prediction_array,
        ground_truth=target_array,
        query_id=np.asarray([row["query_id"] for row in query_rows]),
    )

    iou, auc = calculate_batch_iou_auc(prediction_array, target_array)
    sims = calculate_batch_sim(prediction_array, target_array)
    maes = calculate_batch_mae(prediction_array, target_array)
    query_metrics: list[dict[str, object]] = []
    prediction_by_id: dict[str, np.ndarray] = {}
    target_by_id: dict[str, np.ndarray] = {}
    metric_by_id: dict[str, tuple[float, float]] = {}
    for index, row in enumerate(query_rows):
        query_id = row["query_id"]
        prediction_by_id[query_id] = prediction_array[index]
        target_by_id[query_id] = target_array[index]
        metric_by_id[query_id] = (float(sims[index]), float(maes[index]))
        query_metrics.append(
            {
                "query_id": query_id,
                "split": row["split"],
                "shape_id": row["shape_id"],
                "class": row["class"],
                "affordance": row["affordance"],
                "condition": row["query_condition"],
                "IOU": float(iou[index]),
                "AUC": float(auc[index]),
                "SIM": float(sims[index]),
                "MAE": float(maes[index]),
            }
        )
    write_csv(output / "query_metrics.csv", query_metrics)

    switching_rows: list[dict[str, object]] = []
    for pair in pair_rows:
        for condition in ("Label", "Canonical"):
            prefix = f"val::{pair['shape_id']}"
            query_a = f"{prefix}::{pair['affordance_a']}::{condition}"
            query_b = f"{prefix}::{pair['affordance_b']}::{condition}"
            pred_a, pred_b = prediction_by_id[query_a], prediction_by_id[query_b]
            gt_a, gt_b = target_by_id[query_a], target_by_id[query_b]
            sim_a, mae_a = metric_by_id[query_a]
            sim_b, mae_b = metric_by_id[query_b]
            gt_change = float(np.mean(np.abs(gt_b - gt_a)))
            pred_change = float(np.mean(np.abs(pred_b - pred_a)))
            margin_a = sim(pred_a, gt_a) - sim(pred_a, gt_b)
            margin_b = sim(pred_b, gt_b) - sim(pred_b, gt_a)
            switching_rows.append(
                {
                    "pair_id": pair["pair_id"],
                    "shape_id": pair["shape_id"],
                    "class": pair["class"],
                    "pair_type": pair["pair_type"],
                    "condition": condition,
                    "gt_change_l1": gt_change,
                    "prediction_change_l1": pred_change,
                    "response_ratio": pred_change / (gt_change + 1e-12),
                    "sim_a": sim_a,
                    "sim_b": sim_b,
                    "mae_a": mae_a,
                    "mae_b": mae_b,
                    "margin_a": margin_a,
                    "margin_b": margin_b,
                    "bca": int(margin_a > 0 and margin_b > 0),
                    "both_sim_ge_05": int(sim_a >= 0.5 and sim_b >= 0.5),
                }
            )
    write_csv(output / "pair_switching.csv", switching_rows)

    summary: dict[str, object] = {
        "queries": len(query_rows),
        "pairs": len(pair_rows),
        "shapes": len(selected_shapes),
        "conditions": {},
    }
    for condition in ("Label", "Canonical"):
        rows = [row for row in switching_rows if row["condition"] == condition]
        qualified = [row for row in rows if row["both_sim_ge_05"]]
        summary["conditions"][condition] = {
            "pair_count": len(rows),
            "median_prediction_change_l1": float(np.median([row["prediction_change_l1"] for row in rows])),
            "median_response_ratio": float(np.median([row["response_ratio"] for row in rows])),
            "bca_rate_all": float(np.mean([row["bca"] for row in rows])),
            "both_sim_ge_05_count": len(qualified),
            "bca_rate_both_sim_ge_05": (
                float(np.mean([row["bca"] for row in qualified])) if qualified else None
            ),
            "near_zero_ratio_lt_01_all": float(
                np.mean([row["response_ratio"] < 0.1 for row in rows])
            ),
            "near_zero_ratio_lt_01_both_sim_ge_05": (
                float(np.mean([row["response_ratio"] < 0.1 for row in qualified]))
                if qualified
                else None
            ),
        }
    (output / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
