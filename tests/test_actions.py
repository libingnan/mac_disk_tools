import os
import unittest

from mac_disk_tools.actions import get_delete_policy


class DeletePolicyTests(unittest.TestCase):
    def test_blocks_danger_root_descendants(self):
        policy = get_delete_policy("/private/tmp/example", require_exists=False)

        self.assertFalse(policy["deletable"])
        self.assertEqual(policy["delete_safety"], "danger")

    def test_blocks_paths_outside_configured_roots(self):
        policy = get_delete_policy("/__mac_disk_tools_unknown__/item", require_exists=False)

        self.assertFalse(policy["deletable"])
        self.assertIn("扫描范围", policy["delete_reason"])

    def test_allows_safe_configured_descendants(self):
        cache_child = os.path.expanduser("~/Library/Caches/example-cache")
        policy = get_delete_policy(cache_child, require_exists=False)

        self.assertTrue(policy["deletable"])
        self.assertEqual(policy["delete_safety"], "safe")


if __name__ == "__main__":
    unittest.main()
