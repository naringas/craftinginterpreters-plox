import sys

from scanner import Scanner, Token, TokenType
from parser import Parser

global hadError


def runPrompt():
	while True:
		try:
			line = input("plox> ")
		except EOFError:
			print("\n\nbuhbuy!")
			break
		else:
			run(line)
		hadError = False

def runFile(filepath):
	print(f'readin {filepath}')
	with open(filepath, 'r', encoding="utf-8") as f:
		run(f.read())

def run(source):
	tokens = Scanner(source).scanTokens()
	if not hadError:
		print('TOKENS')
		for t in tokens:
			print(t)
		print('')
	else:
		print('scan (token gen) ERROR')
		return

	topExp = Parser(tokens).parse()
	if not hadError:
		if topExp is not None:
			from expressions import AstPrinter

			print("AstPriner printout")
			AstPrinter().printout(topExp)
		else:
			print('need more IMPL')
	else:
		print("Parser error")
		return


if __name__ == "__main__":
	hadError = False
	# print(sys.argv)
	if len(sys.argv) == 1:
		runPrompt()
	elif len(sys.argv) == 2:
		runFile(sys.argv[1])
		if hadError:
			sys.exit(65)  # uhm say wha!?
