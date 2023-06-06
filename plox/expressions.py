# expressions.py
from abc import ABC
from dataclasses import dataclass, fields
from typing import Protocol

from scanner import Token, TokenType
from util import Visitable, Visitor


class Expr(ABC, Visitable):
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
class Assign(Expr):
	name: Token  #identifier
	value: Expr

@dataclass
class Logical(Expr):
	left: Expr
	op: Token
	right: Expr

@dataclass
class Call(Expr):
	callee: Expr
	paren: Token
	args: list[Expr]


class ExprVisitorProt(Protocol):
	def visitLiteral(self, expr: Literal): ...

	def visitGrouping(self, expr: Grouping): ...

	def visitUnary(self, expr: Unary): ...

	def visitBinary(self, expr: Binary): ...

	def visitVariable(self, expr: Variable): ...

	def visitAssign(self, expr: Assign): ...

	def visitLogical(self, expr: Logical): ...

	def visitCall(self, expr: Call): ...


class AstPrinter(ExprVisitorProt, Visitor):
	"""only good at printing out (and making strings) from binary expressions"""

	def printout(self, expr: Expr):
		assert isinstance(expr, Expr), f'expr is not a Expr, but a {expr.__class__}'
		print('\nAST print')
		print(self.start_walk(expr))

	def parensiffy(self, name, *exprs):
		if len(exprs) >= 1 and exprs[0] is None:
			return '()'
		s = f'({name} '
		try:
			s += ' '.join((self.start_walk(exp) for exp in exprs))
		except AttributeError as e:
			print('\n', exprs, '\n')
			raise e  #why this? how to avoid this?
		s += ')'
		return s

	def visitGrouping(self, expr: Grouping):
		return self.parensiffy('Group', expr.expr)

	def visitLiteral(self, expr):
		return "nil" if expr.value is None else f'"{expr.value}"'

	def visitUnary(self, expr):
		return self.parensiffy(expr.op.lexeme, expr.right)

	def visitBinary(self, expr):
		return self.parensiffy(expr.op.lexeme, expr.left, expr.right)

	def visitTernary(self, expr):
		return (f'if [{self.start_walk(expr.comparison)}]; '
			f'then [{self.start_walk(expr.left)}]; '
			f'else [{self.start_walk(expr.right)}]')

	def visitCall(self, expr):
		s = self.start_walk(expr.callee)
		s += ", ".join((self.start_walk(e) for e in expr.args))
		return s

	"""
	def visitExpr(self, expr):
		return self.parensiffy(expr.expr)
	"""
	def visitAssign(self, e):
		return str(e)

	def visitBlock(self, e):
		return str(e)

	def visitLogical(self, e):
		return str(e)

	def visitVariable(self, e):
		return str(e)

	def visit(self, expr):
		# print(f"\t!!def visit of {expr}")
		return str(expr)


