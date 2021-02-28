import time
import random

from utils import LEDCubeMap

from led_matrix import *


def def_neighbors(neighbors, x, y, lower_bound_x, upper_bound_x, lower_bound_y, upper_bound_y):
    if x != upper_bound_x and y != upper_bound_y:
        neighbors.append(f"{x + 1}.{y + 1}")
    if x != upper_bound_x and y != lower_bound_y:
        neighbors.append(f"{x + 1}.{y - 1}")
    if x != lower_bound_x and y != upper_bound_y:
        neighbors.append(f"{x - 1}.{y + 1}")
    if x != lower_bound_x and y != lower_bound_y:
        neighbors.append(f"{x - 1}.{y - 1}")
    if y != upper_bound_y:
        neighbors.append(f"{x}.{y + 1}")
    if y != lower_bound_y:
        neighbors.append(f"{x}.{y - 1}")
    if x != upper_bound_x:
        neighbors.append(f"{x + 1}.{y}")
    if x != lower_bound_x:
        neighbors.append(f"{x - 1}.{y}")
    return neighbors


def add_neighbor(d, k, data):
    neighbors = d.get(k, [])
    neighbors.append(data)
    return neighbors


class GameOfLife:
    def __init__(self, cube_map):
        self.cube_map = cube_map
        self.color = (255, 255, 255)
        self.game_state = []

        for col in range(self.cube_map.cols):
            row_state = []
            for row in range(self.cube_map.rows):
                row_state.append(random.randint(0, 1))
            self.game_state.append(row_state)

        self.neighbor_map = {}

        for i in range(64):
            # ToDo: Account for neighbors on other face
            # Top North
            k = f"0.{i}"
            neighbors = add_neighbor(self.neighbor_map, k, f"192.{63 - i}")
            self.neighbor_map[k] = def_neighbors(neighbors, x=0, y=i, lower_bound_x=0, upper_bound_x=63,
                                              lower_bound_y=0, upper_bound_y=63)

            k = f"192.{63 - i}"
            neighbors = add_neighbor(self.neighbor_map, k, f"0.{i}")
            self.neighbor_map[k] = def_neighbors(neighbors, x=192, y=63 - i, lower_bound_x=192, upper_bound_x=64,
                                              lower_bound_y=0, upper_bound_y=63)

            # Top West
            k = f"{i}.63"
            neighbors = add_neighbor(self.neighbor_map, k, f"256.{63 - i}")
            self.neighbor_map[k] = def_neighbors(neighbors, x=i, y=63, lower_bound_x=0, upper_bound_x=63,
                                                 lower_bound_y=0, upper_bound_y=63)
            k = f"256.{63 - i}"
            neighbors = add_neighbor(self.neighbor_map, k, f"{i}.63")
            self.neighbor_map[k] = def_neighbors(neighbors, x=256, y=63 - i, lower_bound_x=256, upper_bound_x=319,
                                                 lower_bound_y=0, upper_bound_y=63)
            # Top East
            k = f"{i}.0"
            neighbors = add_neighbor(self.neighbor_map, k, f"128.{i}")
            self.neighbor_map[k] = def_neighbors(neighbors, x=i, y=0, lower_bound_x=0, upper_bound_x=63,
                                                 lower_bound_y=0, upper_bound_y=63)
            k = f"128.{i}"
            neighbors = add_neighbor(self.neighbor_map, k, f"{i}.0")
            self.neighbor_map[k] = def_neighbors(neighbors, x=128, y=i, lower_bound_x=128, upper_bound_x=191,
                                                 lower_bound_y=0, upper_bound_y=63)
            # Top South
            k = f"63.{i}"
            neighbors = add_neighbor(self.neighbor_map, k, f"64.{i}")
            self.neighbor_map[k] = def_neighbors(neighbors, x=63, y=i, lower_bound_x=0, upper_bound_x=63,
                                                 lower_bound_y=0, upper_bound_y=63)
            k = f"64.{i}"
            neighbors = add_neighbor(self.neighbor_map, k, f"63.{i}")
            self.neighbor_map[k] = def_neighbors(neighbors, x=64, y=i, lower_bound_x=64, upper_bound_x=127,
                                                 lower_bound_y=0, upper_bound_y=63)
            # North East
            k = f"{i + 192}.63"
            neighbors = add_neighbor(self.neighbor_map, k, f"{128 + i}.0")
            self.neighbor_map[k] = def_neighbors(neighbors, x=i + 192, y=63, lower_bound_x=192, upper_bound_x=255,
                                                 lower_bound_y=0, upper_bound_y=63)
            k = f"{128 + i}.0"
            neighbors = add_neighbor(self.neighbor_map, k, f"{i + 192}.63")
            self.neighbor_map[k] = def_neighbors(neighbors, x=128 + i, y=0, lower_bound_x=128, upper_bound_x=191,
                                                 lower_bound_y=0, upper_bound_y=63)
            # North West
            k = f"{i + 192}.0"
            neighbors = add_neighbor(self.neighbor_map, k, f"{256 + i}.63")
            self.neighbor_map[k] = def_neighbors(neighbors, x=i + 192, y=0, lower_bound_x=192, upper_bound_x=255,
                                                 lower_bound_y=0, upper_bound_y=63)
            k = f"{256 + i}.63"
            neighbors = add_neighbor(self.neighbor_map, k, f"{i + 192}.0")
            self.neighbor_map[k] = def_neighbors(neighbors, x=256 + i, y=63, lower_bound_x=256, upper_bound_x=319,
                                                 lower_bound_y=0, upper_bound_y=63)
            # South West
            k = f"{i + 64}.63"
            neighbors = add_neighbor(self.neighbor_map, k, f"{256 + i}.0")
            self.neighbor_map[k] = def_neighbors(neighbors, x=i +64, y=63, lower_bound_x=64, upper_bound_x=127,
                                                 lower_bound_y=0, upper_bound_y=63)
            k = f"{256 + i}.0"
            neighbors = add_neighbor(self.neighbor_map, k, f"{i + 64}.63")
            self.neighbor_map[k] = def_neighbors(neighbors, x=256 + i, y=0, lower_bound_x=256, upper_bound_x=319,
                                                 lower_bound_y=0, upper_bound_y=63)
            # South East
            k = f"{i + 64}.0"
            neighbors = add_neighbor(self.neighbor_map, k, f"{i + 128}.63")
            self.neighbor_map[k] = def_neighbors(neighbors, x=i + 64, y=0, lower_bound_x=64, upper_bound_x=127,
                                                 lower_bound_y=0, upper_bound_y=63)
            k = f"{i + 128}.63"
            neighbors = add_neighbor(self.neighbor_map, k, f"{i + 64}.0")
            self.neighbor_map[k] = def_neighbors(neighbors, x=i + 128, y=63, lower_bound_x=128, upper_bound_x=191,
                                                 lower_bound_y=0, upper_bound_y=63)
            # Bottom North
            k = f"{i + 320}.63"
            neighbors = add_neighbor(self.neighbor_map, k, f"255.{i}")
            self.neighbor_map[k] = def_neighbors(neighbors, x=i + 320, y=63, lower_bound_x=320, upper_bound_x=383,
                                                 lower_bound_y=0, upper_bound_y=63)
            k = f"255.{i}"
            neighbors = add_neighbor(self.neighbor_map, k, f"{i + 320}.63")
            self.neighbor_map[k] = def_neighbors(neighbors, x=255, y=i, lower_bound_x=192, upper_bound_x=255,
                                                 lower_bound_y=0, upper_bound_y=63)
            # Bottom East
            k = f"383.{i}"
            neighbors = add_neighbor(self.neighbor_map, k, f"191.{63 - i}")
            self.neighbor_map[k] = def_neighbors(neighbors, x=383, y=i, lower_bound_x=320, upper_bound_x=383,
                                                 lower_bound_y=0, upper_bound_y=63)
            k = f"191.{63 - i}"
            neighbors = add_neighbor(self.neighbor_map, k, f"383.{i}")
            self.neighbor_map[k] = def_neighbors(neighbors, x=191, y=63 - i, lower_bound_x=128, upper_bound_x=191,
                                                 lower_bound_y=0, upper_bound_y=63)
            # Bottom West
            k = f"320.{i}"
            neighbors = add_neighbor(self.neighbor_map, k, f"319.{i}")
            self.neighbor_map[k] = def_neighbors(neighbors, x=320, y=i, lower_bound_x=320, upper_bound_x=383,
                                                 lower_bound_y=0, upper_bound_y=63)
            k = f"319.{i}"
            neighbors = add_neighbor(self.neighbor_map, k, f"320.{i}")
            self.neighbor_map[k] = def_neighbors(neighbors, x=319, y=i, lower_bound_x=256, upper_bound_x=319,
                                                 lower_bound_y=0, upper_bound_y=63)
            # Bottom South
            k = f"{320 + i}.0"
            neighbors = add_neighbor(self.neighbor_map, k, f"127.{63 - i}")
            self.neighbor_map[k] = def_neighbors(neighbors, x=320 + i, y=0, lower_bound_x=320, upper_bound_x=383,
                                                 lower_bound_y=0, upper_bound_y=63)
            k = f"127.{63 - i}"
            neighbors = add_neighbor(self.neighbor_map, k, f"{320 + i}.0")
            self.neighbor_map[k] = def_neighbors(neighbors, x=127, y=63 - i, lower_bound_x=64, upper_bound_x=127,
                                                 lower_bound_y=0, upper_bound_y=63)


    def count_neighbors(self, coord):
        neighbor_count = 0
        neighbors = self.neighbor_map[coord]
        for neighbor in neighbors:
            neighbor_count += self.game_state[neighbor[0]][neighbor[1]]
        return neighbor_count


    def update(self):
        # Determine next state
        for y in range(self.cube_map.rows):
            for x in range(self.cube_map.cols):
                current_state = self.game_state[x][y]
                n_count = self.count_neighbors(f"{x}.{y}")
                if(current_state):
                    if n_count < 2 or n_count > 3:
                        current_state = 1
                else:
                    if n_count == 3:
                        current_state = 1
                self.game_state[x][y] = current_state
        # Update pixels
        self.cube_map.blank()
        for y, col in enumerate(self.game_state):
            for x, value in enumerate(col):
                if value:
                    self.cube_map.set_map_point(x, y, self.color)


def play_GOL(matrix):
    image = Image.new("RGB", (6 * 64, 64))
    pixels = image.load()
    cube_map = LEDCubeMap(rows=image.size[0], cols=image.size[1], pixel_input_map=pixels)

    GOL = GameOfLife(cube_map)

    while True:
        GOL.update()
        time.sleep(0.1)


def main():
    matrix = RGBMatrix(options=options)
    play_GOL(matrix)


if __name__ == "__main__":
    main()
