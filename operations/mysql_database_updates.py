#--------------------------------------------------
# Apply sql updates
#--------------------------------------------------
class mysql_database_updates():

	def __init__(self,breed,operation):
		
		if breed.get_op_var('active') == "True":

			self.log_info('Apply sql updates database')
	
			self.db_name = self.repo_name+"_"+self.branch
			self.sqlupdate_dir = self.repo_config['op_database_sqlupdate_dir']
			
			# if level == 'branch_changed' or level == 'branch_changed' :
				# todo : apply sql updates
				# when merged into develop or master branch, the sqlupdates will be merged too - altering the master database


		else:

			breed.log_op_info("Config says this operation is inactive")
