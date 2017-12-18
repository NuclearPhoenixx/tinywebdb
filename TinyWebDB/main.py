#!/usr/bin/env python
###
### This web service is used in conjunction with App Inventor for Android.
### It stores and retrieves data as instructed by an App Inventor app and its TinyWebDB component.
### It also provides a web interface to the database for administration.
###
### Original author: Dave Wolber via template of Hal Abelson and incorporating changes of Dean Sanvitale
### Maintainer: Phoenix1747 on GitHub
###
### Note-- updated for use with Python2.7 in App Engine, June 2013
###
from webapp2 import RequestHandler, WSGIApplication
from google.appengine.ext import db
from google.appengine.ext.webapp import template

from os import path as Path
from json import dump
from logging import debug
from re import compile
from htmlentitydefs import name2codepoint


### Max entries for trimdb()
max_entries = 1000

### Now come some classes
class StoredData(db.Model):
  tag = db.StringProperty()
  value = db.TextProperty()
  date = db.DateTimeProperty(required=True, auto_now=True)


class StoreAValue(RequestHandler):

  def store_a_value(self, tag, value):
  	store(tag, value)
	# call trimdb if you want to limit the size of db
  	# trimdb()

	## Send back a confirmation message.  The TinyWebDB component ignores
	## the message (other than to note that it was received), but other
	## components might use this.
	result = ["STORED", tag, value]

	if self.request.get('fmt') == "html":
		WriteToWeb(self,tag,value)
	else:
		WriteToAppAfterStore(self,tag,value)

  def post(self):
	tag = self.request.get('tag')
	value = self.request.get('value')
	self.store_a_value(tag, value)
	self.redirect('/')


class DeleteEntry(RequestHandler):

  def post(self):
	debug('/deleteentry?%s\n|%s|' %
				  (self.request.query_string, self.request.body))
	entry_key_string = self.request.get('entry_key_string')
	key = db.Key(entry_key_string)
	tag = self.request.get('tag')
	if tag.startswith("http"):
	  DeleteUrl(tag)
	db.run_in_transaction(dbSafeDelete,key)
	self.redirect('/')


class GetValueHandler(RequestHandler):

  def get_value(self, tag):
    entry = db.GqlQuery("SELECT * FROM StoredData where tag = :1", tag).get()
    if entry:
        value = entry.value
    else: value = ""

    if self.request.get('fmt') == "html":
    	WriteToWeb(self,tag,value )
    else:
        WriteToApp(self,tag,value)

  def post(self):
    tag = self.request.get('tag')
    self.get_value(tag)

  # there is a web ui for this as well, here is the get
  def get(self):
    # this did pump out the form
    template_values={}
    path = Path.join(Path.dirname(__file__),'index.html')
    self.response.out.write(template.render(path,template_values))


class MainPage(RequestHandler):

  def get(self):
    entries = db.GqlQuery("SELECT * FROM StoredData ORDER BY date desc")
    template_values = {"entryList":entries}
    # render the page using the template engine
    path = Path.join(Path.dirname(__file__),'index.html')
    self.response.out.write(template.render(path,template_values))


### Utilty procedures for generating the output
def WriteToApp(handler,tag,value):
    handler.response.headers['Content-Type'] = 'application/jsonrequest'
    dump(["VALUE", tag, value], handler.response.out)

def WriteToWeb(handler, tag,value):
    entries = db.GqlQuery("SELECT * FROM StoredData ORDER BY date desc")
    template_values={"result":  value,"entryList":entries}
    path = Path.join(Path.dirname(__file__),'index.html')
    handler.response.out.write(template.render(path,template_values))

def WriteToAppAfterStore(handler,tag, value):
    handler.response.headers['Content-Type'] = 'application/jsonrequest'
    dump(["STORED", tag, value], handler.response.out)


### db utilities from Dean
### A utility that guards against attempts to delete a non-existent object
def dbSafeDelete(key):
  if db.get(key) :	db.delete(key)

def store(tag, value, bCheckIfTagExists=True):
	if bCheckIfTagExists:
		# There's a potential readers/writers error here :(
		entry = db.GqlQuery("SELECT * FROM StoredData where tag = :1", tag).get()
		if entry:
		  entry.value = value
		else: entry = StoredData(tag = tag, value = value)
	else: entry = StoredData(tag = tag, value = value)
	entry.put()

def trimdb():
	## If there are more than the max number of entries, flush the
	## earliest entries.
	entries = db.GqlQuery("SELECT * FROM StoredData ORDER BY date")
	if (entries.count() > max_entries):
		for i in range(entries.count() - max_entries):
			db.delete(entries.get())

def replace_entities(match):
    try:
        ent = match.group(1)
        if ent[0] == "#":
            if ent[1] == 'x' or ent[1] == 'X':
                return unichr(int(ent[2:], 16))
            else:
                return unichr(int(ent[1:], 10))
        return unichr(name2codepoint[ent])
    except:
        return match.group()

entity_re = compile(r'&(#?[A-Za-z0-9]+?);')

def html_unescape(data):
    return entity_re.sub(replace_entities, data)

def ProcessNode(node, sPath):
	entries = []
	if node.nodeType == minidom.Node.ELEMENT_NODE:
		value = ""
		for childNode in node.childNodes:
			if (childNode.nodeType == minidom.Node.TEXT_NODE) or (childNode.nodeType == minidom.Node.CDATA_SECTION_NODE):
				value += childNode.nodeValue

		value = value.strip()
		value = html_unescape(value)
		if len(value) > 0:
			entries.append(StoredData(tag = sPath, value = value))
		for attr in node.attributes.values():
			if len(attr.value.strip()) > 0:
				entries.append(StoredData(tag = sPath + ">" + attr.name, value = attr.value))

		childCounts = {}
		for childNode in node.childNodes:
			if childNode.nodeType == minidom.Node.ELEMENT_NODE:
				sTag = childNode.tagName
				try:
					childCounts[sTag] = childCounts[sTag] + 1
				except:
					childCounts[sTag] = 1
				if (childCounts[sTag] <= 5):
					entries.extend(ProcessNode(childNode, sPath + ">" + sTag + str(childCounts[sTag])))
		return entries

def DeleteUrl(sUrl):
	entries = StoredData.all().filter('tag >=', sUrl).filter('tag <', sUrl + u'\ufffd')
	db.delete(entries[:500])


### Assign the classes to the URL's
app = WSGIApplication ([('/', MainPage),
                        ('/getvalue', GetValueHandler),
                        ('/storeavalue', StoreAValue),
                        ('/deleteentry', DeleteEntry)])
