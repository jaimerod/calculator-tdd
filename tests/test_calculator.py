import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from calculator import add, subtract, multiply, divide

def test_adds_two_positive_numbers():
    assert add(2, 3) == 5

def test_subtracts_two_numbers():
    assert subtract(5, 3) == 2

def test_multiplies_two_numbers():
    assert multiply(4, 3) == 12

def test_divides_two_numbers():
    assert divide(10, 2) == 5

def test_division_by_zero_raises_error():
    try:
        divide(10, 0)
        assert False, "Should have raised an error"
    except ZeroDivisionError:
        pass

def test_adds_negative_numbers():
    assert add(-5, 3) == -2
    assert add(-5, -3) == -8

if __name__ == '__main__':
    tests = [
        test_adds_two_positive_numbers,
        test_subtracts_two_numbers,
        test_multiplies_two_numbers,
        test_divides_two_numbers,
        test_division_by_zero_raises_error,
        test_adds_negative_numbers
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            print(f"PASS: {test.__name__}")
            passed += 1
        except Exception as e:
            print(f"FAIL: {test.__name__} - {e}")
            failed += 1
    
    print(f"\n{passed} passed, {failed} failed")
    if failed > 0:
        sys.exit(1)