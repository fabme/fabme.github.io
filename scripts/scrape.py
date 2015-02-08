import sys, os
import requests
import re
from bs4 import BeautifulSoup
import unicodecsv

template = "<li class=\"web-design illusration\">\n\t<img src=\"$2\" alt=\"\" />\n\t<div>\n\t\t<a href=\"$1\" target=\"_blank\">\n\t\t\t<h4 class=\"heavy remove-bottom\">Floral Print</h4>\n\t\t\t<p>MRP <span class=\"WebRupee\">&#x20B9;</span>1031</p>\n\t\t\t<p>DIS <span class=\"WebRupee\">&#x20B9;</span>825</p>\n\t\t</a>\n\t</div>\n</li>\n"

def get_snippet(site_url, image_url):
    return template.replace("$1", site_url).replace("$2", image_url)

def extract_image_url_for_jabong(soup):
    for ul in soup.find_all("ul", class_ = "imageview-slider"):
        i = 0
        for li in ul:
            if i == 0:
                i += 1
                continue;
            return li.img.attrs['src']
            break;

def extract_image_url_for_flipkart(soup):
    img = soup.find("img", class_ = "productImage current")
    if img is not None:
        return img.attrs['data-src']
    return ""

def extract_image_url_for_myntra(soup):
    img = soup.find("div", class_ = "blowup").img
    if img is not None:
        return img.attrs['src']
    return ""

def extract_image_url_for_amazon(soup):
    img = soup.find("img", {"id" : "landingImage"})
    print img
    if img is not None:
        return img.attrs['src']
    return ""

requests_session = requests.Session()
if len(sys.argv) != 2:
    exit("Input filename not provided")
fname = sys.argv[1]
if not os.path.exists(fname):
    exit(fname + " does not exist")
dir = os.path.dirname(fname)
with open(fname) as f:
    content = f.readlines()

with open(dir + 'output.txt', 'wb') as output_file:
    for site_url in content:
        r = requests_session.get(site_url)
        soup = BeautifulSoup(r.content)
        image_url = ""
        if "flipkart" in site_url:
            image_url  = extract_image_url_for_flipkart(soup)
        elif "jabong" in site_url:
            image_url  = extract_image_url_for_jabong(soup)
        elif "myntra" in site_url:
            image_url  = extract_image_url_for_myntra(soup)
        elif "amazon" in site_url:
            image_url  = extract_image_url_for_amazon(soup)         
        output_file.write(get_snippet(site_url, image_url))
