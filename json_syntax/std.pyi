from typing import Any, Optional, Type

def atoms(verb, typ: Type[Any], ctx): ...
def enums(verb, typ: Type[Any], ctx) -> Any: ...
def faux_enums(verb, typ: Type[Any], ctx) -> Any: ...
def optional(verb, typ: Type[Any], ctx) -> Any: ...
def lists(verb, typ: Type[Any], ctx) -> Any: ...
def sets(verb, typ: Type[Any], ctx) -> Any: ...
def dicts(verb, typ: Type[Any], ctx) -> Any: ...