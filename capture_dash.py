import asyncio
from playwright.async_api import async_playwright
import time
import os

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={'width': 1920, 'height': 1080})
        
        print("Connecting to Streamlit...")
        await page.goto("http://localhost:8520/")
        
        print("Waiting for dashboard to render...")
        await page.wait_for_selector("h1", timeout=15000)
        await asyncio.sleep(5)  # give charts time to draw
        
        output_path = os.path.join("data", "dashboard_render.png")
        await page.screenshot(path=output_path, full_page=True)
        print(f"Screenshot saved to {output_path}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
