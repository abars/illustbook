#for profile appstats

import os

def webapp_add_wsgi_middleware(app):
	#if os.environ["SERVER_SOFTWARE"].find("Development")!=-1:
	if 1:
		from google.appengine.ext.appstats import recording
		app = recording.appstats_wsgi_middleware(app)
	return app
