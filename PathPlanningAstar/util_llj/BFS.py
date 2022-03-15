from PathPlanningAstar.util_llj.Datatypes import *
import sys

frontier = Queue()
start = set()
goal = set()
explored = {}
cost = {}

class BFS:
	def __init__(self):
		pass

	def search(self,gridworld,begin,end):
		global frontier
		global start, goal, explored, cost

		start = begin ; goal = end
		frontier.put(start)

		explored[start]=None
		cost[start]=0

		gridworld.mark(start)
		gridworld.markpath(start)
		
		
		if self.proceed(gridworld) == 1:
			self.makepath()
			return False
		else:
			self.proceed(gridworld)
			return True
		
	def proceed(self,gridworld):
		global frontier
		global start, goal, explored, cost
		
		if frontier.isEmpty():
			return 1
		
		else:
			current=frontier.get()

			if current==goal:
				return 1
				# sys.exit()
			for next in gridworld.get8Neighbors(current):
				if next not in cost:
					if next[0]==current[0] or next[1] == current[1]:
						cost[next]=cost[current] + 5
					else:
						cost[next]=cost[current] + 7 
					frontier.put(next)
					gridworld.mark(next)
					explored[next]=current
		return 0

	def makepath(self,gridworld):
		global goal, explored,cost,start
		path = []
		current = goal
		while current != start:
			path.append(current)
			gridworld.markpath(current)
			current = explored[current]
		path.reverse() ; path=[start]+path
		return path,explored,cost