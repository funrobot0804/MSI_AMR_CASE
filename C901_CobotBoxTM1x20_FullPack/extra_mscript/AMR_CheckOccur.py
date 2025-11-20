import math
import time
import types
import numpy as np
import copy
from PIL import Image as im

import device

ENABLE_DEBUG = 0
ENABLE_DEBUG_DRAWING = 0

class AMR_CheckOccur():
    def __init__(self, amr_ip="127.0.0.1"):
        self.amr_ip = amr_ip
        self.me = device.robot(self.amr_ip)

        self.pause_range = 0.8
        self.stop_range = 0.2
        self.vw_map_idx = 10

        self.pause_rect_vertices = None
        self.stop_rect_vertices = None
        self.pause_rect_vertices_grid = None
        self.stop_rect_vertices_grid = None
        self.self_pos_grid = None
        self.self_pos_center = [0., 0.]

        self.isFirstGetPoint = True
        self.inner_plan_ring = list(range(0, 400))
        for i in range(len(self.inner_plan_ring)):
            self.inner_plan_ring[i] = 0.


        self.fixed_map = None
        self.laser_map = None

        self.map_info = None
        self.misc = None

        self.amr_pos_x = -1.0
        self.amr_pos_y = -1.0

        self.the_plan_ring = []
        self.detect_point_list = []
        self.laser_set_point_list = []

        self.isGetFixedMapSuccess = 0


    def read_config(self):
        pass

    def get_misc(self):
        tmp_misc = None

        while(tmp_misc is None):
            tmp_misc = self.me.get_misc()
            self.amr_pos_x = tmp_misc['position']['x']
            self.amr_pos_y = tmp_misc['position']['y']
            time.sleep(0.2)

    def get_map_info(self):
        mapInfo = self.me.get_map_information(2)

        if mapInfo is not None:
            self.map_info = types.SimpleNamespace()

            self.map_info.width = mapInfo['width']  # map width unit:<grid>
            self.map_info.height = mapInfo['height']  # map height unit:<grid>
            self.map_info.scale = mapInfo['scale']  # map scale unit:<m/grid>
            self.map_info.orgx = mapInfo['orgx']  # map orgx unit:<m>
            self.map_info.orgy = mapInfo['orgy']  # map orgy unit:<m>

    def enable_detect_point(self, ai_name="AMR_CheckOccur, enable_detect_point"):
        #self.me.set_sensor_display_config(ai_name, 2, 2)
        self.me.debug_SensorDisplayOption(ai_name, "LASER")

    def get_detect_point(self):
        the_plan_ring = self.me.get_plan_ring()
        self.the_plan_ring = the_plan_ring

        #print(f"get_detect_point - self.isFirstGetPoint = {self.isFirstGetPoint}")
        if len(self.the_plan_ring) >= 400:
            for i in range(28, 28+360):
                #print(f"i={i}, self.the_plan_ring[i]={self.the_plan_ring[i]}")
                px = self.the_plan_ring[i][0]
                py = self.the_plan_ring[i][1]
                p_info = self.the_plan_ring[i][2]

                sensor_type = round(math.fabs(p_info) / 100000)

                if self.isFirstGetPoint == False:
                    if sensor_type > 0:
                        self.inner_plan_ring[i] = [px, py, p_info]

                elif self.isFirstGetPoint == True:
                    self.inner_plan_ring[i] = [px, py, p_info]


        if self.laser_map is not None:
            self.laser_map.fill(0)

            for i in range(28, 28+360):
                #print(f"i={i}, self.the_plan_ring[i]={self.the_plan_ring[i]}")
                px = self.inner_plan_ring[i][0]
                py = self.inner_plan_ring[i][1]
                g_px, g_py = self.Pos2Grid(px, py)

                self.laser_map[g_py, g_px] = 1


        #print(f"get_detect_point - self.inner_plan_ring = {self.inner_plan_ring}")

        if self.isFirstGetPoint == False:
            self.isFirstGetPoint = True



    def reset_get_fixed_map_flag(self):
        self.isGetFixedMapSuccess = 0


    def get_fixed_map(self):

        if self.isGetFixedMapSuccess == 0:
            now_amr_grid_x, now_amr_grid_y = self.Pos2Grid(self.amr_pos_x, self.amr_pos_y)
            pause_range_grid = self.pause_range / self.map_info.scale
            stop_range_grid = self.stop_range / self.map_info.scale

            # max_range_grid = 0
            # if pause_range_grid >= stop_range_grid:
                # max_range_grid = pause_range_grid
            # else:
                # max_range_grid = stop_range_grid

            # max_range_grid = round(max_range_grid) * 2
            # max_range_grid = 500
            #
            # w1 = max_range_grid
            # h1 = max_range_grid
            # x1 = now_amr_grid_x - max_range_grid/2
            # y1 = now_amr_grid_y - max_range_grid/2
            #
            # w1 = int(w1)
            # h1 = int(h1)
            # x1 = int(x1)
            # y1 = int(y1)

            w1 = 8192
            h1 = 8192
            x1 = 0
            y1 = 0

            print(f"AMR_CheckOccur - get_fixed_map - w1={w1}, h1={h1}, x1={x1}, y1={y1}")

            try:
                raw_map_data = None
                map = self.me.get_map(50, x1, y1, w1, h1)
                if map is not None:
                    if (map.size != 0):
                        raw_map_data = map.copy()


                # vw_map_data = None
                # map = self.me.get_map(self.vw_map_idx, 0, 0, 8192, 8192)
                # if map is not None:
                #     if (map.size != 0):
                #         vw_map_data = map.copy()


                # img_array = np.arange(0, w1*h1, 1, np.uint8)
                # img_array = img_array.reshape(w1, h1)
                # img_array.fill(255)

                fullmap_array = np.arange(0, 8192*8192, 1, np.int8)
                fullmap_array = fullmap_array.reshape(8192, 8192)
                fullmap_array.fill(0)

                fullmap_array[y1:y1+h1, x1:x1+w1] = raw_map_data
                # occupied_where = np.where(vw_map_data > 0)
                # fullmap_array[occupied_where] = 1

                img_array = np.arange(0, 8192*8192, 1, np.uint8)
                img_array = img_array.reshape(8192, 8192)
                img_array.fill(255)


                occupied_where = np.where(fullmap_array > 0)
                img_array[occupied_where] = 0

                self.fixed_map = img_array

                #img_file_data = im.fromarray(img_array)
                #img_file_data.save("AMR_CheckOccur.png")

                self.isGetFixedMapSuccess = 1

            except Exception as e:
                print("=+=+=+=+=+=+=+=+")
                print("AMR_CheckOccur : get_fixed_map Exception!")
                exec('''try:\n    print('Error Code: {c}, Message, {m}'.format(c = type(e).__name__, m = str(e)))\nexcept:\n    pass''')
                print("=+=+=+=+=+=+=+=+")


    def dot_prod_with_shared_start(self, start, end1, end2):
        """
        Compute the dot product of the vectors pointing from start to end1 and end2

        Parameters
            start: starting point of both vectors
            end1: end point of first vector
            end2: end point of second vector

        Returns
            dot product of (end1 - start) and (end2 - start)
        """
        return (end1[0] - start[0]) * (end2[0] - start[0]) + (end1[1] - start[1]) * (end2[1] - start[1])

    def is_inside_rectangle(self, vertices, point):
        """
        Given the vertices of a rectangle, determine whether a point is inside it.

        Parameters
            vertices: a list of tuples representing rectangle vertices in clockwise or
                      counter-clockwise order
            point: a tuple representing the point to check

        Returns
            True if the point is inside the rectangle. False otherwise.
        """
        return all(self.dot_prod_with_shared_start(vertices[i - 1], v, point) > 0 for i, v in enumerate(vertices))



    def pre_calculate_V2(self):
        # STEP 0: Fetch self size data
        self_pos_0 = self.the_plan_ring[0]
        self_pos_1 = self.the_plan_ring[1]
        self_pos_2 = self.the_plan_ring[2]
        self_pos_3 = self.the_plan_ring[3]
        print(f"self_pos 0:{self_pos_0}, 1:{self_pos_1}, 2:{self_pos_2}, 3:{self_pos_3}")

        self.self_pos_grid = []
        for i in range(4):
            px, py = self.the_plan_ring[i][0], self.the_plan_ring[i][1]
            gx, gy = self.Pos2Grid(px, py)

            self.self_pos_grid.append([gx, gy])


        self_pos_center = [ (self_pos_0[0] + self_pos_2[0]) / 2.0, \
                            (self_pos_0[1] + self_pos_2[1]) / 2.0]

        self.self_pos_center = self_pos_center

        diagonal_dist = math.sqrt((self_pos_0[0] - self_pos_center[0]) ** 2 + \
                                  (self_pos_0[1] - self_pos_center[1]) ** 2)

        self.diagonal_dist = diagonal_dist

        print(f"self_pos_center = {self_pos_center}")
        print(f"len(self.the_plan_ring) = {len(self.the_plan_ring)}")
        print(f"diagonal_dist = {diagonal_dist}")

        self_pos_0_uvec = [ (self_pos_0[0] - self_pos_center[0]) / diagonal_dist, \
                            (self_pos_0[1] - self_pos_center[1]) / diagonal_dist ]

        self_pos_0_pause = [ self_pos_0[0] + self.pause_range*self_pos_0_uvec[0], \
                             self_pos_0[1] + self.pause_range*self_pos_0_uvec[1] ]

        self_pos_0_stop = [ self_pos_0[0] + self.stop_range*self_pos_0_uvec[0], \
                            self_pos_0[1] + self.stop_range*self_pos_0_uvec[1] ]



        self_pos_1_uvec = [ (self_pos_1[0] - self_pos_center[0]) / diagonal_dist, \
                            (self_pos_1[1] - self_pos_center[1]) / diagonal_dist ]

        self_pos_1_pause = [ self_pos_1[0] + self.pause_range*self_pos_1_uvec[0], \
                             self_pos_1[1] + self.pause_range*self_pos_1_uvec[1] ]

        self_pos_1_stop = [ self_pos_1[0] + self.stop_range*self_pos_1_uvec[0], \
                            self_pos_1[1] + self.stop_range*self_pos_1_uvec[1] ]



        self_pos_2_uvec = [ (self_pos_2[0] - self_pos_center[0]) / diagonal_dist, \
                            (self_pos_2[1] - self_pos_center[1]) / diagonal_dist ]

        self_pos_2_pause = [ self_pos_2[0] + self.pause_range*self_pos_2_uvec[0], \
                             self_pos_2[1] + self.pause_range*self_pos_2_uvec[1] ]

        self_pos_2_stop = [ self_pos_2[0] + self.stop_range*self_pos_2_uvec[0], \
                            self_pos_2[1] + self.stop_range*self_pos_2_uvec[1] ]



        self_pos_3_uvec = [ (self_pos_3[0] - self_pos_center[0]) / diagonal_dist, \
                            (self_pos_3[1] - self_pos_center[1]) / diagonal_dist ]

        self_pos_3_pause = [ self_pos_3[0] + self.pause_range*self_pos_3_uvec[0], \
                             self_pos_3[1] + self.pause_range*self_pos_3_uvec[1] ]

        self_pos_3_stop = [ self_pos_3[0] + self.stop_range*self_pos_3_uvec[0], \
                            self_pos_3[1] + self.stop_range*self_pos_3_uvec[1] ]


        self.pause_rect_vertices = [ tuple(self_pos_0_pause), \
                                     tuple(self_pos_1_pause), \
                                     tuple(self_pos_2_pause), \
                                     tuple(self_pos_3_pause)
                                    ]


        self.stop_rect_vertices = [  tuple(self_pos_0_stop), \
                                     tuple(self_pos_1_stop), \
                                     tuple(self_pos_2_stop), \
                                     tuple(self_pos_3_stop)
                                    ]


        self_pos_0_pause_grid = [0, 0]
        self_pos_0_pause_grid[0], self_pos_0_pause_grid[1] = self.Pos2Grid(self_pos_0_pause[0], \
                                                                           self_pos_0_pause[1])

        self_pos_1_pause_grid = [0, 0]
        self_pos_1_pause_grid[0], self_pos_1_pause_grid[1] = self.Pos2Grid(self_pos_1_pause[0], \
                                                                           self_pos_1_pause[1])

        self_pos_2_pause_grid = [0, 0]
        self_pos_2_pause_grid[0], self_pos_2_pause_grid[1] = self.Pos2Grid(self_pos_2_pause[0], \
                                                                           self_pos_2_pause[1])

        self_pos_3_pause_grid = [0, 0]
        self_pos_3_pause_grid[0], self_pos_3_pause_grid[1] = self.Pos2Grid(self_pos_3_pause[0], \
                                                                           self_pos_3_pause[1])

        self.pause_rect_vertices_grid = [ tuple(self_pos_0_pause_grid), \
                                          tuple(self_pos_1_pause_grid), \
                                          tuple(self_pos_2_pause_grid), \
                                          tuple(self_pos_3_pause_grid)
                                        ]

        self_pos_0_stop_grid = [0, 0]
        self_pos_0_stop_grid[0], self_pos_0_stop_grid[1] = self.Pos2Grid(self_pos_0_stop[0], \
                                                                         self_pos_0_stop[1])

        self_pos_1_stop_grid = [0, 0]
        self_pos_1_stop_grid[0], self_pos_1_stop_grid[1] = self.Pos2Grid(self_pos_1_stop[0], \
                                                                         self_pos_1_stop[1])

        self_pos_2_stop_grid = [0, 0]
        self_pos_2_stop_grid[0], self_pos_2_stop_grid[1] = self.Pos2Grid(self_pos_2_stop[0], \
                                                                         self_pos_2_stop[1])

        self_pos_3_stop_grid = [0, 0]
        self_pos_3_stop_grid[0], self_pos_3_stop_grid[1] = self.Pos2Grid(self_pos_3_stop[0], \
                                                                         self_pos_3_stop[1])

        self.stop_rect_vertices_grid = [  tuple(self_pos_0_stop_grid), \
                                          tuple(self_pos_1_stop_grid), \
                                          tuple(self_pos_2_stop_grid), \
                                          tuple(self_pos_3_stop_grid)
                                       ]


        empty_fullmap_array = np.arange(0, 8192 * 8192, 1, np.int8)
        empty_fullmap_array = empty_fullmap_array.reshape(8192, 8192)
        empty_fullmap_array.fill(0)

        for i in range(28, 28+360):
            #print(f"i={i}, self.the_plan_ring[i]={self.the_plan_ring[i]}")
            px = self.the_plan_ring[i][0]
            py = self.the_plan_ring[i][1]
            g_px, g_py = self.Pos2Grid(px, py)

            empty_fullmap_array[g_py, g_px] = 1

        self.laser_map = empty_fullmap_array



    def calculate_V2(self):
        allowed_sensor_type_list = [1, 2, 3]

        # print("self.the_plan_ring =")
        # print(self.the_plan_ring)

        #print(f"calculate_V2 - self.inner_plan_ring = {self.inner_plan_ring}")

        self_pos_center = self.self_pos_center
        diagonal_dist = self.diagonal_dist
        calc_result = 0

        # STEP 1: Find the Obstacle
        obstacle_point_list = []
        self.detect_point_list = []
        self.laser_set_point_list = []
        for i in range(28, 28+360):
            #print(f"i={i}, self.the_plan_ring[i]={self.the_plan_ring[i]}")
            #print(f"i={i}, self.inner_plan_ring[{i}]={self.inner_plan_ring[i]}")
            px = self.the_plan_ring[i][0]
            py = self.the_plan_ring[i][1]
            p_info = self.the_plan_ring[i][2]

            px = self.inner_plan_ring[i][0]
            py = self.inner_plan_ring[i][1]
            p_info = self.inner_plan_ring[i][2]

            sensor_status = math.fabs(p_info) / 1000 % 100
            sensor_status = int(math.floor(sensor_status))

            sensor_type = round(math.fabs(p_info) / 100000)

            g_px, g_py = self.Pos2Grid(px, py)

            # print(f"i={i}, sensor_status={sensor_status}")
            # print(f"i={i}, p_info={p_info}")
            # print(f"i={i}, px={px}, py={py}")
            # print(f"i={i}, g_px={g_px}, g_py={g_py}")
            # print(f"i={i}, map_value={self.fixed_map[g_py, g_px]}")

            wall_detect_count = 0
            wall_where = np.where(self.fixed_map[g_py - 2:g_py + 3, g_px - 2:g_px + 3] < 32)
            #print("wall_where =")
            #print(wall_where)
            #print(f"i={i}, wall_where[0].shape={wall_where[0].shape[0]}")

            wall_count = wall_where[0].shape[0]

            obstacle_point_list.append([sensor_status])
            self.detect_point_list.append([g_px, g_py])

            # euclidean = math.sqrt((px - self_pos_center[0]) ** 2 + \
            #                       (py - self_pos_center[1]) ** 2)
            #
            # new_euclidean = euclidean - diagonal_dist

            #print(f"i={i}, euclidean={euclidean}")
            #print(f"i={i}, new_euclidean={new_euclidean}")
            #print("=============")

            test_point = (px, py)
            rect_vertices = self.pause_rect_vertices
            is_in_pause_range = self.is_inside_rectangle(rect_vertices, test_point)

            rect_vertices = self.stop_rect_vertices
            is_in_stop_range = self.is_inside_rectangle(rect_vertices, test_point)

            if 1:
                if wall_count <= 0:
                    #if (new_euclidean > self.pause_range):
                    if (is_in_pause_range == False) and \
                       (is_in_stop_range == False):
                        pass

                    if (is_in_pause_range == True) and \
                         (is_in_stop_range == False):

                        laser_where = np.where(self.laser_map[g_py - 1:g_py + 2, g_px - 1:g_px + 2] > 0)
                        laser_where_count = laser_where[0].shape[0]

                        if laser_where_count > 1:

                            self.laser_set_point_list.append([g_px, g_py])

                            if ENABLE_DEBUG == 1:
                                print(f"i={i}, sensor_status={sensor_status}")
                                print(f"i={i}, p_info={p_info}")
                                print(f"i={i}, px={px}, py={py}")
                                print(f"i={i}, g_px={g_px}, g_py={g_py}")
                                print(f"i={i}, map_value={self.fixed_map[g_py, g_px]}")
                                print("wall_where =")
                                print(wall_where)
                                print(f"i={i}, wall_where[0].shape={wall_where[0].shape[0]}")
                                # print(f"i={i}, euclidean={euclidean}")
                                # print(f"i={i}, new_euclidean={new_euclidean}")
                                print(f"i={i}, pause_range={self.pause_range}")
                                print(f"i={i}, stop_range={self.stop_range}")
                                print(f"i={i}, laser_where_count={laser_where_count}")
                                print("||| PAUSE |||")
                                print("=============")

                            if calc_result == 0:
                                calc_result = 1

                    if (is_in_pause_range == True) and \
                         (is_in_stop_range == True):

                        laser_where = np.where(self.laser_map[g_py - 1:g_py + 2, g_px - 1:g_px + 2] > 0)
                        laser_where_count = laser_where[0].shape[0]

                        if laser_where_count > 1:

                            self.laser_set_point_list.append([g_px, g_py])

                            if ENABLE_DEBUG == 1:
                                print(f"i={i}, sensor_status={sensor_status}")
                                print(f"i={i}, p_info={p_info}")
                                print(f"i={i}, px={px}, py={py}")
                                print(f"i={i}, g_px={g_px}, g_py={g_py}")
                                print(f"i={i}, map_value={self.fixed_map[g_py, g_px]}")
                                print("wall_where =")
                                print(wall_where)
                                print(f"i={i}, wall_where[0].shape={wall_where[0].shape[0]}")
                                # print(f"i={i}, euclidean={euclidean}")
                                # print(f"i={i}, new_euclidean={new_euclidean}")
                                print(f"i={i}, pause_range={self.pause_range}")
                                print(f"i={i}, stop_range={self.stop_range}")
                                print("!!! DANGER !!!")
                                print("=============")

                            if calc_result > 0:
                                calc_result = 2





        if ENABLE_DEBUG_DRAWING == 1:
            color_img_array = np.arange(0, 8192 * 8192 * 3, 1, np.uint8)
            color_img_array = color_img_array.reshape(8192, 8192, 3)
            color_img_array.fill(255)

            where_less_32 = np.where(self.fixed_map < 32)

            color_img_array[where_less_32[0], where_less_32[1], 0] = 0
            color_img_array[where_less_32[0], where_less_32[1], 1] = 0
            color_img_array[where_less_32[0], where_less_32[1], 2] = 0

            front_half_pos = [ (self.the_plan_ring[0][0] + self.the_plan_ring[1][0]) / 2.0, \
                               (self.the_plan_ring[0][1] + self.the_plan_ring[1][1]) / 2.0]

            fh2c_len = math.sqrt( (front_half_pos[0] - self.self_pos_center[0]) ** 2 + \
                                  (front_half_pos[1] - self.self_pos_center[1]) ** 2)

            print(f"fh2c_len = {fh2c_len}")
            print(f"front_half_pos = {front_half_pos}")
            print(f"self.self_pos_center = {self.self_pos_center}")

            fh2c_uvec = [  (front_half_pos[0] - self.self_pos_center[0]) / fh2c_len, \
                           (front_half_pos[1] - self.self_pos_center[1]) / fh2c_len  ]

            print(f"fh2c_uvec = {fh2c_uvec}")

            trangle_mid_pos = [ self.self_pos_center[0] - (0.5 * fh2c_len * fh2c_uvec[0]), \
                                self.self_pos_center[1] - (0.5 * fh2c_len * fh2c_uvec[1]) ]


            tmpgx, tmpgy = self.Pos2Grid(trangle_mid_pos[0], trangle_mid_pos[1])
            trangle_mid_pos_grid = [tmpgx, tmpgy]

            fhpgx, fhpgy = self.Pos2Grid(front_half_pos[0], front_half_pos[1])
            front_half_pos_grid = [fhpgx, fhpgy]

            cgx, cgy = self.Pos2Grid(self.self_pos_center[0], self.self_pos_center[1])
            self_pos_center_grid = [cgx, cgy]

            trangle_direct_shape = [ front_half_pos_grid, self.self_pos_grid[2], \
                                     trangle_mid_pos_grid, self.self_pos_grid[3]
                                    ]


            for i in range(4):
                if (i > 0):
                    x0 = self.self_pos_grid[i - 1][0]
                    x1 = self.self_pos_grid[i][0]
                    y0 = self.self_pos_grid[i - 1][1]
                    y1 = self.self_pos_grid[i][1]

                    num_points = max(abs(x1 - x0), abs(y1 - y0)) + 1

                    x, y = np.linspace(x0, x1, num_points), np.linspace(y0, y1, num_points)
                    x, y = np.round(x).astype(int), np.round(y).astype(int)

                    color_img_array[y, x, 0] = 0
                    color_img_array[y, x, 1] = 0
                    color_img_array[y, x, 2] = 255


                    x0 = trangle_direct_shape[i - 1][0]
                    x1 = trangle_direct_shape[i][0]
                    y0 = trangle_direct_shape[i - 1][1]
                    y1 = trangle_direct_shape[i][1]

                    num_points = max(abs(x1 - x0), abs(y1 - y0)) + 1

                    x, y = np.linspace(x0, x1, num_points), np.linspace(y0, y1, num_points)
                    x, y = np.round(x).astype(int), np.round(y).astype(int)

                    color_img_array[y, x, 0] = 96
                    color_img_array[y, x, 1] = 96
                    color_img_array[y, x, 2] = 96


                if i == 3:
                    x0 = self.self_pos_grid[0][0]
                    x1 = self.self_pos_grid[i][0]
                    y0 = self.self_pos_grid[0][1]
                    y1 = self.self_pos_grid[i][1]

                    num_points = max(abs(x1 - x0), abs(y1 - y0)) + 1

                    x, y = np.linspace(x0, x1, num_points), np.linspace(y0, y1, num_points)
                    x, y = np.round(x).astype(int), np.round(y).astype(int)

                    color_img_array[y, x, 0] = 0
                    color_img_array[y, x, 1] = 0
                    color_img_array[y, x, 2] = 255

                    x0 = trangle_direct_shape[0][0]
                    x1 = trangle_direct_shape[i][0]
                    y0 = trangle_direct_shape[0][1]
                    y1 = trangle_direct_shape[i][1]

                    num_points = max(abs(x1 - x0), abs(y1 - y0)) + 1

                    x, y = np.linspace(x0, x1, num_points), np.linspace(y0, y1, num_points)
                    x, y = np.round(x).astype(int), np.round(y).astype(int)

                    color_img_array[y, x, 0] = 96
                    color_img_array[y, x, 1] = 96
                    color_img_array[y, x, 2] = 96



            for i, p in enumerate(self.pause_rect_vertices_grid):
                if (i > 0):
                    x0 = self.pause_rect_vertices_grid[i - 1][0]
                    x1 = self.pause_rect_vertices_grid[i][0]
                    y0 = self.pause_rect_vertices_grid[i - 1][1]
                    y1 = self.pause_rect_vertices_grid[i][1]

                    num_points = max(abs(x1 - x0), abs(y1 - y0)) + 1

                    x, y = np.linspace(x0, x1, num_points), np.linspace(y0, y1, num_points)
                    x, y = np.round(x).astype(int), np.round(y).astype(int)

                    color_img_array[y, x, 0] = 51
                    color_img_array[y, x, 1] = 0
                    color_img_array[y, x, 2] = 102

                if i == 3:
                    x0 = self.pause_rect_vertices_grid[0][0]
                    x1 = self.pause_rect_vertices_grid[i][0]
                    y0 = self.pause_rect_vertices_grid[0][1]
                    y1 = self.pause_rect_vertices_grid[i][1]

                    num_points = max(abs(x1 - x0), abs(y1 - y0)) + 1

                    x, y = np.linspace(x0, x1, num_points), np.linspace(y0, y1, num_points)
                    x, y = np.round(x).astype(int), np.round(y).astype(int)

                    color_img_array[y, x, 0] = 51
                    color_img_array[y, x, 1] = 0
                    color_img_array[y, x, 2] = 102

            for i, p in enumerate(self.stop_rect_vertices_grid):
                if (i > 0):
                    x0 = self.stop_rect_vertices_grid[i - 1][0]
                    x1 = self.stop_rect_vertices_grid[i][0]
                    y0 = self.stop_rect_vertices_grid[i - 1][1]
                    y1 = self.stop_rect_vertices_grid[i][1]

                    num_points = max(abs(x1 - x0), abs(y1 - y0)) + 1

                    x, y = np.linspace(x0, x1, num_points), np.linspace(y0, y1, num_points)
                    x, y = np.round(x).astype(int), np.round(y).astype(int)

                    color_img_array[y, x, 0] = 0
                    color_img_array[y, x, 1] = 102
                    color_img_array[y, x, 2] = 0

                if i == 3:
                    x0 = self.stop_rect_vertices_grid[0][0]
                    x1 = self.stop_rect_vertices_grid[i][0]
                    y0 = self.stop_rect_vertices_grid[0][1]
                    y1 = self.stop_rect_vertices_grid[i][1]

                    num_points = max(abs(x1 - x0), abs(y1 - y0)) + 1

                    x, y = np.linspace(x0, x1, num_points), np.linspace(y0, y1, num_points)
                    x, y = np.round(x).astype(int), np.round(y).astype(int)

                    color_img_array[y, x, 0] = 0
                    color_img_array[y, x, 1] = 102
                    color_img_array[y, x, 2] = 0

            for g in self.detect_point_list:
                color_img_array[g[1], g[0], 0] = 255
                color_img_array[g[1], g[0], 1] = 0
                color_img_array[g[1], g[0], 2] = 0

            for g in self.laser_set_point_list:
                color_img_array[g[1], g[0], 0] = 184
                color_img_array[g[1], g[0], 1] = 134
                color_img_array[g[1], g[0], 2] = 11

            gui_color_img_array = np.flipud(color_img_array)
            img_file_data = im.fromarray(gui_color_img_array)
            img_file_data.save("AMR_CheckOccur2.png")

        return calc_result


    def SetDebugEnable(self):
        pass

    def SaveDebugImage(self):
        color_img_array = np.arange(0, 8192 * 8192 * 3, 1, np.uint8)
        color_img_array = color_img_array.reshape(8192, 8192, 3)
        color_img_array.fill(255)

        where_less_32 = np.where(self.fixed_map < 32)

        color_img_array[where_less_32[0], where_less_32[1], 0] = 0
        color_img_array[where_less_32[0], where_less_32[1], 1] = 0
        color_img_array[where_less_32[0], where_less_32[1], 2] = 0

        front_half_pos = [ (self.the_plan_ring[0][0] + self.the_plan_ring[1][0]) / 2.0, \
                           (self.the_plan_ring[0][1] + self.the_plan_ring[1][1]) / 2.0]

        fh2c_len = math.sqrt( (front_half_pos[0] - self.self_pos_center[0]) ** 2 + \
                              (front_half_pos[1] - self.self_pos_center[1]) ** 2)

        print(f"fh2c_len = {fh2c_len}")
        print(f"front_half_pos = {front_half_pos}")
        print(f"self.self_pos_center = {self.self_pos_center}")

        fh2c_uvec = [  (front_half_pos[0] - self.self_pos_center[0]) / fh2c_len, \
                       (front_half_pos[1] - self.self_pos_center[1]) / fh2c_len  ]

        print(f"fh2c_uvec = {fh2c_uvec}")

        trangle_mid_pos = [ self.self_pos_center[0] - (0.5 * fh2c_len * fh2c_uvec[0]), \
                            self.self_pos_center[1] - (0.5 * fh2c_len * fh2c_uvec[1]) ]


        tmpgx, tmpgy = self.Pos2Grid(trangle_mid_pos[0], trangle_mid_pos[1])
        trangle_mid_pos_grid = [tmpgx, tmpgy]

        fhpgx, fhpgy = self.Pos2Grid(front_half_pos[0], front_half_pos[1])
        front_half_pos_grid = [fhpgx, fhpgy]

        cgx, cgy = self.Pos2Grid(self.self_pos_center[0], self.self_pos_center[1])
        self_pos_center_grid = [cgx, cgy]

        trangle_direct_shape = [ front_half_pos_grid, self.self_pos_grid[2], \
                                 trangle_mid_pos_grid, self.self_pos_grid[3]
                                ]


        for i in range(4):
            if (i > 0):
                x0 = self.self_pos_grid[i - 1][0]
                x1 = self.self_pos_grid[i][0]
                y0 = self.self_pos_grid[i - 1][1]
                y1 = self.self_pos_grid[i][1]

                num_points = max(abs(x1 - x0), abs(y1 - y0)) + 1

                x, y = np.linspace(x0, x1, num_points), np.linspace(y0, y1, num_points)
                x, y = np.round(x).astype(int), np.round(y).astype(int)

                color_img_array[y, x, 0] = 0
                color_img_array[y, x, 1] = 0
                color_img_array[y, x, 2] = 255


                x0 = trangle_direct_shape[i - 1][0]
                x1 = trangle_direct_shape[i][0]
                y0 = trangle_direct_shape[i - 1][1]
                y1 = trangle_direct_shape[i][1]

                num_points = max(abs(x1 - x0), abs(y1 - y0)) + 1

                x, y = np.linspace(x0, x1, num_points), np.linspace(y0, y1, num_points)
                x, y = np.round(x).astype(int), np.round(y).astype(int)

                color_img_array[y, x, 0] = 96
                color_img_array[y, x, 1] = 96
                color_img_array[y, x, 2] = 96


            if i == 3:
                x0 = self.self_pos_grid[0][0]
                x1 = self.self_pos_grid[i][0]
                y0 = self.self_pos_grid[0][1]
                y1 = self.self_pos_grid[i][1]

                num_points = max(abs(x1 - x0), abs(y1 - y0)) + 1

                x, y = np.linspace(x0, x1, num_points), np.linspace(y0, y1, num_points)
                x, y = np.round(x).astype(int), np.round(y).astype(int)

                color_img_array[y, x, 0] = 0
                color_img_array[y, x, 1] = 0
                color_img_array[y, x, 2] = 255

                x0 = trangle_direct_shape[0][0]
                x1 = trangle_direct_shape[i][0]
                y0 = trangle_direct_shape[0][1]
                y1 = trangle_direct_shape[i][1]

                num_points = max(abs(x1 - x0), abs(y1 - y0)) + 1

                x, y = np.linspace(x0, x1, num_points), np.linspace(y0, y1, num_points)
                x, y = np.round(x).astype(int), np.round(y).astype(int)

                color_img_array[y, x, 0] = 96
                color_img_array[y, x, 1] = 96
                color_img_array[y, x, 2] = 96



        for i, p in enumerate(self.pause_rect_vertices_grid):
            if (i > 0):
                x0 = self.pause_rect_vertices_grid[i - 1][0]
                x1 = self.pause_rect_vertices_grid[i][0]
                y0 = self.pause_rect_vertices_grid[i - 1][1]
                y1 = self.pause_rect_vertices_grid[i][1]

                num_points = max(abs(x1 - x0), abs(y1 - y0)) + 1

                x, y = np.linspace(x0, x1, num_points), np.linspace(y0, y1, num_points)
                x, y = np.round(x).astype(int), np.round(y).astype(int)

                color_img_array[y, x, 0] = 51
                color_img_array[y, x, 1] = 0
                color_img_array[y, x, 2] = 102

            if i == 3:
                x0 = self.pause_rect_vertices_grid[0][0]
                x1 = self.pause_rect_vertices_grid[i][0]
                y0 = self.pause_rect_vertices_grid[0][1]
                y1 = self.pause_rect_vertices_grid[i][1]

                num_points = max(abs(x1 - x0), abs(y1 - y0)) + 1

                x, y = np.linspace(x0, x1, num_points), np.linspace(y0, y1, num_points)
                x, y = np.round(x).astype(int), np.round(y).astype(int)

                color_img_array[y, x, 0] = 51
                color_img_array[y, x, 1] = 0
                color_img_array[y, x, 2] = 102

        for i, p in enumerate(self.stop_rect_vertices_grid):
            if (i > 0):
                x0 = self.stop_rect_vertices_grid[i - 1][0]
                x1 = self.stop_rect_vertices_grid[i][0]
                y0 = self.stop_rect_vertices_grid[i - 1][1]
                y1 = self.stop_rect_vertices_grid[i][1]

                num_points = max(abs(x1 - x0), abs(y1 - y0)) + 1

                x, y = np.linspace(x0, x1, num_points), np.linspace(y0, y1, num_points)
                x, y = np.round(x).astype(int), np.round(y).astype(int)

                color_img_array[y, x, 0] = 0
                color_img_array[y, x, 1] = 102
                color_img_array[y, x, 2] = 0

            if i == 3:
                x0 = self.stop_rect_vertices_grid[0][0]
                x1 = self.stop_rect_vertices_grid[i][0]
                y0 = self.stop_rect_vertices_grid[0][1]
                y1 = self.stop_rect_vertices_grid[i][1]

                num_points = max(abs(x1 - x0), abs(y1 - y0)) + 1

                x, y = np.linspace(x0, x1, num_points), np.linspace(y0, y1, num_points)
                x, y = np.round(x).astype(int), np.round(y).astype(int)

                color_img_array[y, x, 0] = 0
                color_img_array[y, x, 1] = 102
                color_img_array[y, x, 2] = 0

        for g in self.detect_point_list:
            color_img_array[g[1], g[0], 0] = 255
            color_img_array[g[1], g[0], 1] = 0
            color_img_array[g[1], g[0], 2] = 0

        for g in self.laser_set_point_list:
            color_img_array[g[1], g[0], 0] = 184
            color_img_array[g[1], g[0], 1] = 134
            color_img_array[g[1], g[0], 2] = 11

        gui_color_img_array = np.flipud(color_img_array)
        img_file_data = im.fromarray(gui_color_img_array)
        img_file_data.save("AMR_CheckOccur2.png")


        # for i in range(28, 28+360):
        #     a = "%.3f" % self.the_plan_ring[i][0]
        #     b = "%.3f" % self.the_plan_ring[i][1]
        #     c = "%.3f" % self.the_plan_ring[i][2]
        #     print(f"i={i}, self.the_plan_ring[{i}]={a}, {b}, {c}")
        #     sensor_type = round(math.fabs(self.the_plan_ring[i][2]) / 100000)
        #     print(f"i={i}, sensor_type={sensor_type}")

        for i in range(28, 28+360):
            a = "%.3f" % self.inner_plan_ring[i][0]
            b = "%.3f" % self.inner_plan_ring[i][1]
            c = "%.3f" % self.inner_plan_ring[i][2]
            print(f"i={i}, self.the_plan_ring[{i}]={a}, {b}, {c}")
            sensor_type = round(math.fabs(self.the_plan_ring[i][2]) / 100000)
            print(f"i={i}, sensor_type={sensor_type}")


    def Pos2Grid(self, x, y):
        mapOrgX=self.map_info.orgx
        mapOrgY=self.map_info.orgy
        mapScale=self.map_info.scale
        return int((x-mapOrgX)/mapScale + 0.5), int((y-mapOrgY)/mapScale + 0.5 )

    def Grid2Pos(self, gridX, gridY):
        mapOrgX=self.map_info.orgx
        mapOrgY=self.map_info.orgy
        mapScale=self.map_info.scale

        final_x = int((gridX * mapScale + mapOrgX)*1000) / 1000
        final_y = int((gridY * mapScale + mapOrgY)*1000) / 1000

        return final_x, final_y




if __name__ == '__main__':
    aco = AMR_CheckOccur('172.16.50.48')
    aco.get_map_info()
    aco.get_misc()

    while(aco.isGetFixedMapSuccess == 0):
        aco.get_fixed_map()
        time.sleep(1.0)

    aco.enable_detect_point("AMR_CheckOccur, enable_detect_point")
    time.sleep(2.0)

    ENABLE_DEBUG = 1

    aco.get_detect_point()
    aco.pre_calculate_V2()
    aco.get_detect_point()
    result = aco.calculate_V2()

    aco.SaveDebugImage()

    print(f"AMR_CheckOccur - Result= {result}")

