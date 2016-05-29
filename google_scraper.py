from bs4 import BeautifulSoup
from requests import get
from re import sub
from sys import argv
from nltk.util import ngrams
from time import sleep
from random import choice, randint
from configparser import ConfigParser


class GoogleScraper():
  def __init__(self, search_ngram, min_sleep_length=30, max_sleep_length=60, domain=".nl", next_word="Volgende", stop=1, noresults="Geen resultaten gevonden"):
    with open("useragents.prop") as f:
      self.user_agents = f.readlines()
    self.min_sleep_length = float(min_sleep_length)
    self.max_sleep_length = float(max_sleep_length)
    self.stop_searching_after_page = stop
    self.noresultssentence = noresults
    self.next_word = next_word
    self.list_of_urls = []
    self.get_urls(first_page_url)

  def get_urls(self, first_page_url):
    page_count = 1
    print("\tChecking search page", page_count)
    next_page_url, urls = self.get_info_from_page(first_page_url)
    self.list_of_urls.extend(urls)
    page_count += 1
    while next_page_url and page_count < self.stop_searching_after_page:
      print("\tChecking search page", page_count)
      next_page_url, urls = self.get_info_from_page(next_page_url)
      self.list_of_urls.extend(urls)
      page_count += 1

  def get_info_from_page(self, url):
    sleep(randint(self.min_sleep_length, self.max_sleep_length))
    soup = BeautifulSoup(get(url, headers={'User-agent': choice(self.user_agents).strip()}).text, "lxml")
    for div in soup.findAll("div", {"class": "med"}):
      if self.noresultssentence in (div.text):
        print("\t\tNo exact matches found")
        return None, []
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
  '$ python3 google_scraper.py settings.prop'
  config = ConfigParser()
  config.read("settings.prop")
  urls = {}
  with open(config.get("InputOutput", "infile"), "r") as f:
    for line in f.readlines():
      for ngram in ngrams(line.strip().split(), int(config.get("Ngram", "n"))):
        search_term = " ".join(ngram)
        print(search_term)
        gs = GoogleScraper(search_term, 
                           config.get("Timing", "minsleep"), 
                           config.get("Timing", "maxsleep"), 
                           config.get("Google", "extension"),
                           config.get("Google", "nextword"),
                           config.get("Google", "noresultssentence"))
        urls[search_term] = gs.list_of_urls
  out = []
  for ngram in urls:
    for url in urls[ngram]:
      out.append(",".join([ngram, sub("https?://[w]{0,3}\.?", "", url).split("/")[0], url]))
  with open(config.get("InputOutput", "outfile"), "w") as f:
    f.write("\n".join(out))

