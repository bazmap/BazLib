# -*-coding:Utf-8 -*

""" Gestion des sous-processus
v1.0
Interface de gestion des sous-processus via le module subprocess

Classes
-------
baz_subprocess(
	logger: logging.Logger = None
) : 

	Classe de lancement de sous processus.

baz_streamreader(
	stream: flux de données à lire (en général stdout ou stderr)
) :

	Classe de lecture des flux de données

"""

# Modules requis
import logging
import os
import queue
import subprocess
import sys
import threading



# Création d'une classe pour gérer les sous processus
class baz_subprocess():
	"""Classe de gestion des sous-processus.

	Attributes
	----------
	logger: logging.Logger
		Logger utilisé pour logguer les messages de sortie des sous processus
	stdout_level: str
		Niveau de log de la sortie standard (par défaut 'debug').
	stderr_level: str
		Niveau de log de la sortie d'erreur (par défaut 'debug').

	Methods
	-------
	popen():
		Permet d'initialiser un nouveau processus.
	"""

	# Initialisation de la classe
	def __init__(
		self, 
		logger: any = None,
		stdout_level: str = None,
		stderr_level: str = None
	):
		"""
			Initialisation d'une nouvelle instance de baz_subprocess.

			Parameters
			----------
			logger: logging.logger
				Objet logger permettant de logger ce qui se passe.
			stdout_level: str
				Niveau de log de la sortie standard (par défaut 'debug').
			stderr_level: str
				Niveau de log de la sortie d'erreur (par défaut 'error').
		"""

		# Récupération et vérification des paramètres
		# Récupération d'un logger passé en paramètre sinon, utilisation du logger par défaut
		self.logger = logger if logger is not None else logging.getLogger()
		self.stdout_level = stdout_level if stdout_level is not None else 'debug'
		self.stderr_level = stderr_level if stderr_level is not None else 'error'




	# Méthode de lancement d'un sous processus
	def popen(
		self,
		args: list, 
		env_var_perso: dict = None,
		out_encoding: str = None
	):
		"""
			Lancement d'un sous processus.

			Parameters
			----------
			args: list
				Commande à exécuter. Le premier élément de la liste est le programme à exécuter. Les autres éléments sont les paramètres à passer au programme.
			env_var_perso: dict
				Tableau de variables à ajouter aux variables d'environnement.
				Ce tableau surcharge les variables d'environnement.
			out_encoding: str
				Encodage de la sortie standard et de la sortie d'erreur.
				Par défaut utf-8

			Returns
			-------
			boolean
				Renvoie "True" lorsque le processus a terminé son execution et "False" s'il y a eu une erreur.
		"""

		# Récupération et vérification des paramètres
		out_encoding = out_encoding if out_encoding is not None else sys.stdout.encoding



		# Récupérer les variables d'environnement actuelles
		var_env = dict(os.environ)

		# Modifier la valeur de la variable d'environnement spécifique
		if env_var_perso:
			var_env.update(env_var_perso)



		# Démarrage du sous processus
		try:
			process = subprocess.Popen(
				args,
				bufsize=-1,
				stdin=subprocess.PIPE,
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE,
				shell=False,
				env=var_env
			)

			# Création des threads de lecture des sorties
			p_stdout = baz_streamreader(process.stdout)
			p_stderr = baz_streamreader(process.stderr)

			# Ecriture des sorties
			while True:

				# Récupération des données
				output_stdout = p_stdout.readline()
				output_stderr = p_stderr.readline()

				# Sortie des données
				if output_stdout:
					getattr(self.logger, self.stdout_level)(
						self.try_decode(output_stdout).strip()
					)
				if output_stderr:
					getattr(self.logger, self.stderr_level)(
						self.try_decode(output_stderr).strip()
					)

				# Si le process est terminé : on stoppe la boucle
				return_code = process.poll()
				if (
					return_code != None
					and not output_stdout 
					and not output_stderr 
				):
					break

			# Renvoie de True si le processus s'est terminé correctement
			if return_code == 0:
				getattr(self.logger, self.stdout_level)("Le processus s'est terminé avec succès.")
				return True

		# Si une erreur survient, on affiche les information sur l'erreur
		except Exception as inst:
			self.logger.error(inst)
			self.logger.error("La commande était : " + (' '.join(map(str, args))) )

		# Dans tous les cas, on renvoi False
		else:
			getattr(self.logger, self.stderr_level)("Le processus s'est terminé avec une erreur.")
			return False

	def try_decode(
		self,
		byte,
		encoding: list = None,
	):
		"""
			Lancement d'un sous processus.

			Parameters
			----------
			byte: byte
				Données binaire à décoder.
			codecs: dict
				Liste d'encodages à tester.

			Returns
			-------
			boolean
				Renvoie "True" lorsque le processus a terminé son execution et "False" s'il y a eu une erreur.
		"""

		# Récupération et vérification des paramètres
		encoding = encoding if encoding is not None else [
			sys.stdout.encoding,
			'utf8',
			'cp1252',
			'latin_1',
			'cp1251',
			'cp1250',
			'cp1256',
			'euc_kr',
			'euc_jp',
			'GB2312',
			'utf16',
			'utf32'
		]

		return_value = ''
		error_value = None

		for i in encoding:
			try:
				return_value = byte.decode(i)
				error_value = None
				break
			except UnicodeDecodeError:
				error_value = True

		if error_value is not None:
			self.logger.warning('Valeur non décodée')
	
		return return_value






class baz_streamreader:
	"""Classe de lecture des flux de données.

	Attributes
	----------
	stream: stream
		flux de données à lire (en général stdout ou stderr).

	Methods
	-------
	readline():
		Lecture des dernières données extraites du flux de donnée.
	"""

	def __init__(self, stream):
		"""
			Initialisation d'une nouvelle instance de baz_streamreader.

			Parameters
			----------
			stream: stream
				flux de données à lire (en général stdout ou stderr).
		"""

		# Récupération du flux de données
		self.stream = stream
		# Création de la file synchronisée
		self.queue = queue.Queue()

		# Fonction de récupération des lignes d'un flux de données
		def populateQueue(stream, queue):
			# Boucle infinie
			while True:
				# Lecture du stream
				line = stream.readline()
				if line:
					# Ajout à la file synchronisée
					queue.put(line)

		# Création d'un thread 
		self.thread = threading.Thread(
			target = populateQueue,
			args = (
				self.stream,
				self.queue
			)
		)

		# Démonisation : arrêt du thread lors de l'arrêt du programme principal
		self.thread.daemon = True

		# Démarrage du thread
		self.thread.start() #start collecting lines from the stream



	def readline(self, timeout = None):
		"""
			Lecture des dernières données extraites du flux de donnée.

			Parameters
			----------
			timeout: integer
				Si None, la méthode renvoie immédiatement les données disponibles.
				Si une valeur de timout est indiquée, la méthode attend le temps indiqué avant de renvoyer les données pour laisser le temps au programme de renvoyer quelque chose.

			Returns
			-------
			bytea
				Renvoie les dernières données extraites du flux de donnée .
		"""

		try:
			return self.queue.get(
				block = timeout is not None,
				timeout = timeout
			)

		except queue.Empty:
			return None


