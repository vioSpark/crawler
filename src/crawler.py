import mechanicalsoup
from urllib.request import urlopen
from urllib.error import HTTPError
import os
import re
import pickle
import datetime as dt
import networkx as nx
import matplotlib.pyplot as plt
import logging
import sys

# import networkx as nx

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
log.addHandler(handler)


class Crawler:
    graph = nx.DiGraph()
    base_url = None
    recursion_level = None
    # visited = []
    browser = mechanicalsoup.StatefulBrowser()
    quantity_limit = 5

    def config(self, base_url, recursion_level):
        self.base_url = base_url
        self.recursion_level = recursion_level

    def crawl(self, url, origin):
        def set_log_indent(self):
            tmp = ''
            for i in range(self.recursion_level):
                tmp += '\t'
            return tmp

        def error_check(self, new_url, number_of_visited_links, tmp):
            if number_of_visited_links > self.quantity_limit:
                log.debug(tmp + 'quantity limit reached, returning')
                return True
            if new_url.startswith('#'):
                log.debug(tmp + 'reference to the same page, omitting:\t' + new_url)
                return True
            if new_url[:2] == '//':
                log.debug(tmp + 'outside of the boundaries, omitting:\thttps:' + new_url)
                return True
            return False

        number_of_visited_links = 0
        self.graph.add_edge(origin, url)
        self.download_page(url)

        tmp = set_log_indent(self)

        if self.recursion_level > 1:
            log.debug(tmp + 'depth limit reached, returning')
            # self.recursion_level -= 1
            return

        self.recursion_level += 1

        log.debug(tmp + 'crawling started at recursion level:\t' + str(self.recursion_level))
        self.browser.open(url)
        log.debug(tmp + 'link opened:\t' + url)

        for link in self.browser.links():
            number_of_visited_links += 1
            new_url = link.attrs['href']

            error = error_check(self, new_url, number_of_visited_links, tmp)
            if error:
                continue
            if new_url.startswith(self.base_url) or new_url.startswith('/'):
                if new_url.startswith('/'):
                    # trimming the last character down, than appending the new_url
                    new_url = re.findall('(^(?:.*?\/){3})', self.base_url)[0][:-1] + new_url
                    if new_url in self.graph.nodes:
                        log.debug(tmp + 'already visited, omitting:\t' + new_url)
                        continue
                try:
                    self.crawl(new_url, self.browser.get_url())
                except HTTPError or UnicodeDecodeError or OSError as e:
                    print(tmp + "ERROR:\t\t\t\t\t" + str(e))
            else:
                log.debug(tmp + 'outside of the boundaries, omitting:\t' + new_url)
                continue
        log.debug(tmp + 'crawling stopped on recursion level:\t' + str(self.recursion_level))
        self.recursion_level -= 1

    def run(self):
        try:
            os.mkdir("../data")
        except FileExistsError:
            pass

        try:
            self.crawl(self.base_url, 'START')
        except ... as e:
            print("general error occurred: " + str(e))
        print(list(self.graph.nodes()))
        self.save()

    def save(self):
        pass
        # file = open("../data/visited", 'ab')
        # pickle.dump(list(self.graph.nodes()), file)
        # file.close()

    @staticmethod
    def download_page(url):
        pass
        # log.info("downloading:\t" + url)
        # page = urlopen(url)
        # print("data/"+re.sub('[\r\n?]*','',str(link.text)) +".htm")
        # log.debug('\tomitting download, only testing')
        # file=open("data/"+re.sub('[\r\n?*]','',str(link.text)) +".htm", "w")
        # file.write(page)
        # file.close()

    def visualize(self):
        plt.figure(111, figsize=(12, 12))
        pos = nx.spring_layout(self.graph, k=30, iterations=1000)
        nx.draw(self.graph, pos=pos, with_labels=True, node_size=60, font_size=20)
        # nx.draw(self.graph, with_labels=True, font_weight='bold')
        plt.show()
