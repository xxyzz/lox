use crate::token::Token;

#[derive(Debug)]
pub enum Expr {
    Binary(Binary),
    Grouping(Box<Self>),
    Literal(Literal),
    Unary(Unary),
}

#[derive(Debug)]
pub struct Binary {
    pub left: Box<Expr>,
    pub right: Box<Expr>,
    pub operator: Token,
}

#[derive(Debug, Clone, Default)]
pub enum Literal {
    #[default]
    Nil,
    Number(f64),
    Bool(bool),
    String(String),
}

#[derive(Debug)]
pub struct Unary {
    pub operator: Token,
    pub right: Box<Expr>,
}
