import unittest
from unittest.mock import patch

import release


class ReleaseSurveyTests(unittest.TestCase):
    def test_collect_notes_groups_user_facing_release_details(self):
        answers = [
            "A clearer release",
            "Add a new command",
            "",
            "",
            "Improve error messages",
            "",
            "",
            "",
            "Run unit tests and build validation",
        ]

        with (
            patch("builtins.input", side_effect=answers),
            patch("builtins.print"),
        ):
            notes = release.collect_notes()

        self.assertEqual(
            notes,
            [
                "Summary: A clearer release",
                "Feature: Add a new command",
                "Fix: Improve error messages",
                "Validation: Run unit tests and build validation",
            ],
        )

    def test_collect_notes_requires_summary_and_validation(self):
        with patch("builtins.input", return_value=""):
            with self.assertRaisesRegex(ValueError, "summary is required"):
                release.collect_notes()

        answers = ["A release", "", "", "", "", "", ""]
        with (
            patch("builtins.input", side_effect=answers),
            patch("builtins.print"),
        ):
            with self.assertRaisesRegex(ValueError, "validation performed"):
                release.collect_notes()

    def test_collect_commit_name_requires_a_title(self):
        with (
            patch("builtins.input", return_value=""),
            patch("builtins.print"),
        ):
            with self.assertRaisesRegex(ValueError, "commit title is required"):
                release.collect_commit_name()


if __name__ == "__main__":
    unittest.main()
