# expressions.py
from dataclasses import dataclass, fields

from scanner import Token, TokenType
from util import Visitable, Visitor


@dataclass
class Expr(Visitable):
	# what if I put a Token here, the token that started this Expr for any Expr.
	# in some cases it'll be a TokenType like VAR
	# in others, it'll be an IDENTIFIER or LITERAL. just the first token in thing.
	# an empty file, with only an EOF would be that StmtExpr.expr = Expr().token=that EOF/
	# this would conttain file position data.
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

@dataclass
class Ternary(Expr):
	comparison: Expr
	left: Expr  # true evaluation, comparison must be boolean
	right: Expr


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
			raise e  #why this? how to avoid this?
		s += ')'
		return s

	def visitGrouping(self, expr):
		return self.parensiffy('Group', expr.expr)

	def visitLiteral(self, expr):
		return "nil" if expr.value is None else f'"{expr.value}"'

	def visitUnary(self, expr):
		return self.parensiffy(expr.op.lexeme, expr.right)

	def visitBinary(self, expr):
		return self.parensiffy(expr.op.lexeme, expr.left, expr.right)

	def visitTernary(self, expr):
		return (f'if [{expr.comparison.accept(visitor=self)}]; '
			f'then [{expr.left.accept(visitor=self)}]; '
			f'else [{expr.right.accept(visitor=self)}]')
	"""
	def visitExpr(self, expr):
		return self.parensiffy(expr.expr)

	def visit(self, expr):
		# print(f"\t!!def visit of {expr}")
		return str(expr)
	"""
