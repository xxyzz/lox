use std::env;

use crate::chunk::{Chunk, OpCode};
use crate::compiler::Compiler;
use crate::debug::disassemble_instruction;
use crate::value::Value;

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
    ( $vm:ident, $value_constructor:expr, $op:tt ) => {
        {
            let p_b = $vm.peek(0);
            let p_a = $vm.peek(1);
            if let Value::Number(a) = p_a && let Value::Number(b) = p_b {
                $vm.pop();
                $vm.pop();
                $vm.push($value_constructor(a $op b));
            } else {
                $vm.runtime_error("Operands must be numbers.");
                return InterpretResult::RuntimeError;
            }
        }
    }
}

impl VM {
    pub fn new() -> Self {
        VM {
            chunk: Chunk::new(),
            ip: 0,
            stack: [Value::Number(0.0); STACK_MAX],
            stack_top: 0,
        }
    }

    fn runtime_error(&self, message: &str) {
        eprintln!("{message}");
        eprintln!("[line {}] in script", self.chunk.lines[self.ip - 1]);
    }

    fn push(&mut self, value: Value) {
        self.stack[self.stack_top] = value;
        self.stack_top += 1;
    }

    fn pop(&mut self) -> Value {
        self.stack_top -= 1;
        self.stack[self.stack_top]
    }

    fn run(&mut self) -> InterpretResult {
        loop {
            let instruction = self.chunk.code[self.ip];
            if env::var("DEBUG_TRACE_EXECUTION").is_ok() {
                print!("          ");
                for slot in self.stack.iter() {
                    print!("[ {} ]", slot);
                }
                println!();
                disassemble_instruction(&self.chunk, self.ip);
            }
            self.ip += 1;
            match instruction {
                OpCode::Constant(constant_index) => {
                    self.push(self.chunk.constants[constant_index]);
                }
                OpCode::Nil => self.push(Value::Nil),
                OpCode::True => self.push(Value::Bool(true)),
                OpCode::False => self.push(Value::Bool(false)),
                OpCode::Equal => {
                    let b = self.pop();
                    let a = self.pop();
                    self.push(Value::Bool(a == b));
                }
                OpCode::Greater => binary_op!(self, Value::Bool, >),
                OpCode::Less => binary_op!(self, Value::Bool, <),
                OpCode::Add => binary_op!(self, Value::Number, +),
                OpCode::Subtract => binary_op!(self, Value::Number, -),
                OpCode::Multiply => binary_op!(self, Value::Number, *),
                OpCode::Divide => binary_op!(self, Value::Number, /),
                OpCode::Not => {
                    let v = self.pop();
                    self.push(Value::Bool(self.is_falsey(v)))
                }
                OpCode::Negate => {
                    let value = self.peek(0);
                    if let Value::Number(num) = value {
                        self.pop();
                        self.push(Value::Number(-num));
                    } else {
                        self.runtime_error("Operand must be a number.");
                        return InterpretResult::RuntimeError;
                    }
                }
                OpCode::Return => {
                    println!("{}", self.pop());
                    return InterpretResult::Ok;
                }
            }
        }
    }

    pub fn interpret(&mut self, source: &str) -> InterpretResult {
        let mut compiler = Compiler::new(source);
        if let Some(chunk) = compiler.compile() {
            self.chunk = chunk;
        } else {
            return InterpretResult::ComplileError;
        }
        self.run()
    }

    fn peek(&self, distance: usize) -> Value {
        self.stack[self.stack_top - 1 - distance]
    }

    fn is_falsey(&self, value: Value) -> bool {
        match value {
            Value::Nil => true,
            Value::Bool(b) => !b,
            _ => true,
        }
    }
}
