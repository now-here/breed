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
			db_name_prefix = breed.dbname_safe(breed.repo_name)+"_"

		db_name_to = db_name_prefix+breed.dbname_safe(breed.branch)

		if breed.get_op_var('db_name_from'):
			db_name_from = breed.get_op_var('db_name_from')
		else:
			db_name_from = db_name_prefix+"master"

		if operation == 'branch_created':

			p = breed.run(stdin='CREATE DATABASE '+db_name_to, command=['mysql',
					'--user='+db_u,
					'--password='+db_p],raise_error=False)
					
			# if error code is 1 - database already exists - we deployed this already
			if p[2] == 1:
				breed.log_op_info("Database %s exists - already deployed" % db_name_to)
				return
			
			self.db_copy(breed,db_u,db_p,db_name_from,db_name_to,False)

		elif operation == 'branch_changed' :

			breed.log_op_info('Doing nothing')

		elif operation == 'branch_deleted':
   
			# @todo - if del_ exists create multiple? del2_ etc
			self.db_copy(breed,db_u,db_p,db_name_to,"del_"+db_name_to,True)
			
			# @todo - make an option set in ini - drop db seems too dangerous?
			breed.run(stdin='DROP DATABASE '+db_name_to, command=['mysql',
					'--user='+db_u,
					'--password='+db_p])


	# @todo - check if to db exists, if not create.

	def db_copy(self,breed,db_u,db_p,db_name_from,db_name_to, create=False):

			if create== True:
				p = breed.run(stdin='CREATE DATABASE '+db_name_to, command=['mysql',
						'--user='+db_u,
						'--password='+db_p],raise_error=False)

			command = ['mysqldump',
					'--user='+db_u,
					'--password='+db_p,
					db_name_from,
					'--no-create-db']
			p = breed.run(stdout_log=False, command=command)

			command = ['mysql',
					'--user='+db_u,
					'--password='+db_p,
					db_name_to]
			breed.run(stdin=p[0], command=command)
	