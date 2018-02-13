import argparse

import collect
import scrape

go_nums = collect.get_go_nums()
scraper = scrape.Scraper()

try:
    for go_num in go_nums:
        print go_num
        scraper.find_case(go_num)
except Exception as e:
    print 'Encountered unexpected error: ', e

scraper.close()
