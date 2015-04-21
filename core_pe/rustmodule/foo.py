import ctypes

p = 'target/release/libblock-b7b66d53f276d597.so'
imgp = b'/home/hsoft/src/dupeguru/images/dgme_logo_128.png'
block = ctypes.CDLL(p)
s = ctypes.create_string_buffer(imgp)
print(repr(block.block(imgp)))

