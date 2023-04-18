import sys

from scanner import Scanner

hadError = False

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
	tokens: list = Scanner(source).scanTokens()

	for token in tokens:
		print(token)

if __name__ == "__main__":
	# print(sys.argv)
	if len(sys.argv) == 1:
		runPrompt()
	elif len(sys.argv) == 2:
		runFile(sys.argv[1])
