import mechanicalsoup
from urllib.error import HTTPError
import os
import re
import networkx as nx
import matplotlib.pyplot as plt
import logging
import sys

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
log.addHandler(handler)


class Crawler:
    graph = nx.DiGraph()
    base_url = None
    # visited = []
    browser = mechanicalsoup.StatefulBrowser()
    quantity_limit = None
    recursion_limit = None
    start_url = None

    def config(self, start_url, quantity_limit, depth_limit):
        self.start_url = start_url
        self.base_url = re.findall('(^(?:.*?/){3})', start_url)[0]
        self.quantity_limit = quantity_limit
        self.recursion_limit = depth_limit

    def crawl(self, url, origin, recursion_level):
        def set_log_indent(recursion_level_tmp):
            tabs = ''
            for i in range(recursion_level_tmp):
                tabs += '\t'
            return tabs

        def skip(url_tmp, origin_tmp, tabs):
            if new_url == '':
                return True
            if not new_url.startswith(self.base_url):
                log.debug(tabs + 'outside of the boundaries, skipping:\thttps:' + url_tmp)
                return True
            if url_tmp.find('/w/') != -1:
                log.debug(tabs + 'not ordinary link, skipping:\thttps:' + url_tmp)
                return True
            if url_tmp.startswith('https://en.wikipedia.org/wiki/Special:') or \
                    url_tmp.startswith('https://en.wikipedia.org/wiki/Category:'):
                log.debug(tabs + 'Special resource, skipping:\thttps:' + url_tmp)
                return True
            if recursion_level >= self.recursion_limit:
                self.graph.add_edge(origin_tmp, url_tmp)
                log.debug(tabs + 'depth limit reached, skipping:\t' + url_tmp)
                return True
            if new_url in self.graph.nodes:
                self.graph.add_edge(url, new_url)
                log.debug(tmp + 'already visited, omitting:\t' + new_url)
                return True
            return False

        def return_check(number_of_visited_links_tmp, tabs):
            if number_of_visited_links_tmp > self.quantity_limit:
                log.debug(tabs + 'quantity limit reached, returning')
                return True

        def fix_url(url_tmp):
            if url_tmp.startswith('//'):
                return 'https:' + url_tmp
            # creating full link
            if url_tmp.startswith('/'):
                # finding the third '/', trimming the last character down than appending the new_url
                url_tmp = self.base_url[:-1] + url_tmp
            # removing '#' part
            loc = url_tmp.find('#')
            if loc != -1:
                url_tmp = url_tmp[:loc]
            return url_tmp

        tmp = set_log_indent(recursion_level)

        self.graph.add_edge(origin, url)
        self.download_page(url)
        number_of_visited_links = 0
        recursion_level += 1

        log.debug(tmp + 'crawling started at recursion level:\t' + str(recursion_level))
        self.browser.open(url)
        log.debug(tmp + 'link opened:\t' + url)

        for link in self.browser.get_current_page().find(id='bodyContent').find_all('a'):
            try:
                new_url = fix_url(link.attrs['href'])
            except KeyError as e:
                log.debug(tmp+str(e))

            if skip(new_url, url, tmp):
                continue
            if return_check(number_of_visited_links, tmp):
                return
            number_of_visited_links += 1

            try:
                self.crawl(new_url, url, recursion_level)
            except HTTPError or UnicodeDecodeError or OSError as e:
                print(tmp + "ERROR:\t" + str(e))

        log.debug(tmp + 'crawling stopped on recursion level:\t' + str(recursion_level))
        log.debug(tmp + 'ended parsing site:\t' + url)
        recursion_level -= 1

    def run(self):
        try:
            os.mkdir("../data")
        except FileExistsError:
            pass

        try:
            self.crawl(self.start_url, 'START', 0)
            self.graph.remove_node('START')
        except ... as e:
            print("general error occurred: " + str(e))
        print(list(self.graph.nodes()))
        self.save_graph()

    def save_graph(self, p=r'../data/last_run'):
        log.debug('saving results to: ' + p)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        nx.write_gml(self.graph, p)

    def load_graph(self, p=r'../data/last_run'):
        log.debug('loading save-file from: ' + p)
        self.graph = nx.read_gml(p)

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
        # pos = graphviz_layout(self.graph, prog="twopi", args="")
        plt.figure(figsize=(8, 8))
        # log.debug('generating kamada_kawai_layout')
        # pos = nx.kamada_kawai_layout(self.graph)
        # log.debug('generating spring layout')
        # pos = nx.spring_layout(self.graph, pos=pos, iterations=30)
        log.debug('generating spring layout')
        pos = nx.spring_layout(self.graph, iterations=10)
        # nx.draw(self.graph, pos, node_size=20, alpha=0.1, node_color="blue", with_labels=False)
        log.debug('drawing nodes')
        nx.draw_networkx_nodes(self.graph, pos, node_size=20, alpha=0.1, node_color="blue")

        plt.axis("equal")
        plt.show()
