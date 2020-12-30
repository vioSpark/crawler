import crawler
import logging
import sys

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
log.addHandler(handler)

cr = crawler.Crawler()
download = True

# todo: progress bar
# todo: save sub-graphs

if download:
    cr.config(start_url="https://en.wikipedia.org/wiki/Graph_(discrete_mathematics)",
              quantity_limit=100000,
              depth_limit=3)
    log.info('Starting crawler with: ' + cr.base_url)
    cr.run()
else:
    log.info('loading graph')
    cr.load_graph()

log.info('Starting visualisation')
cr.visualize()
