import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import time 

startTime = time.time()

# Reading data from json file and scraping data from all the 10 urls in it
with open('data/sample.json') as f:
  data = json.load(f)
  
allresdetails=[]

for urls in data:
    URL = urls
    r = requests.get(URL)
    soup = BeautifulSoup(r.content, 'html5lib') 

    fres={}                    # Dictionary for storing all the final details

    #Converting the string obtained the contents of the first item in list to dictionary
    res_details=json.loads(soup.findAll("script", type='application/ld+json')[0].contents[0])

    fres["restaurant_name"]=res_details["name"]
    fres["restaurant_logo"]=res_details["image"]
    fres["latitude"]=float(res_details["geo"]["latitude"])
    fres["longitude"]=float(res_details["geo"]["longitude"])
    fres["cuisine_tags"]=res_details["servesCuisine"].split(", ")

    mdetails=json.loads(soup.findAll("script", type='application/json')[0].text)
    #list_items=mdetails['props']['pageProps']['initialMenuState']['menuData']['items']

    inames=[]
    idesc=[]
    iprice=[]
    iimgs=[]

    # For searching the dictionary containing all menu items
    def recursive_items(dictionary):
        for key, value in dictionary.items():
            if type(value) is dict:
                yield from recursive_items(value)
            else:
                yield (key, value)        

    for key, value in recursive_items(mdetails):
        if(key=="filteredCategories"):
            for j in range(len(value)):
                items_list=value[j]["items"]
                for i in range(len(items_list)):
                   inames.append(items_list[i]["name"])
                   idesc.append(items_list[i]["description"])
                   iprice.append(float(items_list[i]["price"]))
                   iimgs.append(items_list[i]["image"])

    fres["menu_items"]=[inames,idesc,iprice,iimgs]
    allresdetails.append(fres)
    
#converting the list dictionary containing restaurant and menu details to dataframe and then to csv file    
df = pd.DataFrame.from_dict(allresdetails)
df.to_csv('output/finaloutput.csv') 

executionTime = (time.time() - startTime)
print('Execution time: ' + str(executionTime) + ' secs')