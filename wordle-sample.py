#!/Library/Frameworks/Python.framework/Versions/Current/bin/python3
from WordleSolver import Solver

solver = Solver()
solver.guess("arose")
solver.miss("are")
solver.hit("o", 3)
solver.hit("s")
solver.guess("sloth")
solver.miss("lh")
solver.hit("s", 1)
solver.hit("t")
solver.guess("stowp")
solver.miss("w")
solver.hit("t", 2)
solver.hit("p", 5)
#solver.guess("booth")
#solver.hit("t",4)
#solver.miss("bh")
print("YOUR NEXT GUESS SHOULD BE: " + solver.next_guess(True))
#print("INCLUSIVE: " + solver.next_guess(True))
#print("ALL EXCLUSIVE:")
#print(solver.matches())
print("ALL INCLUSIVE:")
print(solver.matches(True))
