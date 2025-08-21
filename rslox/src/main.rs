mod chunk;
mod compiler;
mod debug;
mod scanner;
mod value;
mod vm;

use std::env;
use std::fs;
use std::io;
use std::io::Write;
use std::process;

use crate::vm::{InterpretResult, VM};

fn main() {
    let args: Vec<String> = env::args().collect();

    match args.len() {
        1 => repl(),
        2 => run_file(&args[1]),
        _ => {
            eprintln!("Usage: rslox [path]");
            process::exit(64);
        }
    }
}

fn repl() {
    loop {
        print!("> ");
        io::stdout().flush().unwrap();
        let mut buffer = String::new();
        io::stdin().read_line(&mut buffer).unwrap();
        let mut vm = VM::new();
        vm.interpret(&buffer);
    }
}

fn run_file(path: &str) {
    let source = fs::read_to_string(path).unwrap();
    let mut vm = VM::new();
    let result = vm.interpret(&source);
    match result {
        InterpretResult::ComplileError => process::exit(65),
        InterpretResult::RuntimeError => process::exit(70),
        InterpretResult::Ok => {}
    }
}
