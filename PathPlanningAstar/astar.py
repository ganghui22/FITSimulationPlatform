#!/usr/bin/env python

import heapq as hq
from PIL import Image
import math
import cv2


class Map:
    """
    The Map class - this builds a map from a given map image
    Given map image is a binary image - it is already an occupancy grid map
    Coordinates must be converted from pixels to world when used
    For each pixel on the map, store value of the pixel - true if pixel obstacle-free,
    false otherwise
    """

    def __init__(self, mapPath):
        """
        Construct an occupancy grid map from the image
        """
        self.map_image = Image.open(mapPath)  # PathPlanningAstar/middle.png
        self.width, self.height = self.map_image.size
        self.pixels = self.map_image.load()
        self.grid_map = []
        self.obscale = []
        for x in range(self.width):
            row = []
            for y in range(self.height):
                if self.pixels[x, y] == 0:
                    row.append(False)
                    self.obscale.append([x, y])
                else:
                    row.append(True)
            self.grid_map.append(row)
        self.obscale_start = self.obscale

    def reinit(self):
        self.obscale = self.obscale_start


def world_to_pixel(world_points):
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


def smooth_path2(path):
    from scipy.signal import savgol_filter
    x = [item[0] for item in path]
    y = [item[1] for item in path]
    new_x = savgol_filter(x, 71, 5, mode='nearest')
    new_y = savgol_filter(y, 71, 5, mode='nearest')
    path = []
    for i in range(len(new_x)):
        path.append([int(new_x[i]), int(new_y[i])])
    return path


if __name__ == '__main__':
    from util_llj import Simulator_llj


    def huatu(map_, path_):
        current_map = map_
        for k in path_:
            cv2.circle(current_map, (k[0], k[1]), 3, (0, 0, 213), -1)
            map_resize = current_map.copy()
            # 显示
            cv2.namedWindow('findCorners', 0)
            cv2.resizeWindow('findCorners', 700, 900)  # 自己设定窗口图片的大小
            cv2.imshow("findCorners", current_map)
            cv2.waitKey(1)
        cv2.imwrite('/home/llj/PathPlanningAstar/result.png', current_map)
        return current_map


    path_search = Simulator_llj.search(start=(1700, 155), goal=(1470, 1821))
    path = path_search.make_path()
    path = smooth_path2(path)
    map = cv2.imread('./PathPlanningAstar/fit4_5Dealing_draw.png')
    huatu(map, path)
