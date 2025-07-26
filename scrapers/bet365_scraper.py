import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
from datetime import datetime

def scrape_bet365():
    print("Launching browser...")
    options = uc.ChromeOptions()
    options.headless = False
    driver = uc.Chrome(options=options)
    driver.set_window_size(1400, 900)

    try:
        print("Navigating to Bet365 football...")
        driver.get("https://www.bet365.com/#/IP/")

        # Wait for match list to load
        print("Waiting for elements to load...")
        WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'ovm-Fixture')]"))
        )

        # Dismiss popup if present
        try:
            popup_close = driver.find_element(By.XPATH, "//div[@aria-label='Close']")
            popup_close.click()
            print("Closed popup.")
        except:
            print("No popup appeared.")

        print("Extracting matches and odds...")
        rows = driver.find_elements(By.XPATH, "//div[contains(@class, 'ovm-Fixture')]")

        results = []

        for row in rows:
            try:
                # Extract teams
                teams_elem = row.find_element(By.XPATH, ".//div[contains(@class, 'rcl-ParticipantFixtureDetails')]")
                event = teams_elem.text.replace("\n", " vs ")

                # Extract odds
                odds_elems = row.find_elements(By.XPATH, ".//span[contains(@class, 'sba-Odds')]")
                if len(odds_elems) >= 3:
                    home = odds_elems[0].text if odds_elems[0].text else None
                    draw = odds_elems[1].text if odds_elems[1].text else None
                    away = odds_elems[2].text if odds_elems[2].text else None

                    results.append({
                        "bookie": "bet365",
                        "event": event,
                        "market": "1X2",
                        "odds": {
                            "home": home,
                            "draw": draw,
                            "away": away
                        },
                        "timestamp": datetime.utcnow().isoformat() + "Z"
                    })
            except Exception as e:
                print("⚠️ Couldn’t parse one item:", e)

        print(json.dumps(results, indent=2))

    except Exception as e:
        print("❌ Error during scraping:", e)
        driver.save_screenshot("error_screenshot.png")

    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_bet365()
