def serve_chai():
    yield "Cup 1: Masala Chai"
    yield "Cup 2: Green Tea"
    yield "Cup 3: Lemon Tea"


stall=serve_chai()
print(next(stall))