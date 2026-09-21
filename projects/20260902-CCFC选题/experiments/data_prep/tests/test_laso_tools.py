import json
import sys
import unittest
from pathlib import Path

import numpy as np


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from laso_tools import (  # noqa: E402
    VIEWPOINTS,
    analyze_questions,
    build_pair_rows,
    build_query_rows,
    select_discovery_shapes,
)


class PairConstructionTests(unittest.TestCase):
    def test_builds_direction_independent_pair_metrics(self):
        annotations = [
            {
                "split": "val",
                "annotation_index": 0,
                "shape_id": "door-1",
                "class": "door",
                "affordance": "open",
                "mask": np.array([1.0, 1.0, 0.0, 0.0]),
            },
            {
                "split": "val",
                "annotation_index": 1,
                "shape_id": "door-1",
                "class": "door",
                "affordance": "push",
                "mask": np.array([0.0, 1.0, 1.0, 0.0]),
            },
        ]

        rows, issues = build_pair_rows(annotations)

        self.assertEqual(issues, [])
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["pair_id"], "val::door-1::open::push")
        self.assertAlmostEqual(row["mask_iou"], 1.0 / 3.0)
        self.assertAlmostEqual(row["foreground_fraction_a"], 0.5)
        self.assertAlmostEqual(row["foreground_fraction_b"], 0.5)
        self.assertAlmostEqual(row["mean_abs_gt_diff"], 0.5)

    def test_reports_duplicate_shape_affordance_without_inflating_pairs(self):
        annotations = [
            {
                "split": "test",
                "annotation_index": i,
                "shape_id": "shape-1",
                "class": "mug",
                "affordance": affordance,
                "mask": np.array(mask, dtype=float),
            }
            for i, (affordance, mask) in enumerate(
                [("grasp", [1, 0]), ("grasp", [1, 0]), ("contain", [0, 1])]
            )
        ]

        rows, issues = build_pair_rows(annotations)

        self.assertEqual(rows, [])
        self.assertTrue(any(issue["issue"] == "duplicate_shape_affordance" for issue in issues))


class LanguageAnalysisTests(unittest.TestCase):
    def test_extracts_templates_and_mention_flags(self):
        question_rows = [
            {
                "Object": "door",
                "Affordance": "open",
                "Question0": "Where should I open the door?",
                "Question1": "Which part of the door lets me open it?",
            }
        ]

        inventory, templates, issues = analyze_questions(question_rows)

        self.assertEqual(issues, [])
        self.assertEqual(len(inventory), 2)
        self.assertTrue(inventory[0]["object_mentioned"])
        self.assertTrue(inventory[0]["affordance_mentioned"])
        self.assertIn("{object}", inventory[0]["normalized_template"])
        self.assertIn("{affordance}", inventory[0]["normalized_template"])
        self.assertEqual(sum(row["count"] for row in templates), 2)


class ManifestTests(unittest.TestCase):
    def test_shape_selection_is_deterministic_and_covers_pair_types(self):
        pairs = [
            {"shape_id": "s1", "pair_type": "open|push"},
            {"shape_id": "s2", "pair_type": "open|push"},
            {"shape_id": "s3", "pair_type": "cut|stab"},
            {"shape_id": "s4", "pair_type": "sit|support"},
            {"shape_id": "s5", "pair_type": "grasp|lift"},
        ]

        selected_a = select_discovery_shapes(pairs, fraction=0.4, seed=42)
        selected_b = select_discovery_shapes(pairs, fraction=0.4, seed=42)

        self.assertEqual(selected_a, selected_b)
        self.assertEqual(len(selected_a), 2)
        covered = {
            row["pair_type"] for row in pairs if row["shape_id"] in set(selected_a)
        }
        self.assertEqual(len(covered), 2)

    def test_query_manifest_contains_model_ready_viewpoint_questions(self):
        pairs = [
            {
                "pair_id": "val::door-1::open::push",
                "split": "val",
                "shape_id": "door-1",
                "class": "door",
                "affordance_a": "open",
                "affordance_b": "push",
                "annotation_index_a": 3,
                "annotation_index_b": 4,
            }
        ]
        lookup = {
            ("door", "open"): "Where would you open the door?",
            ("door", "push"): "Where would you push the door?",
        }

        rows = build_query_rows(pairs, lookup)

        self.assertEqual(len(rows), 4)
        canonical = next(
            row
            for row in rows
            if row["affordance"] == "open" and row["query_condition"] == "Canonical"
        )
        model_questions = json.loads(canonical["model_questions_json"])
        self.assertEqual(len(model_questions), len(VIEWPOINTS))
        self.assertEqual(model_questions[0].split(".", 1)[1].strip(), lookup[("door", "open")])


if __name__ == "__main__":
    unittest.main()
