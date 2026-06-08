# External Image Model Escalation v23 — Use GPT Image 2 / ChatGPT image lane

## Decision
There is no creative reason to avoid GPT Image 2 / ChatGPT image generation for this project. The local ComfyUI lane was used because it was available, scriptable, cheap/fast, and supports local ControlNet-style layout testing. But the current bottleneck is finish quality plus object fidelity, so this is exactly the point to escalate.

## Why local ComfyUI was used first
- Fast local iteration without paid external calls.
- Scriptable batches/contact sheets under project folders.
- ControlNet/Canny guides help enforce layout.
- Good for discovering failure modes: museum sameness, object drift, forest hallucination.

## Why GPT Image 2 should be used now
- Higher finish quality and taste level.
- Better at premium editorial/commercial-looking frames.
- Better candidate for hard literal beats like apple + squirrel + nut while keeping charm.
- Useful as a hero-style-frame challenger before continuing full production.

## Updated workflow
1. Keep local ComfyUI for rough layout/control tests only.
2. For production style frames, use GPT Image 2 / ChatGPT image output when available.
3. Test only 3 hard frames first:
   - Shot 1: ancient shark + barren no-tree shoreline.
   - Shot 3: apple + squirrel + nut comparison gag.
   - Shot 4: 400+ million years geologic timeline.
4. If GPT Image 2 produces an 8/10+ style frame, use it as the visual ceiling and rebuild remaining shots around that quality bar.
5. If API/tool access is unavailable from Hermes, generate the 3 prompts manually in ChatGPT image UI and drop results back into the project for curation.

## Current access note
Hermes image_gen toolset is enabled, but this session has no visible OPENAI_API_KEY or image_gen provider/model config. The built-in image_generate tool does not let the agent choose a specific model at call time; the backend/model are user-configured. So using GPT Image 2 from here requires configuring the image generation provider or using the ChatGPT UI manually.
