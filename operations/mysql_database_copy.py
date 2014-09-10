import re
#--------------------------------------------------
# Copy from a master database (usually for DEV environments)
#--------------------------------------------------

class mysql_database_copy():

	def __init__(self,breed,operation):

		db_u = breed.get_op_var('db_u')
		db_p = breed.get_op_var('db_p')

		if breed.get_op_var('db_name_prefix'):
			db_name_prefix = breed.get_op_var('db_name_prefix')
		else:
			db_name_prefix = re.sub('[^0-9a-zA-Z]+', '_', breed.repo_name)+"_"

		db_name_to = db_name_prefix+re.sub('[^0-9a-zA-Z]+', '_', breed.branch)

		if breed.get_op_var('db_name_from'):
			db_name_from = breed.get_op_var('db_name_from')
		else:
			db_name_from = db_name_prefix+"master"

		if operation == 'branch_created':

			command = ['mysqldump',
					'--user='+db_u,
					'--password='+db_p,
					db_name_from,
					'--no-create-db']
			sql = breed.run(stdout_return=True, stdout_log=False, command=command)

			breed.run(stdin='CREATE DATABASE '+db_name_to, command=['mysql',
					'--user='+db_u,
					'--password='+db_p])
			
			command = ['mysql',
					'--user='+db_u,
					'--password='+db_p,
					db_name_to]
			breed.run(stdin=sql, command=command)

		elif operation == 'branch_changed' :

			breed.log_op_info('Doing nothing')

		elif operation == 'branch_deleted':
   
			breed.run(stdin='DROP DATABASE '+db_name_to, command=['mysql',
					'--user='+db_u,
					'--password='+db_p])
