#application

from google.appengine.ext import db
from google.appengine.api import users

class AppCode(db.Model):
	#app mode
	mode = db.IntegerProperty()

	#code
	js_code = db.TextProperty()
	css_code = db.TextProperty()
	plugin_args = db.StringProperty()
	
	#app info
	user_id = db.StringProperty()
	author = db.StringProperty()
	app_name = db.StringProperty()
	app_guide = db.TextProperty()
	app_id = db.StringProperty()
	
	#property
	is_public = db.IntegerProperty()
	bookmark_count = db.IntegerProperty()
	ranking_key = db.StringProperty()
	ranking_order = db.IntegerProperty()

	#icon image
	icon = db.BlobProperty()
	icon_content_type = db.StringProperty()

	#forum
	support_forum = db.ReferenceProperty()	#MesThread

	#image upload
	image_blob_list=db.ListProperty(db.Blob)
	image_type_list=db.StringListProperty()
	image_id_list=db.StringListProperty()

	#date
	create_date = db.DateTimeProperty()
	public_date = db.DateTimeProperty()
	date = db.DateTimeProperty(auto_now=True)