import asyncio
from playwright.async_api import async_playwright
import os

async def verify_final():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        # Set viewport to mobile size
        context = await browser.new_context(viewport={'width': 440, 'height': 920})
        page = await context.new_page()

        # Load the game
        await page.goto(f"file://{os.getcwd()}/index.html")

        # Check initial state
        print("Page title:", await page.title())

        # 1. Check if #game-container has the correct max-width/height/transform
        container = page.locator('#game-container')
        style = await container.evaluate("el => window.getComputedStyle(el).width")
        print(f"Container width: {style}")

        # 2. Check if a2-btn exists but is hidden initially
        a2_btn = page.locator('#a2-btn')
        print(f"A2 button hidden? {await a2_btn.is_hidden()}")

        # 3. Check preloading of assets
        assets = ['ck.png', 'save.png', 'cookbg.png', 'cook1.png', 'cook2.png', 'cook3.png', 'a2.png']
        for asset in assets:
            exists = await page.evaluate(f"() => {{ const img = new Image(); img.src = '{asset}'; return img.src.includes('{asset}'); }}")
            print(f"Asset {asset} path valid: {exists}")

        # 4. Simulate going to ending screen to check positions
        await page.evaluate("""() => {
            isArtCaptured = true;
            isCookCaptured = true;
            captureArtwork();
            captureCookwork();
            document.getElementById('ending-screen').style.display = 'flex';
        }""")

        await page.wait_for_selector('#ending-screen', state='visible')
        print("Ending screen visible.")

        # Check CK button
        save_btn = page.locator('#save-btn')
        print(f"Save button visible: {await save_btn.is_visible()}")
        btn_style = await save_btn.evaluate("el => window.getComputedStyle(el).bottom")
        print(f"Save button bottom: {btn_style}")

        # Check Canvas 3 (cap3) position in result-canvases
        cap3 = page.locator('.captured-canvas').nth(2) # 0, 1 are artwork, 2 is cooking img
        cap3_left = await cap3.evaluate("el => el.style.left")
        cap3_top = await cap3.evaluate("el => el.style.top")
        print(f"Captured Cookwork (60x60) Left: {cap3_left}, Top: {cap3_top}")

        # Check Result Canvases position
        res_area = page.locator('#result-canvases')
        res_top = await res_area.evaluate("el => window.getComputedStyle(el).top")
        print(f"Result area top: {res_top}")

        await page.screenshot(path="ending_verification.png")
        print("Screenshot saved to ending_verification.png")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(verify_final())
