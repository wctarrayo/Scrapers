from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from cnx import DB_PSE
import datetime
import time

# load browser
print('Loading browser...')

# set delay for each page
delay = 7 # seconds

# set headless option
options = Options()
options.set_headless(True)

# website for PSE
url = 'https://pse.com.ph/stockMarket/listedCompanyDirectory.html'

# set broswser driver for firefox
browser = webdriver.Firefox(options=options,executable_path='/media/Code/Scrapers/bin/geckodriver')
browser.get(url)
browser.implicitly_wait(delay)

# get total number of table pages
pages = int(browser.find_element_by_id('ext-gen80').text.split(' ')[1])

# list for all the collected company details
symbols = []

print('Collecting stock details...')

# iterate through table pages
for i in range(pages):
    page = i + 1

    # refresh table using current page number
    browser.execute_script("document.getElementById('ext-gen77').value = {}".format(page))    
    page_selector = browser.find_element_by_xpath('//*[@id="ext-gen77"]')
    page_selector.send_keys(Keys.RETURN)

    # give time for page to load
    time.sleep(delay)

    # get elements for each row
    for rows in browser.find_elements_by_class_name('x-grid3-row'):
        details = rows.text.splitlines()

        # convert string date to ISO format
        details[4] = datetime.datetime.strptime(details[4], '%b %d, %Y').strftime('%Y-%m-%d')
        ref = rows.find_element_by_tag_name('a').get_attribute('href').split('&')
        symbol_id = ref[0][51:]
        security_id = ref[1][9:]
        details.append(int(symbol_id))
        details.append(int(security_id))
        # print("Inserting {} for {}".format(details[1], details[0]))
        symbols.append(details)


# close browser
browser.quit()

# prepare database connection
cnx = DB_PSE()
cursor = cnx.cursor()

for symbol in symbols:
    # prepare SQL command
    sql = ("INSERT INTO companies (company_name, symbol, sector, sub_sector, listing_date, company_id, security_id) VALUES {} ON DUPLICATE KEY UPDATE company_id={}".format(tuple(symbol), symbol[5]))
    
    # execute sql command
    cursor.execute(sql)
    print("Inserting {} for {}".format(symbol[1], symbol[0]))
    cnx.commit()

# close database connection
cursor.close()
cnx.close()