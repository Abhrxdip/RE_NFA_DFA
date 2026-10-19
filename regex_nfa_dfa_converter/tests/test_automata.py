"""
Automated Test Suite for the Regex-NFA-DFA Converter
====================================================

Tests all core modules: regex_parser, thompson, subset_construction, simulator.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from regex_parser import parse_regex, validate_regex, tokenize
from thompson import thompson_construct, reset_state_counter
from subset_construction import subset_construction, reset_dfa_state_counter
from simulator import simulate_dfa


def run_test(regex, input_string, expected_accept, test_id):
    """Run a single test case and return the result."""
    reset_state_counter()
    reset_dfa_state_counter()

    ast = parse_regex(regex)
    nfa = thompson_construct(ast)
    dfa = subset_construction(nfa)
    result = simulate_dfa(dfa, input_string)

    display_input = input_string if input_string else 'ε'
    status = "PASS" if result['accepted'] == expected_accept else "FAIL"
    expected_str = "Accepted" if expected_accept else "Rejected"
    actual_str = "Accepted" if result['accepted'] else "Rejected"

    print(f"  {test_id:<8} | Regex: {regex:<15} | Input: {display_input:<10} | "
          f"Expected: {expected_str:<10} | Actual: {actual_str:<10} | {status}")

    return status == "PASS"


def test_validation():
    """Test regex validation."""
    print("\n" + "=" * 70)
    print("TEST: Regular Expression Validation")
    print("=" * 70)

    cases = [
        ("", "Empty regular expression."),
        ("(a", "Unmatched opening parenthesis"),
        ("a)", "Unmatched closing parenthesis"),
        ("()", "Empty parentheses"),
        ("|a", "Union operator '|' at position 0"),
        ("a|", "has no right operand"),
        ("*a", "Kleene star '*' at position 0"),
        ("a|*b", "Kleene star '*' at position 2"),
        ("a+b", "Invalid character '+'"),
        ("a", None),
        ("a|b", None),
        ("(a|b)*abb", None),
        ("a*", None),
    ]

    passed = 0
    total = len(cases)
    for regex, expected_error_substr in cases:
        result = validate_regex(regex)
        display = repr(regex)
        if expected_error_substr is None:
            if result is None:
                print(f"  PASS | {display:<20} → Valid")
                passed += 1
            else:
                print(f"  FAIL | {display:<20} → Expected valid, got: {result}")
        else:
            if result and expected_error_substr in result:
                print(f"  PASS | {display:<20} → Error: {result}")
                passed += 1
            else:
                print(f"  FAIL | {display:<20} → Expected error containing '{expected_error_substr}', got: {result}")

    print(f"\nValidation: {passed}/{total} tests passed.")
    return passed == total


def test_single_char():
    """Test: regex = a"""
    print("\n" + "=" * 70)
    print("TEST: Single Character — a")
    print("=" * 70)
    tests = [
        ("a", "a", True, "TC-01"),
        ("a", "b", False, "TC-02"),
        ("a", "", False, "TC-03"),
        ("a", "aa", False, "TC-04"),
    ]
    return all(run_test(*t) for t in tests)


def test_union():
    """Test: regex = a|b"""
    print("\n" + "=" * 70)
    print("TEST: Union — a|b")
    print("=" * 70)
    tests = [
        ("a|b", "a", True, "TC-05"),
        ("a|b", "b", True, "TC-06"),
        ("a|b", "ab", False, "TC-07"),
        ("a|b", "", False, "TC-08"),
        ("a|b", "c", False, "TC-09"),
    ]
    return all(run_test(*t) for t in tests)


def test_concat():
    """Test: regex = ab"""
    print("\n" + "=" * 70)
    print("TEST: Concatenation — ab")
    print("=" * 70)
    tests = [
        ("ab", "ab", True, "TC-10"),
        ("ab", "a", False, "TC-11"),
        ("ab", "b", False, "TC-12"),
        ("ab", "ba", False, "TC-13"),
        ("ab", "", False, "TC-14"),
    ]
    return all(run_test(*t) for t in tests)


def test_kleene_star():
    """Test: regex = a*"""
    print("\n" + "=" * 70)
    print("TEST: Kleene Star — a*")
    print("=" * 70)
    tests = [
        ("a*", "", True, "TC-15"),
        ("a*", "a", True, "TC-16"),
        ("a*", "aaaa", True, "TC-17"),
        ("a*", "b", False, "TC-18"),
        ("a*", "ab", False, "TC-19"),
    ]
    return all(run_test(*t) for t in tests)


def test_complex():
    """Test: regex = (a|b)*abb"""
    print("\n" + "=" * 70)
    print("TEST: Complex — (a|b)*abb")
    print("=" * 70)
    tests = [
        ("(a|b)*abb", "abb", True, "TC-20"),
        ("(a|b)*abb", "aabb", True, "TC-21"),
        ("(a|b)*abb", "babb", True, "TC-22"),
        ("(a|b)*abb", "aababb", True, "TC-23"),
        ("(a|b)*abb", "ab", False, "TC-24"),
        ("(a|b)*abb", "aba", False, "TC-25"),
        ("(a|b)*abb", "", False, "TC-26"),
        ("(a|b)*abb", "a", False, "TC-27"),
        ("(a|b)*abb", "bb", False, "TC-28"),
    ]
    return all(run_test(*t) for t in tests)


def test_nested():
    """Test: regex with nested parentheses"""
    print("\n" + "=" * 70)
    print("TEST: Nested Parentheses — ((a|b))*")
    print("=" * 70)
    tests = [
        ("((a|b))*", "", True, "TC-29"),
        ("((a|b))*", "a", True, "TC-30"),
        ("((a|b))*", "b", True, "TC-31"),
        ("((a|b))*", "abab", True, "TC-32"),
        ("((a|b))*", "c", False, "TC-33"),
    ]
    return all(run_test(*t) for t in tests)


def test_additional():
    """Test additional patterns."""
    print("\n" + "=" * 70)
    print("TEST: Additional Patterns")
    print("=" * 70)
    tests = [
        ("a*b*", "", True, "TC-34"),
        ("a*b*", "a", True, "TC-35"),
        ("a*b*", "b", True, "TC-36"),
        ("a*b*", "ab", True, "TC-37"),
        ("a*b*", "aabb", True, "TC-38"),
        ("a*b*", "ba", False, "TC-39"),
        ("(ab)*", "", True, "TC-40"),
        ("(ab)*", "ab", True, "TC-41"),
        ("(ab)*", "abab", True, "TC-42"),
        ("(ab)*", "a", False, "TC-43"),
        ("(ab)*", "aba", False, "TC-44"),
    ]
    return all(run_test(*t) for t in tests)


def main():
    """Run all tests."""
    print("=" * 70)
    print(" REGEX → NFA → DFA CONVERTER — AUTOMATED TEST SUITE")
    print("=" * 70)

    results = [
        ("Validation", test_validation()),
        ("Single Char", test_single_char()),
        ("Union", test_union()),
        ("Concatenation", test_concat()),
        ("Kleene Star", test_kleene_star()),
        ("Complex (a|b)*abb", test_complex()),
        ("Nested Parentheses", test_nested()),
        ("Additional Patterns", test_additional()),
    ]

    print("\n" + "=" * 70)
    print(" SUMMARY")
    print("=" * 70)
    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {name:<30} {status}")
        if not passed:
            all_passed = False

    if all_passed:
        print(f"\n  🎉 ALL TEST SUITES PASSED!")
    else:
        print(f"\n  ⚠️  SOME TESTS FAILED!")

    print("=" * 70)
    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())
