#!/usr/bin/env python
###
### This web service is used in conjunction with App Inventor for Android.
### It stores and retrieves data as instructed by an App Inventor app and its TinyWebDB component.
### It does NOT provide a web interface to the database for administration.
###
### Original author: Dave Wolber via template of Hal Abelson and incorporating changes of Dean Sanvitale
### Maintainer: Phoenix1747 on GitHub
###
### Note-- updated for use with Python2.7 in App Engine, June 2013
### Note-- updated for use with Django 1.11 in App Engine, September 2017
###
from webapp2 import RequestHandler, WSGIApplication
from google.appengine.ext import db
#from google.appengine.ext import webapp
#from google.appengine.ext.webapp.util import run_wsgi_app
#from google.appengine.ext.db import Key

from json import dump
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
	WriteToPhoneAfterStore(self,tag,value)

  def post(self):
	tag = self.request.get('tag')
	value = self.request.get('value')
	self.store_a_value(tag, value)


class GetValueHandler(RequestHandler):

  def get_value(self, tag):
    entry = db.GqlQuery("SELECT * FROM StoredData where tag = :1", tag).get()
    if entry:
        value = entry.value
    else:
        value = ""
  
    WriteToPhone(self,tag,value)

  def post(self):
    tag = self.request.get('tag')
    self.get_value(tag)


### Utilty procedures for generating the output
def WriteToPhone(handler,tag,value):
    handler.response.headers['Content-Type'] = 'application/jsonrequest'
    dump(["VALUE", tag, value], handler.response.out)

def WriteToPhoneAfterStore(handler,tag, value):
    handler.response.headers['Content-Type'] = 'application/jsonrequest'
    dump(["STORED", tag, value], handler.response.out)


### db utilities from Dean  
def store(tag, value, bCheckIfTagExists=True):
	if bCheckIfTagExists:
		# There's a potential readers/writers error here :(
		entry = db.GqlQuery("SELECT * FROM StoredData where tag = :1", tag).get()
		if entry:
		  entry.value = value
		else: 
          entry = StoredData(tag = tag, value = value)
	else:
		entry = StoredData(tag = tag, value = value)
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


### Assign the classes to the URL's
app = WSGIApplication ([('/getvalue', GetValueHandler),
                        ('/storeavalue', StoreAValue)
                        ])
