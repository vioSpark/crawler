import mechanicalsoup
from urllib.request import urlopen
from urllib.error import HTTPError
import os
import re
import pickle
import datetime as dt




def crawl(link):
    recursion_level=r_level
    recursion_level+=1
    print('crawling started at recursion level:\t' + str(recursion_level))
    for visit in visited:
        if visit==link:
            print('alredy visited:\t\t\t\t' + str(link))
            return
    print('not visited yet:\t\t\t\t' + str(link))
    browser.open(link)
    print('link opened')
    visited.append(link)
    print('link logged')
    for link in browser.links():
        print()
        if str(link.attrs['href']).startswith(base_url):
            print('outside of the boundaries:\t' + str(link))
            # continue
        try:
            print("getting:\t\t\t\t" + str(link.attrs['href']))
            page = urlopen(base_url + link.attrs['href']).read().decode('utf-8')
            # print("data/"+re.sub('[\r\n?]*','',str(link.text)) +".htm")
            print('\tomitting download, only testing')
            crawl(base_url + link.attrs['href'])
            # file=open("data/"+re.sub('[\r\n?*]','',str(link.text)) +".htm", "w")
            # file.write(page)
            # file.close()
        except HTTPError as e:
            print("\tERROR:\t\t\t\t\t"+str(e))
            continue
        except UnicodeDecodeError as e:
            print("\tERROR:\t\t\t\t\t"+str(e))
            continue
        except OSError as e:
            print("\tERROR:\t\t\t\t\t"+str(e))
    print('crawling stopped on recursion level:\t' +str(recursion_level))
    recursion_level-=1



try:
    # Create target Directory
    os.mkdir("data")
except FileExistsError:
    print("Directory data alredy exists")

# Connect to link
base_url="http://bassment.ktk.bme.hu/"
browser = mechanicalsoup.StatefulBrowser()


r_level=0
visited=[]
try:
    crawl(base_url)
except all:
    pass
print(visited)
file=open("data/visited: "+str(dt.datetime.now().strftime("%c")), 'ab')
pickle.dump(visited, file)
file.close()