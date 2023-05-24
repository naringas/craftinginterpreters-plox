# expressions.py
from dataclasses import dataclass, fields

from scanner import Token, TokenType
from expressions import Expr, AstPrinter
from util import Visitable, Visitor


@dataclass
class Stmt(Visitable):
	pass

@dataclass
class StmtExpr(Stmt):
	expr: Expr

@dataclass
class StmtPrint(Stmt):
	expr: Expr

@dataclass
class StmtVar(Stmt):
	name: Token
	initializer: Expr | None

@dataclass
class Block(Stmt):
	statements: list  #TODO how to annotate?

class StmtVisitor(Visitor):
	exprPrinter = AstPrinter()

	def print(self, stmt):
		# Visitor.start_walk
		print(f'{stmt.__class__.__name__}({stmt.accept(visitor=self)})')

	def _exprVisit(self, expr):
		return expr.accept(visitor=self.exprPrinter)

	def visitStmtExpr(self, stmt):
		return self._exprVisit(stmt.expr)

	def visitStmtPrint(self, stmt):
		return self._exprVisit(stmt.expr)

	def visitStmtVar(self, stmt):
		return str(stmt)
