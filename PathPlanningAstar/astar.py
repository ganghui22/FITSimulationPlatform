#!/usr/bin/env python

import heapq as hq
from PIL import Image
import math


def radians(degree):
    return degree * math.pi / 180


SIMILARITY_THRESHOLD = 0.1
SAFETY_OFFSET = 5  # number of pixels away from the wall the robot should remain

ROBOT_SIZE = 0.1
G_MULTIPLIER = 0.2
MOVES = [(0.2, radians(0)),  # move ahead
         (-0.2, radians(0)),  # move backwards
         (0, radians(90)),  # turn left
         (0, -radians(90))  # turn left
         ]  # turn right
TOLERANCE = 0.2


class PathPlanner:
    def __init__(self, start, theta, goal):
        print("building map....")
        self.map = Map().grid_map
        self.start = start
        self.theta = theta
        self.goal = goal
        print("map built. planner initialized")

    def plan(self):
        final = self.a_star(self.start, self.goal, self.map)
        if final is None:
            print("Path not found.")
        else:
            print("Constructing path..")
            path = self.construct_path(final)  # path in world coordinates
            points = []
            for step in path:
                points.append((step.x, step.y))
            points.reverse()
            points = points[1:]
            points.append((self.goal.x, self.goal.y))
            translate_x = points[0][0]
            translate_y = points[0][1]
            for p in range(len(points)):
                new_x = points[p][0] - translate_x
                new_y = points[p][1] - translate_y
                if self.theta == math.pi / 2:
                    points[p] = [-new_y, new_x]
                elif self.theta == math.pi:
                    points[p] = [-new_x, -new_y]
                elif self.theta == -math.pi / 2:
                    points[p] = [new_y, -new_x]
                else:
                    points[p] = [new_x, new_y]
        return path

    def construct_path(self, end):
        """
        backtrack from end to construct path
        """
        current = end
        path = []  # path needs to be in world coordinates
        while current is not None:
            path.append(current)
            current = current.parent
        return path

    @classmethod
    def a_star(cls, start, end, grid_map):
        # start, end are in world coordinates and Node objects

        # before starting A star, check if goal is reachable - ie, in an obstacle free zone - if not, directly reject
        if not end.is_valid(grid_map):
            print("goal invalid")
            return None
        print("goal valid")
        opened = []
        closed = []
        final = None
        hq.heappush(opened, (0.0, start))
        i = 0

        while (final == None) and opened:
            print('1')
            i += 1
            q = hq.heappop(opened)[1]
            for move in MOVES:  # move is in world coordinates
                if (q.is_move_valid(grid_map, move)):
                    next_node = q.apply_move(move)  # Node is returned in world coordinates
                else:
                    next_node = None
                # print("next node is : ", next_node)
                if next_node != None:
                    if next_node.euclidean_distance(end) < TOLERANCE:
                        next_node.parent = q
                        final = next_node
                        break
                    # update heuristics h(n) and g(n)
                    next_node.h = next_node.euclidean_distance(end)
                    next_node.g = q.g + next_node.euclidean_distance(q)
                    # f(n) = h(n) + g(n)
                    next_node.f = G_MULTIPLIER * next_node.g + next_node.h
                    next_node.parent = q

                    # other candidate locations to put in the heap
                    potential_open = any(
                        other_f <= next_node.f and other_next.is_similar(next_node) for other_f, other_next in opened)

                    if not potential_open:
                        potential_closed = any(
                            other_next.is_similar(next_node) and other_next.f <= next_node.f for other_next in closed)
                        if not potential_closed:
                            try:
                                hq.heappush(opened, (next_node.f, next_node))
                            except:
                                pass
            closed.append(q)

        return final


class Map:
    """
    The Map class - this builds a map from a given map image
    Given map image is a binary image - it is already an occupancy grid map
    Coordinates must be converted from pixels to world when used
    For each pixel on the map, store value of the pixel - true if pixel obstacle-free,
    false otherwise
    """

    def __init__(self):
        """
        Construct an occupancy grid map from the image
        """
        self.map_image = Image.open('./PathPlanningAstar/middle.png')
        self.width, self.height = self.map_image.size
        print(self.map_image.size)
        self.pixels = self.map_image.load()
        self.grid_map = []
        for x in range(self.width):
            row = []
            for y in range(self.height):
                if self.pixels[x, y] == 0:
                    row.append(False)
                else:
                    row.append(True)
            self.grid_map.append(row)


class Node:
    def __init__(self, x, y, theta=0.0, parent=None):
        self.x = x
        self.y = y
        self.theta = theta
        self.parent = parent
        # f(n) = h(n) + g(n)
        self.f = 0
        self.h = 0
        self.g = 0

    def euclidean_distance(self, goal):
        """
        Method to compute distance from current position to the goal
        @arg	goal 	Node object with x, y, theta
        @returns 	euclidean distance from current point to goal
        """
        return math.sqrt(math.pow((goal.x - self.x), 2) + math.pow((goal.y - self.y), 2))

    def apply_move(self, move):
        """
        Apply the given move to current position
        @arg 	move 	[length, dtheta]
        """
        theta_new = self.theta + move[1]
        x_new = self.x + math.cos(theta_new) * move[0]  # d.cos(theta)
        y_new = self.y + math.sin(theta_new) * move[0]  # d.sin(theta)
        return Node(x_new, y_new, theta_new)

    def is_move_valid(self, grid_map, move):
        """
        Return true if required move is legal
        """
        goal = self.apply_move(move)
        # convert goal coordinates to pixel coordinates before checking this
        goal_pixel = world_to_pixel((goal.x, goal.y), (2309, 2034))
        # check if too close to the walls

        if goal_pixel[0] >= SAFETY_OFFSET and not grid_map[goal_pixel[0] - SAFETY_OFFSET][goal_pixel[1]]:
            return False
        if goal_pixel[1] >= SAFETY_OFFSET and not grid_map[goal_pixel[0]][goal_pixel[1] - SAFETY_OFFSET]:
            return False
        if goal_pixel[0] >= SAFETY_OFFSET and goal_pixel[1] >= SAFETY_OFFSET and not \
                grid_map[goal_pixel[0] - SAFETY_OFFSET][goal_pixel[1] - SAFETY_OFFSET]:
            return False
        if grid_map[goal_pixel[0]][goal_pixel[1]]:
            return True
        return False

    def is_valid(self, grid_map):
        """
        Return true if the location on the map is valid, ie, in obstacle free zone
        """
        goal_pixel = world_to_pixel((self.x, self.y), (700, 2000))
        if grid_map[goal_pixel[0]][goal_pixel[1]]:
            return True
        return False

    def is_similar(self, other):
        """
        Return true if other node is in similar position as current node
        """
        return self.euclidean_distance(other) <= SIMILARITY_THRESHOLD


def world_to_pixel(world_points, image_size):
    """接入自己的api"""
    img_h = 2034
    img_w = 2309
    origin_x = -4
    origin_y = -79.9708
    resolution = 0.05
    pixel_points = []
    loc_x = world_points[0]
    loc_y = world_points[1]
    loc_x_pix = int((loc_x - origin_x) / resolution)
    pixel_points.append(loc_x_pix)
    loc_y_pix = int(img_h - (loc_y - origin_y) / resolution)
    pixel_points.append(loc_y_pix)
    return pixel_points
