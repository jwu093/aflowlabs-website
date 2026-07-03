# DwellCheck production launch roadmap

## Backend credentials

All secret credentials belong in the backend deployment secret manager. For local development,
copy `server/.env.example` to `server/.env`.

Available backend-only variables:

- `OPENAI_API_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`
- `AWS_REGION`
- `AWS_S3_BUCKET`
- `AWS_KMS_KEY_ID`
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

Do not add these to `mobile/.env`, Expo configuration or any `EXPO_PUBLIC_` variable.

Prefer an AWS IAM role/workload identity over static AWS access keys. Supabase/Postgres stores
accounts, reports, allowances, entitlements and object metadata; S3 stores document artifacts.

## Rewarded-ad previews

Recommended product rule:

- Ads are optional and shown only after the normal free preview is exhausted.
- One verified rewarded ad grants one additional preview.
- Maximum two rewarded previews per account per UTC day initially.
- The backend may lower the limit for abuse, unusually large documents or high AI cost.
- A reward never unlocks a paid report.

Required mobile work:

1. Move from Expo Go to an Expo development build because the AdMob SDK contains native code.
2. Add `react-native-google-mobile-ads` and platform-specific AdMob app/ad-unit IDs.
3. Add consent handling before ad SDK initialization, including UMP and applicable iOS tracking
   disclosures.
4. Use rewarded-ad test IDs in development.
5. Show an explicit opt-in explaining the exact reward before presenting the ad.
6. Poll the backend after the ad for the verified allowance update.

Required backend work:

1. Create a short-lived reward session containing a random nonce, authenticated user ID,
   expiration and intended reward.
2. Pass an opaque session token as AdMob server-side-verification custom data.
3. Add a public AdMob SSV callback endpoint that validates Google's signature and callback
   parameters. This endpoint authenticates the ad network signature rather than a user JWT.
4. Store the ad transaction ID with a unique constraint to prevent replay.
5. Enforce the daily account limit server-side.
6. Grant the preview only after a valid SSV callback. Never trust the mobile reward callback by
   itself.
7. Record AI cost and ad revenue attribution so the reward policy can be adjusted.

Revenue is generally:

`rewarded impressions / 1,000 × rewarded-ad eCPM`

Actual revenue varies by country, advertiser demand, consent status, fill rate and season. A
rewarded ad may not cover the AI cost of a long LIM. Track per-review AI cost before assuming the
ad-funded preview is profitable; consider lower page limits or two verified ads for expensive
document sets if economics require it.

## Store purchases

### iOS

- Load localized product and price data using StoreKit.
- Receive and verify StoreKit 2 signed transactions.
- Send the signed transaction and target report ID to the backend.
- Verify product, bundle, environment, transaction uniqueness and ownership on the backend.
- Persist an entitlement tied to the DwellCheck user and report before returning paid fields.
- Process App Store Server Notifications for refunds and revocations.

The report product is expected to be consumable. Consumable purchase history is not a reliable
cross-device restore mechanism after consumption, so DwellCheck's server entitlement is the
source of truth. Signing into the same DwellCheck account restores purchased report access.

### Android

- Use Google Play Billing to initiate the purchase.
- Send the purchase token and report ID to the backend.
- Verify the token using the Google Play Developer API before granting access.
- Acknowledge/consume purchases according to the chosen product design.
- Store each purchase token once and process refunds/revocations.

## Private document storage

Recommended S3 flow:

1. Backend creates a report/upload ID and a short-lived presigned upload.
2. Files enter a private quarantine prefix or bucket.
3. Block all public access and require TLS.
4. Encrypt objects with SSE-KMS.
5. Use object keys such as
   `users/{userId}/reports/{reportId}/uploads/{randomObjectId}`; never trust a client-supplied
   ownership path.
6. The backend records object ownership and checks the authenticated user on every download or
   deletion.
7. Only short-lived presigned download URLs are returned.

The database should hold metadata, ownership, hashes, scan status and retention dates—not raw
document bytes.

## Malware scanning

Use a quarantine-to-clean workflow:

1. Upload to quarantine.
2. Trigger GuardDuty Malware Protection for S3 or an isolated scanner such as ClamAV running in
   Lambda/Fargate.
3. Reject encrypted archives and unsupported nested containers.
4. Tag scan results and move/copy only clean objects to the processing prefix.
5. Never send an unscanned retained file to downstream storage or expose it for download.
6. Alert and delete/quarantine malicious objects without logging document contents.

## Retention and deletion

Proposed initial policy, subject to legal/privacy review:

- Original uploaded documents: delete 30 days after report creation unless the user explicitly
  chooses longer storage.
- Generated reports and purchase entitlements: retain until the user deletes the report/account
  or the legal retention period expires.
- Malware/quarantine failures: delete within 24 hours after security review metadata is retained.
- Operational logs: 30–90 days, with no document contents or tokens.
- Backups: encrypted and expired within a documented maximum period.

The active periods are configured through `ORIGINAL_FILE_RETENTION_DAYS`,
`DERIVED_ARTIFACT_RETENTION_HOURS` and `REPORT_EXPORT_RETENTION_DAYS`. The same periods must be
applied to S3 Lifecycle rules; application configuration alone does not delete S3 objects.

Implement S3 lifecycle rules, database `delete_after` timestamps, account deletion jobs and a
user-visible delete-report action. Deletion must cover primary storage, derived page images and
eventual backup expiry.

## Penetration testing

Before launch:

- Commission an independent mobile and API penetration test.
- Test OWASP API authorization failures, JWT handling, rate-limit bypass, upload parser attacks,
  presigned URL scope, entitlement replay and cross-account access.
- Test iOS/Android local storage, logs, screenshots, clipboard, deep links and certificate
  handling.
- Run SAST, dependency auditing, secret scanning and API DAST in CI.
- Remediate high/critical findings and retest before submission.
- Repeat after major authentication, purchase, storage or AI-processing changes.
