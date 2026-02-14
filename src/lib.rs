use pyo3::prelude::*;

#[pymodule]
mod scryer {
    use num_bigint::BigInt;
    use num_rational::BigRational;
    use ordered_float::OrderedFloat;
    use pyo3::prelude::*;
    use scryer_prolog::{LeafAnswer, Machine, MachineBuilder, Term};
    use std::collections::HashMap;
    use std::fmt;
    use std::str::FromStr;

    #[pyclass(name = "Machine", unsendable)]
    struct PyMachine {
        machine: Machine,
    }

    fn leafanswer_to_pyresult(ans: LeafAnswer) -> PyResult<Option<HashMap<String, PyTerm>>> {
        match ans {
            LeafAnswer::True => Ok(Some(HashMap::new())),
            LeafAnswer::False => Ok(None),
            LeafAnswer::Exception(e) => {
                let pyterm = PyTerm::from(e);
                Err(pyo3::exceptions::PyRuntimeError::new_err(format!(
                    "Prolog exception: {pyterm}"
                )))
            }
            LeafAnswer::LeafAnswer { bindings, .. } => {
                let mut vars = HashMap::with_capacity(bindings.len());
                for (name, value) in bindings {
                    vars.insert(name, PyTerm::from(value));
                }
                Ok(Some(vars))
            }
        }
    }

    #[pymethods]
    impl PyMachine {
        #[new]
        fn new() -> Self {
            Self {
                machine: MachineBuilder::default().build(),
            }
        }

        fn load_module_filename(&mut self, module_name: &str, filename: &str) -> PyResult<()> {
            let contents = std::fs::read_to_string(filename).map_err(|e| {
                pyo3::exceptions::PyIOError::new_err(format!("Failed to read file: {e}"))
            })?;
            self.machine.load_module_string(module_name, contents);
            return Ok(());
        }

        fn load_module_string(&mut self, module_name: &str, program: &str) {
            self.machine.load_module_string(module_name, program);
        }

        fn query_one(
            &mut self,
            _py: Python<'_>,
            query: &str,
        ) -> PyResult<Option<HashMap<String, PyTerm>>> {
            let mut qs = self.machine.run_query(query.to_owned());
            match qs.next() {
                Some(Ok(ans)) => leafanswer_to_pyresult(ans),
                Some(Err(term)) => {
                    let pyterm = PyTerm::from(term);
                    Err(pyo3::exceptions::PyRuntimeError::new_err(format!(
                        "Prolog error term: {pyterm}"
                    )))
                }
                None => Ok(None),
            }
        }

        fn query_all(
            &mut self,
            _py: Python<'_>,
            query: &str,
        ) -> PyResult<Vec<HashMap<String, PyTerm>>> {
            let mut results = Vec::new();
            let mut qs = self.machine.run_query(query.to_owned());
            while let Some(ans) = qs.next() {
                match ans {
                    Ok(LeafAnswer::False) => break,
                    Ok(ans) => {
                        if let Some(vars) = leafanswer_to_pyresult(ans)? {
                            results.push(vars);
                        }
                    }
                    Err(term) => {
                        let pyterm = PyTerm::from(term);
                        return Err(pyo3::exceptions::PyRuntimeError::new_err(format!(
                            "Prolog error term: {pyterm}"
                        )));
                    }
                }
            }
            Ok(results)
        }
    }

    #[pyclass(name = "Term", eq, hash, frozen, str, from_py_object, unsendable)]
    #[derive(Debug, Clone, PartialEq, Eq, Hash)]
    pub enum PyTerm {
        /// An arbitrary precision integer.
        Integer {
            value: BigInt,
        },
        /// An arbitrary precision rational.
        Rational {
            value: BigRational,
        },
        /// A float.
        Float {
            value: OrderedFloat<f64>,
        },
        /// A Prolog atom.
        Atom {
            value: String,
        },
        /// A Prolog string.
        ///
        /// In particular, this represents Prolog lists of characters.
        String {
            value: String,
        },
        /// A Prolog list.
        List {
            values: Vec<PyTerm>,
        },
        /// A Prolog compound term.
        Compound {
            functor: String,
            args: Vec<PyTerm>,
        },

        Var {
            name: String,
        },
    }

    impl fmt::Display for PyTerm {
        fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
            match self {
                PyTerm::Integer { value } => write!(f, "{value}"),
                PyTerm::Rational { value } => write!(f, "{value}"),
                PyTerm::Float { value } => write!(f, "{}", value.into_inner()),
                PyTerm::Atom { value } => write!(f, "{value}"),
                PyTerm::String { value } => write!(f, "\"{value}\""),
                PyTerm::List { values } => {
                    let item_strs: Vec<String> =
                        values.iter().map(|item| item.to_string()).collect();
                    write!(f, "[{}]", item_strs.join(", "))
                }
                PyTerm::Compound { functor, args } => {
                    let arg_strs: Vec<String> = args.iter().map(|arg| arg.to_string()).collect();
                    write!(f, "{}({})", functor, arg_strs.join(", "))
                }
                PyTerm::Var { name } => write!(f, "{name}"),
            }
        }
    }
    #[pymethods]
    impl PyTerm {
        fn __repr__(&self) -> String {
            format!("{:?}", self)
        }
    }

    impl From<Term> for PyTerm {
        fn from(term: Term) -> Self {
            match term {
                Term::Integer(i) => Self::Integer {
                    value: BigInt::from_str(&i.to_string())
                        .expect("dashu Integer should parse as BigInt"),
                },
                Term::Rational(r) => Self::Rational {
                    value: BigRational::from_str(&r.to_string())
                        .expect("dashu Rational should parse as BigRational"),
                },
                Term::Float(f) => Self::Float {
                    value: OrderedFloat(f),
                },
                Term::Atom(a) => Self::Atom { value: a },
                Term::String(s) => Self::String { value: s },
                Term::List(l) => Self::List {
                    values: l.into_iter().map(PyTerm::from).collect(),
                },
                Term::Compound(functor, args) => Self::Compound {
                    functor,
                    args: args.into_iter().map(PyTerm::from).collect(),
                },
                Term::Var(name) => Self::Var { name },
                t => Self::String {
                    value: format!("{t:?}"),
                },
            }
        }
    }

    impl From<PyTerm> for Term {
        fn from(term: PyTerm) -> Self {
            match term {
                PyTerm::Integer { value } => Self::Integer(
                    value
                        .to_string()
                        .parse()
                        .expect("BigInt should parse as dashu Integer"),
                ),
                PyTerm::Rational { value } => Self::Rational(
                    value
                        .to_string()
                        .parse()
                        .expect("BigRational should parse as dashu Rational"),
                ),
                PyTerm::Float { value } => Self::Float(value.into_inner()),
                PyTerm::Atom { value } => Self::Atom(value),
                PyTerm::String { value } => Self::String(value),
                PyTerm::List { values } => Self::List(values.into_iter().map(Term::from).collect()),
                PyTerm::Compound { functor, args } => {
                    Self::Compound(functor, args.into_iter().map(Term::from).collect())
                }
                PyTerm::Var { name } => Self::Var(name),
            }
        }
    }
}
