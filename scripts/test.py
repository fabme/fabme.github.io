import sys, os
import requests
import re
from bs4 import BeautifulSoup
from os.path import basename
import unicodecsv


#template = "<li class=\"web-design illusration\">\n\t<img src=\"$1\" alt=\"\" />\n\t<div>\n\t\t<a href=\"$2\" target=\"_blank\">\n\t\t\t<h4 class=\"heavy remove-bottom\">Floral Print</h4>\n\t\t\t<p>MRP <span class=\"WebRupee\">&#x20B9;</span>$3</p>\n\t\t</a>\n\t</div>\n</li>\n"
#template_with_disc = "<li class=\"web-design illusration\">\n\t<img src=\"$1\" alt=\"\" />\n\t<div>\n\t\t<a href=\"$2\" target=\"_blank\">\n\t\t\t<h4 class=\"heavy remove-bottom\">Floral Print</h4>\n\t\t\t<p>MRP <span class=\"WebRupee\">&#x20B9;</span>$3</p>\n\t\t\t<p>DIS <span class=\"WebRupee\">&#x20B9;</span>$4</p>\n\t\t</a>\n\t</div>\n</li>\n"
template = "<li class=\"web-design illusration\">\n\t<img src=\"$1\" alt=\"\" />\n\t<div>\n\t\t<a href=\"$2\" target=\"_blank\">\n\t\t\t<h4 class=\"heavy remove-bottom\">$3</h4>\n\t\t\t<p>MRP <span class=\"WebRupee\">&#x20B9;</span>$4</p>\n\t\t</a>\n\t</div>\n</li>"
template_with_disc = "<li class=\"web-design illusration\">\n\t<img src=\"$1\" alt=\"\" />\n\t<div>\n\t\t<a href=\"$2\" target=\"_blank\">\n\t\t\t<h4 class=\"heavy remove-bottom\">$3</h4>\n\t\t\t<p>MRP <span class=\"WebRupee\">&#x20B9;</span>$4</p>\n\t\t\t<p>DIS <span class=\"WebRupee\">&#x20B9;</span>$5</p>\n\t\t</a>\n\t</div>\n</li>"
row_template =  "<ul class=\"grid portfolio\">\n\t$1\n</ul>\n"
class Data:
	image_url = ""
	price = ""
	disc_price = ""
	out_of_stock = False
	def __init__(self, url, price, disc_price, out_of_stock=False):
		self.image_url = url
		self.price = price
		self.disc_price = disc_price
		self.out_of_stock = out_of_stock

def get_snippet(site_url, image_url, style, price, disc_price):
	style = style.strip().title()
	if disc_price == "":
		return template.replace("$1", image_url).replace("$2", site_url).replace("$3", style).replace("$4", price)
	return template_with_disc.replace("$1", image_url).replace("$2", site_url).replace("$3", style).replace("$4", price).replace("$5", disc_price)

def get_row_snippet(column_data):
	return row_template.replace("$1", column_data.replace("\n", "\n\t"))

def extract_image_url_for_jabong(soup):
	image_url = ""
	price = ""
	disc_price = ""
	for ul in soup.find_all("ul", class_ = "imageview-slider"):
		i = 0
		for li in ul:
			if i == 0:
				i += 1
				continue;
			image_url =  li.img.attrs['src'].strip()
			break;
	price = soup.find("span", {"itemprop" : "price"}).string.strip()
	disc_price_node = soup.find("div", {"id" : "pdp-voucher-price"})
	if disc_price_node is not None:
		disc_price = disc_price_node.string.replace("Rs.", "").strip()
	d = Data(image_url, price, disc_price)
	return d

def extract_image_url_for_flipkart(soup):
	image_url = ""
	price = ""
	img = soup.find("img", class_ = "productImage current")
	out_of_stock = soup.find("div", class_="out-of-stock")
	if out_of_stock is not None:
		d = Data(image_url, price, "", True)
		return	d	
	if img is not None:
		image_url =  img.attrs['data-src'].strip()
	price = soup.find("meta", {"itemprop" : "price"}).attrs['content'].strip()
	d = Data(image_url, price, "")
	return d

def extract_image_url_for_myntra(soup):
	image_url = ""
	price = ""
	img = soup.find("div", class_ = "blowup").img
	if img is not None:
		image_url = img.attrs['src'].strip()
	price = soup.find("div", class_ = "price").attrs['data-discountedprice'].strip()
	d = Data(image_url, price, "")
	return d

def extract_image_url_for_amazon(soup):
	image_url = ""
	price = ""
	disc_price = ""
	img = soup.find("img", {"id" : "landingImage"})
	if img is not None:
		image_url = img.attrs['src']
	price_div = soup.find("div", {"id" : "price"})
	trs = price_div.findAll("tr")
	if len(trs) >= 1:
		tr = trs[0]
		td = tr.findAll("td")[1]
		price =  td.contents[1].replace(",","").replace(".00", "").strip()
	if len(trs) >= 2:
		tr = trs[1]
		td = tr.findAll("td")[1]
		disc_price =  td.contents[0].contents[1].replace(",","").replace(".00", "").strip()
	d = Data(image_url, price, disc_price)
	return d

requests_session = requests.Session()
if len(sys.argv) != 2:
	exit("Input filename not provided")
fname = sys.argv[1]
print basename(fname)
if not os.path.exists(fname):
	exit(fname + " does not exist")
dir = os.path.dirname(fname)
with open(fname) as f:
    content = f.readlines()
i = 0
row_snippet_buffer = ""
with open(dir + basename(fname) + '_output.txt', 'wb') as output_file:
	for data in content:
		try:
			if data.strip() == "":
				continue
			site_url, style = data.split("\t")
			r = requests_session.get(site_url)
			soup = BeautifulSoup(r.content)
			image_url = ""
			d = None
			if "flipkart" in site_url:
				d  = extract_image_url_for_flipkart(soup)
			elif "jabong" in site_url:
				d  = extract_image_url_for_jabong(soup)
			elif "myntra" in site_url:
				d  = extract_image_url_for_myntra(soup)
			elif "amazon" in site_url:
				d  = extract_image_url_for_amazon(soup)
			if d is not None:
				if d.out_of_stock is True:
					print "OUT OF STOCK-" + data
					continue
				row_snippet_buffer = row_snippet_buffer + get_snippet(site_url, d.image_url, style, d.price, d.disc_price)
				i += 1
				if i%4 == 0:
					output_file.write(get_row_snippet(row_snippet_buffer))
					i = 0
					row_snippet_buffer = ""				
				else:
					row_snippet_buffer += "\n"
		except:
			print "Error in processing-" + data
			raise
			exit("Failed")
	if row_snippet_buffer is not "":
		output_file.write(get_row_snippet(row_snippet_buffer))	