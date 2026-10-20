# SDK method reference

Import and create a client as shown in the [quickstart](usage.md). Each method calls the corresponding daily.dev public API endpoint and returns decoded JSON, or `None` if a successful response has no body.

## Feeds

| Method | Purpose |
| --- | --- |
| `getPersonalisedFeed()` | Get the personalized feed. |
| `getPopularFeed()` | Get popular posts. |
| `getDiscussedFeed()` | Get discussed posts. |
| `getTagFeed(tag)` | Get posts for a tag. |
| `getSourceFeed(source)` | Get posts from a source. |

## Posts and search

| Method | Purpose |
| --- | --- |
| `getPost(post_id)` | Retrieve a post by ID. |
| `getPostComments(post_id)` | Retrieve comments for a post. |
| `searchPosts(query)` | Search posts. |
| `searchTags(query)` | Search tags. |
| `searchSources(query)` | Search sources. |
| `getTags()` | Retrieve tags. |
| `recommendByKeyword(keyword)` | Get keyword-based recommendations. |

`recommendSemantic(**params)` calls a daily.dev endpoint marked deprecated by the API. Prefer `recommendByKeyword()`.

## Bookmarks

`getBookmarks()`, `addBookmarks(post_ids, list_id=None)`, `searchBookmarks(query)`, and `getBookmarkLists()` manage or search bookmarks. Use `createBookmarkList(name, icon=None)` and `deleteBookmarkList(list_id)` for lists, and `deleteBookmark(bookmark_id)` or `moveBookmark(bookmark_id, list_id)` for individual bookmarks.

## Profile, stack, and experience

- Profile: `getProfile()`, `updateProfile(**data)`
- Stack: `searchStack(query)`, `getStack()`, `addStackItem(**data)`, `updateStackItem(item_id, **data)`, `deleteStackItem(item_id)`, `reorderStack(**data)`
- Experience: `getExperiences()`, `createExperience(**data)`, `getExperience(experience_id)`, `updateExperience(experience_id, **data)`, `deleteExperience(experience_id)`
- Signup: `signup(**data)`

Write-method payloads are passed through as JSON. Refer to the API's endpoint documentation for accepted fields.

## Rate-limit headers

After a request, `getRateLimit()`, `getRateRemaining()`, `getRateResetTime()`, and `getRetryTime()` return the matching headers from the most recent response. Values are strings as received from the server; before a response, or when a header is absent, the result is `None`.
