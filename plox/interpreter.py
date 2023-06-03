# interpreter

from scanner import Token, TokenType
from environment import Environment
from expressions import *
from statements import *

import libplox
from util import PloxCallable, Visitable, Visitor

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

	def __init__(self):
		self.environment = Environment()
		self.globals = self.environment
		self.globals.define("clock", libplox.clock())

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

	def visitStmtVar(self, stmt: StmtVar):
		"""
		stmt.name
		stmt.initializer
		"""
		value = self.evaluate(stmt.initializer) if stmt.initializer is not None else None

		try:
			self.environment.define(stmt.name, value)
		except KeyError as e:
			raise InterpreterError(stmt.name, "Variable was already declared")

	def visitLiteral(self, expr: Literal):
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

	def visitStmtIf(self, stmt: StmtIf):
		if self.evaluate(stmt.condition):
			return self.evaluate(stmt.thenBranch)
		else:
			if stmt.elseBranch is not None:
				return self.evaluate(stmt.elseBranch)
		# this feels a bit silly

	def visitStmtWhile(self, stmt):
		while self.evaluate(stmt.condition):
			self.evaluate(stmt.body)

	def visitVariable(self, expr: Variable):
		assert isinstance(expr, Variable), f'Oops, found instance of: {expr.__class__}'
		assert isinstance(expr.name, Token), f'Oops, found instance of: {expr.__class__}'
		assert isinstance(expr.name.lexeme, str), f'Oops, found instance of: {expr.__class__}'
		try:
			var_value = self.environment[expr.name]
		except KeyError:# as e:
			raise InterpreterError(expr.name, f"Undeclared variable.")
		if var_value is None:
			raise InterpreterError(expr.name, f"Variable without a value.")

		return var_value

	def visitAssign(self, expr: Assign):
		assert isinstance(expr, Assign), f'Oops, found instance of: {expr.__class__}'

		value = self.evaluate(expr.value)
		try:
			self.environment[expr.name] = value
		except KeyError:
			raise InterpreterError(expr.name, f"Undeclared variable.")
		return value

	def visitBlock(self, stmt: Block):
		self.runBlock(stmt.statements, Environment(enclosing=self.environment))

	def visitLogical(self, expr: Logical):
		left = self.evaluate(expr.left)

		if expr.op.ttype == TokenType.OR:
			if left:
				return left
		elif expr.op.ttype == TokenType.AND:
			if not left:
				return left  # because it already is falsey
		return self.evaluate(expr.right)

	def runBlock(self, stmts: list, env: Environment):
		above_orig_env = self.environment
		self.environment = env
		try:
			for stmt in stmts:
				self.evaluate(stmt)
		finally:
			self.environment = above_orig_env

	def visitCall(self, expr: Call):
		callee: PloxCallable = self.evaluate(expr.callee)
		args = [self.evaluate(a) for a in expr.args]

		# TODO ensure callee is reall callable
		# assert isinstance(callee, PloxCallable)
		if len(args) != callee.arity:
			raise InterpreterError(expr.paren, "wrong argument count")
		return callee.call(interpreter=self, args=args)

	def visit(self, expr):
		raise NotImplementedError(f"know not what to do with {expr.__class__.__name__}")
		# print(f"\t!!Guessing what to do with {expr.__class__.__name__}")
		# return str(expr)
