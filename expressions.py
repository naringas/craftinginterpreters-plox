# expressions.py
from dataclasses import dataclass, fields

from scanner import Token, TokenType


@dataclass
class Expr:
	def accept(self, visitor):
		method = getattr(visitor, f'visit{self.__class__.__name__}', visitor.visit)
		return method(self)

	def __str__(self):
		return " ".join((f'{f.name}({getattr(self, f.name)})' for f in fields(self)))


class ExprVisitor:
	def visit(self, expr: Expr):
		raise NotImplementedError(expr.__class__.__name__)


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


class AstPrinter(ExprVisitor):
	def printout(self, expr: Expr):
		print(expr.accept(visitor=self))

	def parensiffy(self, name, *exprs):
		s = f'({name} '
		try:
			s += ' '.join((exp.accept(visitor=self) for exp in exprs))
		except AttributeError as e:
			print (exprs)
		s += ')'
		return s

	def visitGrouping(self, expr):
		return self.parensiffy('Group', expr.expr)

	def visitLiteral(self, expr):
		return "nil" if expr.value is None else expr.value.__str__()

	def visitUnary(self, expr):
		return self.parensiffy(expr.op.lexeme, expr.right)

	def visitBinary(self, expr):
		return self.parensiffy(expr.op.lexeme, expr.left, expr.right)

	def visit(self, expr):
		print( "def visit of " + repr(expr))
		return ''


# if __name__=="__main__":
	# expr=
	# AstPrinter().printout(expr)
