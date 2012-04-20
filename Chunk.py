from google.appengine.ext import db
from google.appengine.api import users

from Bbs import Bbs
from ThreadImage import ThreadImage

class Chunk(db.Model): 
	bbs_key = db.ReferenceProperty(Bbs)
	data = db.BlobProperty() 
	index = db.IntegerProperty()
	date = db.DateTimeProperty(auto_now=True)