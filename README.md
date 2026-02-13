# scryerpy

Simple Maturin based python bindings to scryer prolog.

This is distinct from <https://github.com/jjtolton/scrypy> which tries to be more cohesive between python and prolog

```python
from scryer import Machine, Term

m = Machine()
machine = Machine()
machine.load_module_string("mymod", "foo(a). foo(b). bar(X) :- foo(X).")
assert machine.query_all("foo(X).") == [
    {"X": Term.Atom("a")},
    {"X": Term.Atom("b")},
]
```
