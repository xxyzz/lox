mod chunk;
mod debug;
mod value;

use crate::chunk::{Chunk, OpCode};
use crate::debug::disassemble_chunk;

fn main() {
    let mut chunk = Chunk::new();

    chunk.add_constant(1.2, 123);
    chunk.write(OpCode::OpReturn, 123);
    disassemble_chunk(&chunk, "test chunk");
}
