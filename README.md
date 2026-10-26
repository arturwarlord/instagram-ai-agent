# Instagram AI Agent

A GitHub Actions project for generating realistic, varied photos of fictional adult character Alicia, preparing captions, and optionally scheduling reviewed Instagram feed posts through Metricool.

## Current workflow

- **Generate a photo:** run **Actions → Instagram AI Agent → Run workflow**, or wait for the daily schedule at 15:00 UTC.
- **Review the result:** open the successful run and download the `alicia-generated-image` artifact, or inspect the committed image in `content/generated/`.
- **Keep a favorite:** use **Actions → Select Alicia Photo → Run workflow**. Enter the exact PNG filename from `content/generated/` (filename only, no folder path). The workflow copies it to `content/selected/` and commits it.
- **Generate a caption:** use **Actions → Generate Alicia Caption → Run workflow** and enter the selected PNG filename.
- **Prepare a post:** use **Actions → Prepare Alicia Post Queue Entry → Run workflow**. Enter the selected filename and a future UTC timestamp, then choose whether to enable automatic Metricool scheduling. The default is **false**; keep it false for a draft.
- **Preview the scheduling queue:** use **Actions → Sync Alicia Queue to Metricool → Run workflow** and leave `dry_run` enabled. The preview does not call Metricool or submit a post.
- **Enable a scheduled post:** only after the Metricool setup is complete, run that sync workflow with `dry_run` disabled. It submits queue entries whose `publishing_enabled` flag is explicitly `true`; Metricool then manages the scheduled publication. A workflow checks the queue every 15 minutes.
- **Review content inventory:** use **Actions → Alicia Content Status Report → Run workflow**. It updates `reports/content_status.md`.
- **Check the direct Instagram API connection (optional):** follow [the read-only setup guide](docs/INSTAGRAM_API_SETUP.md), save `INSTAGRAM_ACCESS_TOKEN` as a GitHub secret, then run **Actions → Instagram API Connection Check**. This connection check does not publish and is separate from Metricool publishing.

## Metricool requirement

The GitHub-to-Metricool automatic scheduling integration uses Metricool's REST API, which the current Metricool documentation limits to **Advanced or Custom** plans. The Free plan can schedule posts in Metricool's own planner (up to 20 per month according to current plan documentation), but does not provide the REST API needed for this GitHub Actions integration.

See [Metricool automatic publishing setup](docs/METRICOOL_SETUP.md) for connecting Alicia, retrieving the IDs, configuring secrets, and testing safely.

## Required GitHub Actions secrets

For image generation and caption drafting:
- `Workers_AI` — Cloudflare Workers AI API token.
- `CLOUDFLARE_ACCOUNT_ID` — Cloudflare account ID.

For Metricool automatic scheduling (Advanced or Custom plan):
- `METRICOOL_API_TOKEN` — Metricool REST API token.
- `METRICOOL_USER_ID` — numeric user ID shown in Metricool.
- `METRICOOL_BLOG_ID` — numeric brand/blog ID shown in Metricool.

For the optional, read-only direct Instagram Login API check:
- `INSTAGRAM_ACCESS_TOKEN` — Instagram Login token, used only by the connection-check workflow.

Never put access tokens in source files, commits, issues, screenshots, or chat messages.

## Safety and scope

- The generator creates one photo per run and uses `character/reference/alicia.jpg` as the identity reference. Do not replace it unless intentionally changing Alicia's appearance.
- Generated photos and generation history are stored in the repository. The curated `content/selected/` folder contains manually chosen favorites.
- Queue entries have `publishing_enabled: false` by default. Only an entry explicitly prepared with the opt-in set to true can be submitted to Metricool.
- The Metricool sync workflow has a dry-run mode and skips disabled or already submitted entries. After submission, Metricool owns the publication schedule.
- The content status report and Instagram API connection check are read-only.
- Automatic replies to Instagram messages/comments are not enabled.
