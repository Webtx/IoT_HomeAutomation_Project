"""
Playwright test to check the floating animation on the home page
"""
from playwright.sync_api import sync_playwright
import time

def test_floating_animation():
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        # Navigate to the home page
        page.goto('http://127.0.0.1:5000/')
        
        # Wait for page to load
        page.wait_for_load_state('networkidle')
        time.sleep(2)
        
        # Get the title element
        title = page.locator('h1.hero-title-animated')
        subtitle = page.locator('p.hero-subtitle-animated')
        
        print("\n=== Checking CTRLHOUSE Title ===")
        print(f"Title text: {title.inner_text()}")
        print(f"Title is visible: {title.is_visible()}")
        
        # Get computed styles
        title_styles = page.evaluate('''() => {
            const el = document.querySelector('h1.hero-title-animated');
            const styles = window.getComputedStyle(el);
            return {
                animation: styles.animation,
                animationName: styles.animationName,
                animationDuration: styles.animationDuration,
                animationIterationCount: styles.animationIterationCount,
                transform: styles.transform,
                opacity: styles.opacity
            };
        }''')
        
        print(f"Title computed styles:")
        for key, value in title_styles.items():
            print(f"  {key}: {value}")
        
        print("\n=== Checking Subtitle ===")
        print(f"Subtitle text: {subtitle.inner_text()[:50]}...")
        print(f"Subtitle is visible: {subtitle.is_visible()}")
        
        subtitle_styles = page.evaluate('''() => {
            const el = document.querySelector('p.hero-subtitle-animated');
            const styles = window.getComputedStyle(el);
            return {
                animation: styles.animation,
                animationName: styles.animationName,
                animationDuration: styles.animationDuration,
                animationIterationCount: styles.animationIterationCount,
                transform: styles.transform,
                opacity: styles.opacity
            };
        }''')
        
        print(f"Subtitle computed styles:")
        for key, value in subtitle_styles.items():
            print(f"  {key}: {value}")
        
        # Wait and check transform changes over time
        print("\n=== Monitoring transform changes (10 seconds) ===")
        for i in range(5):
            time.sleep(2)
            current_transform = page.evaluate('''() => {
                const title = document.querySelector('h1.hero-title-animated');
                const subtitle = document.querySelector('p.hero-subtitle-animated');
                return {
                    title: window.getComputedStyle(title).transform,
                    subtitle: window.getComputedStyle(subtitle).transform
                };
            }''')
            print(f"Time {i*2}s:")
            print(f"  Title transform: {current_transform['title']}")
            print(f"  Subtitle transform: {current_transform['subtitle']}")
        
        # Keep browser open for manual inspection
        print("\n=== Browser will stay open for 30 seconds for manual inspection ===")
        time.sleep(30)
        
        browser.close()

if __name__ == "__main__":
    print("Make sure Flask app is running on http://127.0.0.1:5000/")
    print("Starting Playwright test...\n")
    test_floating_animation()
