# util.py
from abc import ABC, abstractmethod
from dataclasses import fields, asdict, is_dataclass


class Visitable:  #somehow tell mypy that this is a mixin that will be used in a Dataclass instance ALWAYS
	def accept(self, visitor):#: Visitor):
		method = getattr(visitor, f'visit{self.__class__.__name__}', visitor.visit)
		return method(self)

	def __str__(self):
		assert is_dataclass(self), "self is not a dataclass"

		s_field_val_pairs = []
		for f in fields(self):
			# get the field's value
			f_val = getattr(self, f.name)

			'''
			if issubclass(f_val.__class__, Visitable):
				s_field_val_pairs.append(f'{f.name}="{f_val.accept(visitor=

					# STR OR DEFAULT VISITOR? 🤔

					)}"')
			else:
				s_field_val_pairs.append(f'{f.name}="{str(f_val)}"')
			'''
			s_field_val_pairs.append(f'{f.name}="{str(f_val)}"')

		return (f'{self.__class__.__name__}('
			+ (", ".join(s_field_val_pairs)) + ")")

	"""
		'''
		mypy complains that fields(self)
		plox/util.py:13: error: Argument 1 to "fields" has incompatible type "Visitable"; expected "Union[DataclassInstance, Type[DataclassInstance]]"  [arg-type]

		but all my Dataclasses stuff (Expr and Stmt), inherit from Visitable.'''
		s += ")"
	"""

class Visitor(ABC):
	def start_walk(self, obj: Visitable):
		assert isinstance(obj, Visitable)
		return obj.accept(visitor=self)

	@abstractmethod
	def visit(self, obj):
		...
