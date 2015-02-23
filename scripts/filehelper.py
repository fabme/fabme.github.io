import urllib
import os
import shutil
from os.path import basename

def downloadfile(url, dest_folder, dest_filename):
	print url
	try:
		filename, headers = urllib.urlretrieve(url)
		print 'File:', filename
		fileName, fileExtension = os.path.splitext(basename(filename))

		shutil.move(filename, dest_folder + "/" + dest_filename + fileExtension)
		print 'File exists before cleanup:', os.path.exists(filename)
	finally:
		urllib.urlcleanup()
