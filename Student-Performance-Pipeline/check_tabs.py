from playwright.sync_api import sync_playwright
import time
import os

def run():
    print("Starting playwright...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        errors = []
        page.on("pageerror", lambda err: errors.append(f"PAGE ERROR: {err}"))
        page.on("console", lambda msg: errors.append(f"CONSOLE {msg.type}: {msg.text}") if msg.type in ['error', 'warning'] else None)

        print("Navigating to app...")
        try:
            page.goto("http://localhost:5173/", timeout=10000)
            page.wait_for_load_state("networkidle", timeout=10000)
            
            print("Logging in...")
            page.fill('input[type="text"], input[name="username"], input[placeholder*="utilisateur"]', 'admin')
            page.fill('input[type="password"]', 'admin123')
            page.click('button:has-text("Connexion")')
            page.wait_for_load_state("networkidle", timeout=10000)
            time.sleep(2)
            
            print("Clicking Predictions Tab...")
            page.click('xpath=//button[contains(., "Prédict")]', timeout=5000)
            time.sleep(1)
            
            print("Clicking EDA Tab...")
            page.click('xpath=//button[contains(., "EDA") or contains(., "Analyse")]', timeout=5000)
            time.sleep(1)
            
            print("Clicking Strategy Tab...")
            page.click('xpath=//button[contains(., "Stratégie")]', timeout=5000)
            time.sleep(1)
            
            print("Clicking About Tab...")
            page.click('xpath=//button[contains(., "propos")]', timeout=5000)
            time.sleep(1)
            
        except Exception as e:
            print(f"Exception during navigation: {e}")
            
        print("\n--- BROWSER CONSOLE ERRORS ---")
        for e in errors:
            print(e)
            
        browser.close()

if __name__ == '__main__':
    run()
