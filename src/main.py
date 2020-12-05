import crawler

cr = crawler.Crawler()
cr.config(base_url="https://en.wikipedia.org/wiki/Graph_(discrete_mathematics)", recursion_level=0)
cr.run()
