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

use crate::chunk::{Chunk, OpCode};
use crate::vm::{InterpretResult, VM, interpret};

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

    let chunk = Chunk::new();
    let mut vm = VM::new(chunk);

    vm.chunk.add_constant(2.0, 123);
    vm.chunk.add_constant(1.0, 123);
    vm.chunk.write(OpCode::Multiply, 123);
    vm.chunk.add_constant(3.0, 123);
    vm.chunk.write(OpCode::Add, 123);

    vm.chunk.write(OpCode::Return, 123);

    vm.run();
}

fn repl() {
    loop {
        print!("> ");
        io::stdout().flush().unwrap();
        let mut buffer = String::new();
        io::stdin().read_line(&mut buffer).unwrap();
        interpret(&buffer);
    }
}

fn run_file(path: &str) {
    let source = fs::read_to_string(path).unwrap();
    let result = interpret(&source);

    match result {
        InterpretResult::ComplileError => process::exit(65),
        InterpretResult::RuntimeError => process::exit(70),
        InterpretResult::Ok => {}
    }
}
