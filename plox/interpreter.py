# interpreter

from scanner import Token, TokenType
from environment import Environment
from expressions import *
from statements import *

from util import Visitor, Visitable

global hadError

class InterpreterError(RuntimeError):
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

class Interpreter(Visitor):
	str_visitor = StmtVisitor()
	environment = Environment()

	def interpret(self, expr: Visitable):
		assert isinstance(expr, Visitable), f'expr is {expr.__class__}'
		try:
			val = self.evaluate(expr)
			return val
		except InterpreterError as e:
			parse_error(e.token, e.msg)

	def evaluate(self, expr):  # AKA execute
		return expr.accept(visitor=self)

	def visitStmtExpr(self, stmt):
		val = self.evaluate(stmt.expr)
		# print("# ", stmt.accept(visitor=self.str_visitor))  # print anyways, with a '# '
		# print("#->", val)  # print anyways, with a '# '
		return val

	def visitStmtPrint(self, stmt):
		val = self.evaluate(stmt.expr)
		print(val)
		return val

	def visitStmtVar(self, stmt):
		"""
		stmt.name
		stmt.initializer
		"""
		assert isinstance(stmt, StmtVar), f'Oops, found instance of: {stmt.__class__}'
		value = self.evaluate(stmt.initializer) if stmt.initializer is not None else None
		self.environment.define(stmt.name.lexeme, value)

	def visitLiteral(self, expr):
		return expr.value

	def visitGrouping(self, expr):
		return self.evaluate(expr.expr)

	def visitUnary(self, expr):
		assert isinstance(expr.op, Token)
		assert isinstance(expr.right, Expr)
		r = self.evaluate(expr.right)

		match expr.op.ttype:
			case TokenType.MINUS:
				return -1 * float(r) # wut
			case TokenType.BANG:
				"""private boolean isTruthy(Object object) {
					if (object == null) return false;
					if (object instanceof Boolean) return (boolean)object;
					return true;
				}"""
				return not r
		#unreachable "return None"

	def visitBinary(self, expr):
		assert isinstance(expr.op, Token)
		assert isinstance(expr.left, Expr)
		assert isinstance(expr.right, Expr)

		l = self.evaluate(expr.left)
		r = self.evaluate(expr.right)

		match expr.op.ttype:
			case TokenType.MINUS:
				return float(l) - float(r)
			case TokenType.SLASH:
				return float(l) / float(r)
			case TokenType.STAR:
				return float(l) * float(r)
			case TokenType.PLUS:
				# "it's a little special, the strings and numbers..." but LOL.PYTHON
				return float(l) + float(r)

			case TokenType.GREATER:
				return l > r
			case TokenType.GREATER_EQUAL:
				return l >= r
			case TokenType.LESS:
				return l < r
			case TokenType.LESS_EQUAL:
				return l <= r

			case TokenType.BANG_EQUAL:  #maybe 'is' and 'is not' ?? what kind of equality is this?
				return l != r
			case TokenType.EQUAL_EQUAL:
				return l == r
		#unreachable "return None"

	def visitTernary(self, expr):
		# assert isinstance(expr.comparison, ??? and somehow assert it's boolean
		assert isinstance(expr.left, Expr)
		assert isinstance(expr.right, Expr)

		if self.evaluate(expr.comparison):
			return self.evaluate(expr.left)
		else:
			return self.evaluate(expr.right)
		# this feels a bit silly

	def visitVariable(self, expr):
		assert isinstance(expr, Variable), f'Oops, found instance of: {expr.__class__}'
		assert isinstance(expr.name, Token), f'Oops, found instance of: {expr.__class__}'
		assert isinstance(expr.name.lexeme, str), f'Oops, found instance of: {expr.__class__}'
		try:
			var_value = self.environment[expr.name]
		except KeyError:# as e:
			raise InterpreterError(expr.name, f"Undeclared variable.")
		if var_value is None:
			raise InterpreterError(expr.name, f"Variable without a value.")
		return self.environment[expr.name]

	def visitAssign(self, expr):
		assert isinstance(expr, Assign), f'Oops, found instance of: {expr.__class__}'
		value = self.evaluate(expr.value)
		self.environment[expr.name] = value
		return value

	def visitBlock(self, stmt: Block):
		print('BLOCK into ', self.environment)
		self.runBlock(stmt.statements, Environment(enclosing=self.environment))

	def visit(self, expr):
		print(f"\t!!Guessing what to do with {expr.__class__.__name__}")
		return str(expr)

	#...
	def runBlock(self, stmts: list, env: Environment):
		above_orig_env = self.environment
		self.environment = env
		try:
			for stmt in stmts:
				self.evaluate(stmt)
		finally:
			self.environment = above_orig_env
