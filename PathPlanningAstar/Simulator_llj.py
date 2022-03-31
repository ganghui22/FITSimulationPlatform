# from ConfigFileReader import *
from PathPlanningAstar.util_llj import Init
from PathPlanningAstar.util_llj.Dijkstra import *
# from Interface import *
from PathPlanningAstar.util_llj.AStar import *
from PathPlanningAstar.util_llj.BFS import *
import sys
from PathPlanningAstar.astar import Map

sys.setrecursionlimit(100000)  # 例如这里设置为十万


class search():
    def __init__(self, map):
        self.map = map
        self.width, self.height, self.obstacles = self.map.width, self.map.height, self.map.obscale
        self.algoflag = 3
        self.initializer = Init.Initialize(self.height, self.width, self.obstacles)
        self.flag = False
        self.p = []
        self.cost = 0

    def make_path(self,start, goal):
        self.start = start
        self.goal = goal
        if self.initializer.gridworld.cells[self.goal[0]][self.goal[1]].obstacle == True:
            raise ('Goal is an obstacle!')

        if self.initializer.gridworld.cells[self.start[0]][self.start[1]].obstacle == True:
            raise ('Start is an obstacle!')
        self.initializer.gridworld.isstart(self.start)
        self.initializer.gridworld.isgoal(self.goal)
        while self.flag == False:
            if self.algoflag == 1:
                self.path = BFS().search(self.initializer.gridworld, self.start, self.goal)
            elif self.algoflag == 2:
                self.path = Dijkstra().search(self.initializer.gridworld, self.start, self.goal)
            else:
                self.path = AStar().search(self.initializer.gridworld, self.start, self.goal)
            self.run()
        return self.p

    def run(self):

        if self.path == True and self.initializer.gridworld.cells[self.goal[0]][self.goal[1]].visited == False:
            if self.algoflag == 1:
                BFS().search(self.initializer.gridworld, self.start, self.goal)
            elif self.algoflag == 2:
                Dijkstra().search(self.initializer.gridworld, self.start, self.goal)
            else:
                AStar().search(self.initializer.gridworld, self.start, self.goal)

        else:
            if self.algoflag == 1:
                self.p, self.explored, self.cost = BFS().makepath(self.initializer.gridworld)
            elif self.algoflag == 2:
                self.p, self.explored, self.cost = Dijkstra().makepath(self.initializer.gridworld)
            else:
                self.p, self.explored, self.cost = AStar().makepath(self.initializer.gridworld)
            self.flag = True


if __name__ == '__main__':
    path_map = Map()
    a=search(map=path_map)
    print(a.make_path(start=(920, 1614), goal=(1700, 154)))
    print(1)
    print(a.make_path(start=(1700, 154), goal=(1470, 1820)))
