from google.appengine.ext import db
from google.appengine.api import users

from Bbs import Bbs
from MesThread import MesThread

#deleted

class Favorite(db.Model):
	owner = db.UserProperty()
	bbs_key = db.ReferenceProperty(Bbs)
	thread_key = db.ReferenceProperty(MesThread)
	mode = db.IntegerProperty()
	date = db.DateTimeProperty(auto_now=True)
