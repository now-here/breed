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
	
		self.run(breed,operation)
		
	def run(self,breed,operation):
	
		breed.log_op_info("Processing type {0}".format(operation))
		branch_dir = breed.get_op_var('root_dir')+'/'+breed.branch
		
		if operation == 'branch_created' :
		
			breed.log_op_info("Attempting to create %s" % branch_dir)

			# has this branch been deployed already?
			if os.path.isdir(branch_dir):
				breed.log_op_info("Branch already created {0}".format(branch_dir))
				return

			# first deployment, so check root exists
			if not os.path.exists(breed.get_op_var('root_dir')):
				breed.log_op_raise('Root dir %s does not exist, please create it' % breed.get_op_var('root_dir'))
				return

			# make branch dir ready for git init
			os.makedirs(branch_dir)

			# Start git in branch dir
			breed.log_op_info("Change dir %s - attempt git init, fetch, checkout" % branch_dir)
			os.chdir(branch_dir)
			breed.git("init")
			breed.git("fetch",breed.repo_url,'{0}:{0}'.format(breed.branch))
			breed.git("checkout",breed.branch)
		
		elif operation == 'branch_changed' :
		
			breed.log_op_info("Pull in %s" % branch_dir)

			# has this branch been deployed?
			if not os.path.isdir(branch_dir):
				# create because this branch has not been created yet
				breed.log_op_info("Branch not created yet! {0}".format(branch_dir))
				self.run(breed,'branch_created')
				breed.log_op_info("We created it now pull in %s" % branch_dir)

			os.chdir(branch_dir)
			breed.git("pull",breed.repo_url,'{0}:{0}'.format(breed.branch))
			
		elif operation == 'branch_deleted' :
		
			breed.log_op_info("Deleting %s" % branch_dir)

			# has this branch been deployed?
			if not os.path.isdir(branch_dir):
				breed.log_op_raise("Cannot delete as it does not exist %s" % branch_dir)
				return
				
			shutil.rmtree(branch_dir)
		
		
		
