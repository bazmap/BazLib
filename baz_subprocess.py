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
		args, 
		env_var_perso
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

			Returns
			-------
			boolean
				Renvoie "True" lorsque le processus a terminé son execution et "False" s'il y a eu une erreur.
		"""

		# Récupérer les variables d'environnement actuelles
		var_env = dict(os.environ)

		# Modifier la valeur de la variable d'environnement spécifique
		var_env.update(env_var_perso)

		# Démarrage du sous processus
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

			# Récupération des données toutes les 0.1s
			output_stdout = p_stdout.readline()
			output_stderr = p_stderr.readline()

			# Sortie des données
			if output_stdout:
				getattr(self.logger, self.stdout_level)(output_stdout.decode('utf-8').strip())
			if output_stderr:
				getattr(self.logger, self.stderr_level)(output_stderr.decode('utf-8').strip())

			# Si le process est terminé : on stoppe la boucle
			return_code = process.poll()
			if (
				return_code != None
				and not output_stdout 
				and not output_stderr 
			):
				break

		# Renvoie d'une information selon le code d'erreur de sortie
		if return_code == 0:
			getattr(self.logger, self.stdout_level)("Le processus s'est terminé avec succès.")
			return True
		else:
			getattr(self.logger, self.stderr_level)("Le processus s'est terminé avec une erreur.")
			return False







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


