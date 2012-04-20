#perpetuation data

from google.appengine.ext import db
from google.appengine.api import users

from AppCode import AppCode

class ApiPerpetuationData(db.Model):
	app_key = db.ReferenceProperty(AppCode)
	data_key = db.StringProperty()
	user_id = db.StringProperty()
	text_data = db.TextProperty()
	int_data = db.IntegerProperty()
	date = db.DateTimeProperty(auto_now=True)