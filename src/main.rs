use std::{
    env, fs,
    io::{self, Write},
};

use parser::Parser;
use scanner::Scanner;
use token::{Token, TokenType};

mod expr;
mod parser;
mod scanner;
mod token;

fn main() {
    let args: Vec<String> = env::args().collect();
    match args.len() {
        2 => run_file(args[1].as_str()),
        1 => run_prompt(),
        _ => println!("Usage: lox [script]"),
    }
}

fn run_file(path: &str) {
    let text = fs::read_to_string(path).unwrap();
    run(&text);
}

fn run_prompt() {
    loop {
        print!("> ");
        io::stdout().flush().unwrap();
        let mut line = String::new();
        io::stdin().read_line(&mut line).unwrap();
        if !line.is_empty() {
            run(&line);
        }
    }
}

fn run(source: &str) {
    let mut scanner = Scanner::new(source.chars().collect());
    let tokens = scanner.scan_tokens();
    let mut parser = Parser::new(tokens);
    let expr = parser.parse();
    println!("{:#?}", expr);
}

fn error(line_num: usize, message: &str) {
    report(line_num, "", message)
}

fn token_error(token: Token, message: &str) {
    if token.token_type == TokenType::Eof {
        report(token.line_num, " at end", message);
    } else {
        report(
            token.line_num,
            format!(" at '{}'", token.lexeme).as_str(),
            message,
        );
    }
}

fn report(line_num: usize, where_e: &str, message: &str) {
    eprintln!("[line {line_num}] Error{where_e}: {message}");
}
