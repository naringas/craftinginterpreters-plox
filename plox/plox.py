import sys

from scanner import Scanner, Token, TokenType
from parser import Parser
from interpreter import Interpreter
from statements import StmtVisitor, Stmt


global hadError


def runPrompt():
	i = Interpreter()  #making a new interpreter makes a new Enviornment also

	while True:
		try:
			line = input("plox> ")
		except (EOFError, KeyboardInterrupt):
			print("\n\nbuhbuy!")
			break
		else:
			# print('TOKENS')
			tokens: list[Token] = Scanner(line).scanTokens()
			stmts_list: list[Stmt] = Parser(tokens).parse()
			print('\nSTATEMENTS')
			stmt_printer = StmtVisitor()
			for stmt in stmts_list:
				if stmt is not None:
					print(StmtVisitor().start_walk(stmt))
				else:
					print('none stmt')

			print('\nINTERPRETATION')
			for stm in stmts_list:
				if stm is not None:
					i.interpret(stm)
				else:
					print(f'skiped a none stmt `{stm}`')

			print()
		hadError = False

def runFile(filepath):
	print(f'readin {filepath}')
	with open(filepath, 'r', encoding="utf-8") as f:
		run(f.read())

def run(source):
	tokens = Scanner(source).scanTokens()

	stmts_list = Parser(tokens).parse()

	i = Interpreter()
	for stm in stmts_list:
		if stm is not None:
			i.interpret(stm)
		else:
			print(f'skiped a none stmt `{stm}`')


if __name__ == "__main__":
	hadError = False
	# print(sys.argv)
	if len(sys.argv) == 1:
		runPrompt()
	elif len(sys.argv) == 2:
		runFile(sys.argv[1])
		if hadError:
			sys.exit(65)  # uhm say wha!?
