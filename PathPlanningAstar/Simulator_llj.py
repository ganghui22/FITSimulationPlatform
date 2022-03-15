# from ConfigFileReader import *
from PathPlanningAstar.util_llj import Init
from PathPlanningAstar.util_llj.Dijkstra import *
# from Interface import *
from PathPlanningAstar.util_llj.AStar import *
from PathPlanningAstar.util_llj.BFS import *
import sys
sys.setrecursionlimit(100000) #例如这里设置为十万



class search():
	def __init__(self,start,goal,map):
		self.map=map
		self.width, self.height, self.obstacles = self.map.width, self.map.height, self.map.obscale
		self.start=start
		self.goal=goal
		self.algoflag=3
		self.initializer = Init.Initialize(self.height, self.width, self.obstacles)
		self.flag=False
		self.p=[]
		self.cost=0
	def make_path(self):
		if self.initializer.gridworld.cells[self.goal[0]][self.goal[1]].obstacle == True:
			raise ('Goal is an obstacle!')

		if self.initializer.gridworld.cells[self.start[0]][self.start[1]].obstacle == True:
			raise ('Start is an obstacle!')
		self.initializer.gridworld.isstart(self.start)
		self.initializer.gridworld.isgoal(self.goal)
		while self.flag==False:
			if self.algoflag == 1:
				self.path = BFS().search(self.initializer.gridworld, self.start, self.goal)
			elif self.algoflag == 2:
				self.path = Dijkstra().search(self.initializer.gridworld, self.start, self.goal)
			else:
				self.path = AStar().search(self.initializer.gridworld, self.start, self.goal)
			self.run()
		print('Path found!')
		print('The path is:', self.p)
		print('The cost is:', self.cost[self.goal])
		# print('GUI will exit in:',t,'seconds')
		# time.sleep(t)
		# sys.exit()
		return self.p
		
	def run(self):

		if self.path== True and self.initializer.gridworld.cells[self.goal[0]][self.goal[1]].visited==False:
			if self.algoflag == 1:
				BFS().search(self.initializer.gridworld, self.start, self.goal)
			elif self.algoflag == 2:
				Dijkstra().search(self.initializer.gridworld, self.start, self.goal)
			else:
				AStar().search(self.initializer.gridworld, self.start, self.goal)

		else:
			if self.algoflag == 1:
				self.p, self.explored, self.cost= BFS().makepath(self.initializer.gridworld)
			elif self.algoflag == 2:
				self.p, self.explored, self.cost= Dijkstra().makepath(self.initializer.gridworld)
			else:
				self.p, self.explored, self.cost= AStar().makepath(self.initializer.gridworld)
			self.flag=True
		print(self.flag)




if __name__ == '__main__':
	path_search=search(start=(1700, 155),goal=(1470, 1821))
	path_search.make_path()

