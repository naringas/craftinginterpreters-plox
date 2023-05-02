# expressions.py
from dataclasses import dataclass, fields

from scanner import Token, TokenType
from util import Visitable, Visitor


@dataclass
class Expr(Visitable):
	pass

@dataclass
class Binary(Expr):
	left: Expr
	op: Token
	right: Expr

@dataclass
class Grouping(Expr):
	expr: Expr

@dataclass
class Literal(Expr):
	value: object

@dataclass
class Unary(Expr):
	op: Token
	right: Expr

@dataclass
class Variable(Expr):
	name: Token  #identifier


class AstPrinter(Visitor):
	"""only good at printing out (and making strings) from binary expressions"""

	def printout(self, expr: Expr):
		assert isinstance(expr, Expr), f'expr is not a Expr, but a {expr.__class__}'
		print('\nAST print')
		print(expr.accept(visitor=self))

	def parensiffy(self, name, *exprs):
		if len(exprs) >= 1 and exprs[0] is None:
			return '()'
		s = f'({name} '
		try:
			s += ' '.join((exp.accept(visitor=self) for exp in exprs))
		except AttributeError as e:
			print('\n', exprs, '\n')
			# raise e
		s += ')'
		return s

	def visitGrouping(self, expr):
		return self.parensiffy('Group', expr.expr)

	def visitLiteral(self, expr):
		return "nil" if expr.value is None else str(expr.value)

	def visitUnary(self, expr):
		return self.parensiffy(expr.op.lexeme, expr.right)

	def visitBinary(self, expr):
		return self.parensiffy(expr.op.lexeme, expr.left, expr.right)

	"""
	def visitExpr(self, expr):
		return self.parensiffy(expr.expr)

	def visit(self, expr):
		# print(f"\t!!def visit of {expr}")
		return str(expr)
	"""
