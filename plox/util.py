# util.py
from dataclasses import fields, asdict


class Visitable:  #somehow tell mypy that this is a mixin that will be used in a Dataclass instance ALWAYS
	def accept(self, visitor):
		assert isinstance(visitor, Visitor)
		method = getattr(visitor, f'visit{self.__class__.__name__}', visitor.visit)
		return method(self)

	def __str__(self):
		s = f'{self.__class__.__name__}('
		s += ", ".join((f'{f.name}={getattr(self, f.name)}' for f in fields(self)) )
		'''
		mypy complains that fields(self)
		plox/util.py:13: error: Argument 1 to "fields" has incompatible type "Visitable"; expected "Union[DataclassInstance, Type[DataclassInstance]]"  [arg-type]

		but all my Dataclasses stuff (Expr and Stmt), inherit from Visitable.'''
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

