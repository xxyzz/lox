use std::env;

use crate::chunk::{Chunk, OpCode};
use crate::compiler::compile;
use crate::debug::disassemble_instruction;
use crate::value::{Value, print_value};

const STACK_MAX: usize = 256;

pub struct VM {
    pub chunk: Chunk,
    ip: usize,
    stack: [Value; STACK_MAX],
    stack_top: usize,
}

pub enum InterpretResult {
    Ok,
    ComplileError,
    RuntimeError,
}

macro_rules! binary_op {
    ( $vm:ident, $op:tt ) => {
        {
            let b = $vm.pop();
            let a = $vm.pop();
            $vm.push(a $op b);
        }
    }
}

impl VM {
    pub fn new(chunk: Chunk) -> Self {
        VM {
            chunk,
            ip: 0,
            stack: [0.0; STACK_MAX],
            stack_top: 0,
        }
    }

    pub fn push(&mut self, value: Value) {
        self.stack[self.stack_top] = value;
        self.stack_top += 1;
    }

    pub fn pop(&mut self) -> Value {
        self.stack_top -= 1;
        self.stack[self.stack_top]
    }

    pub fn run(&mut self) -> InterpretResult {
        loop {
            let instruction = self.chunk.code[self.ip];
            if env::var("DEBUG_TRACE").is_ok() {
                print!("          ");
                for slot in self.stack.iter() {
                    print!("[ ");
                    print_value(*slot);
                    print!(" ]");
                }
                println!();
                disassemble_instruction(&self.chunk, self.ip);
            }
            self.ip += 1;
            match instruction {
                OpCode::Constant(constant_index) => {
                    self.push(self.chunk.constants[constant_index]);
                }
                OpCode::Negate => {
                    let value = self.pop();
                    self.push(-value);
                }
                OpCode::Return => {
                    print_value(self.pop());
                    println!();
                    return InterpretResult::Ok;
                }
                OpCode::Add => binary_op!(self, +),
                OpCode::Subtract => binary_op!(self, -),
                OpCode::Multiply => binary_op!(self, *),
                OpCode::Divide => binary_op!(self, /),
            }
        }
    }
}

pub fn interpret(source: &str) -> InterpretResult {
    compile(source);
    InterpretResult::Ok
}
