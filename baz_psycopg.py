# -*-coding:Utf-8 -*

""" Gestion des connexion PG
v1.0
Préparamétrages du module psycopg3 pour faciliter le requêtage des BDD PostgreSQL

Classes
-------
baz_psycopg(
	logger: logging.Logger = None,
	host: str = None,
	port: str = None,
	dbname: str = None,
	user: str = None,
	password: str = None,
	connexionString: str = None
) : 

	Classe de gestion de la connexion PG et de gestion des requêtes

"""
# Gestion des connexion PG

# Modules requis
import logging
import os
import psycopg
import sys
import re



# Création d'une classe pour gérer les appels à la BDD
class baz_psycopg():
	"""Classe de gestion de la connexion PG et de gestion des requêtes

	Attributes
	----------
	logger: logging.Logger
		Logger utilisé pour logguer les messages

	Methods
	-------
	connect():
		Permet d'initialiser une connexion avec une BDD.
		Cette méthode est appelée lors de l'initialisation de la classe.
	execute():
		Permet d'éxécuter une requête.
	execute_FromFile():
		Permet d'éxécuter une série de requêtes depuis un fichier.
	execute_FromList():
		Permet d'éxécuter une sérier de requêtes depuis une variable de liste.
	format():
		Permet de formater une requête.
	"""

	# Initialisation de la classe
	def __init__(
		self, 
		logger: any = None,
		host: str = None,
		port: str = None,
		dbname: str = None,
		user: str = None,
		password: str = None,
		connexionString: str = None
	):
		"""Initialisation d'une nouvelle instance de baz_api.
		L'initialisation de la classe utilise la méthode connect si des données de connexion sont passées en paramètre.

		Parameters
		----------
		logger: logger
			Objet baz_logger permettant de logger ce qui se passe.
		Voir méthode connect()
		"""

		# Récupération des paramètres
		# Récupération d'un logger passé en paramètre sinon, utilisation du logger par défaut
		self.logger = logger or logging.getLogger()

		if (host != None) or (connexionString != None):
			# Initialisation de la connexion
			self.connect(
				host,
				port,
				dbname,
				user,
				password,
				connexionString
			)



	def connect(
		self,
		host: str = None,
		port: str = '5432',
		dbname: str = 'postgres',
		user: str = 'postgres',
		password: str = 'postgres',
		connexionString: str = 'postgresql://postgres:postgres@127.0.0.1:5432/postgres',
		row_factory: any = psycopg.rows.dict_row
	):
		"""Création de la connexion.

		Parameters
		----------
		host: string 
			Hôte de la base de données.
		port: string
			Port d'accès à la base de données.
		dbname: string
			Nom de la base de données.
		user: string
			Utilisateur.
		password: string
			Mot de passe.
		connexionString: string
			URL de connexion.
			Si une valeur est spécifiée pour le paramètre "host" alors cet argument n'est pas utilisé.
		"""

		# Récupération et vérification des paramètres
		port = port if port is not None else '5432'
		dbname = dbname if dbname is not None else 'postgres'
		user = user if user is not None else 'postgres'
		password = password if password is not None else 'postgres'
		connexionString = connexionString if connexionString is not None else 'postgresql://postgres:postgres@127.0.0.1:5432/postgres'
		row_factory = row_factory if row_factory is not None else psycopg.rows.dict_row

		self.logger.debug("Initialisation connexion PG")

		if host != None:
			connexionString = psycopg.conninfo.make_conninfo(
				"", 
				host = host, 
				port = port,
				dbname = dbname,
				user = user,
				password = password
			)

		try:
			self.conn = psycopg.connect(
				conninfo = connexionString,
				autocommit = False,
				row_factory= row_factory
			)

		except psycopg.Error as exception:
			self.logger.critical(str(exception))
			sys.exit(str(exception))

		else:

			self.logger.debug("	=> Connexion réussie")
			# Ajout d'une écoute sur la sortie PG
			self.conn.add_notice_handler(self._log_notice)



	def _log_notice(self, 
		diag: any = None
	):
		"""
			Création d'un diagnostique.
			Fonction interne.

			Parameters
			----------
			diag: any
				Objet de diagnostique.
		"""

		self.logger.info(diag.severity + ' | ' + diag.message_primary)



	def execute(self, 
		sql_request: str = None, 
		params: any = None
	):
		"""Exécution d'une requête SQL

		Parameters
		----------
		sql_request: string
			Requête à exécuter.
		params: séquence ou mappage
			Paramètres à passer à la requête

		Returns
		-------
		bool
			False si la requête a échouée.
			True si la requête a été exécutée correctement mais n'a rien renvoyée (Par exemple CREATE TABLE).
		list(dict)
			Si la requête renvoie des résultats, chaque ligne correspond à un élément de la liste et est formaté sous la forme d'un dictionnaire.
		list(list(dict))
			Si la requête est multiple et renvoie donc plusieurs jeux de résultats, chaque jeu est un élément de la liste principale.

		Examples
		--------
		>>> execute('CREATE TABLE public.test (id text);')
		True
		>>> execute('CREATE TABLE public.test (id text);')
		False    # La table existe déjà
		>>> execute('SELECT 1;')
		[{'?column?': 1}]
		>>> execute('SELECT 1;SELECT 2;')
		[
			[{'?column?': 1}], 
			[{'?column?': 2}]
		]
		"""

		self.logger.debug("Exécution requête")

		# Définition d'un curseur
		self.cur= self.conn.cursor()

		# Création d'un bloc transactionnel
		with self.conn.transaction():

			try:
				# Execution de la requête
				self.cur.execute(sql_request, params)

			except Exception as exception:
				# Si erreur, on retourne FALSE
				self.logger.error(str(exception))
				return False

			else:
				self.logger.debug("	=> Requête validée")

				# Le retour est récupéré dans une liste
				return_value = []

				# Itération sur chaque jeu de résultat
				while self.cur:

					try:
						# Récupération des résultats sous la forme d'un tableau
						return_value.append(self.cur.fetchall())

					except Exception as exception:
						# Si pas de retour, on renvoie TRUE
						return_value.append(True)

					if not self.cur.nextset():
						# Arrêt de la boucle s'il n'y a plus de résultats
						break

				if len(return_value) == 1:
					# S'il n'y a qu'un seul résultat, on retourne uniquement le résultat, pas une liste
					return_value = return_value[0]

				return return_value



	def execute_FromFile(self, 
		file_path: str = None
	):
		"""Exécution d'une série de requêtes présentes dans un fichier

		Parameters
		----------
		file_path: str
			Emplacement du fichier à executer.

		Returns
		-------
		Retours tels que renvoyés par la méthode "execute".
		"""
		self.logger.debug("Exécution des requêtes d'un fichier")

		# Test de l'existance du fichier de requêtage
		if file_path != '' and os.path.exists(file_path):
			self.logger.debug("Fichier existant")

			# Lecture du fichier
			with open(file_path, "r", encoding="utf-8") as request_file:

				# Exécution des requêtes
				return self.execute(request_file.read())

		else:
			self.logger.error("Le fichier n'existe pas")

			return False



	def execute_FromList(self, 
		scripts_list: list[str] = None
	):
		"""Exécution d'une série de requêtes présentes dans une liste

		Parameters
		----------
		scripts_list: list[string]
			Liste de script SQL à exécuter.

		Returns
		-------
		list(dict)
			Liste de dictionnaires contenant les scripts (clé "script") et leurs retours (clé "return") tels que renvoyés par la méthode "execute".

		Examples
		--------
		>>> list_requete=[
				'SELECT 1;SELECT 2;',
				'SELECT now();',
				'CREATE TABLE public.test (id text);',
			]
		>>> execute_FromList(list_requete)
		[
			{
				'script': 'SELECT 1;SELECT 2;',
				'return': [
					[{'?column?': 1}], 
					[{'?column?': 2}]
				]
			}, 
			{
				'script': 'SELECT now();',
				'return': [
					{'now': datetime.datetime(2023, 11, 23, 8, 36, 45, 545114, tzinfo=datetime.timezone.utc)}
				]
			},
			{
				'script': 'CREATE TABLE public.test (id text);',
				'return': True
			}
		]
		"""
		self.logger.debug("Exécution d'une liste de requêtes")

		return_value = []

		for script_sql in scripts_list:
			return_value.append(
				{
					"script": script_sql,
					"return": self.execute(script_sql),
				}
			)

		return return_value



	def format(self, 
		sql_request: str = None, 
		*arg: any, 
		**kwarg: any
	):
		"""Fonction de formatage des données.

		Parameters
		----------
		sql_request: string
			Une requête SQL à formater contenant des emplacements réservés numérotés ({0}, {1}...), auto-numérotés ({}) ou nommés ({mon_emplacement}).
		*arg: string
			Liste de valeurs à utiliser dans les emplacement numérotés ({0}, {1}...) ou autonuméroté ({}) de la requête.
		**kwarg: string
			Liste de couple "clé='valeurs'" à utiliser dans les emplacement nommés ({mon_emplacement}) de la requête. 
			Les valeurs sont considérées comme des valeur literales et donc quotées comme telles. 
			Il est possible de spécifier une valeur à considérer comme un identifiant PostgreSQL en ajoutant le drapeau "%i" : {mon_emplacement%i}.
			Notez que le drapeau "%l" pour literal est utilisé par défaut.

		Returns
		-------
		text
			La requête formatée.

		Examples
		--------
		>>> format(
		>>> 	"INSERT INTO public.{test_1%i}({col_1%i},{col_2%i}) VALUES ({valeur%l},{valeur2%l})",
		>>> 	test_1='test__a',
		>>> 	col_1='col__1',
		>>> 	col_2='col__2',
		>>> 	valeur='valeur__1'
		>>> )
		INSERT INTO public."test__a"("col__1","col__2") VALUES ('valeur__1',NULL)
		"""

		self.logger.debug("Formatage d'une requête")

		if kwarg:
			# Motif REGEX pour extraire les informations des placeholder
			pattern_placeholder = r'\{(\w+)(%.{0,1})?\}'
			# Récupération des informations
			list_placeholder = re.findall(pattern_placeholder, sql_request)
			self.logger.debug("Liste des placeholder : " + str (list_placeholder))

			# Création d'un dictionnaire avec le formatage
			dict_placeholder = dict()
			for cle, valeur in list_placeholder:

				if cle in kwarg:
					if valeur == '%i':
						dict_placeholder[cle] = psycopg.sql.Identifier(kwarg[cle])
					elif valeur == '%l':
						dict_placeholder[cle] = psycopg.sql.Literal(kwarg[cle])
					else:
						dict_placeholder[cle] = psycopg.sql.Literal(kwarg[cle])
				else:
					dict_placeholder[cle]= None

			# Nettoyage des placeholder dans la requête
			sql_request = re.sub(pattern_placeholder, r'{\1}', sql_request)
			self.logger.debug("Requête nettoyée : " + sql_request)

			# Préparation de la requête
			base_request = psycopg.sql.SQL(sql_request)

			# Formatage des arguments
			format_request = base_request.format(**dict_placeholder)

		else:

			# Préparation de la requête
			base_request = psycopg.sql.SQL(sql_request)

			format_request = base_request.format(*arg)

		self.logger.debug("Requête finale : " + format_request.as_string(self.conn))
		return format_request.as_string(self.conn)


