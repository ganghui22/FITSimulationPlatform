import json
import socket
import time
import math
import cv2
import matplotlib.pyplot as plt
import numpy as np


def edge_node(all_nav_nodes, grid_size):
    edge_nodes = []
    for node in all_nav_nodes:
        edge0 = [node[0], node[1] + grid_size]
        edge1 = [node[0] + grid_size, node[1]]
        edge2 = [node[0], node[1] - grid_size]
        edge3 = [node[0] - grid_size, node[1]]
        if edge0 not in all_nav_nodes or edge1 not in all_nav_nodes or edge2 not in all_nav_nodes or edge3 not in all_nav_nodes:
            edge_nodes.append(node)

    nav_nodes = [iteam for iteam in all_nav_nodes if iteam not in edge_nodes]

    return edge_nodes, nav_nodes


def get_median(data):
    data = sorted(list(set(data)))
    size = len(data)
    madian = data[int(size / 2)]
    return madian


def c_angle(v1, v2):
    dx1 = v1[2] - v1[0]
    dy1 = v1[3] - v1[1]
    dx2 = v2[2] - v2[0]
    dy2 = v2[3] - v2[1]
    angle1 = math.atan2(dy1, dx1)
    angle1 = int(angle1 * 180 / math.pi)
    # print(angle1)
    angle2 = math.atan2(dy2, dx2)
    angle2 = int(angle2 * 180 / math.pi)
    # print(angle2)
    if angle1 * angle2 >= 0:
        included_angle = angle1 - angle2
    else:
        included_angle = angle1 + angle2
        if included_angle > 180:
            included_angle = 360 - included_angle
    return included_angle


def map_dealing(map_path: str) -> None:
    map_origin = cv2.imread(map_path, cv2.IMREAD_GRAYSCALE)
    width, high = np.shape(map_origin)
    for x in range(width):
        for y in range(high):
            if 0 <= map_origin[x, y] <= 204:
                map_origin[x, y] = 0
            else:
                map_origin[x, y] = 255
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(map_origin, connectivity=4)
    area = stats[:, 4:5]  # area
    max1 = np.sort(area, axis=0)[-1]  # first area label
    max_index = area.tolist().index(max1)
    max2 = np.sort(area, axis=0)[-2]  # second area label
    max2_index = area.tolist().index(max2)
    map_connectedcomponents = map_origin
    for x in range(width):
        for y in range(high):
            if labels[x, y] == max2_index:
                map_connectedcomponents[x, y] = 255
            else:
                map_connectedcomponents[x, y] = 204
    for x in range(width):
        for y in range(high):
            if map_origin[x, y] == 0:
                map_connectedcomponents[x, y] = 0
    map_binary = np.array(map_connectedcomponents)
    for x in range(width):
        for y in range(high):
            if map_binary[x, y] == 204:
                map_binary[x, y] = 0
    contours, hierarchy = cv2.findContours(map_binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(map_connectedcomponents, contours, -1, 0, 2)
    map_name = map_path.split('.')
    cv2.imwrite(map_name[0] + 'Dealing' + '.png', map_connectedcomponents)


def map_track_middle(map_path: str) -> None:
    map_origin = cv2.imread(map_path, cv2.IMREAD_GRAYSCALE)
    print(map_origin)
    print(np.shape(map_origin))
    width, high = np.shape(map_origin)
    for x in range(width):
        for y in range(high):
            if 0 <= map_origin[x, y] <= 204:
                map_origin[x, y] = 0
            else:
                map_origin[x, y] = 255
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(map_origin, connectivity=4)
    area = stats[:, 4:5]  # area
    max1 = np.sort(area, axis=0)[-1]  # first area label
    max_index = area.tolist().index(max1)
    max2 = np.sort(area, axis=0)[-2]  # second area label
    max2_index = area.tolist().index(max2)
    map_connectedcomponents = map_origin
    for x in range(width):
        for y in range(high):
            if labels[x, y] == max2_index:
                map_connectedcomponents[x, y] = 255
            else:
                map_connectedcomponents[x, y] = 0
    for x in range(width):
        for y in range(high):
            if map_origin[x, y] == 0:
                map_connectedcomponents[x, y] = 0
    map_binary = np.array(map_connectedcomponents)
    for x in range(width):
        for y in range(high):
            if map_binary[x, y] == 0:
                map_binary[x, y] = 0
    contours, hierarchy = cv2.findContours(map_binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(map_connectedcomponents, contours, -1, 0, 12)
    map_name = map_path.split('.')
    cv2.imwrite('middle' + '.png', map_connectedcomponents)


# 类定义
class WaterApi:
    def __init__(self, host: str, port: int) -> None:
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.connect((host, port))
        self.origin_x, self.origin_y, self.height, self.width, self.resolution = self.get_map_info()

    def forward(self, length: int) -> None:
        for _ in range(length):
            send_data = "/api/joy_control?angular_velocity={}&linear_velocity={}".format(0.0, 0.2)
            self.tcp_socket.send(send_data.encode("utf-8"))
            receive = self.tcp_socket.recv(1024)
            if len(receive): print(str(receive, encoding='utf-8'))
            time.sleep(0.2)

    def backward(self, length: int) -> None:
        for _ in range(length):
            send_data = "/api/joy_control?angular_velocity={}&linear_velocity={}".format(0.0, -0.2)
            self.tcp_socket.send(send_data.encode("utf-8"))
            receive = self.tcp_socket.recv(1024)
            if len(receive): print(str(receive, encoding='utf-8'))
            time.sleep(0.2)

    def rotate_right(self, angle: int) -> None:  # 30
        for _ in range(angle):
            send_data = "/api/joy_control?angular_velocity={}&linear_velocity={}".format(0.19, 0)
            self.tcp_socket.send(send_data.encode("utf-8"))
            receive = self.tcp_socket.recv(1024)
            if len(receive): print(str(receive, encoding='utf-8'))
            time.sleep(0.4)

    def rotate_left(self, angle: int) -> None:  # 30
        for _ in range(angle):
            send_data = "/api/joy_control?angular_velocity={}&linear_velocity={}".format(-0.4, 0)
            self.tcp_socket.send(send_data.encode("utf-8"))
            receive = self.tcp_socket.recv(1024)
            if len(receive): print(str(receive, encoding='utf-8'))

    def as_robot_status(self, dct):
        if 'command' in dct:
            if dct['command'] == "/api/robot_status" & dct['type'] == 'response':
                return dct['results']

    def robot_status(self) -> dict:
        try:
            send_data = "/api/robot_status"
            self.tcp_socket.send(send_data.encode("utf-8"))
            print('-----------------------------1111----------------------')
            rrr = self.tcp_socket.recv(1024)
            print('-----------------------------2333--------------------------')
            rrr = rrr.split()
            try:
                receive = json.loads(rrr[0])
            except json.decoder.JSONDecodeError as e:
                print(e)
                error = str(e).split(':', 1)
                line = error[1].split()[1]  # 行
                column = error[1].split()[3]  # 列
                char = error[1].split()[5].split(')')[0]  # 字节序数
                if error[0] == "Expecting value":  # 开头数据有问题
                    print('error: ', error[0], line, column, char)
                if error[0] == "Extra data":  # 结尾数据有问题
                    print('error: ', error[0], line, column, char)
                if error[0] == "Unterminated string starting at":
                    receive = json.loads(rrr[1])
                print(error)
        except Exception as e:
            receive = self.robot_status()
            print(rrr)
            print(e)
        if 'results' not in receive:
            receive = self.robot_status()
        return receive

    def robot_location(self, loc):
        status = self.robot_status()
        pose = status['results']['current_pose']
        pose = [round(pose['x'], 2), round(pose['y'], 2)]
        vector = pose + loc
        angle = c_angle(vector, [0, 0, 1, 0])
        location = {'name': 'Nav', 'theta': math.radians(angle), 'x': loc[0], 'y': loc[1]}
        self.set_marker(location)
        self.robot_marker(location['name'])
        self.clear()

    def robot_marker(self, marker):
        send_data = "/api/move?marker=" + marker
        self.tcp_socket.send(send_data.encode("utf-8"))
        receive = self.tcp_socket.recv(1024)
        if len(receive): print(str(receive, encoding='utf-8'))

    def set_marker(self, location):
        send_data = "/api/markers/insert_by_pose?name={}&x={}&y={}&theta={}&floor=2&type=0".format(
            location['name'], location['x'], location['y'], location['theta'])
        self.tcp_socket.send(send_data.encode("utf-8"))
        receive = self.tcp_socket.recv(1024)
        if len(receive): print(str(receive, encoding='utf-8'))

    def move_location(self, x, y, theta):
        send_data = "/api/move?location={},{},{}".format(x, y, theta)
        self.tcp_socket.send(send_data.encode("utf-8"))
        receive = self.tcp_socket.recv(1024)
        if len(receive): print(str(receive, encoding='utf-8'))

    def delete_marker(self, name):
        send_data = "/api/markers/delete?name={}".format(name)
        self.tcp_socket.send(send_data.encode("utf-8"))
        receive = self.tcp_socket.recv(1024)
        if len(receive): print(str(receive, encoding='utf-8'))

    def move_cancel(self):
        send_data = "/api/move/cancel"
        self.tcp_socket.send(send_data.encode("utf-8"))
        receive = self.tcp_socket.recv(1024)
        if len(receive): print(str(receive, encoding='utf-8'))

    def make_plan(self, start, goal):
        send_data = "/api/make_plan?start_x={}&start_y={}&start_floor=2&goal_x={}&goal_y={}&goal_floor=2".format(
            start[0], start[1], goal[0], goal[1])
        self.tcp_socket.send(send_data.encode("utf-8"))
        receive = self.tcp_socket.recv(1024)
        receive = json.loads(receive)
        return receive

    def clear(self):
        receive = self.tcp_socket.recv(1024)
        if len(receive): print(str(receive, encoding='utf-8'))

    def judge(self):
        receive = self.tcp_socket.recv(1024)
        receive = json.loads(receive)
        return receive

    def get_path(self):
        receive = self.tcp_socket.recv(1024)
        if len(receive): print(str(receive, encoding='utf-8'))
        send_data = "/api/get_planned_path"
        self.tcp_socket.send(send_data.encode("utf-8"))
        receive = self.tcp_socket.recv(51200)
        receive = json.loads(receive)
        print(receive)
        path = receive['results']['path']
        return path

    def set_color(self, rgb_value):
        # RGB_VALUE --> (R,G,B)
        send_data = "/api/LED/set_color?r={}&g={}&b={}".format(rgb_value[0], rgb_value[1], rgb_value[2])
        self.tcp_socket.send(send_data.encode("utf-8"))

    def read_map(self):
        send_data = "/api/map/get_current_map"
        self.tcp_socket.send(send_data.encode("utf-8"))
        receive = self.tcp_socket.recv(1024)
        receive = json.loads(receive)
        map_name = receive['results']['map_name']
        floor = receive['results']['floor']
        print(map_name)
        print(floor)
        map_name = map_name + '_' + str(floor) + ".png"
        print("Current map's name:", map_name)
        try:
            current_map = cv2.imread("/home/water/音乐/water-realsense/water备份/vsv_zfb/201demo_2.png", cv2.IMREAD_COLOR)
        except IOError:
            print("The current map was not found locally")
        else:
            return current_map

    def get_current_pose(self):
        send_data = "/api/robot_status"
        self.tcp_socket.send(send_data.encode("utf-8"))
        receive = self.tcp_socket.recv(1024)
        receive = json.loads(receive)
        print(receive)
        receive = receive['results']['current_pose']
        return [receive['x'], receive['y'], receive['theta']]

    def get_map_info(self):
        send_data = "/api/map/get_current_map"
        self.tcp_socket.send(send_data.encode("utf-8"))
        receive = self.tcp_socket.recv(1024)
        receive = json.loads(receive)
        receive = receive['results']['info']
        return [receive['origin_x'], receive['origin_y'], receive['height'], receive['width'], receive['resolution']]

    def get_pose_pix(self):
        """
        函数名:get_pose_pix()

        """
        loc_x, loc_y, theta = self.get_current_pose()
        loc_x_pix = int((loc_x - self.origin_x) / self.resolution)
        loc_y_pix = int(self.height - (loc_y - self.origin_y) / self.resolution)
        return [loc_x_pix, loc_y_pix, theta]


def main():
    api = WaterApi("192.168.10.10", 31001)
    api.move_cancel()
    # api.forward(5)
    # api.backward(5)
    # api.move_cancel()
    import matplotlib.pyplot as plt
    all_nav_nodes = []

    start = [0, 0]
    grid_size = 0.25
    for x in range(0, 100, 1):  # 0,14,1
        for y in range(-10, 30, 1):  # 4,-10,-1
            receive = api.make_plan(start, [x * grid_size, y * grid_size])
            if receive['error_message'] == '':
                all_nav_nodes.append([x * grid_size, y * grid_size])

    print(len(all_nav_nodes))
    edge_nodes, nav_nodes = edge_node(all_nav_nodes, grid_size)
    edge_nodes, nav_nodes = edge_node(nav_nodes, grid_size)
    edge_nodes, _ = edge_node(nav_nodes, grid_size)
    # print(edge_nodes)
    plt.figure()
    x = [iteam[0] for iteam in edge_nodes]
    y = [iteam[1] for iteam in edge_nodes]
    plt.scatter(x, y, s=10)
    plt.show()

    x_median = get_median(x)
    y_median = get_median(y)

    sample_nodes = []
    for node in edge_nodes:
        if node[0] == x_median or node[1] == '/home/xdy/workspace/ros_subscriber.pyy_median':
            sample_nodes.append(node)

    print(sample_nodes)

    nodes = {}
    nodes['edge_nodes'] = edge_nodes
    nodes['nav_nodes'] = nav_nodes
    nodes['sample_nodes'] = sample_nodes

    import pickle
    with open(('/home/water/音乐/water-realsense/water备份/vsv_zfb/my_utils/nodes_llj_nodes.pkl'), 'wb') as f:
        pickle.dump(nodes, f)

    plt.figure()
    x = [iteam[0] for iteam in nav_nodes]
    y = [iteam[1] for iteam in nav_nodes]
    plt.scatter(x, y, s=10)

    x = [iteam[0] for iteam in sample_nodes]
    y = [iteam[1] for iteam in sample_nodes]
    plt.scatter(x, y, s=10, c='r')
    plt.show()

    print("ok")


def huatu(curr, origin_x, origin_y, height, width, resolution):
    api1 = WaterApi("192.168.10.10", 31001)  # 192.168.1.7    192.168.1.21#
    current_map = curr
    print(current_map)
    loc_x_pix1, loc_y_pix1, theta1 = api1.get_pose_pix(origin_x, origin_y, height, width, resolution)
    print(loc_x_pix1, loc_y_pix1)
    # cv2.circle(current_map,(loc_y_pix1,loc_y_pix1),1, (0, 255, 0), 8)
    cv2.arrowedLine(current_map, pt1=(loc_x_pix1, loc_y_pix1), pt2=(int(loc_x_pix1 + 4 * math.cos(theta1)),
                                                                    int(loc_y_pix1 + 4 * math.sin(theta1))),
                    color=(0, 0, 255), thickness=2, line_type=cv2.LINE_8,
                    shift=0, tipLength=0.1)
    # cv2.arrowedLine(current_map, pt1=(loc_x_pix1, loc_y_pix1), pt2=(int(loc_x_pix1 + 15 * math.cos(theta1)),
    #                                                                 int(loc_y_pix1 + 15 * math.sin(theta1))),
    #                 color=(255, 255, 0), thickness=2, line_type=cv2.LINE_8,
    #                 shift=0, tipLength=0.5)
    # cv2.imwrite(r'/home/water/音乐/water-realsense/water备份/vsv_zfb/1.png', current_map)
    api1.set_color((255, 255, 255))
    cv2.imshow('map', current_map)
    cv2.waitKey(1)
    return current_map


if __name__ == "__main__":
    map_dealing('../data/map/fit4_5/fit4_5.png')
    # map_track_middle('map.png')
    # main()
    # api = WaterApi("192.168.10.10", 31001)
    # print(api.get_map_info())

    # while 1:
    #
    #     loc = api.robot_status()
    #     time.sleep(0.5)
    #     print(loc)
    # print(loc)
    # 192.168.1.7    192.168.1.21#
    # current_map = cv2.imread("/home/water/音乐/water-realsense/water备份/vsv_zfb/201demo_2.png", cv2.IMREAD_COLOR)
    # api = WaterApi("192.168.1.13", 31001)
    # origin_x, origin_y, height, width, resolution = api.get_map_info()
    # print(origin_x, origin_y, height, width, resolution)
    # api.move_location(15.0296, 1.05863, math.pi/2)

    # i = 2405
    # api.move_location(13.13, 2.97416, math.pi)
    # time.sleep(0.2)
    # dct = {}
    # while i <= 2451:
    #     status = api.robot_status()
    #     current_pose = status['results']['current_pose']
    #     time.sleep(0.15)
    #     dct[str(i)] = [[[9.80316, 5.14088], 487.2390293958824],
    #                    [[current_pose['x'], current_pose['y']], (current_pose['theta'] / math.pi) * 180],
    #                    [[43.5627, -3.69066], 299.1266720141208]]
    #     i = i + 1
    # package = open("package.json")
    # dct_json = json.dumps(dct)
    # print(dct_json)
    # package.write(dct_json)

    # while 1:
    #     # current_map = huatu(current_map, origin_x, origin_y, height, width, resolution)
    #     print(api.robot_status())
    #     time.sleep(0.1)

    # map_dealing('220demo_2.png')
