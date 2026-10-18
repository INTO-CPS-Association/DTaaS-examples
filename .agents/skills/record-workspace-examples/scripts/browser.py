"""The browser part of the recording: sign in to DTaaS and open the workspace desktop."""

import re

import config
from session import shell

USER = "user@intocps.org"
PASSWORD = "user"


async def launch(playwright):
    """A headed Chromium filling the screen, with the clipboard allowed.

    Without the clipboard permissions, a dialog of the desktop covers it.
    """
    browser = await playwright.chromium.launch(
        headless=False, ignore_default_args=["--enable-automation"],
        args=["--window-position=0,0", f"--window-size={config.SIZE.replace('x', ',')}",
              "--no-first-run", "--disable-infobars"])
    context = await browser.new_context(
        no_viewport=True, permissions=["clipboard-read", "clipboard-write"])
    return browser, context


async def sign_in(page):
    """Sign in through Dex; Dex redirects back to the library page."""
    await page.goto("http://localhost/")
    await page.wait_for_timeout(3000)
    await page.get_by_role("button", name="SignIn").click()
    await page.wait_for_url("**/dex/**", timeout=30000)
    await page.wait_for_timeout(1500)
    await page.locator("input[name=login]").type(USER, delay=60)
    await page.locator("input[name=password]").type(PASSWORD, delay=120)
    await page.wait_for_timeout(1000)
    await page.keyboard.press("Enter")
    await page.wait_for_url(re.compile(r".*/[Ll]ibrary.*"), timeout=60000)
    await page.wait_for_timeout(4000)


async def open_desktop(context, page):
    """Open the workspace desktop from the Workbench; it opens in a new tab."""
    await page.get_by_text("Workbench", exact=True).first.click()
    await page.wait_for_timeout(4000)
    async with context.expect_page(timeout=20000) as new_page:
        await page.locator('button[title="Desktop-btn"]').click()
    desktop = await new_page.value
    await desktop.wait_for_timeout(15000)
    return desktop


async def back_to_desktop(desktop):
    """Bring the browser with the desktop in front of the host terminal."""
    shell("wmctrl -a Chromium || xdotool search --class chromium windowactivate")
    await desktop.bring_to_front()
    await desktop.wait_for_timeout(2000)
    await desktop.mouse.click(800, 500)
