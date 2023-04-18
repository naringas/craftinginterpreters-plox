from enum import Enum, auto, unique


@unique
class TokenType(Enum):
	# // Single-character tokens.
	LEFT_PAREN = '('
	RIGHT_PAREN = ')'
	LEFT_BRACE = '['
	RIGHT_BRACE = ']'

	COMMA = ','
	DOT = '.'
	MINUS = '-'
	PLUS = '+'
	SEMICOLON = ';'
	SLASH = '/'
	STAR = '*'

	# // One or two character tokens.
	BANG = '!'
	BANG_EQUAL = '!='
	EQUAL = '='
	EQUAL_EQUAL = '=='
	GREATER = '<'
	GREATER_EQUAL = '<='
	LESS = '>'
	LESS_EQUAL = '>='

	# // Literals.
	IDENTIFIER = auto()
	STRING = auto()
	NUMBER = auto()
	# // Keywords.
	AND = 'and'
	CLASS = 'class'
	ELSE = 'else'
	FALSE = 'false'
	FUN = 'fun'
	FOR = 'for'
	IF = 'if'
	NIL = 'nil'
	OR = 'or'
	PRINT = 'print'
	RETURN = 'return'
	SUPER = 'super'
	THIS = 'this'
	TRUE = 'true'
	VAR = 'var'
	WHILE = 'while'

	EOF = auto()


class Token():
	def __init__(self, ttype: TokenType, lexeme: str, literal, line: int, pos_start: int = None):
		# TODO use a slice object for token Position
		self.ttype = ttype
		self.lexeme = lexeme
		self.literal = literal   # in the java version , this is type "object"
		self.line = line
		self.pos_start = pos_start + 1 if pos_start else -1  # add one because the Scanner()'s first position is 0
		# i dunno why -1? imma use slice objects anyways...

	def __str__(self):
		return f"{self.ttype} {self.lexeme} {self.literal} on line {self.line}:{self.pos_start}"


class Scanner():
	def __init__(self, source: str):
		self.source = source
		self.tokens: list[TokenType] = list()

		# position
		self.start = 0
		self.current = 0
		self.line = 1

	def advance(self):
		char = self.source[self.current]
		self.current += 1
		return char

	def allDone(self):
		return self.current >= len(self.source)

	def scanTokens(self):
		while not self.allDone():
			self.start = self.current
			self.scanToken()

		self.addToken(Token(TokenType.EOF, "", None, self.line))

		# pythonic or "java"onic???
		return self.tokens

	def scanToken(self):
		char = self.advance()
		# bad for runtime
		for token in TokenType:
			if char == token.value:
				self.addToken(token)
		"""
		match char:
			case TokenType:  # must. re-use. TokenType definitions for matching
				pass
			case _:
				# how to 'pythonize' this? why not rely on built-in throws?
				raise Error
		"""

	def addToken(self, ttype: TokenType, literal=None):
		# TODO use a slice object for token Position
		text = self.source[self.start:self.current]
		token = Token(ttype, lexeme=text, literal=literal, line=self.line, pos_start=self.start)
		self.tokens.append(token)
