from google.appengine.ext import db
from google.appengine.api import users

class Response(db.Model):
	editor = db.StringProperty()
	content = db.TextProperty()
	user_id = db.StringProperty()	#Submitter
	homepage_addr = db.StringProperty() #Reserved
	date = db.DateTimeProperty(auto_now=True)