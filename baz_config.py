# -*-coding:Utf-8 -*

""" Gestion des variables de configuration
v1.0
Interface de gestion des variables de configuration passées via des arguments ou des fichiers de configuration

Classes
-------
baz_config(
	logger: logging.Logger = None
) : 

	Classe de gestion des variables de configuration.

"""

# Modules requis
import argparse
import configparser
import copy
import datetime
import inspect
import logging
import os



# Création d'une classe pour gérer les variables de configuration
class baz_config():
	"""Classe de gestion des variables de configuration.

	Attributes
	----------
	logger: logging.Logger
		Logger utilisé pour logguer les messages de sortie des sous processus.
	software_info: dict
		Dictionnaire décrivant le programme (pour affichage de l'aide) contenant les clés suivantes :
			"name": nom du programme
			"version": version
			"resume": description du programme
			"author" : auteur
			"copyright": mention de copyright
	var_default: dict 
		Dictionnaire décrivant les variables disponibles par défaut. Chaque variable est décrite via un dictionnaire :
			'ma_variable': {
				'help_scope' : ['argument','config'], # Variable affichée dans l'aide
				'type' : 'str', # Type (au format Python : bool, str, int, float)
				'default_value' : 'Valeur initiale',
				'expected': 'Un texte au hasard', # Desciption de la valeur attendue
				'group': 'Groupe 1', # Groupe dans lequel la variable apparait dans le fichier de configuration
				'help' : 'Variable de démonstration numéro 1.' # Description de la variable
			}
	var_config_file: dict
		Liste des variables présentes dans le fichier de configuration chargé.
	var_arg: dict
		Liste des variables récupérées en argument.
	var_global: dict
		Fusion de toutes les variables avec l'ordre suivant :
			var_default
			var_config_file
			var_arg
		Si plusieurs fichiers de configurations sont appelés, leurs valeurs peuvent s'écraser entre-elle mais n'écraseront jamais une valeur passée en argument.

	Methods
	-------
	get_argument():
		Récupération des arguments.
	load_argument():
		Chargement des arguments dans les attributs de la classe.
	get_config_file():
		Récupération d'un fichier de configuration.
	load_config_file():
		Chargement d'un fichier de configuration dans les attributs de la classe.
	"""

	# Initialisation de la classe
	def __init__(
		self, 
		logger: any = None,
		software_info: dict = None,
		var_default: dict = None,
		load_arg: bool = True,
		load_config_file: bool = True
	):
		"""
			Initialisation d'une nouvelle instance de baz_conf.

			Parameters
			----------
			logger: logging.logger
				Objet logger permettant de logger ce qui se passe.
			software_info: dict
				Dictionnaire décrivant le programme (pour affichage de l'aide) contenant les clés suivantes :
					"name": nom du programme
					"version": version
					"resume": description du programme
					"author" : auteur
					"copyright": mention de copyright
			var_default: dict 
				Dictionnaire décrivant les variables disponibles par défaut. Chaque variable est décrite via un dictionnaire :
					'ma_variable': {
						'help_scope' : ['argument','config'], # Variable affichée dans l'aide
						'type' : 'str', # Type (au format Python : bool, str, int, float)
						'default_value' : 'Valeur initiale',
						'expected': 'Un texte au hasard', # Desciption de la valeur attendue
						'group': 'Groupe 1', # Groupe dans lequel la variable apparait dans le fichier de configuration
						'help' : 'Variable de démonstration numéro 1.' # Description de la variable
					}
			load_arg: bool 
				Chargement des arguments lors de l'initialisation
				False par défaut.
			load_config_file: bool
				Chargement des variables présentes dans le fichier de configuration lors de l'initialisation
				False par défaut.
		"""

		# Récupération et vérification des paramètres
		# Récupération d'un logger passé en paramètre sinon, utilisation du logger par défaut
		self.logger = logger if logger is not None else logging.getLogger()



		# Info par défaut sur le programme
		self.software_info = {
			"name": "BazLib",
			"version": "1.0",
			"resume": "Bibliothèque de modules Python simplifiant l'utilisation de modules standards et d'autres.",
			"author" : "Arthur Bazin",
			"copyright": "Arthur Bazin " + str(datetime.date.today().year)
		}

		if software_info is not None:
			self.software_info.update(software_info)



		# Argument présents par défaut avec la lib
		self.var_default = {
			'configFile': {
				'help_scope' : ['argument'],
				'type' : 'str',
				'default_value' : None,
				'value' : None,
				'expected': 'Chemin vers un fichier de configuration',
				'group': 'Général',
				'help' : "Fichier de configuration à utiliser. Par défaut, recherche un fichier nommé \"default.config\" dans le même répertoire que le fichier appelant la fonction. Notez que les valeurs passées en argument seront utilisées à la place de celles spécifiées dans le fichier de configuration."
			}
		}

		if var_default is not None:
			self.var_default.update(var_default)



		# Création de la variable globale
		self.var_global = copy.deepcopy(self.var_default)



		# Récupération des arguments
		if load_arg:
			self.load_argument()



		# Récupération des variables dans le fichier de conf
		if load_config_file:
			self.load_config_file()






	# Fonction de gestion des arguments
	def get_argument(
		self
	):
		"""
			Récupération des arguments.

			Returns
			-------
			boolean
				Renvoie vrai si les variables ont bien été chargées
		"""

		self.logger.info('Chargement des arguments')

		# Création d'un parser
		parser = argparse.ArgumentParser(
			description = 
				self.software_info['name'] + '\n' + 
				"Version : " + self.software_info['version'] + '\n' + 
				self.software_info['resume'],
			epilog = 
				"Merci d'utiliser ce programme" + '\n' + 
				self.software_info['author'] + " - " + self.software_info['copyright'],
			formatter_class=argparse.RawTextHelpFormatter,
			allow_abbrev=False
		)



		# Définition des arguments
		self.logger.debug('Définition des arguments')
		for key in self.var_default:

			# Récupération de la valeur par défaut pour l'argument
			if 'default_value' in self.var_default[key]:
				default_arg = str(self.var_default[key]['default_value'] or 'None')
			else:
				default_arg = 'None'



			# Définition de l'action
			if self.var_default[key]['type'] == 'boolean':
				action_arg = 'store_const'
				const_arg = not self.var_default[key]['default_value']
			else:
				action_arg = 'store'
				const_arg = None



			# Suppression de l'aide pour certains arguments
			# L'argument est donc toujours disponible si besoin mais n'est pas mentionné dans l'aide
			# Utile pour le débugage
			if 'argument' in self.var_default[key]['help_scope']:
				help_arg = (
					self.var_default[key]['help'] + ' \n' +
					'Valeur attendue : ' + self.var_default[key]['type'] + ' (- )' + str(self.var_default[key]['expected']) + ')\n' + 
					'Valeur par défaut : ' + default_arg
				)
			else:
				help_arg = argparse.SUPPRESS

			# Ajout des arguments
			parser.add_argument(
				'--' + key,
				action = action_arg,
				const = const_arg,
				default = self.var_default[key]['default_value'],
				help = help_arg
			)

		parser.add_argument(
			'--version', '-v',
			action = 'version',
			version = self.software_info['name'] + ' - v' + self.software_info['version'],
			help = "Version du script"
		)



		# Récupération des variables à utiliser
		self.logger.debug('Parsage des arguments')
		arg_var = dict()

		# Parsage des arguments
		parsed_arg, other_arg = parser.parse_known_args()

		self.logger.warning('Arguments non reconnus : ' + str(other_arg))

		for key, value in vars(parsed_arg).items():
			arg_var[key] = {
				'value' : value
			}

		return arg_var






	# Fonction de chargement des arguments
	def load_argument(
		self
	):
		"""
			Chargement des arguments dans les attributs de la classe.

			Returns
			-------
			boolean
				Renvoie vrai si les arguments ont bien été chargées
		"""

		self.logger.info('Chargement des arguments')

		# Récupération des variables dans le fichier de configuration
		self.var_arg = self.get_argument()



		# Fusion avec les variables par défaut
		self.merge_into_global(
			self.var_arg,
			'argument'
		)



		#Sortie
		if self.var_arg is not None:
			self.logger.debug('Arguments chargés')
			return True

		# Dans tous les autres cas on retourne False
		self.logger.warning('Arguments non chargés')
		return False






	# Fonction de récupération d'un fichier de configuration
	def get_config_file(
		self,
		file_path: str = None
	):
		"""
			Récupération d'un fichier de configuration.

			Parameters
			----------
			file_path: str
				Emplacement absolu du fichier à charger

			Returns
			-------
			dict
				Renvoie un dictionnaire contenant les variables récupérées
		"""

		# Emplacement du fichier de configuration
		# L'emplacement fourni en argument n'est ici pas prédominant.l'ordre respecté est le suivant :
		#	Emplacement fourni
		#	Emplacement fourni en argument
		#	Emplacement par défaut
		if file_path == None:

			# Test pour voir si le fichier de configuration est renseigné dans la variable globale
			# Par exemple défini via les arguments
			v = self.var_global.get('configFile')
			if (
				'configFile' in self.var_global
				and 'value' in self.var_global['configFile']
				and self.var_global['configFile']['value'] is not None
			):
				file_path = self.var_global['configFile']['value']

			else:

				self.logger.warning('Utilisation de l\'emplacement du fichier de configuration par défaut')

				fileStack = []

				# Inspection de la stack
				if __name__ != '__main__':
					for frame in inspect.stack()[1:]:
						if frame.filename[0] != '<':
							fileStack.append(frame.filename)

				# Fichier "default.config" recherché dans le même répertoire que le fichier appelant la fonction
				file_path = os.path.join(
					os.path.dirname(fileStack[-1]),
					'default.conf'
				)



		# Création d'un parser
		parser = configparser.ConfigParser(
			empty_lines_in_values=False,
			interpolation=configparser.ExtendedInterpolation()
		)

		# Ajout des booléens français
		parser.BOOLEAN_STATES.update(
			{
				'oui' : True,
				'Oui' : True,
				'OUI' : True,
				'non' : False,
				'Non' : False,
				'NON' : False
			}
		)

		# Conservation de la casse dans les noms de paramètre
		parser.optionxform = lambda option : option


		var_config = None

		# Lecture du fichier de configuration s'il existe
		if os.path.exists(file_path):
			parser.read(
				file_path,
				encoding='UTF-8'
			)

			# Création d'un dictionnaire qui va stocker les valeurs
			var_config = dict()

			# Récupération des valeurs de variable
			# Pour chaque section de paramètre
			for group in parser.sections():
				self.logger.debug('Groupe : ' + group)

				# Pour chaque variable du groupe
				for key in parser.options(group):
					self.logger.debug('	Option : ' + key)

					# Récupération des valeurs
					var_config[key] = dict(
						value = parser[group][key],
						group = group
					)

		else:
			self.logger.warning("Fichier de configuration non trouvé")

		# Renvoie des valeurs
		return var_config






	# Fonction de chargement d'un fichier de configuration
	def load_config_file(
		self,
		file_path: str = None
	):
		"""
			Chargement d'un fichier de configuration dans les attributs de la classe.

			Parameters
			----------
			file_path: str
				Emplacement absolu du fichier à charger

			Returns
			-------
			boolean
				Renvoie vrai si les variables ont bien été chargées
		"""

		self.logger.info('Chargement du fichier de configuration')

		# Récupération des variables dans le fichier de configuration
		self.var_config_file = self.get_config_file(file_path)



		# Fusion avec les variables par défaut
		self.merge_into_global(
			self.var_config_file,
			'config'
		)



		#Sortie
		if self.var_config_file is not None:
			self.logger.debug('Fichier de configuration chargé')
			return True

		# Dans tous les autres cas on retourne False
		self.logger.warning('Fichier de configuration non chargé')
		return False






	def merge_into_global(
		self,
		var_to_merge: dict = None,
		source: str = None
	):
		"""
			Fusion d'une variable dans la variable globale de paramétrage.

			Parameters
			----------
			var_to_merge: dict
				Variable à fusionner
			source: str
				Source de la variable à fusionner entre :
					'default' : poids = 0
					'config' : poids = 1
					'argument' : poids = 2
				Le poids permet de savoir si une valeur sera remplacée ou non dans la variable globale

			Returns
			-------
			boolean
				Renvoie True
		"""

		# Initialisation de la source de la valeur
		for key in self.var_global:
			if 'source' not in self.var_global[key]:
				self.var_global[key]['source'] = 'default'



		if var_to_merge is not None:
			for key in var_to_merge:
				if key not in self.var_global:
					self.var_global[key] = var_to_merge[key]
					self.var_global[key]['source'] = source
					self.var_global[key]['type'] = 'str'
					self.var_global[key]['default_value'] = var_to_merge[key]['value']

				else:
					if (
						self.var_global[key]['source'] == 'default'
						or (self.var_global[key]['source'] == 'config' and source != 'default')
						or source == 'argument'
					):

						self.var_global[key]['source'] = source
						self.var_global[key]['value'] = var_to_merge[key]['value']

						if 'group' in var_to_merge[key]:
							self.var_global[key]['group'] = var_to_merge[key]['group']

		return True