import time
import random

from utils import LEDCubeMap

from led_matrix import *


def def_neighbors(neighbors, x, y, lower_bound_x, upper_bound_x, lower_bound_y=0, upper_bound_y=63):
    if x != upper_bound_x and y != upper_bound_y:
        neighbors.append((x + 1, y + 1))
    if x != upper_bound_x and y != lower_bound_y:
        neighbors.append((x + 1, y - 1))
    if x != lower_bound_x and y != upper_bound_y:
        neighbors.append((x - 1, y + 1))
    if x != lower_bound_x and y != lower_bound_y:
        neighbors.append((x - 1, y - 1))
    if y != upper_bound_y:
        neighbors.append((x, y + 1))
    if y != lower_bound_y:
        neighbors.append((x, y - 1))
    if x != upper_bound_x:
        neighbors.append((x + 1, y))
    if x != lower_bound_x:
        neighbors.append((x - 1, y))
    return neighbors


def add_neighbor(d, k, data):
    neighbors = d.get(k, [])
    neighbors.append(data)
    return neighbors


class GameOfLife:
    def __init__(self, cube_map):
        self.cube_map = cube_map
        self.color = (0, 255, 0)
        self.x_range = self.cube_map.rows
        self.y_range = self.cube_map.cols
        self.old_state = []
        self.game_state = []

        for row in range(self.y_range):
            row_state = []
            for col in range(self.x_range):
                row_state.append(random.randint(0, 1))
            self.game_state.append(row_state)

        for y in range(self.y_range):
            for x in range(self.x_range):
                if self.game_state[y][x]:
                    self.cube_map.set_map_point(x, y, self.color)

        self.neighbor_map = {}

        for i in range(64):
            # ToDo: Account for neighbors on other face
            # Top North
            k = (0, i)
            neighbors = add_neighbor(self.neighbor_map, k, (192, 63 - i))
            self.neighbor_map[k] = def_neighbors(neighbors, x=0, y=i, lower_bound_x=0, upper_bound_x=63,
                                              lower_bound_y=0, upper_bound_y=63)

            k = (192, 63 - i)
            neighbors = add_neighbor(self.neighbor_map, k, (0, i))
            self.neighbor_map[k] = def_neighbors(neighbors, x=192, y=63 - i, lower_bound_x=192, upper_bound_x=64,
                                              lower_bound_y=0, upper_bound_y=63)

            # Top West
            k = (i, 63)
            neighbors = add_neighbor(self.neighbor_map, k, (256, 63 - i))
            self.neighbor_map[k] = def_neighbors(neighbors, x=i, y=63, lower_bound_x=0, upper_bound_x=63,
                                                 lower_bound_y=0, upper_bound_y=63)
            k = (256, 63 - i)
            neighbors = add_neighbor(self.neighbor_map, k, (i, 63))
            self.neighbor_map[k] = def_neighbors(neighbors, x=256, y=63 - i, lower_bound_x=256, upper_bound_x=319,
                                                 lower_bound_y=0, upper_bound_y=63)
            # Top East
            k = (i, 0)
            neighbors = add_neighbor(self.neighbor_map, k, (128, i))
            self.neighbor_map[k] = def_neighbors(neighbors, x=i, y=0, lower_bound_x=0, upper_bound_x=63,
                                                 lower_bound_y=0, upper_bound_y=63)
            k = (128, i)
            neighbors = add_neighbor(self.neighbor_map, k, (i, 0))
            self.neighbor_map[k] = def_neighbors(neighbors, x=128, y=i, lower_bound_x=128, upper_bound_x=191,
                                                 lower_bound_y=0, upper_bound_y=63)
            # Top South
            k = (63, i)
            neighbors = add_neighbor(self.neighbor_map, k, (64, i))
            self.neighbor_map[k] = def_neighbors(neighbors, x=63, y=i, lower_bound_x=0, upper_bound_x=63,
                                                 lower_bound_y=0, upper_bound_y=63)
            k = (64, i)
            neighbors = add_neighbor(self.neighbor_map, k, (63, i))
            self.neighbor_map[k] = def_neighbors(neighbors, x=64, y=i, lower_bound_x=64, upper_bound_x=127,
                                                 lower_bound_y=0, upper_bound_y=63)
            # North East
            k = (i + 192, 63)
            neighbors = add_neighbor(self.neighbor_map, k, (128 + i, 0))
            self.neighbor_map[k] = def_neighbors(neighbors, x=i + 192, y=63, lower_bound_x=192, upper_bound_x=255,
                                                 lower_bound_y=0, upper_bound_y=63)
            k = (128 + i, 0)
            neighbors = add_neighbor(self.neighbor_map, k, (i + 192, 63))
            self.neighbor_map[k] = def_neighbors(neighbors, x=128 + i, y=0, lower_bound_x=128, upper_bound_x=191,
                                                 lower_bound_y=0, upper_bound_y=63)
            # North West
            k = (i + 192, 0)
            neighbors = add_neighbor(self.neighbor_map, k, (256 + i, 63))
            self.neighbor_map[k] = def_neighbors(neighbors, x=i + 192, y=0, lower_bound_x=192, upper_bound_x=255,
                                                 lower_bound_y=0, upper_bound_y=63)
            k = (256 + i, 63)
            neighbors = add_neighbor(self.neighbor_map, k, (i + 192, 0))
            self.neighbor_map[k] = def_neighbors(neighbors, x=256 + i, y=63, lower_bound_x=256, upper_bound_x=319,
                                                 lower_bound_y=0, upper_bound_y=63)
            # South West
            k = (i + 64, 63)
            neighbors = add_neighbor(self.neighbor_map, k, (256 + i, 0))
            self.neighbor_map[k] = def_neighbors(neighbors, x=i +64, y=63, lower_bound_x=64, upper_bound_x=127,
                                                 lower_bound_y=0, upper_bound_y=63)
            k = (256 + i, 0)
            neighbors = add_neighbor(self.neighbor_map, k, (i + 64, 63))
            self.neighbor_map[k] = def_neighbors(neighbors, x=256 + i, y=0, lower_bound_x=256, upper_bound_x=319,
                                                 lower_bound_y=0, upper_bound_y=63)
            # South East
            k = (i + 64, 0)
            neighbors = add_neighbor(self.neighbor_map, k, (i + 128, 63))
            self.neighbor_map[k] = def_neighbors(neighbors, x=i + 64, y=0, lower_bound_x=64, upper_bound_x=127,
                                                 lower_bound_y=0, upper_bound_y=63)
            k = (i + 128, 63)
            neighbors = add_neighbor(self.neighbor_map, k, (i + 64, 0))
            self.neighbor_map[k] = def_neighbors(neighbors, x=i + 128, y=63, lower_bound_x=128, upper_bound_x=191,
                                                 lower_bound_y=0, upper_bound_y=63)
            # Bottom North
            k = (i + 320, 63)
            neighbors = add_neighbor(self.neighbor_map, k, (255, i))
            self.neighbor_map[k] = def_neighbors(neighbors, x=i + 320, y=63, lower_bound_x=320, upper_bound_x=383,
                                                 lower_bound_y=0, upper_bound_y=63)
            k = (255, i)
            neighbors = add_neighbor(self.neighbor_map, k, (i + 320, 63))
            self.neighbor_map[k] = def_neighbors(neighbors, x=255, y=i, lower_bound_x=192, upper_bound_x=255,
                                                 lower_bound_y=0, upper_bound_y=63)
            # Bottom East
            k = (383, i)
            neighbors = add_neighbor(self.neighbor_map, k, (191, 63 - i))
            self.neighbor_map[k] = def_neighbors(neighbors, x=383, y=i, lower_bound_x=320, upper_bound_x=383,
                                                 lower_bound_y=0, upper_bound_y=63)
            k = (191, 63 - i)
            neighbors = add_neighbor(self.neighbor_map, k, (383, i))
            self.neighbor_map[k] = def_neighbors(neighbors, x=191, y=63 - i, lower_bound_x=128, upper_bound_x=191,
                                                 lower_bound_y=0, upper_bound_y=63)
            # Bottom West
            k = (320, i)
            neighbors = add_neighbor(self.neighbor_map, k, (319, i))
            self.neighbor_map[k] = def_neighbors(neighbors, x=320, y=i, lower_bound_x=320, upper_bound_x=383,
                                                 lower_bound_y=0, upper_bound_y=63)
            k = (319, i)
            neighbors = add_neighbor(self.neighbor_map, k, (320, i))
            self.neighbor_map[k] = def_neighbors(neighbors, x=319, y=i, lower_bound_x=256, upper_bound_x=319,
                                                 lower_bound_y=0, upper_bound_y=63)
            # Bottom South
            k = (320 + i, 0)
            neighbors = add_neighbor(self.neighbor_map, k, (127, 63 - i))
            self.neighbor_map[k] = def_neighbors(neighbors, x=320 + i, y=0, lower_bound_x=320, upper_bound_x=383,
                                                 lower_bound_y=0, upper_bound_y=63)
            k = (127, 63 - i)
            neighbors = add_neighbor(self.neighbor_map, k, (320 + i, 0))
            self.neighbor_map[k] = def_neighbors(neighbors, x=127, y=63 - i, lower_bound_x=64, upper_bound_x=127,
                                                 lower_bound_y=0, upper_bound_y=63)

        # Process standard points, aka not on edges
        for y in range(self.y_range):
            for x in range(self.x_range):
                if not self.neighbor_map.get((x,y), False):
                    self.neighbor_map[(x, y)] = def_neighbors([], x, y, lower_bound_x=0, upper_bound_x=383)


    def count_neighbors(self, coord):
        neighbor_count = 0
        neighbors = self.neighbor_map[coord]
        for neighbor in neighbors:
            neighbor_count += self.old_state[neighbor[1]][neighbor[0]]
        return neighbor_count


    def update(self):
        # Determine next state
        self.cube_map.blank()
        self.old_state = self.game_state
        self.game_state = []
        for y in range(self.y_range):
            row_state = []
            for x in range(self.x_range):
                current_state = self.old_state[y][x]
                n_count = self.count_neighbors((x, y))
                if current_state:
                    if n_count == 2 or n_count == 3:
                        current_state = 1
                    else:
                        current_state = 0
                else:
                    if n_count == 3:
                        current_state = 1
                row_state.append(current_state)
                if current_state:
                    self.cube_map.set_map_point(x, y, self.color)
            self.game_state.append(row_state)


def play_GOL(matrix):
    image = Image.new("RGB", (6 * 64, 64))
    pixels = image.load()
    cube_map = LEDCubeMap(rows=image.size[0], cols=image.size[1], pixel_input_map=pixels)

    GOL = GameOfLife(cube_map)

    while True:
        matrix.Clear()
        matrix.SetImage(image)
        GOL.update()



def main():
    matrix = RGBMatrix(options=options)
    play_GOL(matrix)


if __name__ == "__main__":
    main()
