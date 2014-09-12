import re
import distutils.core

#--------------------------------------------------
# Copy contents of folder into deploy folder
# i.e. Can be used to place env.ini into deploy folders
#--------------------------------------------------

class dir_copy():

	def __init__(self,breed,operation):

		breed.log_op_info("Processing type {0}".format(operation))

		if operation == 'branch_created' :
		
			# @todo - get_op_var(name,default) - much better logic
			copy_from_dir = breed.get_op_var('copy_from_dir')
	
			if breed.get_op_var('copy_to_dir'):
				copy_to_dir = breed.get_op_var('copy_to_dir')
			else:
				copy_to_dir = breed.get_op_var('root_dir')+"/"+breed.filename_safe(breed.branch)
	
			breed.log_op_info("Attempting to copy files from '{0}' to '{1}'".format(copy_from_dir,copy_to_dir))
			
			try:
			
				# @todo - optional create folder if not exists.
				distutils.dir_util.copy_tree(copy_from_dir, copy_to_dir, update=1)
			
			except Exception, e:
				
				raise Exception(str(e))
			
			
		else:
		
			breed.log_op_info("Doing nothing")

