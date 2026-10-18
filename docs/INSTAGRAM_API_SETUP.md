# Official Instagram API setup for Alicia (Creator)

This project uses the official **Instagram API with Instagram Login** path. The connection check is read-only. It does not publish, schedule, or edit posts.

Official Meta documentation:
- [Instagram API documentation by Meta](https://www.postman.com/meta/instagram/documentation/6yqw8pt/instagram-api)
- [Instagram Platform: Content Publishing](https://developers.facebook.com/docs/instagram-platform/content-publishing/)

## 1. Create/configure the Meta app

1. Open [Meta for Developers](https://developers.facebook.com/) and sign in with the account that controls Alicia's Instagram Creator account.
2. Create a Meta app. If asked for an app use case/product, choose the Instagram API / Instagram Login path for managing an Instagram professional account.
3. In the app dashboard, configure **Instagram Login** and add the Instagram account as an app tester if the dashboard requires it while the app is in development mode.
4. Add the permissions needed for this project's intended future use:
   - `instagram_business_basic` — read the connected professional account's basic identity.
   - `instagram_business_content_publish` — permission needed later for publishing.
5. Complete the Instagram Login/token-generation flow for Alicia's Creator account and grant the requested permissions. Follow any Meta prompts to accept the app invitation from the Instagram account if applicable.

Meta's available products and app dashboard labels may change. Do not switch to unofficial APIs or provide your Instagram password to third-party sites.

## 2. Save the token as a GitHub secret

1. Open this repository: [Settings → Secrets and variables → Actions](https://github.com/arturwarlord/instagram-ai-agent/settings/secrets/actions).
2. Choose **New repository secret**.
3. Name it exactly `INSTAGRAM_ACCESS_TOKEN`.
4. Paste the access token into the secret value and save it.

**Do not paste the token into a source file, commit, issue, screenshot, or this chat.** If it is exposed, revoke/rotate it in Meta and replace the GitHub secret.

## 3. Run the read-only connection check

1. Open [Actions](https://github.com/arturwarlord/instagram-ai-agent/actions).
2. Select **Instagram API Connection Check**.
3. Click **Run workflow** → **Run workflow**.
4. Open the run and inspect the **Check Instagram Login API (read-only)** step.

On success, the log prints only the account username and ID. The token is not printed. The check calls the account identity endpoint using GET; it does not create a media container or publish anything.

## Troubleshooting

- **Missing secret:** confirm the secret is named `INSTAGRAM_ACCESS_TOKEN` exactly.
- **HTTP 400/401/403:** regenerate or refresh the token, confirm Instagram Login was configured, ensure the token belongs to Alicia's Creator account, and verify `instagram_business_basic` is granted.
- **Permission error:** check the app's permission setup and whether Alicia accepted any tester invitation. Meta may require additional app setup/review depending on how the app is used and who will use it.
- **API version error:** update `INSTAGRAM_API_VERSION` in `.github/workflows/instagram-connection-check.yml` to a currently supported version after verifying Meta's docs.

## Safety boundary

- This workflow only checks account identity using a GET request.
- It never publishes, schedules, deletes, or edits Instagram content.
- Publishing remains disabled until you explicitly ask to implement and enable it as a separate step.
