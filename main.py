# from selenium import webdriver

# driver = webdriver.Chrome()
# print("Selenium is working!")


import csv
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from seleniumbase import SB
import time

inputData = []
outputData = []
def getInput():
    global inputData
    with open('data.txt', mode='r') as file:
        lines = file.readlines()
        for line in lines:
            inputData.append(line.replace("\n", "").replace("/", ""))

def scrapeCareerData():
    global inputData
    global outputData
    for career in inputData:
        driver = webdriver.Firefox()
        # Bureau of Labor Statistics
        url = f"https://data.bls.gov/search/query/results?q={career}"
        driver.get(url)
        original_window = driver.current_window_handle
        newCareerEntry = {}
        try:
            firstElement = driver.find_element(By.CLASS_NAME, 'gs-title')
            firstLinkName = firstElement.text
            firstLink = firstElement.find_element(By.CLASS_NAME, 'gs-title')
            firstLink.click()
            for window_handle in driver.window_handles:
                if window_handle != original_window:
                    driver.switch_to.window(window_handle)
                    break
            time.sleep(2)
            quickFact = ""
            try:
                quickFact = driver.find_element(By.CSS_SELECTOR, "td").text
            except(selenium.common.exceptions.NoSuchElementException):
                print(f"BLS didn't have anything useful for {career}")
                quickFact = ""
            newCareerEntry = {
                "name": career,
                "blsPage": firstLinkName,
                "blsSalary": quickFact.replace("\n", " - ")
            }
        except:
            newCareerEntry = {
                "name": career,
                "blsPage": "",
                "blsSalary": ""
            }
        # ZipRecruiter
        url = "https://www.ziprecruiter.com/Salaries"
        driver.get(url)
        inputField = driver.find_element(By.ID, "search1")
        inputField.click()
        inputField.send_keys(career)
        inputField.click()
        inputField.send_keys(Keys.ENTER)
        time.sleep(2)
        zipRecruiterPageTitle = ""
        zipRecruiterNationwideTitle = ""
        zipRecruiterNationwide = ""
        zipRecruiterLocalTitle = ""
        zipRecruiterLocal = ""
        try:
            zipRecruiterPageTitle = driver.find_element(By.CSS_SELECTOR, "html.more_nav_showing.nav_checked body.desktop div.site_content main.content div.salary_silo_container.aside_layout section.left_side.salary_body article#salary_title.salary_title.tile div.title_block h1.title").text
            zipRecruiterNationwideTitle = driver.find_element(By.CSS_SELECTOR, "div.location-bar:nth-child(1) > div:nth-child(1) > div:nth-child(1)").text
            zipRecruiterNationwide = driver.find_element(By.CSS_SELECTOR, "div.location-bar:nth-child(1) > div:nth-child(2) > div:nth-child(1)").text
            zipRecruiterLocalTitle = driver.find_element(By.CSS_SELECTOR, "div.location-bar:nth-child(2) > div:nth-child(1) > div:nth-child(1)").text
            zipRecruiterLocal = driver.find_element(By.CSS_SELECTOR, "div.location-bar:nth-child(2) > div:nth-child(2) > div:nth-child(1)").text
        except:
            print(f"{career} had ZipRecruit issues")
        newCareerEntry["zipPage"] = zipRecruiterPageTitle
        newCareerEntry[f"zipNation"] = f"{zipRecruiterNationwideTitle} - {zipRecruiterNationwide}"
        newCareerEntry[f"zipLocal"] = f"{zipRecruiterLocalTitle} - {zipRecruiterLocal}"
        driver.quit()
        
        # GlassDoor
        url = "https://www.glassdoor.com/Salaries/index.htm"
        title = ""
        basePay = ""
        medianTotalPay = ""
        with SB(uc=True, test=True, locale_code="en") as sb:
            sb.open(url)
            sb.type('[name=typedKeyword]', f"{career}")
            sb.click('[class=HeroSearch_searchButton__33N2u]')
            sb.uc_gui_click_captcha()
            sb.sleep(2)
            title = sb.get_text("#__next > div.Layout_Container__0k3OL.app_common__TaXub > main > section:nth-child(1) > div:nth-child(1) > div > span > h1 > span:nth-child(1)")
            basePay = sb.get_text(".mr-0 > div:nth-child(3) > div:nth-child(1) > span:nth-child(1)")
            medianTotalPay = sb.get_text(".TotalPayRange_PayBreakdown__CKswr > div:nth-child(2) > div:nth-child(1) > span:nth-child(1)")
            sb.driver.close()
        newCareerEntry["glassDoorPage"] = title
        newCareerEntry["glassDoorBasePay"] = basePay
        newCareerEntry["glassDoorMedianPay"] = medianTotalPay
        outputData.append(newCareerEntry)
        fieldNames = [
            "name",
            "blsPage",
            "blsSalary",
            "zipPage",
            "zipNation",
            "zipLocal",
            "glassDoorPage",
            "glassDoorBasePay",
            "glassDoorMedianPay"
        ]
        with open("careerSalaries.csv", 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldNames)
            writer.writeheader()
            writer.writerows(outputData)
        print(newCareerEntry)

def main():
    getInput()
    scrapeCareerData()

if __name__=="__main__":
    main()