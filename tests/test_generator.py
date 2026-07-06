import unittest

from generator import generate_copy_pack


class GeneratorTests(unittest.TestCase):
    def setUp(self):
        self.form = {
            "title": "Serving It Up Raw with Chef J",
            "guest": "Chef J",
            "topics": "late-night cooking, creative pressure, and the live show energy",
            "highlights": "The kitchen gets loud\nThe crowd picks a favorite moment",
            "quotes": "We keep it raw and real\nThat timing was wild",
            "cta": "Watch the full episode and share your favorite moment.",
            "direction": "Warm, punchy, and conversational.",
            "platform": "all",
            "tone": "warm and conversational",
        }

    def test_generates_three_platform_packs(self):
        result = generate_copy_pack(self.form, "Chefs, timing, and audience energy were discussed.")

        self.assertIn("episode", result)
        self.assertIn("platforms", result)
        self.assertEqual(set(result["platforms"].keys()), {"facebook", "instagram", "youtube"})
        self.assertIn("export", result)
        self.assertTrue(result["export"]["bundleName"].startswith("Serving It Up Raw with Chef J"))

    def test_platform_pack_contains_variants_and_hooks(self):
        result = generate_copy_pack(self.form, "Chefs, timing, and audience energy were discussed.")
        youtube_pack = result["platforms"]["youtube"]

        self.assertGreaterEqual(len(youtube_pack["descriptions"]), 3)
        self.assertGreaterEqual(len(youtube_pack["hooks"]), 3)
        self.assertGreaterEqual(len(youtube_pack["youtubeTitles"]), 3)
        self.assertTrue(any("#ServingItUpRaw" in tag for tag in youtube_pack["hashtags"]))

    def test_single_platform_selection_is_respected(self):
        form = dict(self.form)
        form["platform"] = "instagram"

        result = generate_copy_pack(form, "Fast edits, crowd reactions, and highlight clips.")

        self.assertEqual(list(result["platforms"].keys()), ["instagram"])
        self.assertIn("highlightHooks", result["platforms"]["instagram"])


if __name__ == "__main__":
    unittest.main()