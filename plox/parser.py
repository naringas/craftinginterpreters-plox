# parser.py
import pdb

from typing import Optional

from scanner import Token, TokenType
from expressions import * #Binary, Grouping, Literal, Unary
from statements import * #Stmt, StmtExpr, StmtPrint, StmtVar, Block
from util import Visitor

global hadError

class ParserError(RuntimeError):
	def __init__(self, token: Token, msg: str, *args, **kwargs):
		assert isinstance(token, Token)
		self.token = token
		self.msg = msg
		return super().__init__(self, *args, **kwargs)


def parse_error(token: Token, msg: str):
	hadError = True
	if token.ttype == TokenType.EOF:
		print(f'Error at line {token.line} at end.', msg)
	else:
		print(f'Error at line {token.detail_pos()} "{token.lexeme}".', msg);


class Parser():
	def __init__(self, tokens: list[Token]):
		self.tokens = tokens
		self.current : int = 0

	# Navigation
	def advance(self) -> Token:
		if not self.allDone():
			self.current += 1
		return self.previous()

	def consume(self, ttype, msg) -> Token:
		if self.check(ttype):
			return self.advance()
		else:
			raise ParserError(self.peek(), msg)

	def match(self, *ttypes) -> bool:
		for t in ttypes:
			if self.check(t):
				self.advance()
				return True
		return False

	def check(self, ttype) -> bool:
		if self.allDone():
			return False
		return self.peek().ttype == ttype

	def allDone(self) -> bool:
		return self.peek().ttype == TokenType.EOF

	def peek(self) -> Token:
		return self.tokens[self.current]

	def previous(self) -> Token:
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

	# the parsing itself:
	"""
	program        → declaration* EOF ;
	declaration    → (varDecl | funDecl | statement) ;

	varDecl        → "var" IDENTIFIER  ("=" expression)? ";" ;
	funDecl        → "fun" IDENTIFIER  "(" parameters? ")" ";" ;
	parameters     → IDENTIFIER ( "," IDENTIFIER )* ;     // a list of IDENTIFIERS

	statement      → exprStmt
	               | forStmt
	               | ifStmt
	               | printStmt
	               | whileStmt
	               | block ;
	exprStmt       → expression ";" ;                     // a grouping-alike
	forStmt        → "for" "("
	                    (varDecl | exprStmt | ";")
	                    expression? ";"
	                    expression? ")" statement ;
	printStmt      → "print" expression ";" ;
	ifStmt         → "if" "(" expression ")" statement ("else" statement)? ;
	whileStmt      → "while" "(" expression ")" statement ;
	block          → "{" declaration* "}"

	expression     → assignment ;
	assignment     → IDENTIFIER "=" assignment
	               | logic_or ;

	logic_or       → logic_and ( "or" logic_and )* ;
	logic_and      → equality ( "and" equality )* ;
	equality       → comparison ( ( "!=" | "==" ) comparison )* ;
	comparison     → term ( ( ">" | ">=" | "<" | "<=" ) term )* ;
	term           → factor ( ( "-" | "+" ) factor )* ;
	factor         → unary ( ( "/" | "*" ) unary )* ;
	unary          → ( "!" | "-" ) unary | call ;
	call           → primary ( "(" arguments? ")" )* ;
	arguments      → expression ( "," expression )* ;
	primary        → NUMBER | STRING | "true" | "false" | "nil"
	               | "(" expression ")"
	               | IDENTIFIER ;
	"""

	def parse(self) -> list[Stmt]:
		"""public endpoint method"""
		statements = []
		while not self.allDone():
			decl = self.declaration()
			if decl is not None:
				statements.append(decl)
		return statements

	def declaration(self) -> Stmt|None:
		try:
			if self.match(TokenType.VAR):
				return self.varDecl()
			return self.statement()
		except ParserError as e:
			parse_error(self.peek(), e.msg)
			self.synchronize()
		return None # wtf mypy... make the None explicit.ffs #Stmt()  #the "null" Stmt

	def varDecl(self) -> StmtVar:
		name: Token = self.consume(TokenType.IDENTIFIER, "Expect varirable name.")
		initer: Expr|None = None
		if self.match(TokenType.EQUAL):
			initer = self.expression()

		self.consume(TokenType.SEMICOLON, "Expected ; after variable declaration.")
		return StmtVar(name, initer)

	def statement(self) -> Stmt:
		if self.match(TokenType.FOR): return self.forStatement()
		if self.match(TokenType.IF): return self.ifStatement()
		if self.match(TokenType.PRINT): return self.printStmt()
		if self.match(TokenType.WHILE): return self.while_()
		if self.match(TokenType.LEFT_BRACE): return Block(self.block())
		return self.expressionStmt()

	def forStatement(self) -> Stmt:
		# de-sugaring into while
		self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'for'.")

		# initializer
		initializer : Optional[Stmt] = None
		if self.match(TokenType.SEMICOLON):
			initializer = None  #null or void or empty Stmt
		elif self.match(TokenType.VAR):
			initializer = self.varDecl()
		else:
			initializer = self.expressionStmt()

		condition = None
		if not self.check(TokenType.SEMICOLON):
			condition = self.expression()
		self.consume(TokenType.SEMICOLON, "Expect ';' after loop condition.")

		increment = None
		if not self.check(TokenType.RIGHT_PAREN):
			increment = self.expression()
		self.consume(TokenType.RIGHT_PAREN, "Expect ')' after 'for' clauses.")

		# print('!! init\n\t', StmtVisitor().start_walk(initializer if initializer is not None else Stmt()))
		# print('!! cond\n\t', AstPrinter().start_walk(condition if condition is not None else Expr()))
		# print('!! incr\n\t', AstPrinter().start_walk(increment if increment is not None else Expr()))
		body: Stmt = self.statement()

		# print('!! origi body\n\t', StmtVisitor().start_walk(body))

		if increment is not None:
			body = Block([body, StmtExpr(increment)])

		if condition is None:
			condition = Literal(True)
		body = StmtWhile(condition, body)

		if initializer is not None:
			body = Block([initializer, body])

		# print('\n!! body', StmtVisitor().start_walk(body), '\nendbody')
		return body

	def ifStatement(self) -> StmtIf:
		self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'.")
		cond : Expr = self.expression()
		self.consume(TokenType.RIGHT_PAREN, "Expect ')' after 'if'.")

		thenBranch = self.statement()
		if self.match(TokenType.ELSE):
			elseBranch = self.statement()
			return StmtIf(cond, thenBranch, elseBranch)
		else:
			return StmtIf(cond, thenBranch, None)

	def printStmt(self) -> StmtPrint:
		if self.match(TokenType.SEMICOLON):
			# `print ;`  printing nothing case...
			return StmtPrint(Expr())
		else:
			val = self.expression()
			self.consume(TokenType.SEMICOLON, "expected a ';' after printStmt. where is my  ; !?")
			return StmtPrint(val)
		# assert isinstance(val, Expr), f'val is {val.__class__}'

	def while_(self) -> StmtWhile:
		self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'while'.")
		cond = self.expression()
		self.consume(TokenType.RIGHT_PAREN, "Expect ')' after 'while'.")
		body = self.statement()

		return StmtWhile(cond, body)

	def block(self) -> list[Stmt]:
		stmts = []
		while not self.check(TokenType.RIGHT_BRACE) and not self.allDone():
			decl = self.declaration()
			if decl is not None:
				stmts.append(decl)

		self.consume(TokenType.RIGHT_BRACE, "expected closing '}'.")
		return stmts

	def expressionStmt(self) -> StmtExpr:
		val : Expr = self.expression()
		self.consume(TokenType.SEMICOLON, "expected a ';' after expressionStmt.")
		return StmtExpr(val)

	def expression(self) -> Expr:
		return self.assignment()

	def assignment(self) -> Expr:
		expr = self.or_()
		if self.match(TokenType.EQUAL):
			equals: Token = self.previous()
			val = self.assignment()

			if isinstance(expr, Variable):
				name: Token = expr.name
				return Assign(name, val)
			else:
				parse_error(equals, "Invalid assignment target.")
		return expr

	def or_(self) -> Expr:
		expr = self.and_()

		while self.match(TokenType.OR):
			op : Token = self.previous()
			right = self.and_()
			expr = Logical(expr, op, right)

		return expr

	def and_(self) -> Expr:
		expr = self.equality()

		while self.match(TokenType.AND):
			op = self.previous()
			right = self.equality()
			expr = Logical(expr, op, right)

		return expr

	def equality(self) -> Expr:
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
		# return self.call() # NOTYET
		return self.primary()

	def call(self) -> Expr:
		expr: Expr = self.primary()

		while True:
			if self.match(TokenType.LEFT_PAREN):
				expr = self.finishCall(expr)
			else:
				break
		return expr

	def finishCall(self, callee: Expr):
		arguments : list[Expr] = []
		if not self.check(TokenType.RIGHT_PAREN):
			arguments.append(self.expression())
			while self.match(TokenType.COMMA):
				arguments.append(self.expression())
				if len(arguments) >= 255:
					raise ParserError(self.peek(), "Can't have more than 255 arguments.")
		paren: Token = self.consume(TokenType.RIGHT_PAREN, "Expect ')' after arguments.")

		return Call(callee, paren, arguments)

	def primary(self) -> Expr:
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

		parse_error(self.peek(), f"Expected more input... near {self.peek()} token#{self.current}")
		if self.match(TokenType.SEMICOLON):
			raise ParserError(self.peek(), "a lone ';' is a syntax error?")
		return Expr()  #null or empty expression.
		'''
			return Expr()  # the void or empty or null expression

		try:
			raise ParserError(self.peek(), "Expected more input...")
		except ParserError:
			import pdb
			pdb.set_trace()
			raise
		'''
