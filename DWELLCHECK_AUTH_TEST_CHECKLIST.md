# DwellCheck manual auth test checklist

Use this checklist while Supabase auth is enabled. Keep the Metro logs open, but never copy access
tokens, refresh tokens, JWTs, service-role keys or provider secrets into screenshots or support notes.

## Expected safe debug logs

The temporary mobile auth logs are prefixed with `[SupabaseAuth]`. They may show:

- app start session check
- auth state change event name
- current user id
- current user email
- provider name
- login success or failure
- logout success or failure
- upload/report blocked because no user is signed in
- upload/report allowed because a user is signed in

They must not show:

- Supabase access tokens
- refresh tokens
- full JWTs
- OpenAI keys
- Supabase service-role keys
- Google or Apple client secrets
- uploaded document text or report contents

## Fresh install / logged-out state

- [ ] Delete/reinstall the development build or clear app data.
- [ ] Launch DwellCheck.
- [ ] Confirm the app opens to Welcome/Login.
- [ ] Confirm logs include `app start session check` and a result with `hasSession: false`.
- [ ] Confirm Home, Reviews, Account, upload, scan and report screens are not reachable without signing in.
- [ ] Try starting an upload/report flow while logged out if any route exposes it.
- [ ] Confirm it is blocked and logs `upload/report attempt blocked`.

## Google sign-in

- [ ] Confirm Supabase's Google provider accepts the iOS OAuth client ID as an authorized
      client ID/audience: `342135933361-mf1t927ntj24a3hqjopsd74j93jjfgfs.apps.googleusercontent.com`.
- [ ] Confirm the backend has `SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY`,
      `SUPABASE_SERVICE_ROLE_KEY` and `GOOGLE_IOS_CLIENT_ID` configured.
- [ ] Confirm the backend is running and reachable from the simulator before tapping Google.
- [ ] Tap Continue with Google.
- [ ] Complete Google sign-in.
- [ ] Confirm the app reaches the main Home screen.
- [ ] Confirm logs include `login success` with provider `google`.
- [ ] Confirm logs show user id/email only, with no token values.
- [ ] Open Account.
- [ ] Confirm the displayed email/user matches the Google account.

## Session persistence

- [ ] Force quit the app.
- [ ] Reopen DwellCheck.
- [ ] Confirm it restores directly to the signed-in app, not Welcome.
- [ ] Confirm logs include `app start session check complete` with `hasSession: true`.
- [ ] Confirm reports restored belong to the signed-in user only.

## Authenticated upload/report generation

- [ ] While signed in, open New property review.
- [ ] Upload a PDF and start analysis.
- [ ] Confirm logs include `upload/report attempt allowed`.
- [ ] Confirm the backend receives a Bearer token, not `x-dev-user-id`, when Supabase auth is configured.
- [ ] Confirm the created report is visible in Reviews for the same account.
- [ ] Confirm the backend record uses the Supabase `auth.user.id` as `user_id`.

## Logout

- [ ] Open Account and tap Sign out.
- [ ] Confirm logs include `logout success` or a handled local logout failure.
- [ ] Confirm the app returns to Welcome/Login.
- [ ] Force quit and reopen the app.
- [ ] Confirm the app remains on Welcome/Login.
- [ ] Confirm logs include `hasSession: false`.
- [ ] Try upload/report generation again and confirm it is blocked.

## Cross-account isolation

- [ ] Sign in as Google account A.
- [ ] Create or restore a report.
- [ ] Sign out.
- [ ] Sign in as account B, or Apple account B when available.
- [ ] Confirm account B does not see account A's reports.
- [ ] Attempt to open account A's report ID through any debug/deep-link/manual request.
- [ ] Confirm the backend returns `404` or `401`, not account A's report.

## Apple sign-in

- [ ] On a supported iOS simulator/device, tap Continue with Apple.
- [ ] Complete Apple sign-in.
- [ ] Confirm Account shows Apple provider and private relay/email where applicable.
- [ ] Repeat session persistence, upload/report, logout and cross-account isolation checks.

## Regression checks

- [ ] Supabase publishable key exists only in mobile env/config.
- [ ] Supabase service-role key exists only in backend env.
- [ ] OpenAI key exists only in backend env.
- [ ] No auth token or service key appears in Metro logs, backend logs, screenshots or crash output.
- [ ] `npm run typecheck` passes in `mobile`.
- [ ] Backend protected routes reject missing, malformed and expired Bearer tokens.
