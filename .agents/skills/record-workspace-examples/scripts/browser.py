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
    # "SignIn" up to dtaas-web 1.7, "Sign In" from the redesigned client on
    await page.get_by_role("button", name=re.compile(r"sign ?in", re.I)).first.click()
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
    # By address and not by the menu text, which a collapsed menu hides
    await page.goto("http://localhost/workbench")
    await page.wait_for_timeout(4000)
    async with context.expect_page(timeout=20000) as new_page:
        # The icon button up to dtaas-web 1.7, the Desktop card from the
        # redesigned client on, whose title is the desktop's address
        await page.locator('button[title="Desktop-btn"], a[title*="/tools/vnc"]').first.click()
    desktop = await new_page.value
    await desktop.wait_for_timeout(15000)
    return desktop


async def page_action(page, action):
    """Wait (seconds), click a button, choose an option, scroll the page or zoom the 3D view.

    The wheel scrolls the page from its right edge, where no canvas takes it,
    and zooms when it is over the first canvas of the page.
    """
    if isinstance(action, (int, float)):
        await page.wait_for_timeout(action * 1000)
        return
    kind, value = action
    if kind == "click":
        await page.get_by_role("button", name=value, exact=True).first.click()
    elif kind == "choose":
        # A select is opened by its name, and the option is the first whose
        # text holds the given part, since a title can be longer than it.
        label, part = value
        await page.get_by_role("combobox", name=label).click()
        await page.get_by_role("option").filter(has_text=part).first.click()
    elif kind == "scroll":
        await page.mouse.move(int(config.SIZE.split("x", maxsplit=1)[0]) - 10, 450)
        await page.mouse.wheel(0, value)
    else:
        box = await page.locator("canvas").first.bounding_box()
        await page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
        await page.mouse.wheel(0, -value)
    await page.wait_for_timeout(1000)


async def show_dtaas_page(desktop, path, actions):
    """Show a page of DTaaS in the signed-in tab, act on it, then go back to the desktop."""
    page = desktop.context.pages[0]
    await page.bring_to_front()
    await page.goto(f"http://localhost{path}")
    for action in actions:
        await page_action(page, action)
    await back_to_desktop(desktop)


async def back_to_desktop(desktop):
    """Bring the browser with the desktop in front of the host terminal."""
    shell("wmctrl -a Chromium || xdotool search --class chromium windowactivate")
    await desktop.bring_to_front()
    await desktop.wait_for_timeout(2000)
    await desktop.mouse.click(800, 500)
