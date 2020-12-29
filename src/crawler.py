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

    def config(self, base_url, quantity_limit, depth_limit):
        self.base_url = base_url
        self.quantity_limit = quantity_limit
        self.recursion_limit = depth_limit

    def crawl(self, url, origin, recursion_level):
        def set_log_indent(recursion_level_tmp):
            tabs = ''
            for i in range(recursion_level_tmp):
                tabs += '\t'
            return tabs

        def skip(url_tmp, tabs):
            if url_tmp.startswith('#'):
                log.debug(tabs + 'reference to the same page, skipping:\t' + url_tmp)
                return True
            if url_tmp[:2] == '//' or not (new_url.startswith(self.base_url) or new_url.startswith('/')):
                log.debug(tabs + 'outside of the boundaries, skipping:\thttps:' + url_tmp)
                return True
            if url_tmp.find('.org/w/') != -1:
                log.debug(tabs + 'not ordinary link, skipping:\thttps:' + url_tmp)
                return True
            if recursion_level >= self.recursion_limit:
                log.debug(tabs + 'depth limit reached, skipping:\t' + url_tmp)
                return True
            return False

        def return_check(number_of_visited_links_tmp, tabs):
            if number_of_visited_links_tmp > self.quantity_limit:
                log.debug(tabs + 'quantity limit reached, returning')
                return True

        tmp = set_log_indent(recursion_level)

        self.graph.add_edge(origin, url)
        self.download_page(url)
        number_of_visited_links = 0
        recursion_level += 1

        log.debug(tmp + 'crawling started at recursion level:\t' + str(recursion_level))
        self.browser.open(url)
        log.debug(tmp + 'link opened:\t' + url)

        for link in self.browser.links():
            new_url = link.attrs['href']

            if skip(new_url, tmp):
                continue
            if return_check(number_of_visited_links, tmp):
                return

            number_of_visited_links += 1
            # creating full link
            if new_url.startswith('/'):
                # finding the third '/', trimming the last character down than appending the new_url
                new_url = re.findall('(^(?:.*?/){3})', self.base_url)[0][:-1] + new_url

            # removing '#' part
            loc = new_url.find('#')
            if loc!=-1:
                new_url = new_url[:loc]

            if new_url in self.graph.nodes:
                number_of_visited_links -= 1
                self.graph.add_edge(url, new_url)
                log.debug(tmp + 'already visited, omitting:\t' + new_url)
                continue
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
            self.crawl(self.base_url, 'START', 0)
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
        nx.draw(self.graph, pos, node_size=20, alpha=0.1, node_color="blue", with_labels=False)
        log.debug('drawing nodes')
        # nx.draw_networkx_nodes(self.graph, pos, node_size=20, alpha=0.1, node_color="blue")

        plt.axis("equal")
        plt.show()
