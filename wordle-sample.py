#!/Library/Frameworks/Python.framework/Versions/Current/bin/python3
from WordleSolver import Solver

solver = Solver()
solver.guess("irate")
solver.miss("irae")
solver.hit("t", 4)
solver.guess("clots")
solver.hit("o")
solver.miss("cls")
solver.guess("punto")
solver.hit("o", 5)
solver.miss("pun")
#solver.guess("booth")
#solver.hit("t",4)
#solver.miss("bh")
print("YOUR NEXT GUESS SHOULD BE: " + solver.next_guess(True))
#print("INCLUSIVE: " + solver.next_guess(True))
#print("ALL EXCLUSIVE:")
#print(solver.matches())
#print("ALL INCLUSIVE:")
#print(solver.matches(True))

