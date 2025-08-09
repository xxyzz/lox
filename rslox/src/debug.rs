use crate::chunk::{Chunk, OpCode};
use crate::value::print_value;

pub fn disassemble_chunk(chunk: &Chunk, name: &str) {
    println!("== {name} ==");

    for (offset, instruction) in chunk.code.iter().enumerate() {
        print!("{offset:04} ");
        if offset > 0 && chunk.lines[offset] == chunk.lines[offset - 1] {
            print!("   | ");
        } else {
            print!("{:04} ", chunk.lines[offset]);
        }

        match instruction {
            OpCode::OpConstant(index) => constant_instruction("OpConstant", chunk, *index),
            OpCode::OpReturn => simple_instructon("OpReturn"),
        }
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
