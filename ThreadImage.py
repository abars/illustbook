from google.appengine.ext import db
from google.appengine.api import users

class ThreadImage(db.Model):
	bbs_key = db.ReferenceProperty()
	image = db.BlobProperty()
	thumbnail = db.BlobProperty()
	moper = db.BlobProperty()
	gif_thumbnail = db.BlobProperty()
	illust_mode = db.IntegerProperty()
	width = db.IntegerProperty()
	height = db.IntegerProperty()
	chunk_list = db.StringListProperty()	#deleted
	chunk_list_key = db.ListProperty(db.Key)
	is_png = db.IntegerProperty()
	date = db.DateTimeProperty(auto_now=True)
