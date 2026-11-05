# Aflow Read public roadmap

`data/aflow-read-roadmap.json` is the single public feature/status/review-date authority. `aflow-read/roadmap/index.html` is generated output, committed because the existing GitHub Pages branch-root pipeline publishes static HTML. No client JavaScript, new service, package manager or hosting workflow is required.

After a genuine approved content review, edit the JSON explicitly, then run:

    python3 -B scripts/build-roadmap.py
    python3 -B scripts/build-roadmap.py --check
    python3 -B scripts/check-roadmap.py

The renderer never assigns today’s date. Run checks during every website build/review before commit. Do not hand-edit independent feature statuses into other HTML pages.

The four public feature statuses are `available`, `up-next`, `planned`, `exploring`. While no public release has been accepted, `Available Now` honestly shows a separate prelaunch foundation preview, not features marked publicly available. To promote an item, record actual accepted public-release provenance in the canonical ledger and supply its matching evidence JSON to `--release-evidence PATH`. A development milestone or TestFlight upload cannot satisfy the gate. When public availability is established, pass the same `--release-evidence PATH` to `scripts/check-roadmap.py` and to the renderer’s `--check` invocation. The evidence must state `publicReleaseAccepted:true` and match the published version, releasedOn and App Store URL; each promoted item must name that released version. Keep internal ledger paths and engineering details out of the public JSON.

Canonical owner procedure: `/Volumes/Lacie 2TB/AflowDevelopment/DevelopmentLedger/WEBSITE_MAINTENANCE.md`. Public releases require website-impact review, approved changes, preserved commit/rollback and independent live HTTPS verification. Internal acceptance triggers review only. Monthly review is genuine work, not an automatically refreshed date. Keep technical planning separately in the internal Development Ledger.
