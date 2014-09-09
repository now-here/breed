import web
import logging
import json
import os
import re
import base64
import time
import sys
import traceback
import ConfigParser

from breed import breed

# Point os at cwd
os.chdir(os.path.dirname(os.path.realpath(__file__)))

# Init webpy framework
urls = (
	"/test", "test",
	"/payload_data", "payload_data",
	"/deploy", "deploy",
)
app = web.application(urls, globals())
render = web.template.render('templates/')


#---------------------------------
# Process payload, deploy based on config and custom hooks
#---------------------------------
class deploy:

	def POST(self):

		# Run main deploy code
		try:
			a = breed()
			a.get_config()
			a.set_payload(web.data())
			a.deploy()
						
		except Exception, e:
			#return "There was an error\n"+traceback.format_exc()+"\n\n"+a.log_get()
			return "There was an error\n"+traceback.format_exc()

		else :
			return a.log_get()

		
#---------------------------------
# Load a test/logs page which helps troubleshooting
#---------------------------------
class test:

	def GET(self):

		if auth(web):

			return render.test()
		
#---------------------------------
# Get recent payloads and logs
#---------------------------------
class payload_data:

	def GET(self):

		a = breed()
		config = a.get_config()

		if auth(web):

			payloads = []
			for x in os.listdir(config.get('general','log_dir')) :
				if "payload_" in x :
					payload = {}
					payload['time'] = x.replace('payload_','')
					f = open(config.get('general','log_dir')+'/'+x+'/payload.json','r')
					payload['json'] = f.read()
					f.close()
					f = open(config.get('general','log_dir')+'/'+x+'/deploy.log','r')
					payload['log'] = f.read()
					payloads.append(payload)
					f.close()
			
			payloads_sorted = reversed(sorted(payloads, key=lambda payload: payload['time']))
			
			return render.payload_data(payloads_sorted,payloads)


#---------------------------------
# Authenticate both test and hook
#---------------------------------
def auth(web, debug=False):

	auth = web.ctx.env.get('HTTP_AUTHORIZATION')

	authreq = False

	if auth is None:
		authreq = True
	else:
		auth = re.sub('^Basic ','',auth)
		username,password = base64.decodestring(auth).split(':')

		a = breed()
		config = a.get_config()

		if config.get('general','password').encode('utf-8') == "change_this":
		
			message = "Please set your password in {0}".format(CONFIG_FILE)
			raise Exception(message)
		
		else:

			if username == config.get('general','username').encode('utf-8') and password == config.get('general','password').encode('utf-8'):
				return True
			else:
				authreq = True

	if authreq:
		web.header('WWW-Authenticate','Basic realm="BREED"')
		web.ctx.status = '401 Unauthorized'
		return
		

#---------------------------------
# It all starts here... 
#---------------------------------
if __name__ == '__main__':
	app.run()
