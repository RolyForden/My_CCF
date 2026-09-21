import csv
import json
import pickle
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np


DATA_PREP = Path(__file__).resolve().parents[1]


def write_fixture(root: Path) -> None:
    rows = {
        "train": [
            {"shape_id": "train-1", "class": "door", "affordance": "open", "mask": np.array([1, 0])},
        ],
        "val": [
            {"shape_id": "val-1", "class": "door", "affordance": "open", "mask": np.array([1, 0])},
            {"shape_id": "val-1", "class": "door", "affordance": "push", "mask": np.array([0, 1])},
        ],
        "test": [
            {"shape_id": "test-1", "class": "door", "affordance": "open", "mask": np.array([1, 0])},
            {"shape_id": "test-1", "class": "door", "affordance": "push", "mask": np.array([0, 1])},
        ],
    }
    for split, annotations in rows.items():
        with (root / f"anno_{split}.pkl").open("wb") as handle:
            pickle.dump(annotations, handle)
        objects = {str(row["shape_id"]): np.zeros((2, 3), dtype=np.float32) for row in annotations}
        with (root / f"objects_{split}.pkl").open("wb") as handle:
            pickle.dump(objects, handle)

    with (root / "Affordance-Question.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["Object", "Affordance", "Question0", "Question1"])
        writer.writeheader()
        writer.writerow(
            {
                "Object": "door",
                "Affordance": "open",
                "Question0": "Where would you open the door?",
                "Question1": "Which part of the door opens?",
            }
        )
        writer.writerow(
            {
                "Object": "door",
                "Affordance": "push",
                "Question0": "Where would you push the door?",
                "Question1": "Which part of the door should be pushed?",
            }
        )


class AuditCliTests(unittest.TestCase):
    def test_audit_writes_pair_and_language_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "data"
            output = Path(tmp) / "audit"
            root.mkdir()
            write_fixture(root)

            subprocess.run(
                [
                    sys.executable,
                    str(DATA_PREP / "audit_laso.py"),
                    "--data-root",
                    str(root),
                    "--output",
                    str(output),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            with (output / "pairs_all.csv").open(encoding="utf-8", newline="") as handle:
                pairs = list(csv.DictReader(handle))
            summary = json.loads((output / "run_summary.json").read_text(encoding="utf-8"))
            self.assertEqual(len(pairs), 2)
            self.assertEqual(summary["splits"]["val"]["pair_count"], 1)
            self.assertEqual(summary["splits"]["test"]["pair_count"], 1)
            self.assertEqual(summary["language"]["question_count"], 4)


class FreezeCliTests(unittest.TestCase):
    def test_freeze_uses_val_for_discovery_and_test_for_confirmation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            audit = root / "audit"
            output = root / "frozen"
            data = root / "data"
            audit.mkdir()
            data.mkdir()
            write_fixture(data)

            subprocess.run(
                [
                    sys.executable,
                    str(DATA_PREP / "audit_laso.py"),
                    "--data-root",
                    str(data),
                    "--output",
                    str(audit),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            with (audit / "pairs_all.csv").open(encoding="utf-8", newline="") as handle:
                pairs = list(csv.DictReader(handle))
            review_path = root / "pair_review.csv"
            review_keys = sorted({(pair["class"], pair["pair_type"]) for pair in pairs})
            with review_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=["class", "pair_type", "include", "reason"])
                writer.writeheader()
                for object_class, pair_type in review_keys:
                    writer.writerow(
                        {
                            "class": object_class,
                            "pair_type": pair_type,
                            "include": "yes",
                            "reason": "fixture",
                        }
                    )

            subprocess.run(
                [
                    sys.executable,
                    str(DATA_PREP / "freeze_manifests.py"),
                    "--audit-dir",
                    str(audit),
                    "--pair-review",
                    str(review_path),
                    "--output",
                    str(output),
                    "--fraction",
                    "1.0",
                    "--seed",
                    "42",
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            discovery = json.loads((output / "discovery_full_shapes.json").read_text(encoding="utf-8"))
            confirmation = json.loads((output / "confirmation_shapes.json").read_text(encoding="utf-8"))
            with (output / "query_manifest.csv").open(encoding="utf-8", newline="") as handle:
                queries = list(csv.DictReader(handle))
            self.assertEqual(discovery, ["val-1"])
            self.assertEqual(confirmation, ["test-1"])
            self.assertEqual(len(queries), 8)


if __name__ == "__main__":
    unittest.main()
