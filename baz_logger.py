# -*-coding:Utf-8 -*

""" Gestion des logs
v1.0
Préparamétrages du module logging pour faciliter la mise en place de logs dans une application

Functions
---------
createLogger(
	log_name: str = None, 
	log_file_name: str = None, 
	log_directory: str = None, 
	file_logging_level: str = 'DEBUG', 
	stdout_logging_level: str = 'DEBUG', 
	nb_of_log: int = 10, 
	regex_to_del: str = None, 
	logger_type: str = 'simple'
) : 
	Returns : logging.logger

	Fonction de création et de paramétrage d'un logger

"""

# Modules requis
import logging
import logging.handlers
import os
import re
import inspect
import pathlib
import datetime



# Fonction de création d'un logger
def createLogger(
	log_name: str = None, 
	log_file_name: str = None, 
	log_directory: str = None, 
	file_logging_level: str = 'DEBUG', 
	stdout_logging_level: str = 'DEBUG', 
	nb_of_log: int = 10, 
	regex_to_del: str = None, 
	logger_type: str = 'simple'
):
	"""
	Fonction de création et de paramétrage d'un logger

	Parameters
	----------
	log_name: string 
		Le nom du logger
	log_file_name: string
		Le nom du fichier de log généré. 
		Par défaut le fichier est sous cette forme : "logger_name_YYYY-MM-DD_HH-MM-SS.log"
	log_directory: string
		Répertoire de stockage des fichiers de log. 
		Par défaut le répertoire est "/logs" et situé dans le répertoire du fichier principal du programme.
	file_logging_level: string
		Niveau minimal de message de log à récupérer dans les fichiers ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'). 
		Par défaut 'DEBUG'.
	stdout_logging_level: string
		Niveau minimal de message de log à récupérer dans les fichiers ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'). 
		Par défaut 'DEBUG'.
	nb_of_log: integer
		Nombre de fichier de log à concerver. 
		Par défaut 10.
	regex_to_del: string 
		Expression régulière pour identifier les fichier de log à supprimer lorsque le log_file_name est précisé.
		Par défaut : "^logger_name.*\.log$"
	logger_type: string 
		Type de log à utiliser : 
			'simple' : chaque lancement du programme génère un fichier de log
			'rotating' : chaque lancement du programme génère un fichier de log rotatif : si le fichier dépasse 2 Mb un nouveau est généré.

	RETURNS
	-------
		logging.logger
			Objet logger du module logging standard, toutes les méthodes peuvent être utilisées (notamment : debug(), info(), warning(), error() et critical() pour logguer des messages)
			Il est possible de spécifier l'argument "extra" suivant pour rediriger les message vers une sortie spécifique :
				'sortie': 'fichier' => sortie fichier uniquement
				'sortie': 'console' => sortie console uniquement
			Par exemple
				logger.info('Test sortie fichier', extra={'sortie': 'fichier'})
	"""

	# Récupération et vérification des paramètres
	file_logging_level = file_logging_level if file_logging_level is not None else 'DEBUG'
	stdout_logging_level = stdout_logging_level if stdout_logging_level is not None else 'DEBUG'
	nb_of_log = nb_of_log if nb_of_log is not None else 10
	logger_type = logger_type if logger_type is not None else 'simple'

	# Instantiation du logger
	logger = logging.getLogger(log_name)

	# Définition du niveau de log
	logger.setLevel(
		min(
			logging.getLevelName(file_logging_level), 
			logging.getLevelName(stdout_logging_level)
		)
	)



	# Définition d'un gestionnaire pour la sortie
	stream_handler = logging.StreamHandler()

	# Définition du niveau de log
	stream_handler.setLevel(
		logging.getLevelName(stdout_logging_level)
	)

	# Ajout d'un filtre
	stream_handler.addFilter(
		_handler_filter_1('console')
	)

	# Formatage des messages
	stream_handler.setFormatter(
		_color_formatter("%(levelname)s | %(filename)s | %(funcName)s | %(message)s")
	)

	# Ajout du handler
	logger.addHandler(stream_handler)



	# Définition d'un gestionnaire pour les fichiers
	# Initialisation des fichiers
	log_files = _init_log_files(
		log_name= log_name,
		log_file_name= log_file_name,
		log_directory= log_directory,
		nb_of_log= nb_of_log, 
		regex_to_del = regex_to_del
	)

	# Ajout du gestionnnaire de fichier
	if logger_type == 'rotating':
		# Par rotation
		file_handler = logging.handlers.RotatingFileHandler(
			filename = os.path.join(log_files['dir'], log_files['filename']),
			maxBytes = 2000000, 
			backupCount = nb_of_log,
			encoding = 'utf-8'
		)
	else:
		# Par simple fichier
		file_handler = logging.FileHandler(
			filename = os.path.join(log_files['dir'], log_files['filename']),
			encoding = 'utf-8'
		)

	# Définition du niveau de log
	file_handler.setLevel(
		logging.getLevelName(file_logging_level)
	)

	# Ajout d'un filtre
	file_handler.addFilter(
		_handler_filter_1('fichier')
	)

	# Assignation du formatter personnalisé au handler
	file_handler.setFormatter(
		logging.Formatter("%(asctime)s | %(levelname)s | %(filename)s | %(funcName)s | %(message)s")
	)

	# Ajout du handler
	logger.addHandler(file_handler)



	# Renvoi du logger
	return logger






# Fonction de nettoyage de fichiers
def _limitFileNumber(
	path_directory: str = None, 
	max_nb_file: int = 10, 
	regex_to_del: str = None
):
	"""
	Nettoyage des fichiers de log

	Parameters
	----------
	log_directory: string
		Répertoire de stockage des fichiers de log. 
		Par défaut le répertoire est "/logs" et situé dans le répertoire du fichier principal du programme.
	nb_of_log: integer
		Nombre de fichier de log à concerver. 
		Par défaut 10.
	regex_to_del: string
		Expression régulière pour identifier les fichier de log à supprimer lorsque le log_file_name est précisé.
		Par défaut : "^logger_name.*\.log$"

	RETURNS
	-------
		None
	"""

	# Récupération et vérification des paramètres
	max_nb_file = max_nb_file if max_nb_file is not None else 10

	# Liste des fichiers situés dans le répertoire
	file_list = filter(
		lambda x: os.path.isfile(
			os.path.join(
				path_directory, 
				x
			)
		),
		os.listdir(path_directory)
	)

	# On ne garde que les fichiers correspondant au motif regex
	if not regex_to_del == None:
		file_list = filter(
			lambda x: bool(
				re.search(
					regex_to_del, 
					x
				)
			),
			file_list
		)

	# Tri des fichiers basé sur leur date de dernière modification
	file_list = sorted(
		file_list,
		key = lambda x: os.path.getmtime(
			os.path.join(
				path_directory, 
				x
			)
		),
		reverse = True
	)


	# Numéro d'itération
	i = 0

	# Pour chaque fichier
	for file_name in file_list:

		# On numérote le fichier
		i += 1

		# Si le numéro de fichier est supérieur à ce qui a été prévu, on le supprime
		if i > max_nb_file:

			os.remove( 
				os.path.join(
					path_directory, 
					file_name
				)
			)



def _init_log_files(
	log_name: str = 'Log',
	log_file_name: str = None,
	log_directory: str = None,
	nb_of_log: int = 10,
	regex_to_del: str = None,
):
	"""
	Fonction de création et de paramétrage d'un logger

	Parameters
	----------
	log_name: string
		Le nom du logger
	log_file_name: string
		Le nom du fichier de log généré. 
		Par défaut le fichier est sous cette forme : "logger_name_YYYY-MM-DD_HH-MM-SS.log"
	log_directory: string
		Répertoire de stockage des fichiers de log. 
		Par défaut le répertoire est "/logs" et situé dans le répertoire du fichier principal du programme.
	nb_of_log: integer
		Nombre de fichier de log à concerver. 
		Par défaut 10.
	regex_to_del: string
		Expression régulière pour identifier les fichier de log à supprimer lorsque le log_file_name est précisé.
		Par défaut : "^logger_name.*\.log$"

	RETURNS
	-------
		dict():
			dir: str
				Répertoire de stockage des fichiers
			filename: str
				Nom du fichier de log
	"""

	# Récupération et vérification des paramètres
	log_name = log_name if log_name is not None else 'Log'
	nb_of_log = nb_of_log if nb_of_log is not None else 10

	# Génération d'un répertoire de log si aucun n'est donné
	if log_directory == None:
		fileStack = []

		# Inspection de la stack
		if __name__ != '__main__':
			for frame in inspect.stack()[1:]:
				if frame.filename[0] != '<':
					fileStack.append(frame.filename)

		# Répertoire /logs créé dans le même répertoire que le fichier appelant la fonction
		log_directory = os.path.join(
			os.path.dirname(fileStack[-1]),
			'logs'
		)

	# Création du répertoire
	repertoire = pathlib.Path(log_directory)
	repertoire.mkdir(parents=True, exist_ok=True)

	# Préparation du nom du fichier de log
	if log_file_name == None:

		execution_date = datetime.datetime.now()
		log_file_name = log_name + "_" + execution_date.strftime("%Y-%m-%d_%H-%M-%S") + ".log"

		# Suppression des fichiers de log en trop
		if regex_to_del == None:
			regex_to_del = '^' + log_name + '_.*\.log$'

	_limitFileNumber(
		log_directory, 
		(nb_of_log - 1), 
		regex_to_del
	)

	return dict(
		dir= log_directory,
		filename= log_file_name
	)



class _color_formatter(logging.Formatter):
	"""Ajoute de la couleur aux message renvoyés par le logger dans la sortie
	
	Adapté de l'article https://alexandra-zaharia.github.io/posts/make-your-own-custom-color-formatter-with-python-logging/
	Code couleur : https://www.lihaoyi.com/post/BuildyourownCommandLinewithANSIescapecodes.html"""

	reset = '\x1b[0m'

	def __init__(self, 
		fmt: str
	):
		super().__init__()
		self.fmt = fmt
		self.FORMATS = {
			# DEBUG = gris
			logging.DEBUG: '\x1b[38;5;238m' + self.fmt + self.reset,
			# INFO = gris clair
			logging.INFO: '\x1b[38;5;10m' + self.fmt + self.reset,
			# WARNING = bleu
			logging.WARNING: '\x1b[38;5;39m' + self.fmt + self.reset,
			# ERROR = rouge
			logging.ERROR: '\x1b[31m' + self.fmt + self.reset,
			# CRITICAL = blanc gras sur fond rouge
			logging.CRITICAL: '\x1b[41;1m' + self.fmt + self.reset
		}

	def format(self, record):
		log_fmt = self.FORMATS.get(record.levelno)
		formatter = logging.Formatter(log_fmt)
		return formatter.format(record)



def _handler_filter_1(
	nom_sortie: str
):
	"""Permet de filtrer les messages loggées par un handler
	"""

	# Création d'une fonction de filtre
	def handler_filter(record: logging.LogRecord):
		# Si on possède l'attribut supplémentaire ("extra") "sortie"
		if hasattr(record, 'sortie'):
			# Le message n'est récupéré que si l'attribut "sortie" est égal à la valeur définie pour le handler
			if record.sortie != nom_sortie:
				return False
		return True

	return handler_filter
