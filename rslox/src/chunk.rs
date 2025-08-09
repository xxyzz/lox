use crate::value::Value;

#[derive(Debug, Clone, Copy)]
pub enum OpCode {
    OpConstant(usize),
    OpReturn,
}

pub struct Chunk {
    pub code: Vec<OpCode>,
    pub constants: Vec<Value>,
    pub lines: Vec<usize>,
}

impl Chunk {
    pub fn new() -> Self {
        Chunk {
            code: vec![],
            constants: vec![],
            lines: vec![],
        }
    }

    pub fn write(&mut self, opcode: OpCode, line: usize) {
        self.code.push(opcode);
        self.lines.push(line);
    }

    pub fn add_constant(&mut self, value: Value, line: usize) {
        self.constants.push(value);
        self.write(OpCode::OpConstant(self.constants.len() - 1), line);
    }
}
