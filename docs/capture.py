"""Drive the running dashboard and photograph it, for the user guide.

    python docs/capture.py

Every image in `docs/USER_GUIDE.md` comes from here: a real browser, clicking
real buttons, against a real database. Nothing is mocked up, so the guide cannot
quietly drift from the application — re-run this after a UI change and the
screenshots are current again.

Expects the app already running on http://localhost:8501 with a fresh demo
(press **Start over** first, or delete `data/demo/sentinelops.db`).
"""

from __future__ import annotations

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

URL = "http://localhost:8501"
SHOTS = Path(__file__).resolve().parent / "images"
VIEWPORT = {"width": 1600, "height": 1000}

#: Streamlit repaints asynchronously; this is how long we let it settle before
#: the shutter. Generous, because a slow frame makes a misleading screenshot.
#:
#: Raised from 2.5s when the corpus grew to eighteen months and eleven units: a
#: single cycle now creates, screens and assesses several hundred instances, and
#: the old wait photographed the page mid-repaint — which produced screenshots
#: of a walkthrough that had not actually advanced.
SETTLE_MS = 9000


def settle(page, ms: int = SETTLE_MS) -> None:
    page.wait_for_timeout(ms)


def shoot(page, name: str, *, full: bool = False) -> None:
    SHOTS.mkdir(parents=True, exist_ok=True)
    path = SHOTS / f"{name}.png"
    page.screenshot(path=str(path), full_page=full)
    print(f"  captured {path.name}")


#: How long to keep looking for a button before giving up on it.
#:
#: Polling rather than sleeping, because the two things that make a button
#: appear late — seeding an eighteen-month corpus on first load, and running a
#: cycle over five hundred instances — take a length of time that depends on the
#: machine. A fixed sleep is either too short on a slow one or wastes minutes on
#: a fast one, and when it is too short the shutter fires on a page that has not
#: advanced, which is worse than failing.
WAIT_MS = 90_000
POLL_MS = 500


def wait_for_button(page, label: str, *, timeout_ms: int = WAIT_MS):
    """Return the button once it exists, or None once we stop waiting."""
    waited = 0
    while waited < timeout_ms:
        button = page.get_by_role("button", name=label, exact=True).first
        if button.count() > 0:
            return button
        page.wait_for_timeout(POLL_MS)
        waited += POLL_MS
    return None


def click(page, label: str, *, settle_ms: int = SETTLE_MS) -> bool:
    """Press a button by its visible text. Returns False if it never appears."""
    button = wait_for_button(page, label)
    if button is None:
        print(f"  ! no button labelled {label!r}")
        return False
    button.scroll_into_view_if_needed()
    button.click()
    settle(page, settle_ms)
    return True


def reset(page) -> None:
    """Start from a fresh demo, so the walkthrough is at step one.

    The database persists between runs, so without this the second capture
    photographs a walkthrough somebody already finished — and the guide then
    shows step 3 with step 5's data in it.
    """
    button = wait_for_button(page, "Start over")
    if button is None:
        print("  ! no Start over button; the shots may not begin at step one")
        return
    button.click()
    settle(page, SETTLE_MS)
    if wait_for_button(page, "Raise the checks that are due") is None:
        print("  ! the walkthrough did not return to step one")


def main() -> int:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport=VIEWPORT)
        page.goto(URL, wait_until="networkidle")
        settle(page, 6000)

        reset(page)
        shoot(page, "01-first-open", full=True)

        print("step 1 — raise the checks")
        click(page, "Raise the checks that are due", settle_ms=9000)
        shoot(page, "02-checks-raised")

        print("step 2 — advance three months")
        click(page, "Advance three months", settle_ms=25000)
        shoot(page, "03-time-passes")

        print("step 3 — the near miss")
        click(page, "Show me one", settle_ms=6000)
        shoot(page, "04-near-miss-walkthrough")
        page.get_by_text("Assessment detail", exact=True).first.scroll_into_view_if_needed()
        settle(page, 1500)
        shoot(page, "05-citation-highlighted")

        print("step 4 — the bill")
        page.get_by_text("GUIDED WALKTHROUGH", exact=False).first.scroll_into_view_if_needed()
        settle(page, 800)
        click(page, "Show the bill", settle_ms=5000)
        shoot(page, "06-what-it-cost")

        print("step 5 — fix it")
        click(page, "File a correction and re-check it", settle_ms=12000)
        shoot(page, "07-remediated")

        print("step 6 — prove it")
        click(page, "Verify the record and build the pack", settle_ms=20000)
        shoot(page, "08-chain-verified")

        print("operator console")
        page.get_by_text("Operator console", exact=True).first.scroll_into_view_if_needed()
        settle(page, 1500)
        shoot(page, "09-operator-console")

        page.get_by_text("Compliance status by process area").first.scroll_into_view_if_needed()
        settle(page, 1200)
        shoot(page, "10-status-and-queue")

        page.get_by_text("Submit evidence", exact=True).first.scroll_into_view_if_needed()
        settle(page, 1200)
        shoot(page, "11-upload-and-actions")

        print("patterns across the portfolio")
        page.get_by_text(
            "Patterns across the portfolio", exact=True
        ).first.scroll_into_view_if_needed()
        settle(page, 1200)
        shoot(page, "14-recurrence-and-brief")

        # The brief is one model call, so it is taken on demand rather than
        # rendered on load — press the button the way a reader would.
        try:
            page.get_by_role("button", name="Write the brief").first.click()
            settle(page, 3000)
            page.get_by_text(
                "Patterns across the portfolio", exact=True
            ).first.scroll_into_view_if_needed()
            settle(page, 1200)
            shoot(page, "15-prioritisation-brief")
        except Exception as error:  # pragma: no cover - capture is best effort
            print(f"  brief not captured: {error}")

        try:
            page.get_by_text(
                "Portfolio analytics", exact=False
            ).first.click()
            settle(page, 2500)
            shoot(page, "16-portfolio-analytics")
        except Exception as error:  # pragma: no cover
            print(f"  analytics not captured: {error}")

        page.get_by_text("Audit", exact=True).last.scroll_into_view_if_needed()
        settle(page, 1200)
        shoot(page, "12-audit-and-downloads")

        shoot(page, "13-whole-page", full=True)

        browser.close()
    print(f"\nwritten to {SHOTS}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
