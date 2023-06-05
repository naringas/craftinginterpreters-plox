# plox_lib.py

import time

from environment import Environment
from statements import StmtFun
from util import PloxCallable, Visitor
from interpreter import Return

class clock(PloxCallable):
	@property
	def arity(self) -> int:
		return 0

	def call(self, interpreter, args: list):
		return time.time()

	def __str__(self):
		return "<native clock fn>"


class PloxFunction(PloxCallable):
	"""Code (user) defined funcion
	"""
	def __init__(self, stmt: StmtFun, closure: Environment):
		self.stmt : StmtFun = stmt
		self._arity = len(self.stmt.params)
		self.closure = closure  # en-CLOSURE environment where function got declared
	@property
	def arity(self):
		return self._arity
	'''
	'''

	def call(self, interpreter, args):
		func_env = Environment(enclosing=self.closure)
		for i, param in enumerate(self.stmt.params):
			try:
				val = args[i]
			except IndexError:
				val = None
			func_env.define(param, val)
		try:
			interpreter.runBlock(self.stmt.body, func_env)
		except Return as ret:
			return ret.value
		# return None

	def __str__(self):
		return f'<fun {self.stmt.name.lexeme}/{self.arity}>'
