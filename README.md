# Instagram AI Agent

A GitHub Actions project that generates one realistic, varied Alicia photo per run. Instagram publishing is intentionally not enabled.

## Current workflow

- **Generate a photo:** run **Actions → Instagram AI Agent → Run workflow**, or wait for the daily schedule at 15:00 UTC.
- **Review the result:** open the successful run and download the `alicia-generated-image` artifact, or inspect the committed image in `content/generated/`.
- **Keep a favorite:** use **Actions → Select Alicia Photo → Run workflow**. Enter the exact PNG filename from `content/generated/` (filename only, no folder path). The workflow copies it to `content/selected/` and commits it.
- **Avoid accidental overwrites:** selecting a filename already present in `content/selected/` fails safely instead of replacing the saved photo.

## Required GitHub Actions secrets

- `Workers_AI` — Cloudflare Workers AI API token.
- `CLOUDFLARE_ACCOUNT_ID` — Cloudflare account ID.

## Safety and scope

- Image generation runs only when manually started or on its daily schedule; selecting a favorite does not generate an image.
- The generator uses `character/reference/alicia.jpg` as the identity reference. Do not replace it unless intentionally changing Alicia's appearance.
- Generated photos and generation history are stored in the repository. The curated `content/selected/` folder is for manually chosen favorites.
- Instagram login, automatic posting, and automatic replies are not enabled.
