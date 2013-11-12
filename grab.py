from gdata.docs.service import DocsService
from ConfigParser import ConfigParser
from os import remove, path, mkdir
from urllib import urlretrieve
import re

class Bot():
	def __init__(self,config_file="config.ini"):
		config = ConfigParser()
		config.readfp(open(config_file))
		email = config.get("google","email")
		password = config.get("google","password")

		self.client = DocsService()
		self.client.ClientLogin(email,password)

		self.doc_id = config.get("google","id")
		self.content = ""

		# initialize the dirs where files will go, if necessary
		if not path.exists("./content"):
			mkdir("./content")
		if not path.exists("./content/images"):
			mkdir("./content/images")

	def my_doc_content(self,format="txt"):
		"""
		Returns the bot's content attribute, retrieving it first
		from Google docs, if necessary.

		Format in which to retrieve the doc can be optionally specified.
		"""
		if not self.doc_id:
			return ""		# I don't actually know when this would happen...
		else:
			if self.content:
				return self.content
			else:
				self.client.Download("https://docs.google.com/feeds/download/documents/export/Export?id=%(id)s&exportFormat=%(format)s&format=%(format)s" % {"id": self.doc_id, "format": format}, "_tempfile")
				f = open("_tempfile")
				self.content = f.read()
				f.close()
				remove("_tempfile")
				return self.content

	def localize_images(self):
		"""
		Goes through the bot's content attribute (which hopefully has content),
		retrieves any and all non-local images,
		puts them in the /content/images directory,
		then updates the content attribute to refer to the local image instead.

		This is necessary for publication on easybooks, since non-local
		images are not supported.
		"""
		xs = self.my_doc_content().split("\n")
		ys = []
		counter = 0
		for i in xs:
			if re.match(r"^!\[.*\]\(http://.*\)",i):
				text = re.search(r"(?<=!\[).*(?=\])",i).group(0)
				rest = re.sub(r"^!\[.*\]","",i)
				url = re.search(r"(?<=\().*(?=\))",rest).group(0)
				img_m = re.search(r"[^/]*((\.jpg)|(\.gif)|(\.png))",url)
				if img_m:
					filename = img_m.group(0)
				else:
					filename = "image%03d.jpg" % counter
					## this really ought to check for MIME type, but ... eh. later.
				urlretrieve(url, "./content/images/" + filename)
				new_line = "![" + text + "](" + filename + ")"
				ys.append(new_line)
			else:
				ys.append(i)
		self.content = "\n".join(ys)

	def remove_local_links(self):
		"""
		Deletes any and all local links (i.e. links to other chapters)
		from the bot's content.

		This is necessary for publication on easybooks, as links
		between chapters are ... well, maybe they're supported, but I
		don't know how they work in PDF publication, which is my major
		concern at the moment.
		"""
		self.content = re.sub(r"\[([^\]]*)\]\(\.(\S*)\)",r"\1",self.content)

def remove_comments(x):
	"""
	Strips comments from text formatted according to OpenSpending's
	(idiosyncratic) manuscript convention.
	"""
	xs = x.split("\n")
	return "\n".join([i for i in xs if not re.match(r"^%%(?!%%)",i)])

def fix_text(x):
	"""
	Fixes problems with the text returned by Google. 
	"""
	fixed = x
	fixed = fixed.replace("\xef\xbb\xbf","")
	fixed = fixed.replace("\r","")
	fixed = fixed.replace("\n\n\n","\n\n")
	return fixed

def manuscript_to_dictionary(x):
	"""
	Takes the (fixed) text returned by Google and chops it up,
	turning it into a dictionary of filenames and content.

	This is so that we can store the source in one giant file
	on Google Docs and use the script to split it up into
	individual chapters.
	"""
	def split_on_headers(x):
		xs = x.split("%%%% ")
		xs = [i for i in xs if not re.match(r"^\s*$",i)]
		return xs

	def string_to_pair(x):
		xs = x.split("\n")
		return {"name": xs[0].strip(),
				"body": "\n".join(xs[1:]).strip()}

	def strings_to_pairs(xs):
		return [string_to_pair(i) for i in xs]

	return strings_to_pairs(split_on_headers(x))

def dump_pairs_to_files(xs):
	"""
	Takes a dictionary of the sort returned by manuscript_to_dictionary
	and writes out the files.
	"""
	counter = 1
	for x in xs:
		f = open("./content/%(c)02d-%(n)s.md" % {"c":counter,"n":x["name"]},"w")
		f.write(x["body"])
		f.close()
		counter += 1

if __name__ == "__main__":
	## usage: python grab.py
	b = Bot("config.ini")
	b.localize_images()
	b.remove_local_links()
	dump_pairs_to_files(manuscript_to_dictionary(remove_comments(fix_text(b.my_doc_content()))))