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

#[derive(Debug)]
pub enum Literal {
    Number(f64),
    Bool(bool),
    Nil,
    String(String),
}

#[derive(Debug)]
pub struct Unary {
    pub operator: Token,
    pub right: Box<Expr>,
}
