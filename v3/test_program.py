"""Planted defects for v3.2's safeguards. python3 -I v3/test_program.py"""
import sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from program import accept

# a and b define each other; c uses a; d uses itself; e is clean and uses primitives; f uses e.
found = {"a": ("b", "x"), "b": ("a",), "c": ("a", "y"), "d": ("x", "d"), "e": ("x", "y"), "f": ("e", "z")}
ok, rejected = accept(found)
assert rejected == {"a", "b", "c", "d"}, rejected
assert set(ok) == {"e", "f"}, ok
# no programs, and programs over primitives only
assert accept({}) == ({}, set())
assert accept({"p": ("x",)}) == ({"p": ("x",)}, set())
print("planted cycles: a<->b, d->d and c (uses a) rejected; e and f (uses e) kept")
