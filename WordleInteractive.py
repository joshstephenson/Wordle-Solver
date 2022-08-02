#!/Library/Frameworks/Python.framework/Versions/Current/bin/python3
from WordleSolver import Solver

solver = Solver()
solver.guess("oater", None, "atr")
solver.guess("lysin", None, None)
print("Your next guess should be: " + solver.next_guess())
