
#--------------------------------------------------
# Copy from a live database in STAGING
#--------------------------------------------------
class mysql_database_copy_remote():

	def __init__(self,breed,operation):
		
		if breed.get_op_var('active') == "True":

			self.log_info('Copy from remote or drop database')

		else:

			breed.log_op_info("Config says this operation is inactive")
