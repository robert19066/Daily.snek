import unittest
from unittest.mock import patch

from snek.snekSDK import SnekSDK
from snek.tokenSys import ManualApiToken


class SDKEndpointTests(unittest.TestCase):
    def setUp(self):
        self.client = SnekSDK(ManualApiToken("test-token"))

    def test_snake_case_and_legacy_feed_methods_are_equivalent(self):
        with patch.object(
            self.client.fetch,
            "fetch",
            return_value={"data": []},
        ) as fetch:
            self.assertEqual(self.client.get_popular_feed(), {"data": []})
            self.assertEqual(self.client.getPopularFeed(), {"data": []})

        self.assertEqual(
            [call.args for call in fetch.call_args_list],
            [
                ("feeds/popular",),
                ("feeds/popular",),
            ],
        )

    def test_custom_feed_methods_use_public_api_routes(self):
        with patch.object(self.client.fetch, "fetch") as fetch:
            self.client.create_custom_feed(name="Python", minUpvotes=5)
            self.client.update_custom_feed_advanced_settings(
                "feed-1",
                settings=[{"id": 2, "enabled": True}],
            )
            self.client.get_custom_feed_info("feed-1")

        self.assertEqual(
            fetch.call_args_list[0].args[0],
            "feeds/custom/",
        )
        self.assertEqual(fetch.call_args_list[0].kwargs["method"], "POST")
        self.assertEqual(
            fetch.call_args_list[1].args[0],
            "feeds/custom/feed-1/advanced",
        )
        self.assertEqual(fetch.call_args_list[1].kwargs["method"], "PATCH")
        self.assertEqual(
            fetch.call_args_list[2].args[0],
            "feeds/custom/feed-1/info",
        )

    def test_bookmark_list_id_is_forwarded_for_plus_accounts(self):
        with patch.object(self.client.fetch, "fetch") as fetch:
            self.client.add_bookmarks(["post-1"], list_id="list-1")

        fetch.assert_called_once_with(
            "bookmarks/",
            method="POST",
            json={"postIds": ["post-1"], "listId": "list-1"},
        )

    def test_feed_filter_supports_global_and_custom_feed_paths(self):
        with patch.object(self.client.fetch, "fetch") as fetch:
            self.client.update_feed_filter(
                "tags",
                "follow",
                ["python"],
            )
            self.client.update_feed_filter(
                "sources",
                "block",
                ["source-1"],
                feed_id="feed-1",
            )

        self.assertEqual(
            fetch.call_args_list[0].args[0],
            "feeds/filters/tags/follow",
        )
        self.assertEqual(
            fetch.call_args_list[0].kwargs["json"],
            {"tags": ["python"]},
        )
        self.assertEqual(
            fetch.call_args_list[1].args[0],
            "feeds/filters/feed-1/sources/block",
        )
        self.assertEqual(
            fetch.call_args_list[1].kwargs["json"],
            {"sources": ["source-1"]},
        )

    def test_feed_filter_rejects_unknown_route_parts(self):
        with self.assertRaises(ValueError):
            self.client.update_feed_filter("unknown", "follow", ["python"])

        with self.assertRaises(ValueError):
            self.client.update_feed_filter("tags", "unknown", ["python"])

    def test_notification_and_plugin_routes(self):
        with patch.object(self.client.fetch, "fetch") as fetch:
            self.client.get_unread_notification_count()
            self.client.mark_notifications_read()
            self.client.search_plugins("editor")
            self.client.update_plugin("daily-skill", name="Updated")

        self.assertEqual(fetch.call_args_list[0].args[0], "notifications/unread/count")
        self.assertEqual(fetch.call_args_list[1].args[0], "notifications/read")
        self.assertEqual(fetch.call_args_list[1].kwargs["method"], "POST")
        self.assertEqual(fetch.call_args_list[2].args[0], "plugins/")
        self.assertEqual(fetch.call_args_list[2].kwargs["params"], {"q": "editor"})
        self.assertEqual(fetch.call_args_list[3].args[0], "plugins/daily-skill")
        self.assertEqual(fetch.call_args_list[3].kwargs["method"], "PUT")


if __name__ == "__main__":
    unittest.main()
