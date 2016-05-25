from bs4 import BeautifulSoup
from requests import get
from re import sub
from sys import argv
from nltk.util import ngrams
from time import sleep


class GoogleScraper():
  def __init__(self, search_ngram, sleep_length=10, next_word="Volgende"):
    first_page_url = "https://www.google.nl/search?q=" + '"' + search_ngram.replace(" ", "+") + '"'
    self.sleep_length = float(sleep_length)
    self.next_word = next_word
    self.list_of_urls = []
    self.get_urls(first_page_url)

  def get_urls(self, first_page_url):
    next_page_url, urls = self.get_info_from_page(first_page_url)
    self.list_of_urls.extend(urls)
    while next_page_url:
      next_page_url, urls = self.get_info_from_page(next_page_url)
      self.list_of_urls.extend(urls)

  def get_info_from_page(self, url):
    sleep(self.sleep_length)
    soup = BeautifulSoup(get(url, headers={'User-agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'}).text, "lxml")
    return self.get_next_page_url(soup), self.get_search_hit_urls(soup)

  def get_next_page_url(self, soup):
    nav = soup.find("table", id="nav")
    if nav:
      next_page = nav(text=self.next_word)
      return "https://www.google.nl" + next_page[0].parent.parent["href"] if len(next_page) > 0 else None
    else:
      return None

  def get_search_hit_urls(self, soup):
    return [sub("&sa.+", "", hit.a["href"].lstrip("/url?q=")) for hit in soup.findAll("h3", {"class": "r"})]


if __name__ == "__main__":
  '$ python google_scraper.py test.txt 10 Volgende test_out.csv'
  urls = {}
  with open(argv[1], "r") as f:
    for ngram in ngrams(f.read().split(), 5):
      search_term = " ".join(ngram)
      print(search_term)
      gs = GoogleScraper(search_term, argv[2], argv[3])
      urls[search_term] = gs.list_of_urls
  out = []
  for ngram in urls:
    print(ngram, urls[ngram])
    for url in urls[ngram]:
      out.append(",".join([ngram, url.lstrip("http://").split("/")[0], url]))
  with open(argv[4], "w") as f:
    f.write("\n".join(out))
