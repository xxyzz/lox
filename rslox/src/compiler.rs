use crate::scanner::{Scanner, TokenType};

pub fn compile(source: &str) {
    let mut line = 0;
    let mut scanner = Scanner::new(&source);
    loop {
        let token = scanner.scan_token();
        if token.line != line {
            print!("{:4} ", token.line);
            line = token.line;
        } else {
            print!("   | ");
        }
        println!("{:?} '{}'", token.token_type, token.lexeme);
        if token.token_type == TokenType::EOF {
            break;
        }
    }
}
