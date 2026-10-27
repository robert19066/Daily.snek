from typing import Literal

from .rawFetch import RawFetch
from .tokenSys import AutoApiToken, ManualApiToken

FilterResource = Literal["tags", "sources"]
FilterAction = Literal["follow", "unfollow", "block", "unblock"]


class SnekSDK:
    """Python client for daily.dev's versioned Public API."""

    def __init__(self, token: ManualApiToken | AutoApiToken):
        self.token = token
        self.base_url = "https://api.daily.dev/public/v1"
        self.fetch = RawFetch(token=self.token)

    def get_rate_limit(self):
        return self.fetch.get_rate_limit_header("x-ratelimit-limit")

    def get_rate_remaining(self):
        return self.fetch.get_rate_limit_header("x-ratelimit-remaining")

    def get_rate_reset_time(self):
        return self.fetch.get_rate_limit_header("x-ratelimit-reset")

    def get_retry_time(self):
        return self.fetch.get_rate_limit_header("retry-after")

    def get_personalised_feed(self, params: dict | None = None):
        return self.fetch.fetch("feeds/foryou", params=params)

    def get_personalized_feed(self, params: dict | None = None):
        """US-spelling alias for :meth:`get_personalised_feed`."""
        return self.get_personalised_feed(params=params)

    def get_popular_feed(self, params: dict | None = None):
        return self.fetch.fetch("feeds/popular", params=params)

    def get_discussed_feed(self, params: dict | None = None):
        return self.fetch.fetch("feeds/discussed", params=params)

    def get_tag_feed(self, tag: str, params: dict | None = None):
        return self.fetch.fetch(f"feeds/tag/{tag}", params=params)

    def get_source_feed(self, source: str, params: dict | None = None):
        return self.fetch.fetch(f"feeds/source/{source}", params=params)

    def get_post(self, post_id: str):
        return self.fetch.fetch(f"posts/{post_id}")

    def get_post_comments(self, post_id: str, params: dict | None = None):
        return self.fetch.fetch(f"posts/{post_id}/comments", params=params)

    def search_posts(self, query: str, params: dict | None = None):
        return self.fetch.fetch(
            "search/posts",
            params={"q": query, **(params or {})},
        )

    def search_tags(self, query: str, params: dict | None = None):
        return self.fetch.fetch(
            "search/tags",
            params={"q": query, **(params or {})},
        )

    def search_sources(self, query: str, params: dict | None = None):
        return self.fetch.fetch(
            "search/sources",
            params={"q": query, **(params or {})},
        )

    def get_bookmarks(self, params: dict | None = None):
        return self.fetch.fetch("bookmarks/", params=params)

    def add_bookmarks(self, post_ids: list[str], list_id: str | None = None):
        data: dict[str, object] = {"postIds": post_ids}
        if list_id is not None:
            data["listId"] = list_id
        return self.fetch.fetch("bookmarks/", method="POST", json=data)

    def search_bookmarks(self, query: str, params: dict | None = None):
        return self.fetch.fetch(
            "bookmarks/search",
            params={"q": query, **(params or {})},
        )

    def get_bookmark_lists(self):
        return self.fetch.fetch("bookmarks/lists")

    def create_bookmark_list(self, name: str, icon: str | None = None):
        data: dict[str, object] = {"name": name}
        if icon is not None:
            data["icon"] = icon
        return self.fetch.fetch("bookmarks/lists", method="POST", json=data)

    def delete_bookmark_list(self, list_id: str):
        return self.fetch.fetch(f"bookmarks/lists/{list_id}", method="DELETE")

    def delete_bookmark(self, bookmark_id: str):
        return self.fetch.fetch(f"bookmarks/{bookmark_id}", method="DELETE")

    def move_bookmark(self, bookmark_id: str, list_id: str | None):
        return self.fetch.fetch(
            f"bookmarks/{bookmark_id}",
            method="PATCH",
            json={"listId": list_id},
        )

    def get_custom_feeds(self, params: dict | None = None):
        return self.fetch.fetch("feeds/custom/", params=params)

    def create_custom_feed(self, **data: object):
        return self.fetch.fetch("feeds/custom/", method="POST", json=data)

    def get_custom_feed(self, feed_id: str, params: dict | None = None):
        return self.fetch.fetch(f"feeds/custom/{feed_id}", params=params)

    def update_custom_feed(self, feed_id: str, **data: object):
        return self.fetch.fetch(
            f"feeds/custom/{feed_id}",
            method="PATCH",
            json=data,
        )

    def delete_custom_feed(self, feed_id: str):
        return self.fetch.fetch(f"feeds/custom/{feed_id}", method="DELETE")

    def get_custom_feed_info(self, feed_id: str):
        return self.fetch.fetch(f"feeds/custom/{feed_id}/info")

    def get_custom_feed_advanced_settings(self):
        return self.fetch.fetch("feeds/custom/advanced-settings")

    def update_custom_feed_advanced_settings(
        self,
        feed_id: str,
        settings: list[dict[str, object]],
    ):
        return self.fetch.fetch(
            f"feeds/custom/{feed_id}/advanced",
            method="PATCH",
            json={"settings": settings},
        )

    def get_feed_filters(self, feed_id: str | None = None):
        endpoint = f"feeds/filters/{feed_id}" if feed_id else "feeds/filters/"
        return self.fetch.fetch(endpoint)

    def update_feed_filter(
        self,
        resource: FilterResource,
        action: FilterAction,
        values: list[str],
        feed_id: str | None = None,
    ):
        """Follow, unfollow, block, or unblock tags or sources."""
        if resource not in ("tags", "sources"):
            raise ValueError("resource must be 'tags' or 'sources'")
        if action not in ("follow", "unfollow", "block", "unblock"):
            raise ValueError("action must be follow, unfollow, block, or unblock")

        prefix = f"feeds/filters/{feed_id}/" if feed_id else "feeds/filters/"
        return self.fetch.fetch(
            f"{prefix}{resource}/{action}",
            method="POST",
            json={resource: values},
        )

    def get_notifications(self, params: dict | None = None):
        return self.fetch.fetch("notifications/", params=params)

    def get_unread_notification_count(self):
        return self.fetch.fetch("notifications/unread/count")

    def mark_notifications_read(self):
        return self.fetch.fetch("notifications/read", method="POST")

    def get_profile(self):
        return self.fetch.fetch("profile/")

    def update_profile(self, **data: object):
        return self.fetch.fetch("profile/", method="PATCH", json=data)

    def search_stack(self, query: str):
        return self.fetch.fetch("profile/stack/search", params={"q": query})

    def get_stack(self):
        return self.fetch.fetch("profile/stack/")

    def add_stack_item(self, **data: object):
        return self.fetch.fetch("profile/stack/", method="POST", json=data)

    def update_stack_item(self, item_id: str, **data: object):
        return self.fetch.fetch(
            f"profile/stack/{item_id}",
            method="PATCH",
            json=data,
        )

    def delete_stack_item(self, item_id: str):
        return self.fetch.fetch(f"profile/stack/{item_id}", method="DELETE")

    def reorder_stack(self, **data: object):
        return self.fetch.fetch(
            "profile/stack/reorder",
            method="PUT",
            json=data,
        )

    def get_experiences(self, params: dict | None = None):
        return self.fetch.fetch("profile/experiences/", params=params)

    def create_experience(self, **data: object):
        return self.fetch.fetch("profile/experiences/", method="POST", json=data)

    def get_experience(self, experience_id: str):
        return self.fetch.fetch(f"profile/experiences/{experience_id}")

    def update_experience(self, experience_id: str, **data: object):
        return self.fetch.fetch(
            f"profile/experiences/{experience_id}",
            method="PUT",
            json=data,
        )

    def delete_experience(self, experience_id: str):
        return self.fetch.fetch(
            f"profile/experiences/{experience_id}",
            method="DELETE",
        )

    def get_tags(self):
        return self.fetch.fetch("tags/")

    def recommend_by_keyword(self, keyword: str):
        return self.fetch.fetch(
            "recommend/keyword",
            params={"keyword": keyword},
        )

    def recommend_semantic(self, **params: object):
        """Call the deprecated semantic recommendation endpoint."""
        return self.fetch.fetch("recommend/semantic", params=params)

    def search_plugins(self, query: str | None = None, **params: object):
        if query is not None:
            params["q"] = query
        return self.fetch.fetch("plugins/", params=params or None)

    def get_plugin(self, plugin_id: str):
        return self.fetch.fetch(f"plugins/{plugin_id}")

    def submit_plugin(self, **data: object):
        return self.fetch.fetch("plugins/", method="POST", json=data)

    def update_plugin(self, plugin_id: str, **data: object):
        return self.fetch.fetch(
            f"plugins/{plugin_id}",
            method="PUT",
            json=data,
        )

    def signup(self, **data: object):
        return self.fetch.fetch("signup/", method="POST", json=data)

    getRateLimit = get_rate_limit
    getRateRemaining = get_rate_remaining
    getRateResetTime = get_rate_reset_time
    getRetryTime = get_retry_time
    getPersonalisedFeed = get_personalised_feed
    getPopularFeed = get_popular_feed
    getDiscussedFeed = get_discussed_feed
    getTagFeed = get_tag_feed
    getSourceFeed = get_source_feed
    getPost = get_post
    getPostComments = get_post_comments
    searchPosts = search_posts
    searchTags = search_tags
    searchSources = search_sources
    getBookmarks = get_bookmarks
    addBookmarks = add_bookmarks
    searchBookmarks = search_bookmarks
    getBookmarkLists = get_bookmark_lists
    createBookmarkList = create_bookmark_list
    deleteBookmarkList = delete_bookmark_list
    deleteBookmark = delete_bookmark
    moveBookmark = move_bookmark
    getProfile = get_profile
    updateProfile = update_profile
    searchStack = search_stack
    getStack = get_stack
    addStackItem = add_stack_item
    updateStackItem = update_stack_item
    deleteStackItem = delete_stack_item
    reorderStack = reorder_stack
    getExperiences = get_experiences
    createExperience = create_experience
    getExperience = get_experience
    updateExperience = update_experience
    deleteExperience = delete_experience
    getTags = get_tags
    recommendByKeyword = recommend_by_keyword
    recommendSemantic = recommend_semantic
