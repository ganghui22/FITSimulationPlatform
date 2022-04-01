from PathPlanningAstar.util_llj.Datatypes import *
import sys



class AStar:
    def __init__(self):
        self.frontier = PriorityQueue()
        self.start = set()
        self.goal = set()
        self.explored = {}
        self.cost = {}


    def heuristic(self, a, b, n=1):
        dx = abs(b[0] - a[0])
        dy = abs(b[1] - a[1])

        # Manhattan Heuristic
        if n == 1:
            return dx + dy

        # Euclidean Heuristic
        elif n == 2:
            return (dx ** 2 + dy ** 2) ** 0.5

        # Chebychev Heuristic
        elif n == 3:
            return max(dx, dy)

        # Octile Heuristic
        else:
            return dx + dy + (2 ** 0.5 - 2) * min(dx, dy)

    def reinit(self):
        self.frontier = PriorityQueue()
        self.start = set()
        self.goal = set()
        self.explored = {}
        self.cost = {}

    def search(self, gridworld, begin, end):
        self.start = begin
        self.goal = end
        self.frontier.put(self.start, 0)

        self.explored[self.start] = None
        self.cost[self.start] = 0

        gridworld.mark(self.start)
        gridworld.markpath(self.start)

        if self.proceed(gridworld) == 1:
            self.makepath()
            return False
        else:
            self.proceed(gridworld)
            return True

    def proceed(self, gridworld):
        if self.frontier.isEmpty():
            return 1

        else:
            current = self.frontier.get()

            if current == self.goal:
                return 1
            # sys.exit()
            for next in gridworld.get8Neighbors(current):
                if next[0] == current[0] or next[1] == current[1]:
                    newcost = self.cost[current] + 5
                else:
                    newcost = self.cost[current] + 7

                if next not in self.cost:
                    self.cost[next] = newcost
                    priority = newcost + self.heuristic(next, self.goal)
                    # print(newself.cost,priority)
                    self.frontier.put(next, priority)
                    gridworld.mark(next)
                    self.explored[next] = current

        return 0

    def makepath(self, gridworld):

        path = []
        current = self.goal
        while current != self.start:
            path.append(current)
            gridworld.markpath(current)
            current = self.explored[current]
        path.reverse()
        path = [self.start] + path
        return path, self.explored, self.cost
