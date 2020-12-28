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

    def crawl(self, link):
        self.recursion_level += 1
        print('crawling started at recursion level:\t' + str(self.recursion_level))
        for visit in self.visited:
            if visit == link:
                print('already visited:\t\t\t\t' + str(link))
                return
        print('not visited yet:\t\t\t\t' + str(link))
        self.browser.open(link)
        print('link opened')
        self.visited.append(link)
        print('link logged')
        for link in self.browser.links():
            print()
            url = link.attrs['href']
            # link to self
            if url.startswith('#'):
                print('reference to the same page:\t' + url)
                continue
            if url[:2] == '//':
                print('outside of the boundaries:\thttps:' + url)
                continue
            if url.startswith(self.base_url) or url.startswith('/'):
                if url.startswith('/'):
                    # self.base_url.split('/')
                    # url = self.base_url + url
                    # searching for the 3rd '/' with regex,
                    # trimming the last character down, than appending the old url
                    url = re.findall('(^(?:.*?\/){3})', self.base_url)[0][:-1] + url
                try:
                    self.download_page(url)
                except HTTPError as e:
                    print("\tERROR:\t\t\t\t\t" + str(e))
                    continue
                except UnicodeDecodeError as e:
                    print("\tERROR:\t\t\t\t\t" + str(e))
                    continue
                except OSError as e:
                    print("\tERROR:\t\t\t\t\t" + str(e))
            else:
                print('outside of the boundaries:\t' + url)
                continue
        print('crawling stopped on recursion level:\t' + str(self.recursion_level))
        self.recursion_level -= 1

    def run(self):
        try:
            os.mkdir("../data")
        except FileExistsError:
            pass

        try:
            self.crawl(self.base_url)
        except ... as e:
            print("general error occurred: " + str(e))
        print(self.visited)
        file = open("../data/visited", 'ab')
        pickle.dump(self.visited, file)
        file.close()

    def download_page(self, url):
        print("getting:\t\t\t\t" + url)
        page = urlopen(url)
        # print("data/"+re.sub('[\r\n?]*','',str(link.text)) +".htm")
        print('\tomitting download, only testing')
        self.crawl(url)
        # file=open("data/"+re.sub('[\r\n?*]','',str(link.text)) +".htm", "w")
        # file.write(page)
        # file.close()

    def visualize(self):
        pass
        # g = nx.Graph()
