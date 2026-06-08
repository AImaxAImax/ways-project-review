# Scan report

A lightweight regex scan was run over the sanitized review bundle. No literal credential/token files were copied.

The scan produced path/env-var references only, all expected and non-secret:

- Scripts reference `~/.hermes/youtube_token.json` as a local token path. The token file itself is not included.
- One script references the environment variable name `ELEVENLABS_API_KEY`; no key value is included.

The raw scan-hit file was intentionally not included because this repo ignores `*secret*` filenames and the useful information is summarized above.
