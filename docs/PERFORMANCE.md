# Performance investigation — 3 October 2026

No local application server, production MongoDB connection, account login, load test, email or payment call was made. Public HTTP checks used curl with a 20-second timeout. These are single workstation samples, not browser performance scores or a regional benchmark.

| Public request before this deployment | HTTP | Time to first byte | Total | Body bytes |
| --- | ---: | ---: | ---: | ---: |
| `https://vernaculearn.africa` without following redirect | 307 | 1.126 s | 1.126 s | 15 |
| Same URL following one redirect | 200 | 1.240 s | 1.241 s | 1,349 |
| Railway `/docs` | 200 | 1.391 s | 1.391 s | 940 |
| Railway `/openapi.json` | 200 | 1.053 s | 1.328 s | 46,299 |

The public documentation endpoints do not query application collections. Their availability is not evidence that database latency is good or that the reported MongoDB startup incident is permanently repaired. No database operation was measured. Authenticated API latency, cold-start duration, repeat browser navigation, LCP/INP/CLS, CPU/rendering cost and low-end mobile performance remain **unmeasured**. There is no claimed live before/after speedup.

## Comparable build evidence

Built committed `766fc12` frontend source in an ignored isolated directory with the same installed Vite/dependencies, then built this change. The production branch subsequently advanced to `38db580` with backend-only performance changes; those were fast-forwarded and preserved before the combined commit. `performance-build.json` records bytes. Gzip sizes use Python gzip and can differ slightly from Vite's reporting. HTML entry JavaScript excludes lazy route chunks and external SDK payloads.

| Metric | Before | After |
| --- | ---: | ---: |
| Initial first-party JS | 162,865 bytes | 166,207 bytes |
| Initial first-party JS gzip | 62,393 bytes | 64,438 bytes |
| All first-party JS across routes | 374,183 bytes / 36 files | 390,970 bytes / 42 files |
| Eager external SDK script tags | 2 | 0 |

The added features slightly increase first-party code; this is not presented as a bundle-size reduction. The meaningful changes are when code/network work happens:

- Google identity loads on sign-in action; Google Pay loads only on an eligible checkout after backend availability and matching frontend environment checks. Neither loads on initial splash/dashboard or recovery pages. Games, chat and video have no dependencies yet.
- Route-level code splitting already existed and is preserved. Explore and foundations are small lazy route chunks. The recovery entry has first-party resources only.
- The old worker recursively downloaded every lazy admin/tutor/lesson chunk at installation. The new worker installs HTML entry assets only; feature chunks cache when fetched under an active worker. Previously unvisited routes are not guaranteed offline. No video/audio bulk preload is introduced. User-specific API isolation and denial handling remain tested. An update notice lets the user refresh deliberately, avoiding mid-lesson forced reloads.
- Auth hydration is no longer repeated by both the router and App mount; concurrent hydration calls share a promise. Public login/registration does not wait on an unnecessary user lookup. Existing API calls have a 15-second timeout so an outage produces feedback rather than an indefinite wait.
- Dashboard catalogue/progress/review requests start in parallel instead of three serial waits. Catalogue requests share in-flight work and reuse the public catalogue for five minutes. Duplicate unit fetch during enrolment is removed.
- Since `766fc12`, unit listing changed from one unit query plus one lesson query per accessible unit to one unit query and one batched aggregation. The incoming `38db580` already implements batching/timing logs; this combined commit retains it and restores the bounded 50 lessons per unit / 50 units result caps. With three accessible units, the cumulative change reduces four database round trips to two by inspection; no production latency reduction is asserted.
- Independent dictionary lookups use bounded indexed prefixes and preserve accents. The old lesson vocabulary lookup remains a two-second/200-candidate fallback; it is not claimed to be a fully indexed lexicon. `ensure_indexes.py` describes required indexes; none were applied in production.

Fonts and Material Icons still use Google-hosted CSS. Primary cards, avatars and logos reserve layout space through existing dimensions, but layout shift has not been measured. There is no large media feed. Incoming `38db580` also batches progress-summary queries and attempts core indexes after the database ping; this work preserves those changes. Their live impact remains unmeasured. Loading/status feedback exists on recovery, dictionary, foundations and payment availability. Future work: browser traces on a representative phone, API timing by route, DB explain plans and large-catalogue bounds, font self-hosting if worthwhile, and CDN/media tuning.
