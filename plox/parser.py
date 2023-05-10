# parser.py

from scanner import Token, TokenType
from expressions import * #Binary, Grouping, Literal, Unary
from statements import * #Stmt, StmtExpr, StmtPrint, StmtVar


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

			if self.peek().ttype in (
				TokenType.CLASS,
				TokenType.FUN,
				TokenType.VAR,
				TokenType.FOR,
				TokenType.IF,
				TokenType.WHILE,
				TokenType.PRINT,
				TokenType.RETURN,
			):
				return

			self.advance()


class Parser(ParserNav):
	"""
	program        → declaration* EOF ;
	declaration    → (varDecl | statement) ;

	varDecl        → "var" IDENTIFIER ( "=" expression )? ";" ;
	statement      → (exprStmt | printStmt) ;
	exprStmt       → expression ";" ;
	printStmt      → "print" expression ";" ;

	expression     → equality |
	                 ternary ;
	ternary        → equality "?" expression ":" expression ;
	equality       → comparison ( ( "!=" | "==" ) comparison )* ;
	comparison     → term ( ( ">" | ">=" | "<" | "<=" ) term )* ;
	term           → factor ( ( "-" | "+" ) factor )* ;
	factor         → unary ( ( "/" | "*" ) unary )* ;
	unary          → ( "!" | "-" ) unary
	               | primary ;
	primary        → NUMBER | STRING | "true" | "false" | "nil"
	               | "(" expression ")"
	               | IDENTIFIER ;
	"""

	def __init__(self, tokens: list[Token]):
		self.tokens = tokens
		self.current = 0

	def parse(self):
		"""public endpoint method"""
		statements = []
		while not self.allDone():
			statements.append(self.declaration())
		return statements

	def declaration(self):
		try:
			if self.match(TokenType.VAR):
				return self.varDecl()
			return self.statement()
		except ParserError as e:
			parse_error(self.peek(), e.msg)
			self.synchronize()
			return

	def varDecl(self):
		name: Token = self.consume(TokenType.IDENTIFIER, "Expect varirable name.")
		initer = None
		if self.match(TokenType.EQUAL):
			initer: Expr = self.expression()

		self.consume(TokenType.SEMICOLON, "Expected ; after variable declaration.")
		return StmtVar(name, initer)

	def statement(self):
		if self.match(TokenType.PRINT):
			return self.printStmt()
		else:
			return self.expressionStmt()

	def printStmt(self):
		if self.match(TokenType.SEMICOLON):
			# `print ;`  printing nothing case...
			return StmtPrint(Expr())
		else:
			val = self.expression()
			self.consume(TokenType.SEMICOLON, "expected a ';' after printStmt. where is my  ; !?")
			return StmtPrint(val)
		# assert isinstance(val, Expr), f'val is {val.__class__}'

	def expressionStmt(self):
		val = self.expression()

		# if val is None:
			# val = Expr()
			# next assert is now guaranteed... lame
		assert isinstance(val, (Stmt, Expr)), f"{val}. repr: `"+repr(val)+"`"

		self.consume(TokenType.SEMICOLON, "expected a ';' after expressionStmt. where is my  ; !?")
		return StmtExpr(val)

	def expression(self):
		"""
		expression → equality |
		             ternary ;
		"""
		eq = self.equality()

		if self.match(TokenType.QUESTION):
			left = self.expression()
			self.consume(TokenType.COLON, "Expected ':' for a ternary expr.")
			right = self.expression()
			return Ternary(eq, left, right)
		else:
			return eq

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

		if self.match(TokenType.IDENTIFIER):
			return Variable(self.previous())

		"""
		if self.previous().ttype == TokenType.EOF:
			# Y we no done?
			return Expr()
		"""
		if self.match(TokenType.SEMICOLON):
			return Stmt()
		if self.match(TokenType.EOF):
			return Expr()  # the void or empty or null expression

		parse_error(self.peek(), "In the end, we expected more INPUT...")
		# raise ParserError(self.peek(), "Expected more...")
