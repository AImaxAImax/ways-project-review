# WAYS review request

## Public review repo

Repo: <https://github.com/AImaxAImax/ways-project-review>

Verification from Hermes after publishing:

```json
{
  "private": false,
  "visibility": "public",
  "html_url": "https://github.com/AImaxAImax/ways-project-review",
  "handoff_doc_public": true
}
```

Working tree at time of publishing:

```text
## master...origin/master
```

The handoff/run-down doc was added and verified public:

- `docs/WAYS_PROJECT_HANDOFF_FULL_RUNDOWN.md`
- Public raw doc check passed. First heading: `# WAYS project handoff: crons, workflows, and philosophy`

## What this repo is

This is a sanitized GitHub review bundle for WAYS / `wait.are.you.seri`, a short-form weird-facts video operation. The goal is not just to review code quality. The reviewer should evaluate the full agent-operable content system: ideation, sourcing, creative direction, local video generation, QA gates, upload/publishing flow, automation, and handoff quality.

Heavy generated assets, model weights, OAuth tokens, local secrets, and private runtime state were intentionally excluded. Reviewers should treat this as a representative code/context bundle, not a full production machine image.

## Start here

1. `README.md`  
   Top-level orientation and repo map.

2. `docs/WAYS_PROJECT_HANDOFF_FULL_RUNDOWN.md`  
   Main human/context layer. Read this before judging the architecture.

3. `docs/AGENT_REVIEW_BRIEF.md`  
   Reviewer-focused brief and expectations.

4. `docs/WORKFLOWS_AND_PHILOSOPHY.md`  
   The content/process philosophy behind WAYS.

5. `docs/CRONS_AND_AUTOMATION.md`  
   Automation and scheduled workflow context.

6. `docs/SCAN_REPORT.md` and `docs/SECRET_SCAN_REPORT.md`  
   Sanitization and safety context for the review bundle.

## What we should review

### 1. Overall strategy and product direction

Review whether WAYS is aimed at the right wedge:

- Weird, high-retention facts for TikTok/Shorts/Reels.
- Agent-operated production with human taste gates.
- Premium-feeling visuals without prematurely spending on paid video generations.
- Reusable pipelines that can scale across topics.

Questions to answer:

- Is this a coherent content product, or is it overbuilt for the current stage?
- What should be simplified before more automation is added?
- What should be doubled down on because it creates durable quality or speed advantages?

### 2. Content quality gates

Review the QA/publish gate philosophy and the concrete test case outputs.

Key angle: the user only wants uploads that clear a high quality bar. Drafts should not be uploaded unless they are strong enough.

Questions to answer:

- Are the publish gates specific enough to prevent mediocre videos from slipping through?
- Are the failure labels actionable enough for agents to fix issues?
- Are there missing checks for retention, pacing, novelty, visual artifacts, or factual clarity?
- Should the gate be more numeric, more taste-based, or both?

### 3. Local video generation workflow

Review the ComfyUI / Wan2.2 / I2V-oriented production lane represented in the repo.

Questions to answer:

- Is the current local-generation approach practical for repeatable short-form production?
- Are there better abstractions around prompts, plates, seeds, shot manifests, and QA notes?
- Are anatomy/artifact constraints handled well enough, especially for animals?
- How should the workflow balance source preservation versus motion richness?

### 4. Code architecture and maintainability

Review scripts, tools, tests, repo organization, and naming.

Questions to answer:

- What code should be promoted into reusable libraries versus kept as per-video scripts?
- Are the test cases organized well enough for future agents to understand and reuse?
- Are there duplicate scripts or one-off files that should be consolidated?
- Is the repo easy for a new coding agent to inspect and operate without context leakage?

### 5. Agent-operability

This project is intended to be run by agents, not only humans.

Questions to answer:

- Can an agent safely pick up a test case and produce a next version without asking many questions?
- Are instructions explicit enough around what to run, what to avoid, and how to verify?
- Are there enough dry-run/limit modes and rollback-safe operations?
- Where should additional machine-readable manifests be added?

### 6. Automation and cron design

Review `docs/CRONS_AND_AUTOMATION.md` and related workflow assumptions.

Questions to answer:

- Which crons are actually useful at this stage?
- Which crons risk creating noisy, low-value work?
- What should be event-driven instead of scheduled?
- What notifications or review queues should exist before auto-publishing anything?

### 7. Publishing and platform workflow

Review the publishing flow at the system level.

Questions to answer:

- What should happen between final QA and upload?
- What metadata, title, caption, hashtag, thumbnail, and provenance records should be stored?
- Where should platform performance feedback loop back into scripts and creative decisions?
- What should never be automated without explicit user approval?

### 8. Security and sanitization

Review the bundle for accidental leakage risk and future repo hygiene.

Questions to answer:

- Did the sanitized bundle exclude the right categories of assets and secrets?
- Are there remaining filenames, logs, configs, or docs that could reveal more than intended?
- What pre-push checks should be mandatory before future public review bundles?

### 9. Tests and verification

Known verification from the publishing step:

```text
33 passed in 10.04s
```

Questions to answer:

- Are these tests meaningful for the pipeline, or mostly smoke tests?
- What test coverage is missing for video assembly, manifests, upload logic, and publish gates?
- What should be validated by unit tests versus manual/video QA?

## Desired reviewer output

Please produce a Markdown review with these sections:

1. **Executive summary**  
   5 to 10 bullets on the biggest findings.

2. **Top risks**  
   Ordered by severity. Include why each risk matters and how to fix it.

3. **Highest-leverage improvements**  
   Specific improvements that make the system faster, safer, or higher quality.

4. **What to delete or simplify**  
   Anything that adds complexity without near-term value.

5. **Agent handoff gaps**  
   Missing docs, manifests, commands, or safety rails that would block another agent.

6. **Content-quality critique**  
   Feedback on whether the pipeline is likely to produce 8/10 or better short videos.

7. **Technical/code critique**  
   Architecture, tests, repo structure, scripts, maintainability.

8. **Recommended next 7 days**  
   A practical sequence of tasks, ordered by impact.

9. **Recommended next 30 days**  
   What to build only after the 7-day fixes are working.

10. **Open questions for Josh**  
   Only questions that materially change implementation choices.

## Review stance

Be direct. Prefer practical fixes over abstract critique. Assume the goal is to ship better videos faster while keeping human approval for anything public-facing. Do not recommend broad automation unless it improves quality, repeatability, or safety.

The bar is not “does the repo run.” The bar is “can this become a reliable, agent-operated content production system that consistently produces impressive weird-fact shorts.”
