import logging
import json
import os
import subprocess
import importlib
import datetime
import ConfigParser
import re
import time
import shutil

now = time.time()

#--------------------------------------------------
# A class that processes git payload data then
# runs deployment operations within autoloaded modules
# with an decent logging system, and test webpage
# @author Boz Kay http://boz.co.uk
# @web https://github.com/bozkay/breed
# @licence GNU General Public License, version 3 (GPL-3.0)
# @todo - private method names
#--------------------------------------------------

BREED_ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__))) # the parent dir
CONFIG_DIR = BREED_ROOT+'/config'

class breed():

	def __init__(self):

		self.log = []
		self.logger = {}
		self.config = self.get_config()
		# @todo - allow ini to set an absolute path
		self.log_dir = BREED_ROOT+'/'+self.config.get('general','log_dir')

	def set_payload(self, json_data):
		self.payload_json = json_data
		
		
	#--------------------------------------------------
	# Main deploy public method
	#--------------------------------------------------

	def deploy(self):
		
		# ensure os is in breed root dir
		os.chdir(BREED_ROOT)
		
		# prepare logs directory
		self.log_fragment_mkdir()
		self.log_fragment_prune()
		
		# init generic logging
		# @todo - rotating file handler
		# self.logger_global = self.set_logger('global',self.log_dir+'/deploy-global.log',True)
		self.logger_global = self.set_logger('global',self.log_dir+'/deploy-global.log')
	
		# init deploy log fragment so we can load individual log for each payload on test page
		self.logger_fragment = self.set_logger('fragment',self.fragment_dir+'/deploy.log')
		
		self.payload = self.parse_save_payload(self.payload_json)

		self.payload_init()
		self.load_repo_config()

		self.log_info("Starting deployment of branch {1} in {0}".format(self.repo_fullname,self.branch))
		
		# Run operations on branch create, change or delete
		self.payload_process()
		
	
	#--------------------------------------------------
	# Load JSON payload vars, so we know what to deploy
	#--------------------------------------------------

	def payload_init(self):
	
		# @todo - detect if payload is bitbucket or other, and set variables accordingly
		# If you adapt - please create a pull request

		# github payload processing
		self.branch 			= self.payload['ref'].replace('refs/heads/','')
		self.repo_name 			= self.payload['repository']['name']
		self.repo_fullname		= self.payload['repository']['organization']+"/"+self.repo_name
		self.repo_config_name	= self.filename_safe(self.repo_name)
		self.repo_url = 'https://'+self.config.get('operations','github_token')+':@github.com/'+self.repo_fullname+'.git'
		
		if self.payload['created']:
			self.operation = 'branch_created'
		elif self.payload['deleted']:
			self.operation = 'branch_deleted'
		else:
			self.operation = 'branch_changed'
		


	#--------------------------------------------------
	# Run operations based on payload status
	#--------------------------------------------------

	def payload_process(self):
		
		self.log_info("Running {0} operations".format(self.operation))
		self.run_operations(self.operation);
		
		self.log_info('Finished deployment!')
		
		return list(self.log)
			

	#--------------------------------------------------
	# create a log file for each payload
	# Prune when older than x days
	#--------------------------------------------------
	def log_fragment_mkdir(self):
		
		# Attempt to create the log dir
		if not os.path.isdir(self.log_dir):
			os.mkdir(self.log_dir)

		# Generate unique ID for this deploy
		deploy_id = datetime.datetime.now()
		
		# Attempt to create the fragment dir
		self.fragment_dir = '{0}/payload_{1}/'.format(self.log_dir,deploy_id)
		print self.fragment_dir

		if not os.path.isdir(self.fragment_dir):
			os.mkdir(self.fragment_dir)
	
	def log_fragment_prune(self):
		
		time_check = int(now) - self.config.getint('general','log_payload_keep') * 86400
		for d in os.listdir(self.log_dir):
			if os.path.isdir(os.path.join(self.log_dir, d)):
				if os.stat(os.path.join(self.log_dir,d)).st_mtime < time_check:
					shutil.rmtree(os.path.join(self.log_dir,d))
					

	#--------------------------------------------------
	# runs git commands via subprocess
	#--------------------------------------------------
	def git(self,*args):
	
		command = ['git']
		command.extend(args)
		self.run(command=command)

	#--------------------------------------------------
	# Runs any command via subprocess
	# Ability to supress stdout logging for sqldumps, etc
	# Ability to return stdout for piping to new command
	#--------------------------------------------------
	def run(self, **kwargs):
	
		command 		= kwargs.get('command')
		stdout_log 		= kwargs.get('stdout_log',True)
		stdin 			= kwargs.get('stdin',False)
		raise_error 	= kwargs.get('raise_error',True)

		try:
			process = subprocess.Popen(list(command), 
							shell=False,
							stdin=subprocess.PIPE,
							stdout=subprocess.PIPE,
							stderr=subprocess.PIPE)
				
		except Exception, e:
			self.log_raise(str(e))
		else:

			if stdin:
				stdout, stderr = process.communicate(stdin)
			else:
				stdout, stderr = process.communicate()
			
			if stdout_log == True:
				msg = 'Executed command "{0}"\nOut : {1}Return code : {2}'.format(" ".join(command), stdout+stderr, process.returncode)
			else:
				msg = 'Executed command "{0}"'.format(" ".join(command))

			msg_op = ['Operation: '+line for line in msg.splitlines(True)]
			self.log_info(''.join(msg_op))

			# The process ran sucessfully, but failed
			if raise_error and process.returncode > 0 :
				stderr_op = ['Operation: '+line for line in stderr.splitlines(True)]
				raise Exception(stderr_op)
			else:
				return [stdout,stderr,process.returncode]


	#--------------------------------------------------
	# Add error to self.log so we can return to test webpage, and raise an exception
	# @todo - somthing not quite right about this logic. Perhaps only raise Exceptions locally?
	# But how do I capture and return logs... brain fuzz
	#--------------------------------------------------
	def log_raise(self, message):
	
		self.logger_global.exception(message)
		self.logger_fragment.exception(message)
	
		self.log_add_msg(message)
		raise 


	#--------------------------------------------------
	# Add info message to self.log so we can return it
	#--------------------------------------------------
	def log_info(self, message):
	
		self.logger_global.info(message)
		self.logger_fragment.info(message)
		self.log_add_msg(message)

	#--------------------------------------------------
	# Logging for operations - add pretext
	#--------------------------------------------------
	def log_op_info(self, message):
		self.log_info('Operation: '+message)	

	def log_op_raise(self, message):
		self.log_raise('Operation: '+message)

	def log_get(self):
		return "Deployment Log\n"+"\n".join(self.log)	

	#--------------------------------------------------
	# Append message to self.log so we can return it
	#--------------------------------------------------
	def log_add_msg(self, message):
	
		self.log.append(message)
		
	
	#--------------------------------------------------
	# Create loggers
	# @todo - fix issue where duplicates appear when running on command line
	#--------------------------------------------------
	def set_logger(self,name,log_file,rotating=False):
	
		logger = logging.getLogger(name)
		if rotating == True:
			handler = logging.handlers.RotatingFileHandler(log_file, maxBytes=self.config.get('general','log_maxbytes'), backupCount=self.config.get('general','log_backupcount'))
		else:
			handler = logging.FileHandler(log_file)
	
		logger.setLevel(logging.DEBUG)
		handler.setLevel(logging.DEBUG)
		
		formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
		handler.setFormatter(formatter)
		logger.addHandler(handler)
		
		return logger

	#--------------------------------------------------
	# Parse and save payload JSON data
	# Save so we can read and re-run later if troubleshooting required
	#--------------------------------------------------
	def parse_save_payload(self, data):
	
		f = open(self.fragment_dir+"/payload.json",'w+')

		try:
			json_data = json.loads(data)
			
		except ValueError, e:

			f.write(data)
			self.log_raise("Payload is not valid JSON")
		
		else:

			f.write(json.dumps(json_data, indent=4, separators=(',', ': ')))
			return json_data

		finally:
		
			f.close()
				
	#--------------------------------------------------
	# Lets us place var of the same name, finding them with a cascade
	# Searching in repo.ini/operation > repo.ini/general > general.ini
	# For example; use to set a generic or a repo specific database u and p
	#--------------------------------------------------
	def get_op_var(self,var_name, cascade=True):

		if self.repo_config.has_option('op_'+self.op_name,var_name):
			return self.repo_config.get('op_'+self.op_name,var_name)
		else:
			if cascade == True:
				if self.repo_config.has_option('general',var_name):
					return self.repo_config.get('general',var_name)
				elif self.config.has_option('operations',var_name):
					return self.config.get('operations',var_name)
		return False

	def load_repo_config(self):

		self.repo_config = ConfigParser.ConfigParser()
		config_file = CONFIG_DIR+'/'+self.repo_config_name+'.ini'
		if os.path.isfile(config_file):
			self.repo_config.read(config_file)
		else:
			raise Exception('Repo config does not exist '+config_file)


	#--------------------------------------------------
	# imports operations modules and runs code
	# @todo - if an operation fails, reverse previous operations
	#--------------------------------------------------
	def run_operations(self, operation):

		self.log_info("Loading operations")

		for section_name in self.repo_config.sections():
		
			# Check section name contains a corresponding operation
			if 'op_' in section_name:
				
				op_name = section_name.replace('op_','')
				
				self.log_op_info("Loading "+op_name)

				import sys
				sys.path.append(BREED_ROOT+"/system/ops/")
				sys.path.append(BREED_ROOT+"/ops/")

				try:
					# @todo - when op is called multiple times, don't import again
					mod = importlib.import_module(op_name)
					op = getattr(mod,op_name)
				except Exception, e:
					self.log_raise(str(e))
				else:
					# set op_name for this.get_op_var()
					self.op_name = op_name
					if self.get_op_var('active',False) == 'True':
						op(self,operation)
					else:
						self.log_op_info('Config says active=False')
					


	#---------------------------------
	# Open and read config file
	#---------------------------------
	def get_config(self):
	
		try:
			if os.path.isfile(CONFIG_DIR+'/general.ini'):
				config = ConfigParser.ConfigParser()
				config.read(CONFIG_DIR+'/general.ini')
			else:
				raise Exception('Config file does not exist '+CONFIG_DIR+'/general.ini')
		except Exception, e:
			raise Exception(str(e))
		else:
			self.config = config
			return config

	#---------------------------------
	# Make names safe for file and dbs
	#---------------------------------
	def filename_safe(self, name):
		return re.sub('[^0-9a-zA-Z\-]+', '_', name)

	def dbname_safe(self, name):
		return re.sub('[^0-9a-zA-Z]+', '_', name)
