# Metricool automatic Instagram publishing setup

This repository submits reviewed Alicia image posts to Metricool through its official API. Metricool then auto-publishes each post at the UTC time stored in the queue. This integration targets Instagram feed image posts.

## Plan requirement

Metricool's current documentation says its REST API is available only on **Advanced or Custom** plans. Free supports up to 20 posts per month when scheduling inside Metricool, but does not provide REST API access for GitHub Actions automation. Check the price in your own account before upgrading.

Official references:
- [Metricool API guide](https://help.metricool.com/basic-guide-for-api-integration-r97af)
- [Plans and API access](https://help.metricool.com/plans-add-ons-and-api-access-explained-xux1u)
- [Instagram connection options](https://help.metricool.com/access-to-instagram-from-metricool-connection-types-and-differences-kcsrb)

## 1. Connect Alicia

1. In Metricool, add a brand for Alicia.
2. Connect the professional **Creator** account.
3. Metricool recommends connecting through Facebook and linking Instagram to a Facebook Page for the most complete features. Instagram Login also supports scheduling and publishing but provides fewer analytics features.
4. In the Planner, confirm Alicia is an Instagram destination and that an image post can be scheduled with Auto-publish enabled.

## 2. Configure GitHub secrets

Only continue with API setup on an Advanced or Custom plan.

1. In Metricool, open **Account Settings → API** and copy the REST API token.
2. Open Alicia's Metricool brand. The browser URL includes the numeric **userId** and **blogId**.
3. Open [GitHub Actions secrets](https://github.com/arturwarlord/instagram-ai-agent/settings/secrets/actions).
4. Create these three repository secrets:

| Secret | Value |
|---|---|
| METRICOOL_API_TOKEN | Metricool REST API token |
| METRICOOL_USER_ID | Numeric userId from the Metricool URL |
| METRICOOL_BLOG_ID | Numeric blogId for Alicia's brand |

Never put the token in a source file, commit, issue, screenshot, or chat message.

## 3. Prepare a post

1. Run **Instagram AI Agent** to generate a photo.
2. Run **Select Alicia Photo** to save the chosen photo under content/selected/.
3. Run **Generate Alicia Caption** using the selected PNG filename.
4. Run **Prepare Alicia Post Queue Entry** with the exact selected filename and a future UTC time, for example 2026-10-28T15:00:00Z.
5. Leave **Enable automatic Metricool scheduling** set to false for a draft. Set it to true only when you intend to send the post to Metricool for automatic publication.

## 4. Verify and schedule

1. Open **Actions → Sync Alicia Queue to Metricool → Run workflow**.
2. Leave **dry_run** checked the first time. It previews eligible posts and makes no API calls.
3. After verifying the image and caption, run it again with **dry_run** unchecked. This sends explicitly enabled future posts to Metricool and saves the returned post ID in the queue.
4. The workflow checks the queue every 15 minutes. Once a queue item is submitted, Metricool owns the schedule and publishes at the selected time.
5. Check the Metricool Planner to verify that the post appears under Instagram with auto-publish enabled.

## Safety

- Queue entries default to publishing_enabled: false.
- The sync workflow ignores drafts unless automatic scheduling was explicitly enabled when preparing the queue entry.
- Dry-run mode does not call Metricool or update queue status.
- Successfully submitted entries are marked submitted_to_metricool.
- The selected image must be committed to the public main branch before Metricool can import it.
- Verify the first scheduled post in Metricool before relying on recurring automation.
