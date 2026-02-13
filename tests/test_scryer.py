from scryer import Machine, Term


def test_scryer():
    machine = Machine()
    machine.load_module_string("mymod", "foo(a). foo(b). bar(X) :- foo(X).")
    Term.Integer(42)
    a = Term.Atom("foo")
    b = Term.Float(3.14)
    assert a.value == "foo"
    assert b.value == 3.14
    fab = Term.Compound("f", [a, b])
    assert Term.Compound("f", [a]) == Term.Compound("f", [a])
    assert machine.query_one("foo(X).") == {"X": Term.Atom("a")}
    assert machine.query_all("foo(X).") == [
        {"X": Term.Atom("a")},
        {"X": Term.Atom("b")},
    ]
    assert str(fab) == "f(foo, 3.14)"
    assert (
        repr(fab)
        == """Compound { functor: "f", args: [Atom { value: "foo" }, Float { value: 3.14 }] }"""
    )
    assert fab.args[0].value == "foo"
    match fab:
        case Term.Compound("f", [Term.Atom(x), Term.Float(y)]):
            assert x == "foo"
            assert y == 3.14
        case _:
            assert False, "Pattern match failed"
