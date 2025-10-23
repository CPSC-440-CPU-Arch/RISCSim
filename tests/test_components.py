from riscsim.utils.components import *

def test_oneBitAdder(a, b, carry_in, expectation):
    result = oneBitAdder(a, b, carry_in)
    print(f"Expected {expectation} got {result}")



if __name__ == "__main__":
    test_oneBitAdder(0, 0, 0, "[0, 0]")
    test_oneBitAdder(0, 0, 1, "[1, 0]")
    test_oneBitAdder(0, 1, 0, "[1, 0]")
    test_oneBitAdder(0, 1, 1, "[0, 1]")
    test_oneBitAdder(1, 0, 0, "[1, 0]")
    test_oneBitAdder(1, 0, 1, "[0, 1]")
    test_oneBitAdder(1, 1, 0, "[0, 1]")
    test_oneBitAdder(1, 1, 1, "[1, 1]")