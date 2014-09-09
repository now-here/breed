#--------------------------------------------------
# Create a blank database
#--------------------------------------------------

class mysql_database_basic():

	def __init__(self,breed,operation):

		if breed.get_op_var('active') == "True":

			self.log_info('Create or drop database')

		else:

			breed.log_op_info("Config says this operation is inactive")
