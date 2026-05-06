from playwright.sync_api import sync_playwright
import time
import os

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        errors = []
        page.on("pageerror", lambda err: errors.append(f"PAGE ERROR: {err}"))
        page.on("console", lambda msg: errors.append(f"CONSOLE {msg.type}: {msg.text}") if msg.type in ['error', 'warning'] else None)

        print("Navigating to app...")
        page.goto("http://localhost:5173/")
        page.wait_for_load_state("networkidle")
        
        print("Logging in...")
        page.fill('input[type="text"], input[name="username"], input[placeholder*="utilisateur"]', 'admin')
        page.fill('input[type="password"]', 'admin123')
        page.click('button:has-text("Connexion")')
        page.wait_for_load_state("networkidle")
        time.sleep(2)
        
        print("Clicking Importer Données...")
        page.click('button:has-text("Importer Données")')
        time.sleep(1)
        
        print("Uploading file...")
        file_path = os.path.join(os.getcwd(), 'test_dynamic.csv')
        # Create it if it doesn't exist
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("Matricule,Age,Score_Partiel,Note_Finale,Absences\n")
            f.write("ETUD01,15,12,14.5,2\n")
            f.write("ETUD02,16,8,9,5\n")
            f.write("ETUD03,15,18,17,0\n")
        
        page.set_input_files('input[type="file"]', file_path)
        time.sleep(1)
        
        print("Clicking Analyser le fichier...")
        page.click('button:has-text("Analyser le fichier")')
        time.sleep(2)
        
        print("Clicking Charger les données...")
        page.click('button:has-text("Charger les données")')
        time.sleep(2)
        
        print("Clicking Lancer le Pipeline IA...")
        page.click('button:has-text("Lancer le Pipeline IA")', timeout=5000)
        time.sleep(5)
        
        print("\n--- BROWSER CONSOLE ERRORS ---")
        for e in errors:
            print(e)
            
        browser.close()

if __name__ == '__main__':
    run()
