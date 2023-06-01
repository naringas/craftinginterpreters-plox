# expressions.py
from abc import ABC
from dataclasses import dataclass, fields

from scanner import Token, TokenType
from expressions import Expr, AstPrinter
from util import Visitable, Visitor


class Stmt(ABC, Visitable):
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
class StmtIf(Stmt):
	condition : Expr
	thenBranch: Stmt
	elseBranch: Stmt | None

@dataclass
class StmtWhile(Stmt):
	condition: Expr
	body: Stmt

@dataclass
class Block(Stmt):
	statements: list[Stmt]


class StmtVisitor(Visitor):
	exprPrinter = AstPrinter()

	def print(self, stmt):
		# Visitor.start_walk
		print(f'{stmt.__class__.__name__}({self.start_walk(stmt)})')


	def visitStmtVar(self, stmt):
		return f"VAR {stmt.name.lexeme}" \
			+ (f" = {str(stmt.initializer)}" if stmt.initializer is not None else "")

	def visitStmtExpr(self, stmt):
		return self.exprPrinter.start_walk(stmt.expr)

	def visitBlock(self, stmt) -> str :
		s = 'BLOCK{\n'
		stmt_strings: list[str] = ["\t"+self.start_walk(s) for s in stmt.statements]
		s += "\n".join(stmt_strings)
		s += '\n}ENDblock'
		return s

	def visitStmtIf(self, stmt):
		s = f'IF {self.exprPrinter.start_walk(stmt.condition)}'
		s += f'\nTHEN {self.start_walk(stmt.thenBranch)}'
		s += '' if stmt.elseBranch is None else f'\nELSE {self.start_walk(stmt.elseBranch)}'
		return s

	def visitStmtWhile(self, stmt):
		return (f'WHILE {self.exprPrinter.start_walk(stmt.condition)}\nDO \t'
			 + self.start_walk(stmt.body))

	def visitStmt(self, stmt):
		return 'Stmt()'

	def visit(self, stmt):
		return str(stmt)
