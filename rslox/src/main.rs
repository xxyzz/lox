mod chunk;
mod debug;
mod value;
mod vm;

use crate::chunk::{Chunk, OpCode};
use crate::vm::VM;

fn main() {
    let chunk = Chunk::new();
    let mut vm = VM::new(chunk);

    vm.chunk.add_constant(2.0, 123);
    vm.chunk.add_constant(1.0, 123);
    vm.chunk.write(OpCode::OpMultiply, 123);
    vm.chunk.add_constant(3.0, 123);
    vm.chunk.write(OpCode::OpAdd, 123);

    vm.chunk.write(OpCode::OpReturn, 123);

    vm.run();
}
