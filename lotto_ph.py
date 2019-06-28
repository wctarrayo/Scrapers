from bs4 import BeautifulSoup
import requests
import datetime
from cnx import DB_Lotto

# lotto ph web address
url = 'http://www.pcso.gov.ph/'

# download page content
page = requests.get(url)

# transfer content to bs4
soup = BeautifulSoup(page.content, 'html.parser')

# get lotto game groups
for game in soup.find_all('div', {'class': 'draw-game'}):
    
    # list that will hold game result details
    details = []

    # get lotto play name
    details.append(game.find('span').get_attribute_list('id')[0][26:][:-1])

    # get game details
    for detail in game.find_all('span'):
        details.append(detail.get_text())
    
    #convert details to proper data types
    for i in range(6):
        details[i + 1] = int(details[i + 1])

    details[7] = float(details[7][3:].replace(',', ''))
    details[8] = int(details[8][:2])
    details[9] = datetime.datetime.strptime(details[9], '%B %d, %Y').strftime('%Y-%m-%d')

    # upload results to mysql db
    cnx = DB_Lotto()
    cursor = cnx.cursor()

    # prepare sql command
    sql = ("INSERT INTO game_results (game, n1, n2, n3, n4, n5, n6, prize, winners, play_date) VALUE {} ON DUPLICATE KEY UPDATE n1={}".format(tuple(details), details[1]))

    # execute sql command
    cursor.execute(sql)
    print("Inserting results for {} on {}".format(details[0], details[9]))
    cnx.commit()

    # close connection
    cursor.close()
    cnx.close()

