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
        OpCode::Constant(index) => constant_instruction("Constant", chunk, index),
        OpCode::Negate => simple_instructon("Negate"),
        OpCode::Return => simple_instructon("Return"),
        OpCode::Add => simple_instructon("Add"),
        OpCode::Subtract => simple_instructon("Substract"),
        OpCode::Multiply => simple_instructon("Multiplay"),
        OpCode::Divide => simple_instructon("Divide"),
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
