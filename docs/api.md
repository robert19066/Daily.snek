# API reference and compatibility

`SnekSDK` targets the daily.dev Public API at
`https://api.daily.dev/public/v1`. It uses bearer-token authentication and
returns the upstream decoded JSON without converting it into SDK-specific
models. A successful response with no body returns `None`.

The method names below use Python `snake_case`. Existing camelCase SDK method
names remain available as compatibility aliases.

## Supported endpoint groups

The SDK wraps these documented Public API routes:

| Group | Routes |
| --- | --- |
| Feeds | `GET /feeds/foryou`, `/feeds/popular`, `/feeds/discussed`, `/feeds/tag/{tag}`, `/feeds/source/{source}` |
| Posts | `GET /posts/{id}`, `/posts/{id}/comments` |
| Search | `GET /search/posts`, `/search/tags`, `/search/sources` |
| Bookmarks | `GET` and `POST /bookmarks/`; `GET /bookmarks/search`; `GET` and `POST /bookmarks/lists`; `PATCH /bookmarks/{id}`; `DELETE /bookmarks/{id}` and `/bookmarks/lists/{id}` |
| Custom feeds | `GET` and `POST /feeds/custom/`; `GET`, `PATCH`, and `DELETE /feeds/custom/{feedId}`; `GET /feeds/custom/{feedId}/info`; `GET /feeds/custom/advanced-settings`; `PATCH /feeds/custom/{feedId}/advanced` |
| Feed filters | `GET /feeds/filters/` and `/feeds/filters/{feedId}`; `POST` to follow, unfollow, block, or unblock tags or sources globally or for a custom feed |
| Notifications | `GET /notifications/`, `GET /notifications/unread/count`, `POST /notifications/read` |
| Profile and experience | `GET` and `PATCH /profile/`; `GET`, `POST`, `PATCH`, `PUT`, or `DELETE` on profile stack and experience routes |
| Tags and recommendations | `GET /tags/`, `/recommend/keyword`, and `/recommend/semantic` |
| Plugins | `GET` and `POST /plugins/`; `GET` and `PUT /plugins/{id}` |

Use the daily.dev [OpenAPI specification](https://api.daily.dev/public/v1/docs/json)
for current parameters, request schemas, and response schemas. Query parameters
can be passed using a method's `params` argument where available. Write payloads
are passed through as JSON.

## Plus features and permissions

Plus users get a higher API quota and Plus-only bookmark-list behavior. For
example, `add_bookmarks(post_ids, list_id=...)` sends the optional `listId`;
the API may ignore it for non-Plus accounts. Some operations or fields can be
plan-gated. The SDK does not hide these responses: a denied request raises the
upstream `requests.HTTPError` (often HTTP 403).

OAuth access tokens also need the right permission: read calls require the
`read` scope and writes require `write`. A read-only OAuth approval can therefore
read data but cannot make changes.

## Python methods

### Feeds, posts, and search

```python
client.get_personalised_feed(params=None)
client.get_popular_feed(params=None)
client.get_discussed_feed(params=None)
client.get_tag_feed(tag, params=None)
client.get_source_feed(source, params=None)
client.get_post(post_id)
client.get_post_comments(post_id, params=None)
client.search_posts(query, params=None)
client.search_tags(query, params=None)
client.search_sources(query, params=None)
```

`get_personalized_feed()` is also available as the US-spelling equivalent.

### Bookmarks

```python
client.get_bookmarks(params=None)
client.add_bookmarks(post_ids, list_id=None)
client.search_bookmarks(query, params=None)
client.get_bookmark_lists()
client.create_bookmark_list(name, icon=None)
client.delete_bookmark_list(list_id)
client.delete_bookmark(bookmark_id)
client.move_bookmark(bookmark_id, list_id)
```

### Custom feeds and filters

```python
client.get_custom_feeds(params=None)
client.create_custom_feed(**data)
client.get_custom_feed(feed_id, params=None)
client.update_custom_feed(feed_id, **data)
client.delete_custom_feed(feed_id)
client.get_custom_feed_info(feed_id)
client.get_custom_feed_advanced_settings()
client.update_custom_feed_advanced_settings(feed_id, settings)
client.get_feed_filters(feed_id=None)
client.update_feed_filter(resource, action, values, feed_id=None)
```

For `update_feed_filter`, `resource` is `"tags"` or `"sources"` and `action` is
`"follow"`, `"unfollow"`, `"block"`, or `"unblock"`. `feed_id=None` applies the
change to the global For You feed; supplying a feed ID targets that custom feed.

### Notifications

```python
client.get_notifications(params=None)
client.get_unread_notification_count()
client.mark_notifications_read()
```

### Profile, stack, experiences, tags, and recommendations

```python
client.get_profile()
client.update_profile(**data)
client.search_stack(query)
client.get_stack()
client.add_stack_item(**data)
client.update_stack_item(item_id, **data)
client.delete_stack_item(item_id)
client.reorder_stack(**data)
client.get_experiences(params=None)
client.create_experience(**data)
client.get_experience(experience_id)
client.update_experience(experience_id, **data)
client.delete_experience(experience_id)
client.get_tags()
client.recommend_by_keyword(keyword)
client.recommend_semantic(**params)
```

`recommend_semantic()` calls a deprecated API route. Prefer
`recommend_by_keyword()`; experimental or deprecated routes may change or be
removed by daily.dev without a client release.

### Marketplace plugins

```python
client.search_plugins(query=None, **params)
client.get_plugin(plugin_id)
client.submit_plugin(**data)
client.update_plugin(plugin_id, **data)
```

`signup(**data)` is also retained for compatibility with earlier SDK versions,
but it is not present in the current Public API specification and is not
included in the supported endpoint list above.

### Rate-limit headers

`get_rate_limit()`, `get_rate_remaining()`, `get_rate_reset_time()`, and
`get_retry_time()` read response headers from the most recent request. They
return strings as received, or `None` when no response or header is available.

## Upstream API changes

The SDK uses the versioned `/public/v1` API, but it does not pin an OpenAPI
schema or validate response bodies. daily.dev controls that upstream contract:

- New upstream routes are not automatically added as named SDK methods. You can
  still call one with `client.fetch.fetch("route/path", ...)` until the SDK
  wraps it.
- Upstream additions appear in returned dictionaries as the API provides them;
  consumers should tolerate unknown fields.
- HTTP errors, including removed routes and insufficient permissions, are
  surfaced as `requests.HTTPError`; there is no success-shaped fallback.
- Deprecated and experimental endpoints may change without notice. Check the
  linked OpenAPI specification and changelog before relying on them.

For OAuth and remote MCP access, see [OAuth and MCP](oauth-mcp.md).
