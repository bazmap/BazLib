# -*-coding:Utf-8 -*

""" Diverses fonctions qui peuvent être bien pratiques
v1.0
De nombreuses fonction qui permettent de réaliser tout un tas d'opérations

Fonction
-------
coalesce() : 
	Renvoi du premier argument non nul

pretty_dict() :
	Formatage d'un dictionnaire en texte indenté

"""

# Modules requis
import argparse
import configparser
import copy
import datetime
import inspect
import logging
import os



# Renvoi du premier argument non nul
def coalesce(
	*args
):
	"""
		Renvoi du premier argument non nul.

		Parameters
		----------
		args: *args
			Succession d'arguments dont le premier non null sera renvoyé

		Returns
		-------
		any
			Le premier argument non null
	"""
	for arg in args:
		if arg is not None:
			return arg
	
	return None



# Formatage d'un dictionnaire en texte indenté
def pretty_dict(
	my_dict: dict,
	prefix: str = '',
	ident: str = '	',
):
	"""
		Renvoi du premier argument non nul.

		Parameters
		----------
		my_dict: dict
			Dictionnaire à parser
		prefix: str
			Préfixe à utiliser devant chaque clé, par défaut vide ''.
		ident: str
			Valeur à utiliser pour l'indentation, par défaut une tabulation '	'.

		Returns
		-------
		str
			Dictionnaire au format texte indenté
	"""

	return_value = ''

	for key, value in my_dict.items():
		return_value += '\n'
		if isinstance(value, dict):
			return_value += prefix + key + ' ' + str(type(value)) + ': {'
			return_value += pretty_dict(value, prefix , ident)
			return_value += '\n' + '}'

		else:
			return_value += ident + prefix + key + ' ' + str(type(value)) + ': ' + str(value)

	return return_value