import re  # for regular expressions string formatting
import xml.etree.ElementTree as ElementTree
from request import REQUEST_FILE
import nlp


class Wiki:
    def __init__(self, url):
        self.url = url

    def xml(self):
        print("Hello my name is " + self.name)


def wiki_save_xpath(root, xpath):
    # xpath = ".//*[@id="mw-content-text"]/div/table/tbody/tr[2]/td[1]/a"
    address = "https://en.wikipedia.org" + root.find(xpath).attrib["href"]
    html = REQUEST_FILE(address, "./city/")
    return html  # rememmber this is a NEW root! not the same at the previous.


# this part of the program will be valuable to study
# List of towns and cities with 100,000 or more inhabitants


def wiki_city_index(website):
    # there is a really cool graph that i should think about using for topic modeling
    # https://www.machinelearningplus.com/nlp/topic-modeling-visualization-how-to-present-results-lda-models/
    website.path = "./city/"
    website.html = REQUEST_FILE(website.url, website.path)
    website.xml = ElementTree.fromstring(website.html)
    root = website.xml
    for index in range(2, 2000):  # todo add code to check the correct END index
        if index == 267:
            print("WOW SLOW DOWN")
        xpath_city = './/*[@id="mw-content-text"]/div/table/tbody/tr[' + str(index) + ']/td[1]/a'
        xpath_country = './/*[@id="mw-content-text"]/div/table/tbody/tr[' + str(index) + ']/td[2]/a'
        if xpath_city is None:
            break  # we found all the cities and countries!
        print("    CITY = " + root.find(xpath_city).text)
        print(" COUNTRY = " + root.find(xpath_country).text)
        html_city = wiki_save_xpath(root, xpath_city)
        html_country = wiki_save_xpath(root, xpath_country)
        print(str(nlp.frequency(html_city)))
        print(str(nlp.frequency(html_country)))
        print("FILE REQUEST to ./city/")

    return


# return the value at a given xpath
def wiki_xpath(website, xpath):
    path = website.xml.find(xpath)
    if path.text:
        return path.text
    else:
        return None


# return the value at a given xpath
# (website, xpath_population_text, "total")
# xpath_population_text = './/*[@id="mw-content-text"]/div/table[1]/tbody/tr[23]/th'


def wiki_xpath_td(website, xpath):
    # left element //*[@id="mw-content-text"]/div/table[1]/tbody/tr[24]/th
    # right element //*[@id="mw-content-text"]/div/table[1]/tbody/tr[24]/td
    # find the last / and remove everthing after the /
    if xpath.rfind("tr["):
        end = xpath.rfind("]")
        xpath = xpath[0:end + 1]
        left_xpath = website.xml.find(xpath + "/th")
        right_xpath = website.xml.find(xpath + "/td")
        if right_xpath is not None:
            return right_xpath.text
        else:
            return None
    else:
        return None


def wiki_search(keywords):
    search_terms = keywords.replace(" ", "+")  # replace spaces with +'s
    search_terms = search_terms.replace("\t", "%09")  # replace tabs
    url = 'https://en.wikipedia.org/w/index.php?cirrusUserTesting=glent_m0&search=' + search_terms + '&title=Special%3ASearch&go=Go&ns0=1'
    directory = "./wikipedia/"
    html = REQUEST_FILE(url, directory=directory, filename=None)
    xml = ElementTree.fromstring(html)
    table = xml.findall('.//*[@id="mw-content-text"]/div[3]/ul/li')
    similarity = []
    for element in table:
        if element.find('div/a') is not None:  # check to see if we have a search result
            search_result = element.find('div/a').attrib["title"]
            similarity.append(similar(search_result, keywords))
    if similarity:
        maxindex = similarity.index(max(similarity))
        url = "https://en.wikipedia.org" + table[maxindex].find('div/a').attrib["href"]
    return url


def wiki_xtable(website, xpath, entry):
    start = xpath.rfind("tr[")
    end = xpath.rfind("]")
    table = website.xml.findall(xpath[0:start + 2])
    th = ""
    td = ""
    for index in table:
        if index.find("th/a") is not None:  # check to see if (link)
            th = index.find("th/a").text
        elif index.find("th") is not None:
            th = index.find("th").text
        if index.find("td/a") is not None:  # check to see if (link)
            td = index.find("td/a").text
        elif index.find("td") is not None:
            td = index.find("td").text
        if th:
            th = re.sub(r'\W+', '', th).lower().strip()
        if td:
            td = re.sub(r'\W+', '', td).lower()  # spaces are valid be careful
        if th == entry:
            break
        else:  # erase the found results
            th = None
            td = None
    return td


def wiki_demographics(website):
    xpath_total_population = './/*[@id="mw-content-text"]/div/table[1]/tbody/tr[24]/th'
    xpath_population_density = './/*[@id="mw-content-text"]/div/table[1]/tbody/tr[26]/th'
    xpath_page_title = './/*[@id="firstHeading"]'

    name = wiki_xpath(website, xpath_page_title)
    population = wiki_xtable(website, xpath_total_population, "estimate")
    density = wiki_xtable(website, xpath_population_density, "density")
    coordinates = wiki_coordinates(website)
    # search the side table for demographic info
    demographics = {'name': name, 'population': population, 'density': density, 'coordinates': coordinates}
    return demographics


def wiki_get_section(website, name):
    website.set_directory("./wikipedia/")
    website.get_html()
    website.get_xml()
    xpath = './/*[@id="mw-content-text"]/div/p/*'
    xpath_title = './/*[@id="Economy"]' # location of the header
    xpath_additional = './/*[@id="mw-content-text"]/div/div[25]/a' # location of the search for next item with details
    xpath_first = './/*[@id="mw-content-text"]/div/p[2]'
    paragraphs = website.get_xml().findall(xpath)
    text = ""
    xpath_crazy = './/*[@id="mw-content-text"]/div/p[2]/span/span[1]/a/span/span[6]'
    for sentence in paragraphs:
        if sentence.text is not None:
            text = text + sentence.text
        if sentence.tail is not None:
            text = text + sentence.tail
    return text

def wiki_read_p(paragraph):
    website.get_xml().findall('.//*[@id="mw-content-text"]/div/p[2]/')
    return result.text

def wiki_get_contents(website):
    website.set_directory("./wikipedia/")
    website.get_html()
    website.get_xml()
    xpath = './/*[@id="toc"]/ul/li[1]'
    start = xpath.rfind("li[")
    end = xpath.rfind("]")
    list = website.xml.findall(xpath[0:start + 2])
    toc = []
    for index in list:
        entry = None
        if index.find('a/span[2]') is not None:  # check to see if (link)
            entry = index.find('a/span[2]').text
        if entry:
            entry = entry.lower()  # spaces are valid be careful
        toc.append(entry)
    return toc


def wiki_study_city(website):
    website.set_directory("./wikipedia/")
    website.html = REQUEST_FILE(website.url, website.path)
    website.xml = ElementTree.fromstring(website.html)

    # get demographics info
    demographics = wiki_demographics(website)
    print("CITY NAME: " + demographics['name'])
    print("POPULATION: (estimate) " + demographics['population'])
    print("DENSITY: " + demographics['density'])
    print("COORDINATES: " + str(demographics['coordinates']))

    # get the word frequency

    return


# source: https://stackoverflow.com/questions/54516687/how-to-print-get-specific-lines-in-an-html-file-in-python-3
# https://stackoverflow.com/questions/11709079/parsing-html-using-python

# load a search from wikipedia and then pick the correct page from the search
# EXAMPLE SEARCH URL:
# https://en.wikipedia.org/w/index.php?cirrusUserTesting=glent_m0&search=APPLE+INC.%09AAPL&title=Special%3ASearch&go=Go&ns0=1
# parsed URL:
# https://en.wikipedia.org/w/index.php?cirrusUserTesting=glent_m0&search=                 &title=Special%3ASearch&go=Go&ns0=1


from difflib import SequenceMatcher


# https://docs.python.org/2/library/difflib.html
def similar(a, b):
    # similarity = SequenceMatcher(None, a, b).ratio()
    a = a.lower()
    b = b.lower()
    similarity = SequenceMatcher(lambda x: x in " \t", a, b)
    s = round(similarity.ratio(), 3)
    print("SequenceMatcher: (" + a + ") : (" + b + ") ratio = " + str(s))
    return s


def largest(arr):
    # Initialize maximum element
    max = arr[0]
    n = len(arr)
    # Traverse array elements from second
    # and compare every element with
    # current max
    for index in range(1, n):
        if arr[index] > max:
            max = arr[i]

    return index


# view the news!
def wiki_news(html):
    # //*[@id="Predicted_and_scheduled"]
    # //*[@id="November"]
    root = ElementTree.fromstring(html)
    # //*[@id="mw-content-text"]/div/ul[1] #january
    month = []
    for m in range(12):
        index = './/*[@id="mw-content-text"]/div/ul[' + str(m + 1) + ']'
        month.append(root.find(index))
    print("WIKI NEWS SAFE!")
    # read the data for each entry
    # for m in range(12):
    #    print "date: " + month[m]._children[i] + " " + month[m]


"""
Revenue	Increase US$265.595 billion[1] (2018)
Operating income
Increase US$70.898 billion[1] (2018)
Net income
Increase US$59.531 billion[1] (2018)
Total assets	Decrease US$365.725 billion[1] (2018)
Total equity	Decrease US$107.147 billion[1] (2018)
Owner	The Vanguard Group (0.0737), BlackRock (0.0676) Edit this on Wikidata
Number of employees
132,000[2] (2018)
"""


def text_geocoder(text):
    # u'37.3349\xc2N 122.0090\xc2W'
    latitude = ""
    logitude = ""
    geocode = {"latitude": latitude, "logitude": logitude}
    # find LATITUDE : NORTH or SOUTH
    start = 0
    end = 0
    if text.find("N") is not -1:
        start = 0
        end = text.find("N ", start)
        latitude = text[start:end - 1].replace('\n', '').replace(' ', '')
    if text.find("S") is not -1:
        start = 0
        end = text.find("S ", start)
        latitude = "-" + text[start:end - 1].replace('\n', '').replace(' ', '')
    # find LOGITUDE : WEST or EAST
    start = end + 1  # end of N or S
    if text.find("W") is not -1:
        end = text.find("W", start + 1)
        longitude = "-" + text[start:end - 1].replace('\n', '').replace(' ', '')
    if text.find("E") is not -1:
        end = text.find("W", start + 1)
        longitude = text[start:end - 1].replace('\n', '').replace(' ', '')
    geocode = {"longitude": longitude, "latitude": latitude}
    return geocode


# this function gets the latitude and logitude coodrinates
# we need to add some code to do some more sophiticated search for the location
def wiki_coordinates(website):
    coordinates = website.xml.find('.//*[@class="geo-dec"]')
    if coordinates is not None:
        geocode = text_geocoder(coordinates.text)
    else:  # we need to look deeper in the text file for the geocode (hopefully not too carefully
        # search for Headquarters //*[@id="mw-content-text"]/div/table[1]/tbody/tr[7]/td/text()[1]
        row = 0  # we dont know what row is the correct xpath for "Revenue" yet
        xpath = './/*[@id="mw-content-text"]/div/table[1]/tbody/tr[' + str(row) + ']/td/'
        if root.find(xpath) is not None:
            for row in range(50):  # todo bad idea to hard code this think about this later
                xpath = './/*[@id="mw-content-text"]/div/table[1]/tbody/tr[' + str(row) + ']/'
                if root.find(xpath).text == "Headquarters":
                    xpath = './/*[@id="mw-content-text"]/div/table[1]/tbody/tr[' + str(row) + ']/td'
                    headquarters = root.find(xpath).text
                    xpath = './/*[@id="mw-content-text"]/div/table[1]/tbody/tr[' + str(row) + ']/td/div[' + str(
                        1) + ']/a'
                    if root.find(xpath) is not None:
                        headquarters = headquarters + " " + root.find(xpath).text
                    import openstreetmaps
                    coordinates = openstreetmaps.OPEN_XML_GEOCODE(headquarters)
                    break  # we found the correct row
        else:
            print("unable to find coordinates : latitude & logitude")
    return coordinates


from re import sub
from decimal import Decimal


def currencyxchange(text_money):
    if text_money is not None:
        value = Decimal(sub(r'[^\d.]', '', text_money))
        # figure out if the number was a billion
        value = float(value * 1000000000)
        return value
    else:
        return None


# this function finds the location of the financial data in wikipedia
# for detailed info on xpath xml
# https://docs.python.org/3/library/xml.etree.elementtree.html#supported-xpath-syntax
def get_financial(root):
    # find the table row "tr" number then assign row
    row = 0  # we dont know what row is the correct xpath for "Revenue" yet
    xpath = './/*[@id="mw-content-text"]/div/table[1]/tbody/tr[' + str(row) + ']/'
    if root.find(xpath) is not None:
        for row in range(50):  # todo bad idea to hard code this think about this later
            xpath = './/*[@id="mw-content-text"]/div/table[1]/tbody/tr[' + str(row) + ']/'
            if root.find(xpath).text == "Revenue":
                break  # we found the correct row
    else:
        print("xpath not found for WIKI FINANCIALs")
        return None

    # check to see if the xpath location exists (not sure about tail)
    xpath = './/*[@id="mw-content-text"]/div/table[1]/tbody/tr[' + str(row) + ']/td/span/a'
    if root.find(xpath) is not None:
        xpath = './/*[@id="mw-content-text"]/div/table[1]/tbody/tr[' + str(row) + ']/td/span/a'
        revenue_increase = currencyxchange(root.find(xpath).tail)
        xpath = './/*[@id="mw-content-text"]/div/table[1]/tbody/tr[' + str(row + 1) + ']/td/span'
        operating_income = currencyxchange(root.find(xpath).text)
        xpath = './/*[@id="mw-content-text"]/div/table[1]/tbody/tr[' + str(row + 2) + ']/td/span'
        net_income = currencyxchange(root.find(xpath).text)
        xpath = './/*[@id="mw-content-text"]/div/table[1]/tbody/tr[' + str(row + 3) + ']/td/span'
        total_assets = currencyxchange(root.find(xpath).text)
        xpath = './/*[@id="mw-content-text"]/div/table[1]/tbody/tr[' + str(row + 4) + ']/td/span'
        total_equity = currencyxchange(root.find(xpath).text)

        money = {"revenue_increase": revenue_increase,
                 "operating_income": operating_income,
                 "net_income": net_income,
                 "total_assets": total_assets,
                 "total_equity": total_equity}
        print("FINANICAL INFO: " + str(money))
        return money


# this function gets the financial information from each stock on wikipedia
def wiki_stock(html):
    print("WIKIPEDIA STOCK INFO FOUND!")
    # doccumentation on elementtree
    # https://docs.python.org/2/library/xml.etree.elementtree.html
    root = ElementTree.fromstring(html)
    # coordinates = get_location(root)
    print("COORDINATES (lat/lon): " + str(coordinates))
    financial = get_financial(root)
    return financial
