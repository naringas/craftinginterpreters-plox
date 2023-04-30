# expressions.py
from dataclasses import dataclass, fields

from scanner import Token, TokenType


@dataclass
class Expr:
	def accept(self, visitor):
		assert isinstance(visitor, ExprVisitor)
		method = getattr(visitor, f'visit{self.__class__.__name__}', visitor.visit)
		return method(self)

	def __str__(self):
		s = f'{self.__class__.__name__}('
		s += ", ".join((f'{f.name}={getattr(self, f.name)}' for f in fields(self)) )
		s += ")"
		return s

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
class Comment(Expr):
	lexeme: str


class ExprVisitor:
	def visit(self, expr: Expr):
		raise NotImplementedError(expr.__class__.__name__)


class AstPrinter(ExprVisitor):
	def printout(self, expr: Expr):
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

	def visit(self, expr):
		print(f"\t!!def visit of {expr}")
		return str(expr)


# if __name__=="__main__":
	# expr=
	# AstPrinter().printout(expr)
