# scanner.py

from enum import Enum, auto, unique


def scan_error(line: int, msg: str):
	global hadError
	hadError = True
	print(f"Error on line: {line}. {msg}")


@unique
class TokenType(Enum):
	def _generate_next_value_(name, start, count, last_values):
		# implements "auto"....
		return count

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
	GREATER = '>'
	GREATER_EQUAL = '>='
	LESS = '<'
	LESS_EQUAL = '<='

	QUESTION = '?'
	COLON = ':'

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
	def __init__(self, ttype: TokenType, lexeme: str, literal, line: int, lineloc: slice = slice(0)):
		# TODO use a slice object for token Position
		self.ttype = ttype
		self.lexeme = lexeme
		self.literal = literal   # in the java version , this is type "object"
		# lexeme vs literal?
		# for example in a string the literal is "asfd" (with quotes)
		# the lexeme is just the asdf (no quote marks)
		self.line = line
		self.lineloc = lineloc
		# i dunno why -1? imma use slice objects anyways...

	def __str__(self):
		tname = str(self.ttype)[10:] # drop the substring 'TokenType.'
		return f"[{tname} '{self.lexeme}' `{self.literal}`]"

	def detail_pos(self):
		return f"on line {self.line}:{self.lineloc.start}-{self.lineloc.stop}"


def isalpha(c):
	v = ord(c) if len(c) == 1 else 0
	return len(c) == 1 and (
		65 <= v <= 90 or   # A, Z
		97 <= v <= 122 or # a, z
		v == 95)  # _

def isdigit(c):
	return len(c) == 1 and 48 <= ord(c) <= 57


class Scanner():
	def __init__(self, source: str):
		self.source = source
		self.tokens: list[TokenType] = list()
		# position
		self.start = 0
		self.current = 0
		self.line = 1

	@property
	def pos_slice(self):
		return slice(self.start, self.current)

	def advance(self):
		if self.allDone(): return ''
		char = self.source[self.current]
		self.current += 1
		return char

	def match(self, expected: str):
		assert len(expected) == 1
		if self.allDone(): return False
		if self.source[self.current] != expected:
			return False
		else:
			self.current += 1
			return True

	def peek(self):
		if not self.allDone():
			return self.source[self.current]
		else:
			return ''

	def peekNext(self):
		if not self.current+1 >= len(self.source):
			return self.source[self.current+1]
		else:
			return ''

	def allDone(self):  # renamed from "isAtEnd"
		return self.current >= len(self.source)

	def scanTokens(self):
		while not self.allDone():
			self.start = self.current
			self.scanToken()

		self.tokens.append(Token(TokenType.EOF, "", None, self.line))
		return self.tokens

	def scanToken(self):
		char = self.advance()
		try:
			match ttype := TokenType(char):
				case TokenType.BANG:
					ttype = TokenType.BANG_EQUAL if self.match('=') else TokenType.BANG
				case TokenType.EQUAL:
					ttype = TokenType.EQUAL_EQUAL if self.match('=') else TokenType.EQUAL
				case TokenType.GREATER:
					ttype = TokenType.GREATER_EQUAL if self.match('=') else TokenType.GREATER
				case TokenType.LESS:
					ttype = TokenType.LESS_EQUAL if self.match('=') else TokenType.LESS
				case TokenType.SLASH:
					if self.match('/'):
						while self.peek() != '\n' and not self.allDone():
							self.advance()
						return  # don't add any tokens in this case

			self.addToken(ttype)

		except ValueError:
			# ttype = None
			match char:
				case ' ':
					pass
				case '\r':
					pass
				case '\t':
					pass
				case '\n':
					self.line +=1

				case '"':
					# why new method for this...?
					while self.peek() != '"' and not self.allDone():
						if self.peek() == '\n':
							self.line += 1
						self.advance()

					if self.allDone():
						scan_error(self.line, f'Infinite string?')  # must. figure. error. shit.

					str_end = self.advance()
					assert str_end == '"'

					str_value = self.source[self.pos_slice]
					self.addToken(TokenType.STRING, literal=str_value[1:-1])
				case _:
					if isdigit(char):
						# number() function
						while isdigit(self.peek()):
							self.advance()

						if self.peek() == '.' and isdigit(self.peekNext()):
							self.advance()
							while isdigit(self.peek()):
								self.advance()

						self.addToken(TokenType.NUMBER, literal=float(self.source[self.pos_slice]))
					elif isalpha(char):
						# identifier() function
						"""
						while isalpha(self.peek()) or isdigit(self.peek()):
							self.advance()
						"""
						while c := self.peek():
							if isalpha(c) or isdigit(c):
								self.advance()
							else:
								break

						literal = self.source[self.pos_slice]
						try:
							ttype = TokenType(literal)
						except ValueError:
							ttype = TokenType.IDENTIFIER
							#stabilize the 'literal' (symbol?) name of IDENTIFIER?
							literal = literal.lower()
						self.addToken(ttype, literal=literal)
					else:
						scan_error(self.line, f'Unexpected character "{char}" '
						f'on line {self.line}:{self.pos_slice.start}-{self.pos_slice.stop}')


	def addToken(self, ttype: TokenType, literal=None):
		assert isinstance(ttype, TokenType)
		text = self.source[self.pos_slice]
		# is this too much pre-emptive compute?
		# this won't work for multiline
		token = Token(ttype, lexeme=text, literal=literal, line=self.line, lineloc=self.pos_slice)
		self.tokens.append(token)
