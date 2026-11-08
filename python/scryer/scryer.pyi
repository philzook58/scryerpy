from typing import ClassVar, Dict, List, Optional


class Machine:
    def __init__(self) -> None: ...
    def load_module_filename(self, module_name: str, filename: str) -> None: ...
    def load_module_string(self, module_name: str, program: str) -> None: ...
    def consult(self, module_name: str, program: str) -> None: ...
    def query_once(self, query: str) -> Optional[Dict[str, "Term"]]: ...
    def query(self, query: str, limit: Optional[int] = ...) -> List[Dict[str, "Term"]]: ...


class Term:
    Integer: ClassVar[type[_Integer]]
    Rational: ClassVar[type[_Rational]]
    Float: ClassVar[type[_Float]]
    Atom: ClassVar[type[_Atom]]
    String: ClassVar[type[_String]]
    List: ClassVar[type[_List]]
    Compound: ClassVar[type[_Compound]]
    Var: ClassVar[type[_Var]]

    value: object
    values: list[Term]
    functor: str
    args: list[Term]
    name: str

    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...


class _Integer(Term):
    __match_args__: ClassVar[tuple[str, ...]]
    value: int
    def __new__(cls, value: int) -> _Integer: ...


class _Rational(Term):
    __match_args__: ClassVar[tuple[str, ...]]
    value: object
    def __new__(cls, value: object) -> _Rational: ...


class _Float(Term):
    __match_args__: ClassVar[tuple[str, ...]]
    value: float
    def __new__(cls, value: float) -> _Float: ...


class _Atom(Term):
    __match_args__: ClassVar[tuple[str, ...]]
    value: str
    def __new__(cls, value: str) -> _Atom: ...


class _String(Term):
    __match_args__: ClassVar[tuple[str, ...]]
    value: str
    def __new__(cls, value: str) -> _String: ...


class _List(Term):
    __match_args__: ClassVar[tuple[str, ...]]
    values: List[Term]
    def __new__(cls, values: List[Term]) -> _List: ...


class _Compound(Term):
    __match_args__: ClassVar[tuple[str, ...]]
    functor: str
    args: List[Term]
    def __new__(cls, functor: str, args: List[Term]) -> _Compound: ...


class _Var(Term):
    __match_args__: ClassVar[tuple[str, ...]]
    name: str
    def __new__(cls, name: str) -> _Var: ...
