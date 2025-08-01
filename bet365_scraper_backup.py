import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
import time
import json
from datetime import datetime, timezone


def is_valid_odds(text):
    # Quick check: do at least 3 items at the end look like odds?
    odds_lines = [line.strip() for line in text.split("\n") if "/" in line]
    return len(odds_lines) >= 3

def scrape_bet365():
    print("Launching browser...")
    options = uc.ChromeOptions()
    options.headless = False
    driver = uc.Chrome(options=options)
    driver.set_window_size(1400, 900)

    try:
        print("Navigating to Bet365 football...")
        driver.get("https://www.bet365.com/#/IP/")

        print("Waiting for fixture list to load...")
        WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'ovm-Fixture')]"))
        )

        # Force close cookie & popup overlays
        driver.execute_script("""
            let cookieBtn = [...document.querySelectorAll('button')].find(b => b.textContent.includes('Accept All'));
            if (cookieBtn) cookieBtn.click();
            let intro = document.querySelector('[class*="iip-IntroductoryPopup"] [aria-label="Close"]');
            if (intro) intro.click();
        """)

        print("Extracting fixture rows...")
        rows = driver.find_elements(By.XPATH, "//div[contains(@class, 'ovm-Fixture')]")
        results = []

        for idx, row in enumerate(rows):
            try:
                driver.execute_script("arguments[0].scrollIntoView(true);", row)
                time.sleep(0.2)

                raw_text = row.text.strip()
                if not raw_text or not is_valid_odds(raw_text):
                    continue

                lines = raw_text.split("\n")
                event_lines = [l for l in lines if "/" not in l]
                odds_lines = [l for l in lines if "/" in l]

# Make sure we actually have 3 odds
                if len(odds_lines) < 3:
                    print(f"⚠️ Row {idx} missing full odds: {odds_lines}")
                    continue

                lines = raw_text.split("\n")
                event_lines = [l for l in lines if "/" not in l]  # everything that's not an odds line
                odds_lines = [l for l in lines if "/" in l]

                if len(event_lines) < 2:
                    print(f"⚠️ Row {idx} missing event lines: {event_lines}")
                    continue

                event = f"{event_lines[0]} vs {event_lines[1]}"
                from datetime import datetime, timezone  # <- also update your import at the top

                timestamp = datetime.now(timezone.utc).isoformat()
                results.append({
                    "bookie": "bet365",
                    "event": event,
                    "odds": {
                        "home": odds_lines[0],
                        "draw": odds_lines[1],
                        "away": odds_lines[2]
                    },
                    "timestamp": timestamp
                })

            except Exception as e:
                print(f"⚠️ Row {idx} error: {e}")
        unique = {(r['event'], json.dumps(r['odds'])): r for r in results}
        results = list(unique.values())
        with open("data/bet365_odds.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        print(json.dumps(results, indent=2))

    except Exception as e:
        print("❌ Error during scraping:", e)
        driver.save_screenshot("error_screenshot.png")
    finally:
        try:
            driver.quit()
        except Exception:
            pass
if __name__ == "__main__":
    scrape_bet365()
