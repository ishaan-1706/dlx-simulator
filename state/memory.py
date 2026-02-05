#state/memory.py
class Memory:
    def __init__(self, size: int = 4096):
        self.mem = [0] * size  # Initialize memory with given size

    def _check_addr(self, address: int, length: int = 1):
        if address < 0 or address + length > len(self.mem):
            raise ValueError(f"Memory access out of bounds: {address}")

    # Load a single byte from memory (unsigned 0-255).
    def load_byte(self, address: int) -> int:
        self._check_addr(address, 1)
        return self.mem[address]

    # Store a single byte to memory (keeps lower 8 bits).
    def store_byte(self, address: int, value: int):
        self._check_addr(address, 1)
        self.mem[address] = value & 0xFF

    # Load a 16-bit halfword (unsigned 0-65535). Address must be halfword-aligned.
    def load_half(self, address: int) -> int:
        if address % 2 != 0:
            raise ValueError('Halfword access must be 2-byte aligned')
        self._check_addr(address, 2)
        return (self.mem[address] << 8) | self.mem[address + 1]

    # Store a 16-bit halfword. Address must be halfword-aligned.
    def store_half(self, address: int, value: int):
        if address % 2 != 0:
            raise ValueError('Halfword access must be 2-byte aligned')
        self._check_addr(address, 2)
        self.mem[address] = (value >> 8) & 0xFF
        self.mem[address + 1] = value & 0xFF

    # Load a 32-bit word (big-endian). Address must be word-aligned.
    def load_word(self, address: int) -> int:
        if address % 4 != 0:
            raise ValueError('Address must be word-aligned')
        self._check_addr(address, 4)
        word = (
            (self.mem[address] << 24)
            | (self.mem[address + 1] << 16)
            | (self.mem[address + 2] << 8)
            | self.mem[address + 3]
        )
        return word
    
    # Store a 32-bit word (big-endian). Address must be word-aligned.
    def store_word(self, address: int, value: int):
        if address % 4 != 0:
            raise ValueError('Address must be word-aligned')
        self._check_addr(address, 4)
        self.mem[address] = (value >> 24) & 0xFF
        self.mem[address + 1] = (value >> 16) & 0xFF
        self.mem[address + 2] = (value >> 8) & 0xFF
        self.mem[address + 3] = value & 0xFF    