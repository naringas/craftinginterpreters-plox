# plox_lib.py

import time

from util import PloxCallable


class clock(PloxCallable):
	@property
	def arity(self) -> int:
		return 0

	def call(self, interpreter, args: list):
		return time.time()

	def __str__(self):
		return "<native clock fn>"
