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
    """
    This allows us to either get an existing neighbor list and add to it, or create a new list. This sorts out not
    needing to know if the location already has a neighbor defined. This is expected to happen in corners where there
    are neighbors on more than one additional face of the cube.
    :param d: Mapping dictionary
    :param k: Key to the dictionary that is the current location as the 2d position in the form of a tuple (x, y)
    :param data: This is a single neighbor's location, format is the same as k
    :return:
    """
    neighbors = d.get(k, [])
    neighbors.append(data)
    return neighbors


def get_plus_minus_one(n, idx=0):
    """
    This function cleans up some of the code for calculating neighbors on other faces that we know to be on either side
    of the primary neighbor location specified by n
    :param n: This is a location as the 2D position in the form of a tuple (x, y)
    :param idx: This specifies the index of the tuple that is being manipulated. The default idx=0 means that the x
    coordinate will be manipulated
    :return: Two new neighbors
    """
    if idx == 0:
        n2 = (n[0] + 1, n[1])
        n3 = (n[0] - 1, n[1])
    else:
        n2 = (n[0], n[1] + 1)
        n3 = (n[0], n[1] - 1)
    return [n2, n3]

class GameOfLife:
    def __init__(self, cube_map):
        self.cube_map = cube_map
        # Red, Green, Blue
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        color = [r, g, b]
        if r < 150 and g < 150 and b < 150:
            # We have a dim color, randomly boost brightness of one color for better effect
            choice = random.randint(0, 2)
            color[choice] = 200
        self.color = tuple(color)

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

        # Iterate and process all edges
        for i in range(64):
            '''
            Organization:
            The first few lines of this for loop are annotated with what the individual parts do, this pattern is then 
            repeated for different sections of the cube for the rest of the for loop
            The code blocks in this for loop sort out all of the edges and corners since these positions have neighbors 
            that exist on a different face and need to be mapped
            The next code block after this for loop takes care of non-edges whose neighbors don't exist on another face
            '''
            # Location
            # Top North
            k = (0, i) # k: This is the key aka, the location where neighbors are calculated from
            n = (192, 63 - i)  # n: This is a neighbor
            neighbors = add_neighbor(self.neighbor_map, k, n)
            if i != 0 and i != 63:
                neighbors.extend(get_plus_minus_one(n, idx=1))
            self.neighbor_map[k] = def_neighbors(neighbors, x=0, y=i, lower_bound_x=0, upper_bound_x=63,
                                              lower_bound_y=0, upper_bound_y=63)
            k = (192, 63 - i)
            n = (0, i)
            neighbors = add_neighbor(self.neighbor_map, k, n)
            if i != 0 and i != 63:
                neighbors.extend(get_plus_minus_one(n, idx=1))
            self.neighbor_map[k] = def_neighbors(neighbors, x=192, y=63 - i, lower_bound_x=192, upper_bound_x=64,
                                              lower_bound_y=0, upper_bound_y=63)
            # Top West
            k = (i, 63)
            n = (256, 63 - i)
            neighbors = add_neighbor(self.neighbor_map, k, n)
            if i != 0 and i != 63:
                neighbors.extend(get_plus_minus_one(n, idx=1))
            self.neighbor_map[k] = def_neighbors(neighbors, x=i, y=63, lower_bound_x=0, upper_bound_x=63,
                                                 lower_bound_y=0, upper_bound_y=63)
            k = (256, 63 - i)
            n = (i, 63)
            neighbors = add_neighbor(self.neighbor_map, k, n)
            if i != 0 and i != 63:
                neighbors.extend(get_plus_minus_one(n))
            self.neighbor_map[k] = def_neighbors(neighbors, x=256, y=63 - i, lower_bound_x=256, upper_bound_x=319,
                                                 lower_bound_y=0, upper_bound_y=63)
            # Top East
            k = (i, 0)
            n = (128, i)
            neighbors = add_neighbor(self.neighbor_map, k, n)
            if i != 0 and i != 63:
                neighbors.extend(get_plus_minus_one(n, idx=1))
            self.neighbor_map[k] = def_neighbors(neighbors, x=i, y=0, lower_bound_x=0, upper_bound_x=63,
                                                 lower_bound_y=0, upper_bound_y=63)
            k = (128, i)
            n = (i, 0)
            neighbors = add_neighbor(self.neighbor_map, k, n)
            if i != 0 and i != 63:
                neighbors.extend(get_plus_minus_one(n))
            self.neighbor_map[k] = def_neighbors(neighbors, x=128, y=i, lower_bound_x=128, upper_bound_x=191,
                                                 lower_bound_y=0, upper_bound_y=63)
            # Top South
            k = (63, i)
            n = (64, i)
            neighbors = add_neighbor(self.neighbor_map, k, n)
            if i != 0 and i != 63:
                neighbors.extend(get_plus_minus_one(n, idx=1))
            self.neighbor_map[k] = def_neighbors(neighbors, x=63, y=i, lower_bound_x=0, upper_bound_x=63,
                                                 lower_bound_y=0, upper_bound_y=63)
            k = (64, i)
            n = (63, i)
            neighbors = add_neighbor(self.neighbor_map, k, n)
            if i != 0 and i != 63:
                neighbors.extend(get_plus_minus_one(n, idx=1))
            self.neighbor_map[k] = def_neighbors(neighbors, x=64, y=i, lower_bound_x=64, upper_bound_x=127,
                                                 lower_bound_y=0, upper_bound_y=63)
            # North East
            k = (i + 192, 63)
            n = (128 + i, 0)
            neighbors = add_neighbor(self.neighbor_map, k, n)
            if i != 0 and i != 63:
                neighbors.extend(get_plus_minus_one(n))
            self.neighbor_map[k] = def_neighbors(neighbors, x=i + 192, y=63, lower_bound_x=192, upper_bound_x=255,
                                                 lower_bound_y=0, upper_bound_y=63)
            k = (128 + i, 0)
            n = (i + 192, 63)
            neighbors = add_neighbor(self.neighbor_map, k, n)
            if i != 0 and i != 63:
                neighbors.extend(get_plus_minus_one(n))
            self.neighbor_map[k] = def_neighbors(neighbors, x=128 + i, y=0, lower_bound_x=128, upper_bound_x=191,
                                                 lower_bound_y=0, upper_bound_y=63)
            # North West
            k = (i + 192, 0)
            n = (256 + i, 63)
            neighbors = add_neighbor(self.neighbor_map, k, n)
            if i != 0 and i != 63:
                neighbors.extend(get_plus_minus_one(n))
            self.neighbor_map[k] = def_neighbors(neighbors, x=i + 192, y=0, lower_bound_x=192, upper_bound_x=255,
                                                 lower_bound_y=0, upper_bound_y=63)
            k = (256 + i, 63)
            n = (i + 192, 0)
            neighbors = add_neighbor(self.neighbor_map, k, n)
            if i != 0 and i != 63:
                neighbors.extend(get_plus_minus_one(n))
            self.neighbor_map[k] = def_neighbors(neighbors, x=256 + i, y=63, lower_bound_x=256, upper_bound_x=319,
                                                 lower_bound_y=0, upper_bound_y=63)
            # South West
            k = (i + 64, 63)
            n = (256 + i, 0)
            neighbors = add_neighbor(self.neighbor_map, k, n)
            if i != 0 and i != 63:
                neighbors.extend(get_plus_minus_one(n))
            self.neighbor_map[k] = def_neighbors(neighbors, x=i +64, y=63, lower_bound_x=64, upper_bound_x=127,
                                                 lower_bound_y=0, upper_bound_y=63)
            k = (256 + i, 0)
            n = (i + 64, 63)
            neighbors = add_neighbor(self.neighbor_map, k, n)
            if i != 0 and i != 63:
                neighbors.extend(get_plus_minus_one(n))
            self.neighbor_map[k] = def_neighbors(neighbors, x=256 + i, y=0, lower_bound_x=256, upper_bound_x=319,
                                                 lower_bound_y=0, upper_bound_y=63)
            # South East
            k = (i + 64, 0)
            n = (i + 128, 63)
            neighbors = add_neighbor(self.neighbor_map, k, n)
            if i != 0 and i != 63:
                neighbors.extend(get_plus_minus_one(n))
            self.neighbor_map[k] = def_neighbors(neighbors, x=i + 64, y=0, lower_bound_x=64, upper_bound_x=127,
                                                 lower_bound_y=0, upper_bound_y=63)
            k = (i + 128, 63)
            n = (i + 64, 0)
            neighbors = add_neighbor(self.neighbor_map, k, n)
            if i != 0 and i != 63:
                neighbors.extend(get_plus_minus_one(n))
            self.neighbor_map[k] = def_neighbors(neighbors, x=i + 128, y=63, lower_bound_x=128, upper_bound_x=191,
                                                 lower_bound_y=0, upper_bound_y=63)
            # Bottom North
            k = (i + 320, 63)
            n = (255, i)
            neighbors = add_neighbor(self.neighbor_map, k, n)
            if i != 0 and i != 63:
                neighbors.extend(get_plus_minus_one(n, idx=1))
            self.neighbor_map[k] = def_neighbors(neighbors, x=i + 320, y=63, lower_bound_x=320, upper_bound_x=383,
                                                 lower_bound_y=0, upper_bound_y=63)
            k = (255, i)
            n = (i + 320, 63)
            neighbors = add_neighbor(self.neighbor_map, k, n)
            if i != 0 and i != 63:
                neighbors.extend(get_plus_minus_one(n))
            self.neighbor_map[k] = def_neighbors(neighbors, x=255, y=i, lower_bound_x=192, upper_bound_x=255,
                                                 lower_bound_y=0, upper_bound_y=63)
            # Bottom East
            k = (383, i)
            n = (191, 63 - i)
            neighbors = add_neighbor(self.neighbor_map, k, n)
            if i != 0 and i != 63:
                neighbors.extend(get_plus_minus_one(n, idx=1))
            self.neighbor_map[k] = def_neighbors(neighbors, x=383, y=i, lower_bound_x=320, upper_bound_x=383,
                                                 lower_bound_y=0, upper_bound_y=63)
            k = (191, 63 - i)
            n = (383, i)
            neighbors = add_neighbor(self.neighbor_map, k, n)
            if i != 0 and i != 63:
                neighbors.extend(get_plus_minus_one(n, idx=1))
            self.neighbor_map[k] = def_neighbors(neighbors, x=191, y=63 - i, lower_bound_x=128, upper_bound_x=191,
                                                 lower_bound_y=0, upper_bound_y=63)
            # Bottom West
            k = (320, i)
            n = (319, i)
            neighbors = add_neighbor(self.neighbor_map, k, n)
            if i != 0 and i != 63:
                neighbors.extend(get_plus_minus_one(n, idx=1))
            self.neighbor_map[k] = def_neighbors(neighbors, x=320, y=i, lower_bound_x=320, upper_bound_x=383,
                                                 lower_bound_y=0, upper_bound_y=63)
            k = (319, i)
            n = (320, i)
            neighbors = add_neighbor(self.neighbor_map, k, n)
            if i != 0 and i != 63:
                neighbors.extend(get_plus_minus_one(n, idx=1))
            self.neighbor_map[k] = def_neighbors(neighbors, x=319, y=i, lower_bound_x=256, upper_bound_x=319,
                                                 lower_bound_y=0, upper_bound_y=63)
            # Bottom South
            k = (320 + i, 0)
            n = (127, 63 - i)
            neighbors = add_neighbor(self.neighbor_map, k, n)
            if i != 0 and i != 63:
                neighbors.extend(get_plus_minus_one(n, idx=1))
            self.neighbor_map[k] = def_neighbors(neighbors, x=320 + i, y=0, lower_bound_x=320, upper_bound_x=383,
                                                 lower_bound_y=0, upper_bound_y=63)
            k = (127, 63 - i)
            n = (320 + i, 0)
            neighbors = add_neighbor(self.neighbor_map, k, n)
            if i != 0 and i != 63:
                neighbors.extend(get_plus_minus_one(n))
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
