use crate::chunk::{Chunk, OpCode};
use crate::value::print_value;

pub fn disassemble_chunk(chunk: &Chunk, name: &str) {
    println!("== {name} ==");

    for index in 0..chunk.code.len() {
        disassemble_instruction(chunk, index);
    }
}

pub fn disassemble_instruction(chunk: &Chunk, offset: usize) {
    print!("{offset:04} ");
    if offset > 0 && chunk.lines[offset] == chunk.lines[offset - 1] {
        print!("   | ");
    } else {
        print!("{:04} ", chunk.lines[offset]);
    }

    match chunk.code[offset] {
        OpCode::OpConstant(index) => constant_instruction("OpConstant", chunk, index),
        OpCode::OpNegate => simple_instructon("OpNegate"),
        OpCode::OpReturn => simple_instructon("OpReturn"),
        OpCode::OpAdd => simple_instructon("OpAdd"),
        OpCode::OpSubtract => simple_instructon("OpSubstract"),
        OpCode::OpMultiply => simple_instructon("OpMultiplay"),
        OpCode::OpDivide => simple_instructon("OpDivide"),
    }
}

fn simple_instructon(name: &str) {
    println!("{name}");
}

fn constant_instruction(name: &str, chunk: &Chunk, index: usize) {
    print!("{name:<16} {index:4} '");
    print_value(chunk.constants[index]);
    println!("'");
}
