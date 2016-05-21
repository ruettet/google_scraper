from bs4 import BeautifulSoup
from requests import get
from re import sub
from sys import argv


class GoogleScraper():
  def __init__(self, search_ngram):
    first_page_url = "http://www.google.com/search?q=" + '"' + search_ngram.replace(" ", "+") + '"'
    self.list_of_urls = []
    self.get_urls(first_page_url)

  def get_urls(self, first_page_url):
    next_page_url, urls = self.get_info_from_page(first_page_url)
    self.list_of_urls.extend(urls)
    while next_page_url:
      next_page_url, urls = self.get_info_from_page(next_page_url)
      self.list_of_urls.extend(urls)

  def get_info_from_page(self, url):
    soup = BeautifulSoup(get(url).text, "lxml")
    return self.get_next_page_url(soup), self.get_search_hit_urls(soup)

  def get_next_page_url(self, soup):
    nav = soup.find("table", id="nav")
    next_page = nav(text="Volgende")
    return "http://www.google.com" + next_page[0].parent.parent["href"] if len(next_page) > 0 else None

  def get_search_hit_urls(self, soup):
    return [sub("&sa.+", "", hit.a["href"].lstrip("/url?q=")) for hit in soup.findAll("h3", {"class": "r"})]


if __name__ == "__main__":
  '$ python google_scraper.py "geen unieke barcode"'
  gs = GoogleScraper(argv[1])
  print("\n".join(gs.list_of_urls))
  
