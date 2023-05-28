import csv
import math
import os
import random
import time
import undetected_chromedriver
import pandas as pd

from itertools import islice
from multiprocessing import freeze_support
from selenium import webdriver
from selenium.webdriver.common.by import By


def getValuesHouses(i):  # i is the link of the house

    # We will store all the data in a list to insert it in the csv file
    houseInfo = []

    print("==== HOUSE RAW DATA ====")

    # Link of the house
    houseInfo.append(i)

    # Scroll down to load all the elements in the page so we get all the data
    # For house info we will only do it 4 times, it's enough, but if N/A is returned increase the number
    scrollDown(4)

    #################
    # ANNOUNCE INFO #
    #################

    # In this section we will retrieve the most basic information of the announce,
    # those params will be: Title, Price and Price Change.

    try:
        title = driver.find_element(
            By.CSS_SELECTOR, '#App > div.re-Page > main > div.re-LayoutContainer.re-LayoutContainer--large > div.re-ContentDetail-topContainer > div > section:nth-child(1) > div > div.re-DetailHeader-header > div.re-DetailHeader-propertyTitleContainer > h1')
        houseInfo.append(title.text)
    except:
        houseInfo.append("N/A")
        pass

    try:
        price = driver.find_element(
            By.CSS_SELECTOR, "#App > div.re-Page > main > div.re-LayoutContainer.re-LayoutContainer--large > div.re-ContentDetail-topContainer > div > section:nth-child(1) > div > div.re-DetailHeader-header > div.re-DetailHeader-userActionContainer > div.re-DetailHeader-priceContainer > span")
        if(price.text.__contains__("€")):
            # with this we treat the price data convertir the price to a number for the dataset
            price = price.text.replace("€", "")
            price = price.replace(".", "")
            houseInfo.append(int(price))
        else:
            houseInfo.append("Error treating price information")
    except:
        houseInfo.append("N/A")
        pass

    try:
        priceChange = driver.find_element(
            By.CSS_SELECTOR, "#App > div.re-Page > main > div.re-LayoutContainer.re-LayoutContainer--large > div.re-ContentDetail-topContainer > div > section:nth-child(1) > div > div.re-DetailHeader-header > div.re-DetailHeader-userActionContainer > div.re-DetailHeader-priceContainer > div")

        if(priceChange.text.__contains__("€")):
            priceChange = priceChange.text.replace("€", "")
            priceChange = priceChange.replace(".", "")

            if(priceChange.__contains__("bajado")):
                priceChange = (int(priceChange.replace("Ha bajado", "")))
                priceChange = -1*priceChange
            # Page will never show if price has increased so we can assume that if it's shown it's because it has decreased
            houseInfo.append(priceChange)

        else:
            houseInfo.append("Error treating price change information")

    except:
        houseInfo.append(0)  # No change (standar case)
        pass

    ######################
    # DETAIL HEADER INFO #
    ######################

    # In this section we retrieve the information from the top detail header (up to the description and title)
    # The parameters will be: Rooms(habs), Bathrooms(baños), Square meters(m²) and Floor (Planta).

    try:

        detailHeader = driver.find_element(
            By.CSS_SELECTOR, "#App > div.re-Page > main > div.re-LayoutContainer.re-LayoutContainer--large > div.re-ContentDetail-topContainer > div > section:nth-child(1) > div > div.re-DetailHeader-header > div.re-DetailHeader-propertyTitleContainer > ul")

        # With this we get all the info in the WebElement and create a list with all the components.
        # It's important because each house will have different info, so we need to know how many components and what are they
        # Later we will be looking in the list and filling the gaps with the info if existing

        detailHeaderList = detailHeader.text.split("\n")
        # print(detailHeaderList)

        if(detailHeader.text.__contains__("habs")):
            for element in detailHeaderList:
                if(element.__contains__("habs")):
                    aux = element.replace("habs.", "")
                    houseInfo.append(int(aux))
                    break
        else:
            houseInfo.append("N/A")

        if(detailHeader.text.__contains__("baño")):
            for element in detailHeaderList:
                if(element.__contains__("baños")):
                    aux = element.replace("baños", "")
                    houseInfo.append(int(aux))
                    break
                elif(element.__contains__("baño")):
                    aux = element.replace("baño", "")
                    houseInfo.append(int(aux))  # 1
                    break
        else:
            houseInfo.append("N/A")

        if(detailHeader.text.__contains__("m²")):
            for element in detailHeaderList:
                if(element.__contains__("m²")):
                    aux = element.replace("m²", "")
                    houseInfo.append(int(aux))
                    break
        else:
            houseInfo.append("N/A")

        if(detailHeader.text.__contains__("Planta")):
            for element in detailHeaderList:
                if(element.__contains__("Planta")):
                    aux = element.replace("Planta", "")

                    # The format is '2º Planta', so if element at pos[1] is not a num it means the house will be less than 10, so we retrieve 1 number
                    # In case it's a num we retrieve 2 digits, ex: 10º Planta. We extend this until 999º Planta by checking twice.

                    # TODO: Other format founded was 'Superior a Planta 15' In case it happens we will pop error treating data. We can ommit it here and then merge with planta from bottom extra info part

                    if (aux[1].isnumeric()):
                        if(aux[2].isnumeric()):
                            houseInfo.append(int(aux[0:3]))
                        else:
                            houseInfo.append(int(aux[0:2]))
                    elif (aux[0].isalpha()):
                        houseInfo.append("Error treating data")
                    else:
                        houseInfo.append(int(aux[0]))
                        break
                elif(element.__contains__("Bajos") or element.__contains__("Principal")):
                    houseInfo.append(0)  # Floor 0
                    break
        else:
            houseInfo.append("N/A")

    except:
        print("Error getting detail header info")
        pass

    ###############
    # DESCRIPTION #
    ###############

    try:

        try:  # In case the description is too long and we need to click on "Leer más" button.
            driver.find_element(By.CSS_SELECTOR, "#App > div.re-Page > main > div.re-LayoutContainer.re-LayoutContainer--large > div.re-ContentDetail-topContainer > div > section:nth-child(1) > div > div.fc-DetailDescriptionContainer > div.sui-MoleculeCollapsible.sui-MoleculeCollapsible--withGradient.is-collapsed > div.sui-MoleculeCollapsible-container.sui-MoleculeCollapsible-container--withGradient.is-collapsed > button > span").click()
        except:
            pass

        description = driver.find_element(
            By.CSS_SELECTOR, "#App > div.re-Page > main > div.re-LayoutContainer.re-LayoutContainer--large > div.re-ContentDetail-topContainer > div > section:nth-child(1) > div > div.fc-DetailDescriptionContainer > div.sui-MoleculeCollapsible.sui-MoleculeCollapsible--withGradient > div.sui-MoleculeCollapsible-content.sui-MoleculeCollapsible-content--withTransition > div > p")
        if(description.text.__contains__(" ")):  # CHECK IF DESCRIPTION IS NOT EMPTY
            houseInfo.append(description.text)
        else:
            houseInfo.append("N/A")
    except:
        houseInfo.append("N/A")
        pass

    ###################
    # EXTRA INFO PART #
    ###################

    try:
        characteristics = driver.find_element(
            By.CSS_SELECTOR, "#App > div.re-Page > main > div.re-LayoutContainer.re-LayoutContainer--large > div.re-ContentDetail-topContainer > div > section:nth-child(2) > div > div > div.re-DetailFeaturesList")

        characteristicsList = characteristics.text.split("\n")
        # print(characteristicsList)

        if(characteristics.text.__contains__("Tipo de inmueble")):
            found = False
            for element in characteristicsList:
                if(found):
                    houseInfo.append(element)
                    break
                if(element.__contains__("Tipo de inmueble")):
                    found = True
        else:
            houseInfo.append("N/A type")

        if(characteristics.text.__contains__("Antigüedad")):
            found = False
            for element in characteristicsList:
                if(found):
                    houseInfo.append(element)
                    break
                if(element.__contains__("Antigüedad")):
                    found = True
        else:
            houseInfo.append("N/A antiquity")

        if(characteristics.text.__contains__("Orientación")):
            found = False
            for element in characteristicsList:
                if(found):
                    houseInfo.append(element)
                    break
                if(element.__contains__("Orientación")):
                    found = True
        else:
            houseInfo.append("N/A orientation")

        if(characteristics.text.__contains__("Calefacción")):
            found = False
            for element in characteristicsList:
                if(found):
                    houseInfo.append(element)
                    break
                if(element.__contains__("Calefacción")):
                    found = True
        else:
            houseInfo.append("N/A heating")

        if(characteristics.text.__contains__("Agua caliente")):
            found = False
            for element in characteristicsList:
                if(found):
                    houseInfo.append(element)
                    break
                if(element.__contains__("Agua caliente")):
                    found = True
        else:
            houseInfo.append("N/A hot water")

        if(characteristics.text.__contains__("Estado")):
            found = False
            for element in characteristicsList:
                if(found):
                    houseInfo.append(element)
                    break
                if(element.__contains__("Estado")):
                    found = True
        else:
            houseInfo.append("N/A condition state")

        if(characteristics.text.__contains__("Planta")):
            # HERE WE WILL COMPARE WITH INITAL PLANTA INFO FOR BETTER FORMATING AND CONFIRM DATA
            found = False
            for element in characteristicsList:
                if(found):
                    houseInfo.append(element)
                    break
                if(element.__contains__("Planta")):
                    found = True
        else:
            houseInfo.append("N/A floor")

        if(characteristics.text.__contains__("Ascensor")):
            found = False
            for element in characteristicsList:
                if(found):
                    houseInfo.append(element)
                    break
                if(element.__contains__("Ascensor")):
                    found = True
        else:
            houseInfo.append("N/A elevator")

        if(characteristics.text.__contains__("Amueblado")):
            found = False
            for element in characteristicsList:
                if(found):
                    houseInfo.append(element)
                    break
                if(element.__contains__("Amueblado")):
                    found = True
        else:
            houseInfo.append("N/A furnished")

        if(characteristics.text.__contains__("Consumo energía")):
            found = False
            for element in characteristicsList:
                if(found):
                    houseInfo.append(element)
                    break
                if(element.__contains__("Consumo energía")):
                    found = True
        else:
            houseInfo.append("N/A power consumption")

        if(characteristics.text.__contains__("Emisiones")):
            found = False
            for element in characteristicsList:
                if(found):
                    houseInfo.append(element)
                    break
                if(element.__contains__("Emisiones")):
                    found = True
        else:
            houseInfo.append("N/A emitions")

        if(characteristics.text.__contains__("Parking")):
            found = False
            for element in characteristicsList:
                if(found):
                    houseInfo.append(element)
                    break
                if(element.__contains__("Parking")):
                    found = True
        else:
            houseInfo.append("N/A parking")

    except:
        print("Error getting characteristics info")
        pass

    ##############
    # OTHER INFO #
    ##############

    try:
        # This will give us ubication but can be a concrete one, a street, a neighborhood, or any other value... so we could have many "Calle Mayor" in different cities or neighborhoods. In order to be concrete result, we obtained the city/town while retrieving links.
        # We can combine this ubication with the other ubication obtained while getting links to get the exact ubication. The merge will be done combining link.
        ubication = driver.find_element(
            By.CSS_SELECTOR, "#App > div.re-Page > main > div.re-LayoutContainer.re-LayoutContainer--large > div.re-ContentDetail-topContainer > div > section:nth-child(3) > div > div > div.re-DetailMap > h2")
        houseInfo.append(ubication.text)
        print(ubication.text)
    except:
        houseInfo.append("N/A")
        print("No ubication found")
        pass

    return houseInfo


def calculateNumPages():

    # We want to calculate how many pages are in pagination in order to iterate over all of them

    pages = 0
    try:
        totalHouses = driver.find_element(
            By.XPATH, '//*[@id="App"]/div[1]/div[2]/main/div/div[1]/div[1]/h2')
        totalHouses = totalHouses.text
        totalHouses = totalHouses.replace(" de segunda mano", "")

        if(totalHouses.__contains__(".")):  # 76.200 casas for example
            totalHouses = totalHouses.replace(".", "")

        print("Total houses: " + totalHouses)
        # Some cities may contain new houses so the display format will be different
        # example: 336 de segunda mano y 9 de obra nueva
        if(totalHouses.__contains__("y") and totalHouses.__contains__("de obra nueva")):
            totalHouses = totalHouses.replace("y ", "")
            totalHouses = totalHouses.replace(" de obra nueva", "")
            newHouses = totalHouses.split(" ")[1]
            oldHouses = totalHouses.split(" ")[0]
            totalHouses = int(newHouses) + int(oldHouses)
            print(totalHouses)

        # calculate pages rounding up the result
        pages = math.ceil(int(totalHouses)/30)
        print("Total pages is: " + str(pages))
    except:
        print("Error getting total houses")
        pass

    return pages


def scrollDown(downs):

    # We can not get final height of the page because it is dynamic so
    # we are going to scroll down little by little to the bottom of the page to load all the houses

    for i in range(downs):
        # ActionChains(driver).send_keys(Keys.PAGE_DOWN).key_up(Keys.PAGE_DOWN).perform() # This is another way to scroll down in case we want to use it
        driver.execute_script("window.scrollBy(0, 380);")
        time.sleep(random.uniform(0.025, 0.125))


def obtainSinglePageLink():

    # We aim to obtain all the links of the announces in the page and the ubication of each of them

    # Get all announces links
    links = []
    # When we get the links, each announce have a text with the location -> "Piso en Cartagena" so we will later find the street/neighbourhood and can combine data.
    ubiTexts = []
    for i in range(1, 31):  # As we have 30 announces per page

        # We will have to append some values whatever happen because we dont want to mess up the order of the data
        # When cleaning data we will check if the value is N/A and if so, we will delete it
        try:
            announce = driver.find_element(
                By.XPATH, '//*[@id="App"]/div[1]/div[2]/main/div/div[2]/section/article[' +
                str(i) + ']/a')
            # print(announce.get_attribute('href'))
            # There are some announces that were casa en poz,uelo -> that ',' moved all the data
            if(announce.get_attribute('href').__contains__(",")):
                # We dont want to mess up the order of the data
                links.append("N/A")
            else:
                links.append(announce.get_attribute('href'))
        except:
            links.append("N/A")

        try:
            ubicationText = driver.find_element(
                By.XPATH, '//*[@id="App"]/div[1]/div[2]/main/div/div[2]/section/article[' + str(i) + ']/div/a/h3/span[1]')
            ubiTexts.append(ubicationText.text)
        except:
            ubiTexts.append("N/A")

    print("OK")
    return links, ubiTexts

################################################
################################################
################################################


def obtainAllLinks(startingUrl):

    #  We obtain the main page of the city and then we will iterate over all the pages. The way announce page is paginated is the following one:
    #  https://www.fotocasa.es/es/comprar/viviendas/madrid/todas-las-zonas/l
    #  https://www.fotocasa.es/es/comprar/viviendas/madrid/todas-las-zonas/l/2

    allLinks = []
    links = []
    ubiTexts = []
    allUbiTexts = []

    pageLinkToVisit = startingUrl  # url
    pages = calculateNumPages()

    print("Obtaining links...")

    for i in range(1, int(pages+1)):
        print("Page: " + str(i))

        # go to page .../l/2, /l/3, etc
        # sleep a bit to avoid being detected as a bot
        time.sleep(random.uniform(0.1, 0.25))
        driver.get(pageLinkToVisit + "/" + str(i))

        # in case of bot detection
        if(driver.title == "SENTIMOS LA INTERRUPCIÓN"):
            solveCaptcha()
            driver.get(pageLinkToVisit + "/" + str(i))

        # When it comes to get all page we will scroll down X times. Some announces have 1 photo, others 3, so depending the houses we will have to scroll down more or less
        ## IMPORTANT INCREASE THIS NUMBER IF NOT RETRIEVING ALL LINKS ##
        scrollDown(40)

        links, ubiTexts = obtainSinglePageLink()
        allLinks = allLinks + links  # append all links to the list
        allUbiTexts = allUbiTexts + ubiTexts  # append all ubiTexts to the list

        # Print percetange of links retrieved
        percentagePages = round((i/pages)*100, 4)
        print("Progress: " + str(percentagePages) + "%")

    ## Currently we're writting links once we have all of them. We could write them as we go but it would be slower ##
    fileLinks = open("links/" + fileName + "-links.csv", "w")
    fileLinks.write("Number,Links,Ubications\n")

    # IMPORTANT! This replace all commas of the announce ubications with dots to avoid problems with csv as the ',' is the separator!! -> "Piso en Cartagena, Cartagena" -> "Piso en Cartagena. Cartagena"
    allUbiTexts = [x.replace(",", ".") for x in allUbiTexts]

    for i in range(0, allLinks.__len__()):
        fileLinks.write(
            str(i) + "," + allLinks[i] + "," + allUbiTexts[i] + "\n")
    fileLinks.close()

    # Links length will round up to 30 because we have 30 announces per page and even if announce link is not retrieved we will append a N/A value so it will be counting. We will have to check if the link is N/A and if so, delete it in a future step
    print("Links obtained: " + str(len(allLinks)))


def deleteLinksDuplicates():

    # We will delete duplicates from the links file
    print("Deleting duplicates...")

    if(not os.path.exists("links/" + fileName + "-links.csv")):
        print("File not found")
        return

    df = pd.read_csv("links/" + fileName + "-links.csv")
    num_rows = len(df)
    print("Links before cleaning duplicates: ", num_rows)

    # Delete invalid links and duplicates
    df = df.drop_duplicates(subset="Links")
    df = df.dropna()

    df.to_csv("links/" + fileName + "-unique-links.csv", index=False)
    num_rows_new = len(df)
    print("Links after cleaning duplicates: ", num_rows_new)
    print(num_rows - num_rows_new, " links deleted")


def readAllLinks():

    # READ THE CSV WITH THE LINKS.
    # This will return us an array with all the links in order to access them and get detailed info of the announce, to access them we will have to do links[0], links[1], etc
    links = []

    print("Reading links...")

    with open("links/" + fileName + "-unique-links.csv", "r") as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            links.append(row[1])

    print("Links read: " + str(len(links)))
    file = open("datasets/" + fileName + '-dataset.csv', 'w')
    writer = csv.writer(file)
    writer.writerow(["Link", "Title", "Price", "Price change", "Rooms", "Bathrooms",
                    "Squares", "Floor", "Description", "Type", "Antiquity", "Orientation", "Heating", "Hot water", "Condition state",
                     "Floor", "Elevator", "Furnished", "Consumption", "Emitions", "Parking", "Ubication"])

    # We will iterate over all the links and get the data
    for i in range(0, links.__len__()):
        print("Link: " + str(i))
        if(links[i] == "N/A"):
            writer.writerow(["N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A",
                            "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"])
        else:  # We write meanwhile we get the data
            # sleep a bit to avoid being detected as a bot
            time.sleep(random.uniform(0.05, 0.11))

            # in case of bot detection
            if(driver.title == "SENTIMOS LA INTERRUPCIÓN"):
                solveCaptcha()

            driver.get(links[i])
            # sleep a bit to avoid being detected as a bot
            time.sleep(random.uniform(0.05, 0.11))
            data = getValuesHouses(links[i])
            writer.writerow(data)

        # Print percetange of links retrieved
        percentageLinks = round((i/links.__len__())*100, 4)
        print("Progress: " + str(percentageLinks) + "%")

    print("Progress: 100%!")
    file.close()


def readPartialLinks(initialLink, finalLink):
    if(initialLink < 2):
        print("Initial link must be greater than 1")
        return

    links = []
    print("Reading partial links...")

    with open("links/" + fileName + "-unique-links.csv", "r") as file:
        reader = csv.reader(file)
        for i in range(initialLink):  # Skip the rows until desired initial link
            next(reader)
        # Extract a slice of the file between the initial and final links
        for row in islice(reader, finalLink - initialLink):
            if(row[1] != "N/A"):
                links.append(row[1])

    print("Links read: " + str(len(links)))

    # Example: Madrid-20300-20400-dataset.csv
    file = open("datasets/" + fileName + "-" + str(initialLink) +
                "-" + str(finalLink) + '-dataset.csv', 'w')
    writer = csv.writer(file)
    writer.writerow(["Link", "Title", "Price", "Price change", "Rooms", "Bathrooms",
                    "Squares", "Floor", "Description", "Type", "Antiquity", "Orientation", "Heating", "Hot water", "Condition state",
                     "Floor", "Elevator", "Furnished", "Consumption", "Emitions", "Parking", "Ubication"])

    # We will iterate over all the links and get the data
    for i in range(0, links.__len__()):
        print("Link: " + str(i))
        if(links[i] == "N/A"):
            writer.writerow(["N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A",
                            "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"])
        else:  # We write meanwhile we get the data
            # sleep a bit to avoid being detected as a bot
            time.sleep(random.uniform(0.05, 0.11))

            # in case of bot detection
            if(driver.title == "SENTIMOS LA INTERRUPCIÓN"):
                solveCaptcha()

            driver.get(links[i])
            # sleep a bit to avoid being detected as a bot
            time.sleep(random.uniform(0.05, 0.11))
            data = getValuesHouses(links[i])
            writer.writerow(data)

        # Print percetange of links retrieved
        percentageLinks = round((i/links.__len__())*100, 4)
        print("Progress: " + str(percentageLinks) + "%")

    print("Progress: 100%!")
    file.close()


def solveCaptcha():
    print("Bot detected...")
    # Wait for captcha to appear and solve it! If we dont put this, bot cant find captcha button and crash
    time.sleep(8)

    # Click on captcha and believe in god to do not ask for image validation
    captchaButton = driver.find_element(
        By.CSS_SELECTOR, '#captcha-box > div > div.geetest_btn > div.geetest_radar_btn > div.geetest_radar_tip')
    print("Captcha button found")
    # DO NOT TOUCH THE CAPTCHA IN SCREEN UNLESS IT'S REQUIRE IMAGE VALIDATION. IF YOU CLICK ON ACCEPT BUTTON meanwhile program is sleeping it will crash
    captchaButton.click()
    time.sleep(5)  # Wait for captcha to be solved automatically

    # In case they ask for image validation we will stop the program and wait for the user to solve it manually
    while (driver.title == "SENTIMOS LA INTERRUPCIÓN"):
        print("Need to solve image validation")
        time.sleep(30)

    time.sleep(8)


# All provinces in Spain
allProvincias = ['A-Coruna', 'Araba-alava', 'Albacete', 'Alicante', 'Almeria', 'Asturias', 'Avila', 'Badajoz', 'Barcelona', 'Burgos', 'Caceres',
                 'Cadiz', 'Cantabria', 'Castellon', 'Ciudad-Real', 'Cordoba', 'Cuenca', 'Girona', 'Granada', 'Guadalajara',
                 'Gipuzkoa', 'Huelva', 'Huesca', 'Illes-balears', 'Jaen', 'Leon', 'Lleida', 'Lugo', 'Madrid', 'Malaga', 'Murcia', 'Navarra',
                 'Ourense', 'Palencia', 'Las-Palmas', 'Pontevedra', 'La-Rioja', 'Salamanca', 'Segovia', 'Sevilla', 'Soria', 'Tarragona',
                 'Santa-Cruz-de-Tenerife', 'Teruel', 'Toledo', 'Valencia', 'Valladolid', 'Bizkaia', 'Zamora', 'Zaragoza']

# Provinces to be scrapped in this execution
provinceciesToScrap = ['Madrid', 'Barcelona']

if __name__ == '__main__':
    freeze_support()

    start_time = time.time()
    options = webdriver.ChromeOptions()
    options.add_argument("--incognito")
    # options.add_argument("--headless") #if we dont use headless mode we can activate the adblock again

    driver = undetected_chromedriver.Chrome(  # type: ignore
        version_main=103, options=options)

    for i in provinceciesToScrap:
        string_url = 'https://www.fotocasa.es/es/comprar/viviendas/' + \
            i + '-provincia/todas-las-zonas/l'
        fileName = i
        print("Province: " + i)
        driver.get(string_url)
        time.sleep(random.uniform(0.3, 0.8))
        obtainAllLinks(string_url)   # -> Save data once we have all the links
        deleteLinksDuplicates()
        readAllLinks()               # -> Save data as soon as each announcement is retrieved
        # readPartialLinks(1000, 5000) # -> Save data as soon as each announcement is retrieved
        print("Done")

    print("--- %s minutes ---" % round((time.time() - start_time)/60, 2))
    driver.close()
