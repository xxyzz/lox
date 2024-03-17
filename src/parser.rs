use crate::expr::{Binary, Expr, Literal, Unary};
use crate::token::{Token, TokenType};
use crate::token_error;

pub struct Parser {
    tokens: Vec<Token>,
    current: usize,
}

impl Parser {
    pub fn new(tokens: Vec<Token>) -> Self {
        Parser { tokens, current: 0 }
    }

    pub fn parse(&mut self) -> Expr {
        self.expression()
    }

    // expression     → equality ;
    fn expression(&mut self) -> Expr {
        self.equality()
    }

    // equality       → comparison ( ( "!=" | "==" ) comparison )* ;
    fn equality(&mut self) -> Expr {
        let mut expr = self.comparison();
        while self.match_type(&[TokenType::BangEqual, TokenType::EqualEqual]) {
            let operator = self.previous();
            let right = self.comparison();
            expr = Expr::Binary(Binary {
                left: Box::new(expr),
                operator,
                right: Box::new(right),
            });
        }
        expr
    }

    fn match_type(&mut self, token_types: &[TokenType]) -> bool {
        for token_type in token_types {
            if self.check(*token_type) {
                self.advance();
                return true;
            }
        }

        false
    }

    fn check(&self, token_type: TokenType) -> bool {
        if self.is_at_end() {
            return false;
        }
        self.peek().token_type == token_type
    }

    fn advance(&mut self) -> Token {
        if !self.is_at_end() {
            self.current += 1;
        }
        self.previous()
    }

    fn is_at_end(&self) -> bool {
        self.peek().token_type == TokenType::Eof
    }

    fn peek(&self) -> Token {
        self.tokens[self.current].clone()
    }

    fn previous(&self) -> Token {
        self.tokens[self.current - 1].clone()
    }

    // comparison     → term ( ( ">" | ">=" | "<" | "<=" ) term )* ;
    fn comparison(&mut self) -> Expr {
        let mut expr = self.term();
        while self.match_type(&[
            TokenType::Greater,
            TokenType::GreaterEqual,
            TokenType::Less,
            TokenType::LessEqual,
        ]) {
            let operator = self.previous();
            let right = self.term();
            expr = Expr::Binary(Binary {
                left: Box::new(expr),
                operator,
                right: Box::new(right),
            });
        }
        expr
    }

    // term           → factor ( ( "-" | "+" ) factor )* ;
    fn term(&mut self) -> Expr {
        let mut expr = self.factor();
        while self.match_type(&[TokenType::Minus, TokenType::Plus]) {
            let operator = self.previous();
            let right = self.factor();
            expr = Expr::Binary(Binary {
                left: Box::new(expr),
                operator,
                right: Box::new(right),
            });
        }
        expr
    }

    // factor         → unary ( ( "/" | "*" ) unary )* ;
    fn factor(&mut self) -> Expr {
        let mut expr = self.unary();
        while self.match_type(&[TokenType::Slash, TokenType::Star]) {
            let operator = self.previous();
            let right = self.unary();
            expr = Expr::Binary(Binary {
                left: Box::new(expr),
                operator,
                right: Box::new(right),
            });
        }
        expr
    }

    // unary          → ( "!" | "-" ) unary
    //                | primary ;
    fn unary(&mut self) -> Expr {
        if self.match_type(&[TokenType::Bang, TokenType::Minus]) {
            let operator = self.previous();
            let right = self.unary();
            return Expr::Unary(Unary {
                operator,
                right: Box::new(right),
            });
        }
        self.primary()
    }

    // primary        → NUMBER | STRING | "true" | "false" | "nil"
    //                | "(" expression ")" ;
    fn primary(&mut self) -> Expr {
        if self.match_type(&[TokenType::False]) {
            return Expr::Literal(Literal::Bool(false));
        }
        if self.match_type(&[TokenType::True]) {
            return Expr::Literal(Literal::Bool(true));
        }
        if self.match_type(&[TokenType::Nil]) {
            return Expr::Literal(Literal::Nil);
        }

        if self.match_type(&[TokenType::Number]) {
            return Expr::Literal(Literal::Number(self.previous().literal.parse().unwrap()));
        }
        if self.match_type(&[TokenType::String]) {
            return Expr::Literal(Literal::String(self.previous().literal.clone()));
        }

        if self.match_type(&[TokenType::LeftParen]) {
            let expr = self.expression();
            self.consume(TokenType::RightParen, "Except ')' after expression.")
                .unwrap();
            return Expr::Grouping(Box::new(expr));
        }

        panic!("{:#?}", token_error(self.peek(), "Expect expression."));
    }

    fn consume<'a>(&mut self, token_type: TokenType, message: &'a str) -> Result<Token, &'a str> {
        if self.check(token_type) {
            return Ok(self.advance());
        }
        token_error(self.peek(), message);
        Err(message)
    }

    fn synchronize(&mut self) {
        self.advance();

        while !self.is_at_end() {
            if self.previous().token_type == TokenType::Semicolon {
                return;
            }

            match self.peek().token_type {
                TokenType::Class
                | TokenType::Fun
                | TokenType::Var
                | TokenType::For
                | TokenType::If
                | TokenType::While
                | TokenType::Print
                | TokenType::Return => return,
                _ => {}
            }

            self.advance();
        }
    }
}
