# environment

import scanner

class Environment(dict):
	""" a stack of dicts"""

	def __init__(self, *args, enclosing=None, **kwargs):
		dict.__init__(self, *args, **kwargs)
		self.enclosing = enclosing

	def __str__(self):
		s = dict.__str__(self)
		if self.enclosing is not None:
			s += '\n\tEnv'
			s+= str(self.enclosing)

		return s

	def define(self, key: scanner.Token, value=None):
		if dict.__contains__(self, key.lexeme):
			raise KeyError("cannot define the same thing twice. do a regular assign")
		dict.__setitem__(self, key.lexeme, value)

	def __getitem__(self, key: scanner.Token):
		assert isinstance(key, scanner.Token), f"Enviroment's key must be a token, not a {key.__class__}"

		try:
			return dict.__getitem__(self, key.lexeme)
		except KeyError as e:
			if self.enclosing is not None:
				return self.enclosing[key]
			else:
				raise e

	def __setitem__(self, key: scanner.Token, val) -> None:
		assert isinstance(key, scanner.Token), f"Enviroment's key must be a token, not a {key.__class__}"

		if dict.__contains__(self, key.lexeme):
			dict.__setitem__(self, key.lexeme, val)
			return

		if self.enclosing is not None:
			self.enclosing[key] = val
			return

		raise KeyError

	def __delitem__(self, key: scanner.Token):
		del self[key]

	def __contains__(self, key) -> bool:
		if not isinstance(key, scanner.Token):
			return False

		return (dict.__contains__(self, key.lexeme)
			or (key in self.enclosing if self.enclosing is not None else False))


'''
tvar = scanner.Token(scanner.TokenType.IDENTIFIER, "a", "a", 0)
bvar = scanner.Token(scanner.TokenType.IDENTIFIER, "b", "b", 10)
top = Environment()
sub1 = Environment(enclosing=top)
sub2 = Environment(enclosing=sub1)

# top.define(tvar, "TOP")
# sub2.define(bvar, "bot000")

'''
