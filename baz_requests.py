# -*-coding:Utf-8 -*

""" Gestion des requêtes HTTP
v1.0
Interface de requêtage HTTP via le module requests

Classes
-------
baz_requests(
	logger: logging.Logger = None,
	user_agent: str = "BaZ API",
	request_timeout: int = None,
	max_iteration: int = 10
) : 

	Classe de gestion des contacts avec une API.

"""

# Modules requis
import logging
import requests
import json
import datetime
import sys
import time
import locale as mod_locale



# Création d'une classe pour gérer les appels à l'API
class baz_requests():
	"""Classe de gestion des contacts avec une API.

	Attributes
	----------
	logger: logging.Logger
		Logger utilisé pour logguer les messages

	Methods
	-------
	init_oauth2_token():
		Permet d'initialiser un token OAuth2 pour contacter une API.
	request_oauth2():
		Permet de récupérer les données via une API.
	request_simple():
		Permet d'envoyer des requêtes et de récupérer les données.

	"""

	# Initialisation de la classe
	def __init__(
		self, 
		logger: any = None,
		user_agent: str = "BaZ Requests",
		locale: str = '',
		request_timeout: int = None,
		delay_before_retry: int = 0,
		max_iteration: int = 10
	):
		"""
			Initialisation d'une nouvelle instance de baz_requests.

			Parameters
			----------
			logger: logging.logger
				Objet logger permettant de logger ce qui se passe.
			user_agent: string
				User-Agent à utiliser pour contacter l'API.
			request_timeout: integer
				Délai maximum d'attente des réponses serveur (None pour attente illimitée : défaut).
			max_iteration: integer
				Nombre de tentatives maximum de contact d'une url en cas de réponse 500 du serveur.
		"""

		# Récupération et vérification des paramètres
		# Récupération d'un logger passé en paramètre sinon, utilisation du logger par défaut
		self.logger = logger if logger is not None else logging.getLogger()
		user_agent = user_agent if user_agent is not None else "BaZ Requests"
		locale = locale if locale is not None else ''
		self.param_request_timeout = request_timeout
		self.delay_before_retry = delay_before_retry if delay_before_retry is not None else 0
		self.param_max_iteration = max_iteration if max_iteration is not None else 10


		self.request_headers = {
			"User-Agent": user_agent
		}

		# Définition de la locale
		mod_locale.setlocale(mod_locale.LC_TIME, locale)






	# Méthode d'initialisation d'un token (si besoin)
	def init_oauth2_token(
		self,
		url: str = None,
		auth_user: str = None,
		auth_pwd: str = None,
		auth_data: dict = None,
		auth_hearders: dict = None
	):
		"""
			Initialisation d'un jeton OAuth2.
			Le jeton est stocké dans l'attribut oauth2_token de la classe principale.

			Parameters
			----------
			url: string
				URL de récupération du jeton.
			auth_user: string
				Client id.
			auth_pwd: string
				Client secret.
			auth_data: dictionnary
				Données à transmettre au serveur.
			auth_hearders: dictionnary
				Headers à transmettre au serveur.
		"""

		# Récupération des paramètres
		self.oauth2_token = dict(
			url = url,
			auth_user = auth_user,
			auth_pwd = auth_pwd,
			auth_data = auth_data,
			auth_hearders = auth_hearders
		)



		# Initialisation du jeton d'accès à l'API
		self._get_oaut2_token()






	# Récupération du jeton d'accès
	def _get_oaut2_token(self, 
		key: str = None, 
		force: bool = False
	):
		"""
			Récupération d'un jeton OAuth2

			Parameters
			----------
			key: string
				Si une valeur est indiquée, alors seul la valeur de cette propriété du jeton est récupérée, sinon toutes les propriétés sont récupérées.
			force: boolean
				Si True, alors un nouveau token est obligatoirement régénéré

			Returns
			-------
			dict
				Les données du token sous forme de dictionnaire tel que retourné par _retrieve_oauth2_token():
		"""

		# Récupération et vérification des paramètres
		force = force if force is not None else False

		# Test de l'existance du jeton
		try:
			# Si on force le rénouvellement du jeton
			if force:
				self.logger.debug("Renouvelement du Token forcé")
				self.oauth2_token.update(self._retrieve_oauth2_token())

			# Si le jeton est expiré, on le renouvèle
			if self.oauth2_token['expire_time'] < datetime.datetime.now():
				self.logger.debug("Token expiré")
				self.oauth2_token.update(self._retrieve_oauth2_token())

		except:
			self.logger.debug("Token non existant")
			# Si le jeton n'existe pas, on le récupère
			self.oauth2_token.update(self._retrieve_oauth2_token())

		self.logger.debug("Token prêt")

		# Si une clé est spécifiée, on retourne la valeur de la clé spécifiée
		if key == None:
			return self.oauth2_token
		# Sinon on retourne tout
		else:
			return self.oauth2_token[key]	






	# Récupération d'un jeton d'accès
	def _retrieve_oauth2_token(self):
		"""
			Récupération d'un jeton OAuth2 auprès du serveur d'authentification.
			La récupération s'appuie sur l'attributs "oauth2_token" de la classe principale pour déterminer les paramètres de contact.

			Returns
			-------
			dict
				Les données du token sous forme de dictionnaire :
					token : str
						La valeur du token token_json_data['access_token'],
					expire_time : datetime
						Le timestamp de fin de validité du token
		"""

		self.logger.info("Récupération d'un nouveau token")

		request_headers = self.request_headers
		if self.oauth2_token['auth_hearders'] is not None:
			request_headers.update(self.oauth2_token['auth_hearders'])

		# Contact de l'API de récupération d'un jeton
		token_data = self.request_simple(
			method= "POST",
			url= self.oauth2_token['url'],
			request_data= self.oauth2_token['auth_data'],
			request_auth= (self.oauth2_token['auth_user'], self.oauth2_token['auth_pwd']),
			request_timeout= self.param_request_timeout,
			max_iteration= self.param_max_iteration,
			request_headers= request_headers
		)

		if token_data == None:
			self.logger.critical("Echec de la récupération du token")
			sys.exit(str("Echec de la récupération du token"))
		else:
			# Récupération des données sous forme de JSON
			token_json_data = json.loads(token_data)

		# Formatage des données à renvoyer
		return_data = dict(
			token = token_json_data['access_token'],
			expire_time = 
				datetime.datetime.now() + 
				datetime.timedelta(
					seconds=token_json_data['expires_in']
				)
		)

		self.logger.debug("Nouveau token récupéré")

		return return_data






	# Gestion des requêtes
	def request(
		self, 
		method: str = None, 
		url: str = None, 
		request_data: dict = None, 
		request_data_json: str = None,
		request_timeout: int = None, 
		request_headers: dict = None, 
		request_auth: dict = None, 
		max_iteration: int = None, 
		delay_before_retry: int = None,
		iteration: int = None,
		response_format: str = None,
		allowed_error_code: list[int] = None,
		force_token_renew: bool = None,
		request_type: str = 'simple'
	):
		"""
			Récupération des données d'une requête HTTP

			Parameters
			----------
			request_type: string
				'simple' : requpete http simple
				'oauth2' : requête http avec utilisation de l'authentification OAuth2
			url: string
				URL de contact.
			request_data: dictionnary
				Données à transmettre au serveur.
			request_data_json: str
				Données à transmettre au serveur au format json.
			request_timeout: integer
				Délai maximum d'attente des réponses serveur
				None pour attente illimitée (valeur par défaut).
			request_headers: dictionnary
				En-têtes à transmettre au serveur.
			request_auth: dictionnary
				Données d'authentification à transmettre au serveur.
			max_iteration: integer
				Nombre de tentatives maximum de contact d'une url en cas de réponse 500 du serveur.
			delay_before_retry: integer
				Delais d'attente en seconde avant de retenter de contacter une url.
			iteration: integer
				Numéro d'itération lors d'échec de contact du serveur.
			allowed_error_code: list[integer]
				Liste de code erreur (entier) pour lesquels la réponse doit être retournée sans nouvel essai.
				La réponse est sous la forme requests.Response
			force_token_renew: boolean
				Forcer le renouvellement du token.
			response_format: string
				Le format de la réponse parmi
					text : format texte unicode
					json : objet Python json
					all : l'objet requests.Response
					binary : les données binaire brutes reçues
					None : la valeur true est renvoyée si la requête a renvoyé une réponse 200

			Returns
			-------
			binary
			json
			text
			requests.Response
				Données récupérées par la requêtes selon le format choisi
			bool
				True si la requête a renvoyé une réponse 200
		"""

		# Récupération et vérification des paramètres
		request_type = request_type if request_type is not None else 'simple'

		if request_type == 'oauth2':
			return self.request_oauth2(
				method = method, 
				url = url, 
				request_data = request_data,
				request_data_json = request_data_json,
				response_format = response_format,
				force_token_renew = force_token_renew
			)

		else:
			return self.request_simple(
				method = method, 
				url = url, 
				request_data = request_data, 
				request_data_json = request_data_json,
				request_timeout = request_timeout, 
				request_headers = request_headers, 
				request_auth = request_auth, 
				max_iteration = max_iteration, 
				delay_before_retry = delay_before_retry,
				iteration = iteration,
				response_format = response_format,
				allowed_error_code = allowed_error_code
			)






	# Gestion des requêtes simples
	def request_simple(
		self, 
		method: str = "GET", 
		url: str = None, 
		request_data: dict = None, 
		request_data_json: str = None,
		request_timeout: int = None, 
		request_headers: dict = None, 
		request_auth: dict = None, 
		max_iteration: int = None, 
		delay_before_retry: int = 0,
		iteration: int = 1,
		allowed_error_code: list[int] = None,
		response_format: str = 'text'
	):
		"""
			Récupération des données d'une requête HTTP

			Parameters
			----------
			method: string
				Méthode de contact.
			url: string
				URL de contact.
			request_data: dictionnary
				Données à transmettre au serveur.
			request_data_json: str
				Données à transmettre au serveur au format json.
			request_timeout: integer
				Délai maximum d'attente des réponses serveur
				None pour attente illimitée (valeur par défaut).
			request_headers: dictionnary
				En-têtes à transmettre au serveur.
			request_auth: dictionnary
				Données d'authentification à transmettre au serveur.
			max_iteration: integer
				Nombre de tentatives maximum de contact d'une url en cas de réponse 500 du serveur.
			delay_before_retry: integer
				Delais d'attente en seconde avant de retenter de contacter une url.
			iteration: integer
				Numéro d'itération lors d'échec de contact du serveur.
			allowed_error_code: list[integer]
				Liste de code erreur (entier) pour lesquels la réponse doit être retournée sans nouvel essai.
				La réponse est sous la forme requests.Response
			response_format: string
				Le format de la réponse parmi
					text : format texte unicode
					json : objet Python json
					all : l'objet requests.Response
					binary : les données binaire brutes reçues
					None : la valeur true est renvoyée si la requête a renvoyé une réponse 200

			Returns
			-------
			binary
			json
			text
			requests.Response
				Données récupérées par la requêtes selon le format choisi
			bool
				True si la requête a renvoyé une réponse 200
		"""

		# Récupération et vérification des paramètres
		method = method if method is not None else 'GET'
		request_timeout = request_timeout if request_timeout is not None else self.param_request_timeout
		request_headers = request_headers if request_headers is not None else self.request_headers
		max_iteration = max_iteration if max_iteration is not None else self.param_max_iteration
		delay_before_retry = delay_before_retry if delay_before_retry is not None else 0
		iteration = iteration if iteration is not None else 1
		response_format = response_format if response_format is not None else 'text'

		self.logger.debug('Requête ' + method + ' n°' + str(iteration) + ' : ' + url)

		# Envoi d'une requête HTTP
		try:
			request_response = requests.request(
				method= method,
				url= url, 
				data=request_data,
				json=request_data_json,
				timeout=request_timeout,
				headers=request_headers, 
				auth=request_auth,
				verify=True
			)

		except Exception as exception:
			self.logger.critical('Erreur de connexion')
			self.logger.critical(str(exception))
			request_response = requests.models.Response()
			request_response.code = "error"
			request_response.error_type = "error"
			request_response.status_code = 0
			request_response._content = bytes(str(exception), 'utf-8')


		# Si le serveur répond correctement
		if request_response.status_code == 200:
			self.logger.debug('	=> Réponse reçue, code : ' + str(request_response.status_code))
			# On renvoi les données
			if response_format == 'text':
				try:
					return request_response.text
				except:
					self.logger.debug('La réponse ne peut être renvoyée sous forme de text')
					return request_response.content
			elif response_format == 'json':
				try:
					return request_response.json()
				except:
					self.logger.debug('La réponse ne peut être renvoyée sous forme de json')
					return request_response.content
			elif response_format == 'binary':
				return request_response.content
			elif response_format == 'all':
				return request_response
			else:
				return True

		# Si on autorise le renvoi d'erreur
		elif allowed_error_code is not None and request_response.status_code in allowed_error_code:
			self.logger.error('Echec de la tentative n°' + str(iteration) + ' : erreur ' + str(request_response.status_code) + '\n' + request_response.text)
			self.logger.debug('Renvoi de la réponse')

			return request_response

		else:
			# Si le nombre d'itération atteind le maximum
			# On stoppe la récursivité
			if iteration == max_iteration:
				self.logger.error('Echec de la tentative n°' + str(iteration) + ' : erreur ' + str(request_response.status_code) + '\n' + request_response.text)
				self.logger.error('Abandon : trop de tentatives (' + str(max_iteration) + ' tentatives maximum)')

				# On arrête de contacter le serveur et on ne renvoi rien
				return None

			# Sinon, si erreur 401 - Invalid Credentials
			elif request_response.status_code == 401:
				pass

			# Sinon, si erreur 429 - too many requests
			elif request_response.status_code == 429:
				self.logger.error('Echec de la tentative n°' + str(iteration) + ' : erreur ' + str(request_response.status_code) + '\n' + request_response.text)

				# Si un en-tête de délay avant nouvelle tentative
				if 'Retry-After' in request_response.headers:

					# Récupération de l'en-tête
					retry_after_value = request_response.headers['Retry-After']

					# Si la valeur n'est pas un entier (nombre de seconde), c'est une date
					if not isinstance(retry_after_value, int):

						self.logger.debug('Header "Retry-After" = ' + retry_after_value)

						# Différents formats de date à tester
						formats_date_http = [
							"%a, %d %b %Y %H:%M:%S GMT",
							"%A, %d-%b-%y %H:%M:%S GMT",
							"%c"
						]

						# Essai de parsage de la date avec les formats définis
						date_time = None
						for fmt in formats_date_http:
							try:
								date_time = datetime.datetime.strptime(retry_after_value, fmt)
								break
							except ValueError:
								pass

						# Si la date a été parsée avec succès
						if date_time:
							# Calcul de la différence en secondes entre la date HTTP et maintenant
							retry_after_value = (date_time - datetime.datetime.utcnow()).total_seconds()

							if not isinstance(retry_after_value, (int, float, complex)) or retry_after_value == 0:
								self.logger.debug('Délai invalide : ' + str(retry_after_value) + 's')

								retry_after_value = self.delay_before_retry

							elif retry_after_value < 0:
								self.logger.debug('Valeur négative : ' + str(retry_after_value) + ' - Utilisation de la valeur absolue')
								retry_after_value = abs(retry_after_value)

						else:
							self.logger.debug('Date non détectée : ' + retry_after_value)

							retry_after_value = self.delay_before_retry
				else:
					self.logger.debug('Aucun Header "Retry-After"')

					retry_after_value = self.delay_before_retry

				self.logger.warning('=> Nouvelle tentative dans ' + str(retry_after_value) + ' secondes')

				time.sleep(retry_after_value)

				return self.request_simple(
					method= method, 
					url= url, 
					request_data= request_data, 
					request_data_json= request_data_json, 
					request_timeout= request_timeout, 
					request_headers= request_headers, 
					request_auth= request_auth, 
					max_iteration= max_iteration, 
					delay_before_retry= delay_before_retry,
					iteration= iteration + 1
				)


			# Sinon, on relance cette fonction avec les même paramètre mais en itération + 1
			# Cela créé une récursivité qui permet le relancer la requête tant que la réponse n'est pas bonne
			else:
				self.logger.warning('Echec de la tentative n°' + str(iteration) + ' : erreur ' + str(request_response.status_code) + '\n' + request_response.text)
				self.logger.warning('=> Nouvelle tentative')

				time.sleep(self.delay_before_retry)

				return self.request_simple(
					method= method, 
					url= url, 
					request_data= request_data, 
					request_data_json= request_data_json, 
					request_timeout= request_timeout, 
					request_headers= request_headers, 
					request_auth= request_auth, 
					max_iteration= max_iteration, 
					delay_before_retry= delay_before_retry,
					iteration= iteration + 1
				)





	# Envoi de requêtes à l'api
	def request_oauth2(
		self, 
		method: str = "GET", 
		url: str = None, 
		request_data: dict = None,
		request_data_json: str = None,
		response_format: str = 'json',
		force_token_renew: bool = False,
		iteration: int = 1
	):
		"""
			Récupération des données au travers d'un appel à une API.
			Si une erreur d'authentification apparait, deux tentatives accompagnées d'un renouvellement de token seront effectuées.

			Parameters
			----------
			method: string
				Méthode de contact de l'API.
			url: string
				URL de contact de l'API.
			request_data: dictionnary
				Données à transmettre au serveur.
			request_data_json: str
				Données à transmettre au serveur au format json.
			response_format: string
				Formatage de la réponse.
			force_token_renew: boolean
				Forcer le renouvellement du token.
			iteration: integer
				Numéro d'itération lors d'échec de contact du serveur.

			Returns
			-------
			vary
				Retourne les données renvoyées par l'API selon le format spécifié tel que retourné par request_simple():
		"""

		# Récupération et vérification des paramètres
		method = method if method is not None else 'GET'
		response_format = response_format if response_format is not None else 'json'
		force_token_renew = force_token_renew if force_token_renew is not None else False
		iteration = iteration if iteration is not None else 1

		self.logger.info("Contact API : " + url)

		# Gestion token
		allowed_error_code= None

		# Si un attribut de token existe
		if hasattr(self, 'oauth2_token'):
			
			# Récupération du token
			self.request_headers["Authorization"] = 'Bearer ' + self._get_oaut2_token('token', force=force_token_renew)
			# Autorisation des messages d'erreur 401 (erreur de token)
			allowed_error_code= [401]

		# Récupération des données de l'API
		request_response = self.request_simple(
			method= method,
			url= url,
			request_data= request_data,
			request_data_json= request_data_json,
			request_timeout= self.param_request_timeout,
			request_headers= self.request_headers,
			response_format= response_format,
			allowed_error_code= allowed_error_code
		)

		# Si une erreur est renvoyée
		if isinstance(request_response, requests.Response):
			# De type 401
			if request_response.status_code == 401 and iteration < 2:
				self.logger.debug("Nouveau contact API")
				# On relance la fonction request_oauth2 qui renouvelera le token
				self.request_oauth2(
					method = method, 
					url = url, 
					request_data = request_data,
					response_format = response_format,
					force_token_renew = True,
					iteration= iteration + 1
				)

			else:
				self.logger.critical("Echec d'authentification")
				sys.exit(str("Echec d'authentification"))

		# Renvoi des données
		return request_response


