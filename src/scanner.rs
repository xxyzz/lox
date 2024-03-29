use std::collections::HashMap;

use crate::{
    error,
    expr::Literal,
    token::{Token, TokenType},
};

#[derive(Default)]
pub struct Scanner {
    source: Vec<char>,
    tokens: Vec<Token>,
    start_index: usize,
    current_index: usize,
    line_num: usize,
    keywords: HashMap<&'static str, TokenType>,
}

impl Scanner {
    pub fn new(source: Vec<char>) -> Self {
        let keywords = HashMap::from([
            ("and", TokenType::And),
            ("class", TokenType::Class),
            ("else", TokenType::Else),
            ("false", TokenType::False),
            ("for", TokenType::For),
            ("fun", TokenType::Fun),
            ("if", TokenType::If),
            ("nil", TokenType::Nil),
            ("or", TokenType::Or),
            ("print", TokenType::Print),
            ("return", TokenType::Return),
            ("super", TokenType::Super),
            ("this", TokenType::This),
            ("true", TokenType::True),
            ("var", TokenType::Var),
            ("while", TokenType::While),
        ]);

        Scanner {
            source,
            keywords,
            ..Default::default()
        }
    }

    pub fn scan_tokens(&mut self) -> Vec<Token> {
        while !self.is_at_end() {
            // We are at the beginning of the next lexeme.
            self.start_index = self.current_index;
            self.scan_token();
        }
        self.tokens.push(Token {
            token_type: TokenType::Eof,
            line_num: self.line_num,
            ..Default::default()
        });
        self.tokens.clone()
    }

    fn is_at_end(&self) -> bool {
        self.current_index >= self.source.len()
    }

    fn advance(&mut self) -> char {
        let c = self.source[self.current_index];
        self.current_index += 1;
        c
    }

    fn add_token(&mut self, token_type: TokenType, literal: Literal) {
        let lexeme = self.source[self.start_index..self.current_index]
            .iter()
            .collect();
        self.tokens.push(Token {
            token_type,
            lexeme,
            line_num: self.line_num,
            literal,
        })
    }

    fn scan_token(&mut self) {
        match self.advance() {
            '(' => self.add_token(TokenType::LeftParen, Literal::Nil),
            ')' => self.add_token(TokenType::RightParen, Literal::Nil),
            '{' => self.add_token(TokenType::LeftBrace, Literal::Nil),
            '}' => self.add_token(TokenType::RightBrace, Literal::Nil),
            ',' => self.add_token(TokenType::Comma, Literal::Nil),
            '.' => self.add_token(TokenType::Dot, Literal::Nil),
            '-' => self.add_token(TokenType::Minus, Literal::Nil),
            '+' => self.add_token(TokenType::Plus, Literal::Nil),
            ';' => self.add_token(TokenType::Semicolon, Literal::Nil),
            '*' => self.add_token(TokenType::Star, Literal::Nil),
            '!' => {
                if self.match_char('=') {
                    self.add_token(TokenType::BangEqual, Literal::Nil);
                } else {
                    self.add_token(TokenType::Bang, Literal::Nil);
                }
            }
            '=' => {
                if self.match_char('=') {
                    self.add_token(TokenType::EqualEqual, Literal::Nil);
                } else {
                    self.add_token(TokenType::Equal, Literal::Nil);
                }
            }
            '<' => {
                if self.match_char('=') {
                    self.add_token(TokenType::LessEqual, Literal::Nil);
                } else {
                    self.add_token(TokenType::Less, Literal::Nil);
                }
            }
            '>' => {
                if self.match_char('=') {
                    self.add_token(TokenType::GreaterEqual, Literal::Nil);
                } else {
                    self.add_token(TokenType::Greater, Literal::Nil);
                }
            }
            '/' => {
                if self.match_char('/') {
                    // A comment goes until the end of the line.
                    while self.peek() != '\n' && !self.is_at_end() {
                        self.advance();
                    }
                } else if self.match_char('*') {
                    self.block_comment();
                } else {
                    self.add_token(TokenType::Slash, Literal::Nil);
                }
            }
            ' ' | '\r' | '\t' => (),
            '\n' => self.line_num += 1,
            '"' => self.string(),
            c if c.is_ascii_digit() => self.number(),
            c if c.is_ascii_alphabetic() || c == '_' => self.identifier(),
            _ => error(self.line_num, "Unexpected character."),
        }
    }

    fn match_char(&mut self, expected: char) -> bool {
        if self.is_at_end() {
            return false;
        }
        if self.source[self.current_index] != expected {
            return false;
        }
        self.current_index += 1;
        true
    }

    fn peek(&mut self) -> char {
        if self.is_at_end() {
            '\0'
        } else {
            self.source[self.current_index]
        }
    }

    fn string(&mut self) {
        while self.peek() != '"' && !self.is_at_end() {
            if self.peek() == '\n' {
                self.line_num += 1;
            }
            self.advance();
        }

        if self.is_at_end() {
            error(self.line_num, "Unterminated string.");
            return;
        }

        // the closing ".
        self.advance();

        // Trim the surrounding quotes.
        self.add_token(
            TokenType::String,
            Literal::String(
                self.source[self.start_index + 1..self.current_index - 1]
                    .iter()
                    .collect::<String>(),
            ),
        );
    }

    fn number(&mut self) {
        while self.peek().is_ascii_digit() {
            self.advance();
        }

        // Look for a fractional part.
        if self.peek() == '.' && self.peek_next().is_ascii_digit() {
            // Consume the "."
            self.advance();

            while self.peek().is_ascii_digit() {
                self.advance();
            }
        }

        self.add_token(
            TokenType::Number,
            Literal::Number(
                self.source[self.start_index..self.current_index]
                    .iter()
                    .collect::<String>()
                    .parse()
                    .unwrap(),
            ),
        );
    }

    fn peek_next(&mut self) -> char {
        if self.current_index + 1 == self.source.len() {
            return '\0';
        }
        self.source[self.current_index + 1]
    }

    fn identifier(&mut self) {
        while self.peek().is_ascii_alphabetic()
            || self.peek() == '_'
            || self.peek().is_ascii_digit()
        {
            self.advance();
        }

        let text: String = self.source[self.start_index..self.current_index]
            .iter()
            .collect();
        let mut token_type = TokenType::Identifier;
        if self.keywords.contains_key(text.as_str()) {
            token_type = self.keywords[text.as_str()];
        }
        self.add_token(token_type, Literal::Nil);
    }

    fn block_comment(&mut self) {
        while !self.is_at_end() {
            match self.advance() {
                '*' => {
                    // end
                    if self.match_char('/') {
                        break;
                    }
                }
                '/' => {
                    // start
                    if self.match_char('*') {
                        self.block_comment();
                    }
                }
                '\n' => self.line_num += 1,
                _ => (),
            }
        }
    }
}
