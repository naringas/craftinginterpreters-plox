# interpreter

from scanner import Token, TokenType
from expressions import *

from util import Visitor, Visitable


class Interpreter(Visitor):
	def interpret(self, expr: Visitable):
		assert isinstance(expr, Visitable), f'expr is {expr.__class__}'
		val = self.evaluate(expr)
		return val

	def evaluate(self, expr):
		return expr.accept(visitor=self)

	def visitStmtExpr(self, stmt):
		val = self.evaluate(stmt.expr)
		print("# ", val)  # print anyways, with a '# '
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
		...

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


	def visit(self, expr):
		print(f"\t!!Guessing what to do with {expr.__class__.__name__}")
		return str(expr)
