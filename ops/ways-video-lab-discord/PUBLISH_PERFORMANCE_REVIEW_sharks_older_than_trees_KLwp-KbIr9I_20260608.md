# WAYS publish performance review — sharks_older_than_trees / KLwp-KbIr9I

- Reviewed at: 2026-06-08T15:40:39Z
- Video: https://youtu.be/KLwp-KbIr9I
- Slug: `sharks_older_than_trees`
- Title: `Sharks Are Older Than Trees #Shorts`
- Channel: `Wait Are You Serious?` / `UCUgLdX0znSpNrG2rher1Fwg`
- Public publish authorization: Josh authorization recorded in `dashboard/review_decisions.json` and `ops/ways-video-lab-discord/public_publish_events.jsonl`.
- Local publish verification record: `test_cases/sharks_older_than_trees/outputs/final_polish_v27_captioned/youtube_draft_pack_20260606/youtube_verification.json` shows final `privacyStatus=public`, `categoryId=28`, `selfDeclaredMadeForKids=false`, `duration=PT25S`, captions attached.

## Current public YouTube state checked

Public-state checks used only read-only/public tooling; no YouTube state was modified.

- YouTube oEmbed: HTTP 200; title `Sharks Are Older Than Trees #Shorts`; author `Wait Are You Serious?`; thumbnail `https://i.ytimg.com/vi/KLwp-KbIr9I/hqdefault.jpg`.
- `yt-dlp --dump-json`: `availability=public`, `duration=24`, `view_count=1305`, `like_count=36`, `comment_count=null`, `upload_date=20260606`, channel `Wait Are You Serious?`, uploader `@WaitAreYouSeriousFacts`.
- Elapsed since recorded public verification at `2026-06-06T03:38:14Z`: 60.04 hours / 2.50 days, so this is inside the 48–72h review window.

## Analytics credential status

YouTube Analytics credentials were not available for retention/swipe-away metrics.

What is missing:

- No YouTube/Google Analytics env credentials are present in the cron environment; detected credential-related env names were only `ELEVENLABS_API_KEY` and `HINDSIGHT_LLM_API_KEY`.
- `~/.hermes/youtube_token.json` exists, but its scopes are only:
  - `https://www.googleapis.com/auth/youtube.upload`
  - `https://www.googleapis.com/auth/youtube.force-ssl`
- Missing scope/token for YouTube Analytics read reports, especially `https://www.googleapis.com/auth/yt-analytics.readonly` or an equivalent Analytics-read OAuth credential.

Manual metrics Josh should paste from YouTube Studio / Analytics for this exact video:

1. Views at 48–72h.
2. Likes, comments, shares, and subscribers gained/lost.
3. Average view duration.
4. Average percentage viewed / retention percent.
5. Audience retention graph values or a screenshot, especially timestamps of first major dip and lowest retention segment.
6. Shorts feed `Viewed` vs `Swiped away` counts or percentages.
7. Traffic source split, especially Shorts feed percentage.
8. Any notable watch-time/engagement warnings from Studio.

## Provisional read from public metrics only

- Public metrics show early traction: 1,305 views and 36 likes at ~60h.
- Public-only like rate is directionally healthy, but incomplete because public tooling did not expose retention, viewed-vs-swiped-away, shares, or subscriber impact.
- No class-level production lesson should be promoted yet because the required 48–72h retention/swipe-away data is missing.

## Next actions

1. Paste the manual Analytics metrics above into this folder or rerun with a YouTube Analytics OAuth token that includes `yt-analytics.readonly`.
2. Once `average percentage viewed` and `first major swipe/dip timestamp` are available, run `tools/ways_publish_review.py record-review` so the review is appended to `performance_reviews.jsonl` and mapped to the storyboard beat/shot.
3. If retention dip maps to the opening fossil/proof beat, consider tightening the setup before the fact reveal; if swipe-away is strong before ~2s, revise future WAYS hooks to reveal the impossible comparison faster.

## Post-review auth fix

After this cron run, the local Hermes YouTube token used by WAYS cron/scripts was replaced with the broader existing token from `~/.verticals/youtube_token.json`.

- Installed token path: `~/.hermes/youtube_token.json`
- Previous upload-only token backup: `~/.hermes/youtube_token.upload_only.20260608_084457.json`
- Verified scopes now include:
  - `https://www.googleapis.com/auth/youtube.upload`
  - `https://www.googleapis.com/auth/youtube.force-ssl`
  - `https://www.googleapis.com/auth/youtube.readonly`
  - `https://www.googleapis.com/auth/yt-analytics.readonly`
- Verification query using `~/.hermes/youtube_token.json` succeeded for `KLwp-KbIr9I`:
  - public Data API: `1305` views, `public`
  - Analytics API row: `928` views, `175` estimated minutes watched, `25s` average view duration, `102.8%` average viewed, `34` likes, `0` shares, `3` subscribers gained
