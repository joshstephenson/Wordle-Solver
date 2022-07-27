#!/Library/Frameworks/Python.framework/Versions/Current/bin/python3
from WordleSolver import Solver

solver = Solver()
solver.guess("irate")
solver.hit("t",4)
solver.miss("irae")
solver.guess("clons")
solver.hit("o")
solver.miss("clns")
solver.guess("dumpy")
solver.hit("m")
solver.miss("dupy")
solver.guess("booth")
solver.hit("o",2)
solver.miss("bh")
print("YOUR NEXT GUESS SHOULD BE:")
print("EXCLUSIVE: " + solver.next_guess(False))
print("INCLUSIVE: " + solver.next_guess(True))
print("ALL EXCLUSIVE:")
print(solver.matches())
print("ALL INCLUSIVE:")
print(solver.matches(True))

