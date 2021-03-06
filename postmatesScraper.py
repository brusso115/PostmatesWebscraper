import time
import random
from csv import DictWriter
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import sys, os

PATH = "/Users/baileyrusso/PycharmProjects/GrubHubScraper/chromedriver"
driver = webdriver.Chrome(PATH)
driver.get('https://postmates.com/feed')

search = driver.find_element_by_xpath('//input[@class="geosuggest__input css-ukyjo8"]')
search.send_keys("Lincoln Square, Manhattan, New York City, New York ")
search.send_keys(Keys.RETURN)

restInfo = []

#Scroll up and down on infinite scrolling page to get more restaurants
try:

    for i in range(10):
        print(i)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        driver.execute_script("window.scrollTo(0, -10);")

        time.sleep(3)

    cards = WebDriverWait(driver,60).until(
        EC.presence_of_all_elements_located((By.XPATH, '//div[@class="css-19f3h52 e12wrbia0"]'))
    )
    print(len(cards))

except:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)
    driver.close()
    driver.quit()


#Get Restaurant Links
links = []
for card in cards:
    element = card.find_element_by_xpath("./a")
    restLink = element.get_attribute("href")
    links.append(restLink)

name = ""
category = ""
favorites = ""
address = ""
itemName = ""
itemDescription = ""
itemPrice = ""
popItemName = ""
popItemDescription = ""
popItemPrice = ""

i = 0
for link in links:
    i = i + 1
    print(i)

    restDict = {}
    try:
        driver.get(link)
    except:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        continue

    try:
        mainContainer = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located(
                (By.XPATH, '//div[@id="js-global-container"]'))
        )
    except:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        #driver.close()
        #driver.quit()
        continue


    try:
        name = mainContainer.find_element_by_xpath('.//h1[@class="css-czd68n eifi54g1"]').text
    except:
        print('Error')
        name = ""

    try:
        category = mainContainer.find_element_by_xpath('.//a[@data-event-category="Merchant Subhead Category"]').text
    except:
        category = ""

    try:

        favorites = mainContainer.find_element_by_xpath('.//span[@class="css-1lzl3v6 e12xa2na1"]').text
    except:
        favorites = ""

    try:
        address = mainContainer.find_element_by_xpath('.//div[@class="css-ifs29b eifi54g7"]').text
    except:
        address = ""

    print('Name: ', name)
    print('Category: ', category)
    print('Favorites: ', favorites)
    print('Address: ', address)

    try:
        menuItems = mainContainer.find_elements_by_xpath('.//div[@class="css-14tel0n e1tw3vxs1"]')
    except:
        menuItems = []

    for item in menuItems:

        try:
            itemName = item.find_element_by_xpath('.//h3[@class="product-name css-1yjxguc e1tw3vxs4"]').text
        except:
            itemName = ""

        try:
            itemDescription = item.find_element_by_xpath('.//div[@class="product-description css-1cwo7kl e1tw3vxs8"]').text
        except:
            itemDescription = ""

        try:
            itemPrice = item.find_element_by_xpath('.//span[@class="css-yzlrwy e1tw3vxs6"]/span').text
        except:
            itemPrice = ""

        print(name.encode('utf-8'), ' - ', category, ' - ',favorites, ' - ', address, ' - ', itemName, ' - ', itemDescription, ' - ', itemPrice)

        restDict['Name'] = name.encode('utf-8')
        restDict['Category'] = category.encode('utf-8')
        restDict['Favorites'] = favorites.encode('utf-8')
        restDict['Address'] = address.encode('utf-8')
        restDict['MenuItem'] = itemName.encode('utf-8')
        restDict['MenuItemDesc'] = itemDescription.encode('utf-8')
        restDict['MenuItemPrice'] = itemPrice.encode('utf-8')

        field_names = ['Name', 'Category', 'Favorites', 'Address', 'MenuItem', 'MenuItemDesc', 'MenuItemPrice']

        with open('lincolnsqday.csv', 'a') as f_object:
            dictwriter_object = DictWriter(f_object, fieldnames=field_names)
            dictwriter_object.writerow(restDict)
            f_object.close()

    sleeptime = random.randint(28,32)
    time.sleep(sleeptime)
    menuItems = []








