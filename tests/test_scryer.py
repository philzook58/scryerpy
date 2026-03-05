from scryer import Machine, Term
# https://www.scryer.pl/


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
    assert machine.query_once("foo(X).") == {"X": Term.Atom("a")}
    assert machine.query("foo(X).") == [
        {"X": Term.Atom("a")},
        {"X": Term.Atom("b")},
    ]
    assert machine.query("foo(X).", limit=1) == [{"X": Term.Atom("a")}]
    assert machine.query("foo(X).", limit=0) == []
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


def test_list_and_var():
    machine = Machine()
    machine.load_module_string("mymod", ":- use_module(library(lists)).")
    assert machine.query_once("length([a, b, c], N).") == {"N": Term.Integer(3)}
    assert machine.query_once("length(L, 3).") == {
        "L": Term.List([Term.Var("_A"), Term.Var("_B"), Term.Var("_C")])
    }
    assert machine.query_once("length(L, N).") == {
        "L": Term.List([]),
        "N": Term.Integer(0),
    }
    assert machine.query_once("L = [foo, b, c], length(L, N).") == {
        "L": Term.List([Term.Atom("foo"), Term.Atom("b"), Term.Atom("c")]),
        "N": Term.Integer(3),
    }
    assert machine.query_once('L =  "hello".') == {"L": Term.String("hello")}


def test_list_length():
    machine = Machine()
    # missing imports does not cause an error?
    prog = """
    :- use_module(library(clpz)).
    list_length([], 0).
    list_length([_|Ls], N) :-
        N #> 0,
        N #= N0 + 1,
        list_length(Ls, N0).
        """
    machine.load_module_string("mymod2", prog)
    assert machine.query_once("list_length([a, b, c], N).") == {"N": Term.Integer(3)}

    # def call(predt: Term) -> Term:
    #    return machine.query_one(f"call({}{t}).")
    # call("")


def test_consult():
    machine = Machine()
    prog = """
    foo(a). foo(b). bar(X) :- foo(X).
    """
    machine.consult("mymod3", prog)
    assert machine.query_once("foo(X).") == {"X": Term.Atom("a")}


def test_libraries():
    m = Machine()
    m.query_once("use_module(library(dif)).")
    m.query_once("use_module(library(dcgs)).")
    m.query_once("use_module(library(lists)).")
    m.query_once("use_module(library(reif)).")
    m.query_once("use_module(library(clpz)).")
    m.query_once("use_module(library(clpb)).")
    m.query_once("false.")
    m.query_once("dif(X,Y).")  # huh. Bad looking answer because we can't see remainder?
    m.load_module_string(
        "",
        """
    :- use_module(library(dcgs)).
    foo --> [a].
    """,
    )
    m.query_once("phrase(foo, [A]).")
    # m.query_one("length(Ls, _), false.") # non terminating
    m.query_once("length(Ls,N), N #= 3.")
    # res = m.query("dif(X,Y), Y = 3.") # leaves it in broken state
    # assert res["X"] == res["Y"]
    # # hmm. also leaves it in a non working state
    # m.query_one("X = 3.")
    m.load_module_string(
        "",
        """
    :- use_module(library(tabling)).
    :- table path/2.
    myedge(a,b).
    myedge(b,c).
    myedge(c,a).
    path(X,Y) :- myedge(X,Y).
    path(X,Y) :- myedge(X,Z), path(Z,Y).
    """,
    )
    m.query("path(X,Y).")
