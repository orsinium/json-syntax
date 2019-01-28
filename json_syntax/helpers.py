from importlib import import_module
try:
    from typing import _eval_type
except ImportError:
    _eval_type = None


J2P = 'json_to_python'
P2J = 'python_to_json'
# IJ = 'inspect_json'
# IP = 'inspect_python'
JP = (J2P, P2J)
NoneType = type(None)
NOTHING = object()


def identity(value):
    return value


def has_origin(typ, origin, *, num_args=None):
    '''
    Determines if a concrete class (a generic class with arguments) matches an origin and has a specified number of
    arguments.

    The typing classes use dunder properties such that ``__origin__`` is the generic class and ``__args__`` are the
    type arguments.
    '''
    try:
        t_origin = typ.__origin__
    except AttributeError:
        return False
    else:
        if not isinstance(origin, tuple):
            origin = (origin,)
        return t_origin in origin and (num_args is None or len(typ.__args__) == num_args)


def issub_safe(sub, sup):
    try:
        return issubclass(sub, sup)
    except TypeError:
        return False


def resolve_fwd_ref(typ, context_class):
    '''
    Tries to resolve a forward reference given a containing class. This does nothing for regular types.
    '''
    try:
        namespace = vars(import_module(context_class.__module__))
    except AttributeError:
        return typ

    return _eval_type(typ, namespace, {})


if _eval_type is None:
    # If typing's internal API changes, we should have tests that break quite quickly.
    def resolve_fwd_ref(typ, context_class):  # noqa
        return typ
