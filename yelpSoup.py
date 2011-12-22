from BeautifulSoup import BeautifulSoup
import urllib2
from pymongo import Connection

connection = Connection()
db = connection.placemillDB
citiesCollection = db.places
categoriesCollection = db.categories

f = urllib2.urlopen('http://www.yelp.com/developers/documentation/neighborhood_list')

raw = f.read()

soup = BeautifulSoup(raw)

places = soup.find('ul', {'class':'attr-list'})

usa = soup.firstText('USA').findNext('ul')

#get list of cities in usa
usaCities = usa.findAll('li', recursive=False)

#take out <li> tags

for i in range(len(usaCities)):
    usaCities[i] = usaCities[i].text

#get list of places in each city
places = {}
for i in usaCities:
   temp =  usa.firstText(i).findNext('ul').findAll('li')
   for j in range(len(temp)):
       temp[j] = temp[j].text
   places[i] = temp


print places[usaCities[0]]
#need to replace the spaces with '+', could do that when constructing the url

#get a list of categories to search
f = urllib2.urlopen('http://www.yelp.com/developers/documentation/category_list')
raw = f.read()
soup = BeautifulSoup(raw)
attrList = soup.find('ul', {'class':'attr-list'})
categories = attrList.findAll('li')
for i in range(len(categories)):
    temp = categories[i].text.split()
    temp = temp[len(temp)-1]
    temp = rstrip('()')
    temp = lstrip('()')
    categories[i] = temp[len(temp)-1]

'''
need to build a list of URLs to visit
e.g.: 'http://www.yelp.com/search?find_desc=%s&find_loc=%s' % (category, place)

Then from each starting URL look for <strong class="pager_total"> to get the total number of pages for that search
The default is 10 results per page, so pager_total / 10 is the total number of pages
To get the next URL in the results add #start=10 to the end of the original serch URL, 
e.g.: http://www.yelp.com/search?find_desc=restaraunts&find_loc=Los+Angeles+CA#start=10

keep a counter for individual results. 
get all the individual business links of each result page
e.g.: resultPage.find('a', {'id':'bizTitleLink'+resultCnt})
for each individual result page, load page and check for the existence of <div id="bizUrl">
if bizUrl exists pass on result, if it does not exist, collect name, number and address of business. 

'''
for city in usaCities:
    getLinksForPlaces(city)

def getLinksForPlaces(city):
    for place in places[city]:
        for category in categories:
            crawlYelp(category, place, city)

def crawlYelp(category, place, city):
    place += city
    startlink = 'http://www.yelp.com/search?find_desc=%s&find_loc=%s' % (category, place)
    searchResults = getSearchResults(startlink)
    cnt = 0
    pager_total = searchResults.find('strong', {'class':'pager_total'}).text
    num_pages = pager_total/10
    for i in range(num_pages):
        #fix this to not have place and cat hard coded
        link = 'http://www.yelp.com/search?find_desc=%s&find_loc=%s#start=%s' % (category, place, cnt)
        searchResults = getSearchResults(link)
        for j in range(10):
            searchBizPage(searchResults,cnt)
            cnt+=1

def searchBizPage(searchResults,cnt):
    bizLink = searchResults.find('a', {'id':'bizTitleLink'+cnt})
    tempBizPage = getSearchResults(bizLink)
    if tempBizPage.find('div', {'id':'bizUrl'}) != '':
        return
    else:
        #get biz title
        #get biz address
        #get biz number
        #return biz or store to mongo or something, use number for key
        #also check if number exists already, there will be overlap from other searches
             
def getSearchResults(link):
    f = urllib2.urlopen(startlink)
    raw = f.read()
    searchResults = BeautifulSoup(raw)
    return searchResults
