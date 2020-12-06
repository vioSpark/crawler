import mechanicalsoup
from urllib.request import urlopen
from urllib.error import HTTPError
import os
import re
import pickle
import datetime as dt


# import networkx as nx


class Crawler:
    base_url = None
    recursion_level = None
    visited = []
    browser = mechanicalsoup.StatefulBrowser()

    def config(self, base_url, recursion_level):
        self.base_url = base_url
        self.recursion_level = recursion_level

    def crawl(self, link, visited):
        self.recursion_level += 1
        print('crawling started at recursion level:\t' + str(self.recursion_level))
        for visit in visited:
            if visit == link:
                print('already visited:\t\t\t\t' + str(link))
                return
        print('not visited yet:\t\t\t\t' + str(link))
        self.browser.open(link)
        print('link opened')
        visited.append(link)
        print('link logged')
        for link in self.browser.links():
            print()
            url = link.attrs['href']
            if url.startswith(self.base_url):
                print('outside of the boundaries:\t' + str(link))
                continue
            # link to self
            if url.startswith('#'):
                continue
            try:
                print("getting:\t\t\t\t" + str(link.attrs['href']))
                page = urlopen(self.base_url + link.attrs['href']).read().decode('utf-8')
                # print("data/"+re.sub('[\r\n?]*','',str(link.text)) +".htm")
                print('\tomitting download, only testing')
                self.crawl(self.base_url + link.attrs['href'], visited)
                # file=open("data/"+re.sub('[\r\n?*]','',str(link.text)) +".htm", "w")
                # file.write(page)
                # file.close()
            except HTTPError as e:
                print("\tERROR:\t\t\t\t\t" + str(e))
                continue
            except UnicodeDecodeError as e:
                print("\tERROR:\t\t\t\t\t" + str(e))
                continue
            except OSError as e:
                print("\tERROR:\t\t\t\t\t" + str(e))
        print('crawling stopped on recursion level:\t' + str(self.recursion_level))
        self.recursion_level -= 1

    def run(self):
        try:
            os.mkdir("../data")
        except FileExistsError:
            pass

        try:
            self.crawl(self.base_url, self.visited)
        except:
            print("general error occurred, quitting")
        print(self.visited)
        file = open("../data/visited", 'ab')
        pickle.dump(self.visited, file)
        file.close()

    def visualize(self):
        pass
        # g = nx.Graph()
