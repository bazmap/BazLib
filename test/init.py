# -*-coding:Utf-8 -*

""" Test des lib
v1.0

"""

# Modules requis
import sys
import os

# Répertoire parent du parent
current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)

# Ajout du parent au chemin système
sys.path.append(parent_dir)

# Import des modules requis
import baz_logger
from baz_requests import baz_requests
from baz_psycopg import baz_psycopg
from baz_subprocess import baz_subprocess






# Logger
main_logger = baz_logger.createLogger(
	log_name= "log_principal",
	file_logging_level= 'INFO', 
	stdout_logging_level= 'DEBUG',
	nb_of_log=5
)

main_logger.info("Appli de test")
main_logger.info('Test des éléments de BazLib')
main_logger.warning('Test logger')






# Psycopg
main_logger.warning('Test Psycopg')

main_pg_conn = baz_psycopg(
	logger= main_logger,
	connexionString= "postgresql://postgres:postgres@127.0.0.1:5433/postgres"
)

pg_result = main_pg_conn.execute("""
SELECT 
	*
FROM (
	VALUES 
		('ligne A', 1),
		('ligne B', 2)
) AS t1(commentaire, id)
;
""")

for line in pg_result:
	main_logger.info('	Info ligne : ' + str(line['id']) + ' - ' + line['commentaire'])






# Requests
main_logger.warning('Test Requests')

main_rest_api = baz_requests(
	logger= main_logger,
	user_agent= "Appli de test",
	locale= 'fr_FR.UTF-8',
	request_timeout= 10,
	delay_before_retry= 5,
	max_iteration= 2
)
"""
api_result = main_rest_api.request(
	url= "https://dummyjson.com/products?limit=10",
	response_format= 'json'
)

for product in api_result['products']:
	main_logger.info(
		'	Produit ' + str(product['id']) + ' : ' + product['brand'] + ' - ' + product['title'] + ' (' + str(product['price']) + ' €)'
	)"""






# Subprocess
main_logger.warning('Test Subprocess')

main_subprocess = baz_subprocess(
	logger= main_logger,
	stdout_level= 'debug',
	stderr_level = 'warning'
)

subprocess_result = main_subprocess.popen(
	args= [
		"cmd", 
		"/c", 
		"dir",
		parent_dir
	],
	out_encoding= 'cp1252'
)

if subprocess_result:
	main_logger.info("Processus terminé sans erreurs")
else:
	main_logger.info("Processus terminé avec erreurs")