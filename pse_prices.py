from selenium import webdriver
from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
from cnx import DB_PSE
import datetime
import time

# expects tuple with 3 elements, a) symbol, b) company_id, c) security_id
def GetHistorical(company):
    symbol, company_id, security_id = company
    url = "https://pse.com.ph/stockMarket/companyInfo.html?id={}&security={}&tab=3".format(company_id, security_id)
    print(symbol)
    print(url)


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
companies = companies [:1]


# iterate through all the results
for company in companies:
    GetHistorical(company)

