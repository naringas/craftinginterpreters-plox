# environment

import scanner

class Environment(dict):
	""" a stack of dicts"""

	def __init__(self, *args, enclosing=None, **kwargs):
		dict.__init__(self, *args, **kwargs)
		self.enclosing = enclosing

	def __str__(self):
		if self.enclosing is not None:
			s = 'SupEnv'
			s+= dict.__str__(self.enclosing)
			s += '\n\tEnv'
			s+= dict.__str__(self)
			return s
		else:
			return 'Env' + dict.__str__(self)

	def define(self, name: str, value=None):
		assert isinstance(name, str), "Enviroment variable name must be a string"
		# print ('!!!DEBUG set ', name, ' to ', value)
		dict.__setitem__(self, name, value)

	def __getitem__(self, key: scanner.Token):
		assert isinstance(key, scanner.Token), f"Enviroment's key must be a token, not a {key.__class__}"
		# strage... the keys are strings, but set as tokens? or smthin
		try:
			return dict.__getitem__(self, key.lexeme)
		except KeyError as e:
			if self.enclosing is not None:
				return self.enclosing[key]
			else:
				raise e

	def __setitem__(self, key: scanner.Token, val):
		assert isinstance(key, scanner.Token), f"Enviroment's key must be a token, not a {key.__class__}"
		return dict.__setitem__(self, key.lexeme, val)

	def __delitem__(self, key):
		del self[key]

	def __contains__(self, key: scanner.Token):
		assert isinstance(key, scanner.Token), f"Enviroment's key must be a token, not a {key.__class__}"
		try:
			return dict.__contains__(self, key.lexeme)
		except KeyError as e:
			if self.enclosing is not None:
				return key in self.enclosing
			else:
				raise e
