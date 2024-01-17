use std::{
    env, fs,
    io::{self, Write},
};

use scanner::Scanner;

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
    for token in tokens {
        println!("{token}");
    }
}

fn error(line_num: usize, message: &str) {
    report(line_num, "", message);
}

fn report(line_num: usize, where_e: &str, message: &str) {
    eprintln!("[line {line_num}] Error{where_e}: {message}");
}
