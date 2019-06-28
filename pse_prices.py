from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from cnx import DB_PSE
import datetime
import time

def GetHistorical(company, browser):
    """
    Expects tuple with 3 elements, a) symbol, b) company_id, c) security_id
    Returns a list containing 30 days worth of stock prices for the given company
    """

    # explode company details to 3 variables
    symbol, company_id, security_id = company

    # prepare web url
    url = "https://pse.com.ph/stockMarket/companyInfo.html?id={}&security={}&tab=3".format(company_id, security_id)
    
    print('Fetching prices for {}...'.format(symbol))

    # load web page for company
    browser.get(url)
    time.sleep(10)


    # prepare an empty list that will hold the list of prices and will be used to return the list
    prices = []

    # get the prices for the past 30 days for the given company
    for rows in browser.find_elements_by_class_name('x-grid3-row-table'):
        details = rows.text.splitlines()
        details.insert(0, symbol)

        # convert date to ISO format
        details[1] = datetime.datetime.strptime(details[1], '%b %d, %Y').strftime('%Y-%m-%d')

        # remove commas from numeric data
        for i in range(7):
            details[i + 2] = details[i + 2].replace(',','')

        prices.append(details)
        
    # return the list of prices
    return prices


# connect to database
cnx = DB_PSE()
cursor = cnx.cursor()

# prepare SQL command
sql = "SELECT symbol, company_id, security_id FROM companies ORDER BY symbol"

# get SQL results and store in a variable
cursor.execute(sql)
companies = cursor.fetchall()

# close database connections
cursor.close()
cnx.close()

# limit results for testing
# companies = companies [:1]

# set browser options
driver_path = '/media/Code/Scrapers/bin/geckodriver'
options = Options()
options.set_headless(True)

# load the website
browser = webdriver.Firefox(options=options, executable_path=driver_path)


# iterate through all the results
prices = None
for company in companies:
    prices = GetHistorical(company, browser)

    # prepare database connection
    cnx = DB_PSE()
    cursor = cnx.cursor()

    # upload prices
    for price in prices:

        # prepare sql command
        sql = "INSERT INTO prices (symbol, trade_date, price_open, price_high, price_low, price_close, price_ave, volume, trade_value) VALUES {} ON DUPLICATE KEY UPDATE price_ave={}".format(tuple(price), price[6])
        print('Inserting {} prices for {} trading day.'.format(price[0], price[1]))
        # print(sql)
        cursor.execute(sql)
        cnx.commit()

    cursor.close()
    cnx.close()

# release the browser
browser.quit()

    



