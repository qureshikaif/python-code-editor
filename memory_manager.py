class MemoryManager:
    def __init__(self, size):
        self.size = size
        self.memory = [0] * size  # Simulated memory
        self.blocks = [(0, size)]  # Start with one large block

    def best_fit_allocate(self, request_size):
        # Find the best fitting block
        best_index = -1
        best_size = self.size + 1

        for index, (start, size) in enumerate(self.blocks):
            if size >= request_size and size < best_size:
                best_index = index
                best_size = size

        if best_index == -1:
            return None  # No suitable block found

        start, size = self.blocks[best_index]
        self.blocks.pop(best_index)

        if size > request_size:
            self.blocks.append((start + request_size, size - request_size))

        self.memory[start:start + request_size] = [1] * request_size  # Allocate memory
        return start

    def deallocate(self, start, size):
        self.memory[start:start + size] = [0] * size  # Free memory
        self.blocks.append((start, size))
        self.blocks = sorted(self.blocks)

        # Merge adjacent free blocks
        merged_blocks = []
        for block in self.blocks:
            if merged_blocks and merged_blocks[-1][0] + merged_blocks[-1][1] == block[0]:
                merged_blocks[-1] = (merged_blocks[-1][0], merged_blocks[-1][1] + block[1])
            else:
                merged_blocks.append(block)

        self.blocks = merged_blocks
