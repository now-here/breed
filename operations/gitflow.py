import os
import shutil

#--------------------------------------------------
# GitFlow deployment
# Create/Pull/Delete dirs for each branch
# All feature, hotfix, release in separate dirs in DEV env.
# Only release branchs in separate dirs in STAGING env
# Update master in live
#--------------------------------------------------

class gitflow():

	def __init__(self,breed,operation):

		breed.log_op_info("processing type {0} {1}".format(operation,breed.get_op_var('active')))
		branch_dir = breed.get_op_var('root_dir')+'/'+breed.branch
		
		if operation == 'branch_created' :
		
			# first deployment, so check root exists
			if not os.path.exists(breed.get_op_var('root_dir')):
				breed.log_raise('Root dir %s does not exist, please create it' % breed.get_op_var('root_dir'))

			# make branch dir ready for git init
			breed.log_op_info("Attempting to create %s" % branch_dir)
			os.makedirs(branch_dir)

			# Start git in branch dir
			breed.log_op_info("Change dir %s - attempt git init, fetch, checkout" % branch_dir)
			os.chdir(branch_dir)
			breed.git("init")
			breed.git("fetch",breed.repo_url,'{0}:{0}'.format(breed.branch))
			breed.git("checkout",breed.branch)
		
		elif operation == 'branch_changed' :
		
			breed.log_op_info("Pull in %s" % branch_dir)
			os.chdir(branch_dir)
			breed.git("pull",breed.repo_url,'{0}:{0}'.format(breed.branch))
			
		elif operation == 'branch_deleted' :
		
			breed.log_op_info("Delete %s" % branch_dir)
			shutil.rmtree(branch_dir)
		
		
		
