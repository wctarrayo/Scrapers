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
    browser.implicitly_wait(5)
    browser.get(url)
    # time.sleep(10)


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

# get date today
dt_today = datetime.date.today().strftime('%Y-%m-%d')

# connect to database
cnx = DB_PSE()
cursor = cnx.cursor()

# prepare SQL command, get symbols that haven' been processed for the day
sql = ( "SELECT c.symbol, c.company_id, c.security_id "
        "FROM companies c "
        "LEFT JOIN done_list d ON d.symbol=c.symbol AND d.today=\'{}\' "
        "WHERE ISNULL(d.symbol) "
        "ORDER BY c.symbol").format(dt_today)

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

    # initialize symbol to None indicating that it hasn't been processed yet
    symbol = None

    # upload prices
    for price in prices:

        symbol = price[0]

        # prepare sql command
        sql = "INSERT INTO prices (symbol, trade_date, price_open, price_high, price_low, price_close, price_ave, volume, trade_value) VALUES {} ON DUPLICATE KEY UPDATE price_ave={}".format(tuple(price), price[6])
        print('Inserting {} prices for {} trading day.'.format(symbol, price[1]))
        # print(sql)
        cursor.execute(sql)
        cnx.commit()

    # if symbol has been processed put entry in the database
    if symbol != None:
        sql = "INSERT INTO done_list (symbol, today) VALUES (\'{}\', \'{}\') ON DUPLICATE KEY UPDATE today=\'{}\'".format(symbol, dt_today, dt_today)
        cursor.execute(sql)
        cnx.commit()

    # close database connections
    cursor.close()
    cnx.close()

# release the browser
browser.quit()

    



