
from .tokenSys import ManualApiToken, AutoApiToken
from .rawFetch import RawFetch


class SnekSDK:
    def __init__(self, token: ManualApiToken | AutoApiToken):
        self.token = token
        self.base_url = "https://api.daily.dev/public/v1"
        self.fetch = RawFetch(token=self.token)



    def getRateLimit(self):
        return self.fetch.get_rate_limit_header("x-ratelimit-limit")

    def getRateRemaining(self):
        return self.fetch.get_rate_limit_header("x-ratelimit-remaining")

    def getRateResetTime(self):
        return self.fetch.get_rate_limit_header("x-ratelimit-reset")

    def getRetryTime(self):
        return self.fetch.get_rate_limit_header("retry-after")


    def getPersonalisedFeed(self):
        return self.fetch.fetch("feeds/foryou")

    def getPopularFeed(self):
        return self.fetch.fetch("feeds/popular")

    def getDiscussedFeed(self):
        return self.fetch.fetch("feeds/discussed")

    def getTagFeed(self, tag: str):
        return self.fetch.fetch(f"feeds/tag/{tag}")

    def getSourceFeed(self, source: str):
        return self.fetch.fetch(f"feeds/source/{source}")



    def getPost(self, post_id: str):
        return self.fetch.fetch(f"posts/{post_id}")

    def getPostComments(self, post_id: str):
        return self.fetch.fetch(f"posts/{post_id}/comments")



    def searchPosts(self, query: str):
        return self.fetch.fetch("search/posts", params={"q": query})

    def searchTags(self, query: str):
        return self.fetch.fetch("search/tags", params={"q": query})

    def searchSources(self, query: str):
        return self.fetch.fetch("search/sources", params={"q": query})



    def getBookmarks(self):
        return self.fetch.fetch("bookmarks/")

    def addBookmarks(self, post_ids: list[str], list_id: str | None = None):
        data: dict[str, object] = {
            "postIds": post_ids,
        }

        if list_id is not None:
            data["listId"] = list_id

        return self.fetch.fetch(
            "bookmarks/",
            method="POST",
            json=data,
        )

    def searchBookmarks(self, query: str):
        return self.fetch.fetch(
            "bookmarks/search",
            params={"q": query},
        )

    def getBookmarkLists(self):
        return self.fetch.fetch("bookmarks/lists")

    def createBookmarkList(self, name: str, icon: str | None = None):
        data = {
            "name": name,
        }

        if icon is not None:
            data["icon"] = icon

        return self.fetch.fetch(
            "bookmarks/lists",
            method="POST",
            json=data,
        )

    def deleteBookmarkList(self, list_id: str):
        return self.fetch.fetch(
            f"bookmarks/lists/{list_id}",
            method="DELETE",
        )

    def deleteBookmark(self, bookmark_id: str):
        return self.fetch.fetch(
            f"bookmarks/{bookmark_id}",
            method="DELETE",
        )

    def moveBookmark(self, bookmark_id: str, list_id: str | None):
        return self.fetch.fetch(
            f"bookmarks/{bookmark_id}",
            method="PATCH",
            json={
                "listId": list_id,
            },
        )



    def getProfile(self):
        return self.fetch.fetch("profile")

    def updateProfile(self, **data):
        return self.fetch.fetch(
            "profile",
            method="PATCH",
            json=data,
        )



    def searchStack(self, query: str):
        return self.fetch.fetch(
            "profile/stack/search",
            params={"q": query},
        )

    def getStack(self):
        return self.fetch.fetch("profile/stack/")

    def addStackItem(self, **data):
        return self.fetch.fetch(
            "profile/stack/",
            method="POST",
            json=data,
        )

    def updateStackItem(self, item_id: str, **data):
        return self.fetch.fetch(
            f"profile/stack/{item_id}",
            method="PATCH",
            json=data,
        )

    def deleteStackItem(self, item_id: str):
        return self.fetch.fetch(
            f"profile/stack/{item_id}",
            method="DELETE",
        )

    def reorderStack(self, **data):
        return self.fetch.fetch(
            "profile/stack/reorder",
            method="PUT",
            json=data,
        )



    def getExperiences(self):
        return self.fetch.fetch("profile/experiences/")

    def createExperience(self, **data):
        return self.fetch.fetch(
            "profile/experiences/",
            method="POST",
            json=data,
        )

    def getExperience(self, experience_id: str):
        return self.fetch.fetch(
            f"profile/experiences/{experience_id}",
        )

    def updateExperience(self, experience_id: str, **data):
        return self.fetch.fetch(
            f"profile/experiences/{experience_id}",
            method="PUT",
            json=data,
        )

    def deleteExperience(self, experience_id: str):
        return self.fetch.fetch(
            f"profile/experiences/{experience_id}",
            method="DELETE",
        )



    def getTags(self):
        return self.fetch.fetch("tags/")



    def recommendByKeyword(self, keyword: str):
        return self.fetch.fetch(
            "recommend/keyword",
            params={"keyword": keyword},
        )

    def recommendSemantic(self, **params):
        """
        Deprecated by daily.dev.
        Prefer recommendByKeyword().
        """
        return self.fetch.fetch(
            "recommend/semantic",
            params=params,
        )


    def signup(self, **data):
        return self.fetch.fetch(
            "signup/",
            method="POST",
            json=data,
        )


    
    