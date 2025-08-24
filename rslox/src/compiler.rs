use std::collections::HashMap;
use std::env;
use std::ops::Add;

use crate::chunk::{Chunk, OpCode};
use crate::debug::disassemble_chunk;
use crate::scanner::{Scanner, Token, TokenType};
use crate::value::Value;

struct Parser<'a> {
    current: Token<'a>,
    previous: Token<'a>,
    has_error: bool,
    panic_mode: bool,
}

#[derive(PartialEq, Eq, PartialOrd, Ord, Clone, Copy)]
enum Precedence {
    None,
    Assignment, // =
    Or,         // or
    And,        // and
    Equality,   // == !=
    Comparison, // < > <= >=
    Term,       // + -
    Factor,     // * /
    Unary,      // ! -
    Call,       // . ()
    Primary,
}

impl From<usize> for Precedence {
    fn from(i: usize) -> Self {
        match i {
            0 => Precedence::None,
            1 => Precedence::Assignment,
            2 => Precedence::Or,
            3 => Precedence::And,
            4 => Precedence::Equality,
            5 => Precedence::Comparison,
            6 => Precedence::Term,
            7 => Precedence::Factor,
            8 => Precedence::Unary,
            9 => Precedence::Call,
            10 => Precedence::Primary,
            _ => unreachable!(),
        }
    }
}

impl Add<usize> for Precedence {
    type Output = Self;

    fn add(self, other: usize) -> Self {
        Precedence::from(self as usize + other)
    }
}

type ParserFn<'a> = fn(&mut Compiler<'a>);

struct ParserRule<'a> {
    prefix: Option<ParserFn<'a>>,
    infix: Option<ParserFn<'a>>,
    precedence: Precedence,
}

pub struct Compiler<'a> {
    scanner: Scanner<'a>,
    parser: Parser<'a>,
    compiling_chunk: Chunk,
    parser_rules: HashMap<TokenType, ParserRule<'a>>,
}

impl<'a> Compiler<'a> {
    pub fn new(source: &'a str) -> Self {
        Compiler {
            scanner: Scanner::new(source),
            parser: Parser {
                current: Token::default(),
                previous: Token::default(),
                has_error: false,
                panic_mode: false,
            },
            compiling_chunk: Chunk::new(),
            parser_rules: HashMap::from([
                (
                    TokenType::LeftParen,
                    ParserRule {
                        prefix: Some(Compiler::grouping),
                        infix: None,
                        precedence: Precedence::None,
                    },
                ),
                (
                    TokenType::RightParen,
                    ParserRule {
                        prefix: None,
                        infix: None,
                        precedence: Precedence::None,
                    },
                ),
                (
                    TokenType::LeftBrace,
                    ParserRule {
                        prefix: None,
                        infix: None,
                        precedence: Precedence::None,
                    },
                ),
                (
                    TokenType::RightBrace,
                    ParserRule {
                        prefix: None,
                        infix: None,
                        precedence: Precedence::None,
                    },
                ),
                (
                    TokenType::Comma,
                    ParserRule {
                        prefix: None,
                        infix: None,
                        precedence: Precedence::None,
                    },
                ),
                (
                    TokenType::Dot,
                    ParserRule {
                        prefix: None,
                        infix: None,
                        precedence: Precedence::None,
                    },
                ),
                (
                    TokenType::Minus,
                    ParserRule {
                        prefix: Some(Compiler::unary),
                        infix: Some(Compiler::binary),
                        precedence: Precedence::Term,
                    },
                ),
                (
                    TokenType::Plus,
                    ParserRule {
                        prefix: None,
                        infix: Some(Compiler::binary),
                        precedence: Precedence::Term,
                    },
                ),
                (
                    TokenType::Semicolon,
                    ParserRule {
                        prefix: None,
                        infix: None,
                        precedence: Precedence::None,
                    },
                ),
                (
                    TokenType::Slash,
                    ParserRule {
                        prefix: None,
                        infix: Some(Compiler::binary),
                        precedence: Precedence::Factor,
                    },
                ),
                (
                    TokenType::Star,
                    ParserRule {
                        prefix: None,
                        infix: Some(Compiler::binary),
                        precedence: Precedence::Factor,
                    },
                ),
                (
                    TokenType::Bang,
                    ParserRule {
                        prefix: Some(Compiler::unary),
                        infix: None,
                        precedence: Precedence::None,
                    },
                ),
                (
                    TokenType::BangEqual,
                    ParserRule {
                        prefix: None,
                        infix: Some(Compiler::binary),
                        precedence: Precedence::Equality,
                    },
                ),
                (
                    TokenType::Equal,
                    ParserRule {
                        prefix: None,
                        infix: None,
                        precedence: Precedence::None,
                    },
                ),
                (
                    TokenType::EqualEqual,
                    ParserRule {
                        prefix: None,
                        infix: Some(Compiler::binary),
                        precedence: Precedence::Equality,
                    },
                ),
                (
                    TokenType::Greater,
                    ParserRule {
                        prefix: None,
                        infix: Some(Compiler::binary),
                        precedence: Precedence::Comparison,
                    },
                ),
                (
                    TokenType::GreaterEqual,
                    ParserRule {
                        prefix: None,
                        infix: Some(Compiler::binary),
                        precedence: Precedence::Comparison,
                    },
                ),
                (
                    TokenType::Less,
                    ParserRule {
                        prefix: None,
                        infix: Some(Compiler::binary),
                        precedence: Precedence::Comparison,
                    },
                ),
                (
                    TokenType::LessEqual,
                    ParserRule {
                        prefix: None,
                        infix: Some(Compiler::binary),
                        precedence: Precedence::Comparison,
                    },
                ),
                (
                    TokenType::Identifier,
                    ParserRule {
                        prefix: None,
                        infix: None,
                        precedence: Precedence::None,
                    },
                ),
                (
                    TokenType::String,
                    ParserRule {
                        prefix: None,
                        infix: None,
                        precedence: Precedence::None,
                    },
                ),
                (
                    TokenType::Number,
                    ParserRule {
                        prefix: Some(Compiler::number),
                        infix: None,
                        precedence: Precedence::None,
                    },
                ),
                (
                    TokenType::And,
                    ParserRule {
                        prefix: None,
                        infix: None,
                        precedence: Precedence::None,
                    },
                ),
                (
                    TokenType::Class,
                    ParserRule {
                        prefix: None,
                        infix: None,
                        precedence: Precedence::None,
                    },
                ),
                (
                    TokenType::Else,
                    ParserRule {
                        prefix: None,
                        infix: None,
                        precedence: Precedence::None,
                    },
                ),
                (
                    TokenType::False,
                    ParserRule {
                        prefix: Some(Compiler::literal),
                        infix: None,
                        precedence: Precedence::None,
                    },
                ),
                (
                    TokenType::For,
                    ParserRule {
                        prefix: None,
                        infix: None,
                        precedence: Precedence::None,
                    },
                ),
                (
                    TokenType::Fun,
                    ParserRule {
                        prefix: None,
                        infix: None,
                        precedence: Precedence::None,
                    },
                ),
                (
                    TokenType::If,
                    ParserRule {
                        prefix: None,
                        infix: None,
                        precedence: Precedence::None,
                    },
                ),
                (
                    TokenType::Nil,
                    ParserRule {
                        prefix: Some(Compiler::literal),
                        infix: None,
                        precedence: Precedence::None,
                    },
                ),
                (
                    TokenType::Or,
                    ParserRule {
                        prefix: None,
                        infix: None,
                        precedence: Precedence::None,
                    },
                ),
                (
                    TokenType::Print,
                    ParserRule {
                        prefix: None,
                        infix: None,
                        precedence: Precedence::None,
                    },
                ),
                (
                    TokenType::Return,
                    ParserRule {
                        prefix: None,
                        infix: None,
                        precedence: Precedence::None,
                    },
                ),
                (
                    TokenType::Super,
                    ParserRule {
                        prefix: None,
                        infix: None,
                        precedence: Precedence::None,
                    },
                ),
                (
                    TokenType::This,
                    ParserRule {
                        prefix: None,
                        infix: None,
                        precedence: Precedence::None,
                    },
                ),
                (
                    TokenType::True,
                    ParserRule {
                        prefix: Some(Compiler::literal),
                        infix: None,
                        precedence: Precedence::None,
                    },
                ),
                (
                    TokenType::Var,
                    ParserRule {
                        prefix: None,
                        infix: None,
                        precedence: Precedence::None,
                    },
                ),
                (
                    TokenType::While,
                    ParserRule {
                        prefix: None,
                        infix: None,
                        precedence: Precedence::None,
                    },
                ),
                (
                    TokenType::Error,
                    ParserRule {
                        prefix: None,
                        infix: None,
                        precedence: Precedence::None,
                    },
                ),
                (
                    TokenType::EOF,
                    ParserRule {
                        prefix: None,
                        infix: None,
                        precedence: Precedence::None,
                    },
                ),
            ]),
        }
    }

    pub fn compile(&mut self) -> Option<Chunk> {
        self.compiling_chunk = Chunk::new();
        self.advance();
        self.expression();
        self.consume(TokenType::EOF, "Expect end of expression.");
        self.end_compiler();
        if self.parser.has_error {
            None
        } else {
            Some(self.compiling_chunk.clone())
        }
    }

    fn current_chunk(&mut self) -> &mut Chunk {
        &mut self.compiling_chunk
    }

    fn error_at(&mut self, token: Token, message: &str) {
        if self.parser.panic_mode {
            return;
        }
        self.parser.panic_mode = true;
        eprint!("[line {}] Error", token.line);
        match token.token_type {
            TokenType::EOF => eprint!(" at end"),
            TokenType::Error => {}
            _ => eprint!(" at '{}'", token.lexeme),
        }
        eprintln!(": {}", message);
        self.parser.has_error = true;
    }

    fn error_at_current(&mut self, message: &str) {
        self.error_at(self.parser.current, message);
    }

    fn error(&mut self, message: &str) {
        self.error_at(self.parser.previous, message);
    }

    fn advance(&mut self) {
        self.parser.previous = self.parser.current;
        loop {
            self.parser.current = self.scanner.scan_token();
            if self.parser.current.token_type != TokenType::Error {
                break;
            }
            self.error_at_current(self.parser.current.lexeme);
        }
    }

    fn consume(&mut self, token_type: TokenType, message: &str) {
        if self.parser.current.token_type == token_type {
            self.advance();
            return;
        }
        self.error_at_current(message);
    }

    fn emit_byte(&mut self, byte: OpCode) {
        let line = self.parser.previous.line;
        self.current_chunk().write(byte, line);
    }

    fn emit_bytes(&mut self, byte1: OpCode, byte2: OpCode) {
        self.emit_byte(byte1);
        self.emit_byte(byte2);
    }

    fn emit_return(&mut self) {
        self.emit_byte(OpCode::Return);
    }

    fn end_compiler(&mut self) {
        self.emit_return();
        if env::var("DEBUG_PRINT_CODE").is_ok() && !self.parser.has_error {
            disassemble_chunk(&self.compiling_chunk, "code");
        }
    }

    fn binary(&mut self) {
        let operator_type = self.parser.previous.token_type;
        let rule = self.get_rule(operator_type);
        self.parse_precedence(rule.precedence + 1);
        match operator_type {
            TokenType::BangEqual => self.emit_bytes(OpCode::Equal, OpCode::Not),
            TokenType::EqualEqual => self.emit_byte(OpCode::Equal),
            TokenType::Greater => self.emit_byte(OpCode::Greater),
            TokenType::GreaterEqual => self.emit_bytes(OpCode::Less, OpCode::Not),
            TokenType::Less => self.emit_byte(OpCode::Less),
            TokenType::LessEqual => self.emit_bytes(OpCode::Greater, OpCode::Not),
            TokenType::Plus => self.emit_byte(OpCode::Add),
            TokenType::Minus => self.emit_byte(OpCode::Subtract),
            TokenType::Star => self.emit_byte(OpCode::Multiply),
            TokenType::Slash => self.emit_byte(OpCode::Divide),
            _ => unreachable!(),
        }
    }

    fn literal(&mut self) {
        match self.parser.previous.token_type {
            TokenType::False => self.emit_byte(OpCode::False),
            TokenType::Nil => self.emit_byte(OpCode::Nil),
            TokenType::True => self.emit_byte(OpCode::True),
            _ => unreachable!(),
        }
    }

    fn grouping(&mut self) {
        self.expression();
        self.consume(TokenType::RightParen, "Expect ')' after expression.");
    }

    fn expression(&mut self) {
        self.parse_precedence(Precedence::Assignment);
    }

    fn number(&mut self) {
        let value: f64 = self.parser.previous.lexeme.parse().unwrap();
        self.emit_constant(Value::Number(value));
    }

    fn unary(&mut self) {
        let operator_type = self.parser.previous.token_type;
        // Compile the operand.
        self.parse_precedence(Precedence::Unary);
        // Emit the operator instruction.
        match operator_type {
            TokenType::Bang => self.emit_byte(OpCode::Not),
            TokenType::Minus => self.emit_byte(OpCode::Negate),
            _ => unreachable!(),
        }
    }

    fn emit_constant(&mut self, value: Value) {
        let index = self.make_constant(value);
        self.emit_byte(OpCode::Constant(index));
    }

    fn make_constant(&mut self, value: Value) -> usize {
        self.current_chunk().add_constant(value)
    }

    fn parse_precedence(&mut self, precedence: Precedence) {
        self.advance();
        let prefix_rule = self.get_rule(self.parser.previous.token_type).prefix;
        if let Some(rule) = prefix_rule {
            rule(self);
            while precedence <= self.get_rule(self.parser.current.token_type).precedence {
                self.advance();
                let infix_rule = self.get_rule(self.parser.previous.token_type).infix;
                if let Some(rule) = infix_rule {
                    rule(self);
                }
            }
        } else {
            self.error("Expect expression.");
        }
    }

    fn get_rule(&self, token_type: TokenType) -> &ParserRule<'a> {
        &self.parser_rules[&token_type]
    }
}
