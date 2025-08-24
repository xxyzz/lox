use std::fmt;

#[derive(Clone, Copy, PartialEq)]
pub enum Value {
    Bool(bool),
    Nil,
    Number(f64),
}

impl fmt::Display for Value {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            Value::Bool(v) => write!(f, "{v}"),
            Value::Nil => write!(f, "nil"),
            Value::Number(num) => write!(f, "{num}"),
        }
    }
}
