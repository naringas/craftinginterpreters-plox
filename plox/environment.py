# environment

import scanner

class Environment(dict):
	""" a tree of dicts"""

	def __init__(self, *args, enclosing=None, **kwargs):
		dict.__init__(self, *args, **kwargs)
		self.enclosing = enclosing

	def define(self, name: str, value=None):
		assert isinstance(name, str), "Enviroment variable name must be a string"
		# print ('!!!DEBUG set ', name, ' to ', value)
		dict.__setitem__(self, name, value)

	def assign(self, name, value):
		if name in self:
			return dict.__setitem__(self, name, val)
		else:
			raise KeyError

	def __getitem__(self, key: scanner.Token):
		assert isinstance(key, scanner.Token), f"Enviroment's key must be a token, not a {key.__class__}"
		# strage... the keys are strings, but set as tokens? or smthin
		try:
			return dict.__getitem__(self, key.lexeme)
		except KeyError as e:
			if self.enclosing is not None:
				return self.enclosing[key.lexeme]
			else:
				raise e

	def __setitem__(self, key: scanner.Token, val):
		assert isinstance(key, scanner.Token), f"Enviroment's key must be a token, not a {key.__class__}"
		return dict.__setitem__(self, key.lexeme, val)

	def __contains__(self, key: scanner.Token):
		assert isinstance(key, scanner.Token), f"Enviroment's key must be a token, not a {key.__class__}"
		return dict.__contains__(self, key.lexeme)
