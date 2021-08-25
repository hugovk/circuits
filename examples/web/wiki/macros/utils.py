"""Utils macros

Utility macros
"""
from inspect import getdoc


def macros(macro, environ, *args, **kwargs):
    """Return a list of available macros"""

    macros = environ["macros"].items()
    s = "\n".join(["== {} ==\n{}\n".format(k, getdoc(v)) for k, v in macros])

    return environ["parser"].generate(s, environ=environ)
