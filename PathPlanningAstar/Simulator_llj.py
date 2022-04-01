# from ConfigFileReader import *
from PathPlanningAstar.util_llj import Init
from PathPlanningAstar.util_llj.AStar import *
import sys
from PathPlanningAstar.astar import Map

sys.setrecursionlimit(100000)  # 例如这里设置为十万


class search():
    def __init__(self, map):
        self.search = None
        self.initializer = None
        self.obstacles = None
        self.height = None
        self.width = None
        self.flag = None
        self.cost = None
        self.explored = None
        self.p = None
        self.path = None
        self.goal = None
        self.start = None
        self.map = map

    def reint(self):
        """
        增加重设参数,进行下一次循环

        """
        self.map.reinit()
        self.width, self.height, self.obstacles = self.map.width, self.map.height, self.map.obscale
        self.initializer = Init.Initialize(self.height, self.width, self.obstacles)
        self.flag = False
        self.p = []
        self.cost = 0
        self.search = AStar()

    def make_path(self, start, goal):
        self.reint()
        self.start = start
        self.goal = goal
        if self.initializer.gridworld.cells[self.goal[0]][self.goal[1]].obstacle:
            raise 'Goal is an obstacle!'

        if self.initializer.gridworld.cells[self.start[0]][self.start[1]].obstacle:
            raise 'Start is an obstacle!'
        self.initializer.gridworld.isstart(self.start)
        self.initializer.gridworld.isgoal(self.goal)

        while not self.flag:
            self.path = self.search.search(self.initializer.gridworld, self.start, self.goal)
            self.run()
        return self.p

    def run(self):

        if self.path and not self.initializer.gridworld.cells[self.goal[0]][self.goal[1]].visited:
            self.search.search(self.initializer.gridworld, self.start, self.goal)

        else:
            self.p, self.explored, self.cost = self.search.makepath(self.initializer.gridworld)
            self.flag = True


if __name__ == '__main__':
    path_map = Map()
    a = search(map=path_map)
    print(a.make_path(start=(920, 1614), goal=(1700, 154)))
    # a=search(map=path_map)
    print(1)
    print(a.make_path(start=(1700, 154), goal=(1470, 1820)))
