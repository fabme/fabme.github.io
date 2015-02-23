import urlparse
from bs4 import BeautifulSoup
import sys, os
import requests
import re
from filehelper import *
from shared import *

requests_session = requests.Session()

def extract_data_from_jabong(soup):
	image_url = ""
	price = ""
	disc_price = ""
	out_of_stock = soup.find("div", class_="prd-sold-out")
	if out_of_stock is not None:
		d = Data(image_url, price, "", True)
		return	d	
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

def extract_data_from_flipkart(soup):
	image_url = ""
	price = ""
	img = soup.find("img", class_ = "productImage current")
	out_of_stock = soup.find("div", {'class' : ["out-of-stock", "listing-obsolete-section"]})
	if out_of_stock is not None:
		d = Data(image_url, price, "", True)
		return	d
	if img is not None:
		image_url =  img.attrs['data-src'].strip()
	price = soup.find("meta", {"itemprop" : "price"}).attrs['content'].strip()
	d = Data(image_url, price, "")
	return d

def extract_data_from_myntra(soup):
	image_url = ""
	price = ""
	img = soup.find("div", class_ = "blowup").img
	if img is not None:
		image_url = img.attrs['src'].strip()
	price = soup.find("div", class_ = "price").attrs['data-discountedprice'].strip()
	out_of_stock = soup.find("div", class_="oos")
	if out_of_stock is not None:
		d = Data(image_url, price, "", True)
		return	d
	d = Data(image_url, price, "")
	return d

def extract_data_from_amazon(soup):
	image_url = ""
	price = ""
	disc_price = ""
	img = soup.find("img", {"id" : "landingImage"})
	if img is not None:
		image_url = img.attrs['src']
	out_of_stock = soup.find("div", {"id" : "availability_feature_div"})
	if out_of_stock is not None:
		children = out_of_stock.findChildren()
		if len(children) > 0:
			d = Data(image_url, price, "", True)
			return	d	
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

def extract_data_from_aliexpress(soup, tuple):
	url = tuple[0]
	image_url = ""
	price = tuple[2]
	disc_price = ""
	image_index = tuple[3]
	url_parsed = urlparse.urlparse(url)
	path_elems = url_parsed.path.split("/")
	product_id = path_elems[len(path_elems) -1].split(".")[0]
	product_desc_url = "http://desc.aliexpress.com/getDescModuleAjax.htm?productId=$1"
	r = requests_session.get(product_desc_url.replace("$1", product_id))
	product_soup = BeautifulSoup(r.content)
	images_on_page =  product_soup.findAll("img")
	current_product_img_counter = 0
	for img in images_on_page:
		if ".alicdn" in img.attrs['src']:
			if current_product_img_counter == int(image_index):
				image_url = img.attrs['src']
				break
			current_product_img_counter += 1
	#downloadfile(image_url, "/tmp", product_id)
	d = Data(image_url, price, disc_price, False, product_id, True)
	return d
