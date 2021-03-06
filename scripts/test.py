import sys, os, errno
import requests
import re
from bs4 import BeautifulSoup
from os.path import basename
import unicodecsv
import urlparse
import urllib
from external_data_extractor import *
from shared import *
import argparse

#template = "<li class=\"web-design illusration\">\n\t<img src=\"$1\" alt=\"\" />\n\t<div>\n\t\t<a href=\"$2\" target=\"_blank\">\n\t\t\t<h4 class=\"heavy remove-bottom\">Floral Print</h4>\n\t\t\t<p>MRP <span class=\"WebRupee\">&#x20B9;</span>$3</p>\n\t\t</a>\n\t</div>\n</li>\n"
#template_with_disc = "<li class=\"web-design illusration\">\n\t<img src=\"$1\" alt=\"\" />\n\t<div>\n\t\t<a href=\"$2\" target=\"_blank\">\n\t\t\t<h4 class=\"heavy remove-bottom\">Floral Print</h4>\n\t\t\t<p>MRP <span class=\"WebRupee\">&#x20B9;</span>$3</p>\n\t\t\t<p>DIS <span class=\"WebRupee\">&#x20B9;</span>$4</p>\n\t\t</a>\n\t</div>\n</li>\n"
template = "<li class=\"web-design illusration\">\n\t<img src=\"$1\" alt=\"\" />\n\t<div>\n\t\t<a href=\"$2\" target=\"_blank\">\n\t\t\t<h4 class=\"heavy remove-bottom\">$3</h4>\n\t\t\t<p>MRP <span class=\"WebRupee\">&#x20B9;</span>$4</p>\n\t\t</a>\n\t</div>\n</li>"
template_with_disc = "<li class=\"web-design illusration\">\n\t<img src=\"$1\" alt=\"\" />\n\t<div>\n\t\t<a href=\"$2\" target=\"_blank\">\n\t\t\t<h4 class=\"heavy remove-bottom\">$3</h4>\n\t\t\t<p>MRP <span class=\"WebRupee\">&#x20B9;</span>$4</p>\n\t\t\t<p>DIS <span class=\"WebRupee\">&#x20B9;</span>$5</p>\n\t\t</a>\n\t</div>\n</li>"
row_template =  "<ul class=\"grid portfolio\">\n\t$1\n</ul>\n"
self_template = "<li class=\"web-design illusration\">\n\t<img src=\"$1\" alt=\"\" />\n\t<div>\n\t\t<a class=\"venobox\" data-type=\"iframe\" href=\"$2\">\n\t\t\t<h4 class=\"heavy remove-bottom\">$3</h4>\n\t\t\t<p>MRP <span class=\"WebRupee\">&#x20B9;</span>$4</p>\n\t\t</a>\n\t</div>\n</li>"

google_form_url = "https://docs.google.com/forms/d/18SIsSj1fMwbGQnJoRPD8sG_o1yMa3_QpGAtO5B_poUg/viewform?entry.1623113492=$1&entry.1600146443"

def get_snippet(site_url, image_url, style, price, disc_price):
	style = style.strip().title()
	if disc_price == "":
		return template.replace("$1", image_url).replace("$2", site_url).replace("$3", style).replace("$4", price)
	return template_with_disc.replace("$1", image_url).replace("$2", site_url).replace("$3", style).replace("$4", price).replace("$5", disc_price)

def get_snippet(site_url, style, data):
	style = style.strip().title()
	image_url = data.image_url
	price = data.price
	disc_price = data.disc_price
	m_template = template
	if data.embed_google_form:
		site_url = google_form_url.replace("$1", data.product_code)
		m_template = self_template
		disc_price = ""
	if disc_price == "":
		return m_template.replace("$1", image_url).replace("$2", site_url).replace("$3", style).replace("$4", price)
	return template_with_disc.replace("$1", image_url).replace("$2", site_url).replace("$3", style).replace("$4", price).replace("$5", disc_price)


def get_row_snippet(column_data):
	return row_template.replace("$1", column_data.replace("\n", "\n\t"))

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

requests_session = requests.Session()
parser = argparse.ArgumentParser()
parser.add_argument('-i', action='store', dest='input_file',
                    help='Input File Name', required=True)
parser.add_argument('-t', action='store', dest='template_file',
                    help='Template File Name', required=True)
parser.add_argument('-d', action='store', dest='destination_file',
                    help='Destination File Name', required=True)
parser.add_argument('-s', action='store', dest='staging_dir',
                    help='Staging Dir')
parser.add_argument('-p', action='store', dest='place_holder',
                    help='Placeholder variable name in template')

arguments = parser.parse_args()

fname = arguments.input_file
print basename(fname)
if not os.path.exists(fname):
	exit(fname + " does not exist")
mkdir_p(os.path.dirname(os.path.abspath(arguments.destination_file)))

dir = os.path.dirname(os.path.abspath(fname))
fileName, fileExtension = os.path.splitext(os.path.abspath(fname))
output_file = os.path.join(dir, fileName + '_output.txt')
with open(fname) as f:
    content = f.readlines()
i = 0
output_file_template = ""
with open (arguments.template_file, "r") as template_file:
	output_file_template=template_file.read()
row_snippet_buffer = ""
with open(arguments.destination_file, 'wb') as output_file:
	for data in content:
		try:
			if data.strip() == "":
				continue
			tuple = data.split("\t")	
			site_url = tuple[0]
			style = tuple[1]
			r = requests_session.get(site_url)
			soup = BeautifulSoup(r.content)
			image_url = ""
			d = None
			if "flipkart" in site_url:
				d  = extract_data_from_flipkart(soup)
			elif "jabong" in site_url:
				d  = extract_data_from_jabong(soup)
			elif "myntra" in site_url:
				d  = extract_data_from_myntra(soup)
			elif "amazon" in site_url:
				d  = extract_data_from_amazon(soup)
			elif "aliexpress" in site_url:
				d  = extract_data_from_aliexpress(soup, tuple)
			if d is not None:
				if d.out_of_stock is True:
					print "OUT OF STOCK-" + data
					continue
				row_snippet_buffer = row_snippet_buffer + get_snippet(site_url, style, d)
				i += 1
				# if i%4 == 0:
				# 	output_file.write(get_row_snippet(row_snippet_buffer))
				# 	i = 0
				# 	row_snippet_buffer = ""				
				# else:
				row_snippet_buffer += "\n"
		except:
			print "Error in processing-" + data
			raise
			exit("Failed")
	if row_snippet_buffer is not "":
		data_snippet = get_row_snippet(row_snippet_buffer)
		output_file.write(output_file_template.replace(arguments.place_holder, data_snippet))
