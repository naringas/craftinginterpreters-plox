# util.py
from dataclasses import fields, asdict


class Visitable:
	def accept(self, visitor):
		assert isinstance(visitor, Visitor)
		method = getattr(visitor, f'visit{self.__class__.__name__}', visitor.visit)
		return method(self)

	def __str__(self):
		s = f'{self.__class__.__name__}('
		s += ", ".join((f'{f.name}={getattr(self, f.name)}' for f in fields(self)) )
		s += ")"
		return s


class Visitor:
	def start_walk(self, obj):
		assert isinstance(obj, Visitable)
		return obj.accept(visitor=self)

	def visit(self, obj):
		return str(obj)
		# assert isinstance(obj, Visitable)  # doesn't matter, next line errors
		# raise NotImplementedError(obj.__class__.__name__)
		# return asdict(obj)  #{f.name: getattr(obj, f.name) for f in fields(obj)}

