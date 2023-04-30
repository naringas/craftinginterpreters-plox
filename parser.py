# parser.py

from scanner import Token, TokenType
from expressions import * #Binary, Grouping, Literal, Unary


class ParserError(RuntimeError):
	def __init__(self, token: Token, msg: str, *args, **kwargs):
		assert isinstance(token, Token)
		self.token = token
		self.msg = msg
		return super().__init__(self, *args, **kwargs)


def parse_error(token: Token, msg: str):
	global hadError
	hadError = True
	if token.ttype == TokenType.EOF:
		print(f'Error at line {token.line} at end.', msg)
	else:
		print(f'Error at line {token.detail_pos()} "{token.lexeme}".', msg);


class ParserNav:
	def advance(self):
		if not self.allDone():
			self.current += 1
		return self.previous()

	def consume(self, ttype, msg):
		if self.check(ttype):
			return self.advance()
		else:
			raise ParserError(self.peek(), msg)

	def match(self, *ttypes):
		for t in ttypes:
			if self.check(t):
				self.advance()
				return True
		return False

	def check(self, ttype):
		if self.allDone():
			return False
		return self.peek().ttype == ttype

	def allDone(self):
		return self.peek().ttype == TokenType.EOF

	def peek(self):
		return self.tokens[self.current]

	def previous(self):
		return self.tokens[self.current - 1]

	def synchronize(self):
		"""error recovery"""
		self.advance()
		while not self.allDone():
			if self.previous().ttype == TokenType.SEMICOLON:
				return

			if self.peek().ttype in [
				TokenType.CLASS,
				TokenType.FUN,
				TokenType.VAR,
				TokenType.FOR,
				TokenType.IF,
				TokenType.WHILE,
				TokenType.PRINT,
				TokenType.RETURN]:
				return

			self.advance()


class Parser(ParserNav):
	"""
	expression     → equality ;
	equality       → comparison ( ( "!=" | "==" ) comparison )* ;
	comparison     → term ( ( ">" | ">=" | "<" | "<=" ) term )* ;
	term           → factor ( ( "-" | "+" ) factor )* ;
	factor         → unary ( ( "/" | "*" ) unary )* ;
	unary          → ( "!" | "-" ) unary
	               | primary ;
	primary        → NUMBER | STRING | "true" | "false" | "nil"
	               | "(" expression ")" ;
   """

	def __init__(self, tokens: list[Token]):
		self.tokens = tokens
		self.current = 0

	def parse(self):
		"""public endpoint method"""
		try:
			return self.expression()
		except ParserError as e:
			parse_error(e.token, e.msg)
			return None

	def expression(self):
		if self.match(TokenType.SLASH):
			return self.comment()
		return self.equality()

	def comment(self):
		return Comment(lexeme=self.previous().lexeme)

	def equality(self):
		expr = self.comparison()

		while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
			op = self.previous()
			right = self.comparison()
			expr = Binary(expr, op, right)
		return expr

	def comparison(self):
		expr = self.term()

		while self.match(TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS,
		TokenType.LESS_EQUAL):
			op = self.previous()
			right = self.term()
			expr = Binary(expr, op, right)
		return expr

	def term(self):
		expr = self.factor()

		while self.match(TokenType.MINUS, TokenType.PLUS):
			op = self.previous()
			right = self.factor()
			expr = Binary(expr, op, right)
		return expr

	def factor(self):
		expr = self.unary()

		while self.match(TokenType.SLASH, TokenType.STAR):
			op = self.previous()
			right = self.unary()
			expr = Binary(expr, op, right)
		return expr

	def unary(self):
		if self.match(TokenType.BANG, TokenType.MINUS):
			op = self.previous()
			right = self.unary()
			return Unary(op, right)
		return self.primary()

	def primary(self):
		if self.match(TokenType.FALSE):
			return Literal(False)
		if self.match(TokenType.TRUE):
			return Literal(True)
		if self.match(TokenType.NIL):
			return Literal(None)

		if self.match(TokenType.NUMBER, TokenType.STRING):
			return Literal(self.previous().literal)

		if self.match(TokenType.LEFT_PAREN):
			expr = self.expression()
			self.consume(TokenType.RIGHT_PAREN, "expect ')'")
			return Grouping(expr)

		parse_error(self.peek(), "Expected more...")
