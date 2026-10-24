# Verified API reference

Import paths:

```python
from snek.snekSDK import SnekSDK
from snek.tokenSys import AutoApiToken, ManualApiToken
from snek.rawFetch import RawFetch, RateLimitError
```

`SnekSDK` methods:

- Feeds: `getPersonalisedFeed()`, `getPopularFeed()`, `getDiscussedFeed()`, `getTagFeed(tag)`, `getSourceFeed(source)`
- Posts/search: `getPost(post_id)`, `getPostComments(post_id)`, `searchPosts(query)`, `searchTags(query)`, `searchSources(query)`, `getTags()`, `recommendByKeyword(keyword)`, `recommendSemantic(**params)` (deprecated)
- Bookmarks: `getBookmarks()`, `addBookmarks(post_ids, list_id=None)`, `searchBookmarks(query)`, `getBookmarkLists()`, `createBookmarkList(name, icon=None)`, `deleteBookmarkList(list_id)`, `deleteBookmark(bookmark_id)`, `moveBookmark(bookmark_id, list_id)`
- Profile: `getProfile()`, `updateProfile(**data)`
- Stack: `searchStack(query)`, `getStack()`, `addStackItem(**data)`, `updateStackItem(item_id, **data)`, `deleteStackItem(item_id)`, `reorderStack(**data)`
- Experience: `getExperiences()`, `createExperience(**data)`, `getExperience(experience_id)`, `updateExperience(experience_id, **data)`, `deleteExperience(experience_id)`
- Other: `signup(**data)`, `getRateLimit()`, `getRateRemaining()`, `getRateResetTime()`, `getRetryTime()`

`RawFetch` also provides `get`, `post`, `put`, `patch`, `delete`, and `fetch`. Its constructor is `RawFetch(token, max_rate_limit_retries=3)`; negative retry counts raise `ValueError`.
