def encode_action(block_index, x, y, grid_size=8):
    """
    Encode aksi ke dalam 1 bilangan bulat:
    block_index ∈ [0, 2], x ∈ [0,7], y ∈ [0,7]
    """
    assert 0 <= block_index <= 2, "block_index harus 0, 1, atau 2"
    assert 0 <= x < grid_size and 0 <= y < grid_size, "x/y di luar batas"
    return block_index * (grid_size * grid_size) + y * grid_size + x

def decode_action(action_index, grid_size=8):
    """
    Decode bilangan menjadi (block_index, x, y)
    """
    block_index = action_index // (grid_size * grid_size)
    rem = action_index % (grid_size * grid_size)
    y, x = divmod(rem, grid_size)
    return block_index, x, y


# Contoh:
if __name__ == "__main__":
    for bi in range(3):
        for x in range(8):
            for y in range(8):
                idx = encode_action(bi, x, y)
                bi2, x2, y2 = decode_action(idx)
                assert (bi, x, y) == (bi2, x2, y2), "Mismatch!"
