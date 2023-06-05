# plox errors.py

from scanner import Token
from parser import ParserError  #get all errors in this mod


class InterpreterError(RuntimeError):
	def __init__(self, token: Token, msg: str, *args, **kwargs):
		assert isinstance(token, Token)
		self.token = token
		self.msg = msg
		return super().__init__(self, *args, **kwargs)


class Return(RuntimeError):
	def __init__(self, value=None):
		self.value = value

