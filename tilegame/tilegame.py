from copy import deepcopy
from numbers import Number
from typing import Sequence
import numpy as np

from tilegame.interfaces import Game, GameState
from tilegame.agents import AStarAgent


class Coordinate(tuple):
    def __new__(cls, row, col):
        return super(Coordinate, cls).__new__(cls, [row, col])

    def __init__(self, row, col):
        self.row = row
        self.col = col

    def __add__(self, direction):
        try:
            d_row, d_col = Directions.coord_delta[direction]
        except KeyError:
            raise ValueError(f"Invalid direction: {direction}")
        else:
            return Coordinate(
                self.row + d_row,
                self.col + d_col
            )

    def __sub__(self, direction):
        try:
            d_row, d_col = Directions.coord_delta[direction]
        except KeyError:
            raise ValueError(f"Invalid direction: {direction}")
        else:
            return Coordinate(
                self.row - d_row,
                self.col - d_col
            )

    # def __str__(self):
    #     return f"({self.row}, {self.col})"


class Directions:
    UP = "Up"
    DOWN = "Down"
    LEFT = "Left"
    RIGHT = "Right"

    coord_delta = {
        UP: (-1, 0),
        DOWN: (1, 0),
        LEFT: (0, -1),
        RIGHT: (0, 1)
    }


class TileGameState(GameState):
    def __init__(self, tile, coordinate0):
        self.tile = tile
        self.nrows, self.ncols = tile.shape
        self.coordinate0 = coordinate0

    def __eq__(self, other):
        return np.all(self.tile == other.tile)

    def __str__(self):
        return str(self.tile)

    # TODO: Check here
    def __hash__(self):
        return id(self.tile)

    def _is_coord_valid(self, row, col):
        if 0 <= row <= self.nrows - 1 and 0 <= col <= self.ncols - 1:
            return True
        else:
            return False

    def _is_move_possible(self, direction):
        new_coordinate0 = self.coordinate0 + direction

        if self._is_coord_valid(*new_coordinate0):
            return new_coordinate0
        else:
            return False

    def move(self, direction):
        _new_coordinate0 = self._is_move_possible(direction)

        # 不可行的移动, 啥也不做
        if not _new_coordinate0:
            return

        # 可行的移动
        _tile = deepcopy(self.tile)
        _tile[self.coordinate0] = _tile[_new_coordinate0]
        _tile[_new_coordinate0] = 0
        return TileGameState(_tile, _new_coordinate0)

    @property
    def successors(self):
        """
        返回后继状态节点的信息三元组 (state, action, cost).

        :return: tuple

        """
        _successors = []
        for direction in Directions.coord_delta.keys():
            if self._is_move_possible(direction):
                _successors.append((
                    self.move(direction),
                    direction,
                    1
                ))

        return _successors


class TileGame(Game):
    # 给定图像边长, 随机初始化打乱拼图
    def __init__(self, shape=(4, 4), MAX_INIT_NSTEPS=10):
        super(Game, self).__init__()

        if not shape:
            raise ValueError(f"Invalid shape parameter: {shape}")

        if isinstance(shape, Number):
            self.nrows = self.ncols = shape
        elif isinstance(shape, Sequence):
            if len(shape) == 1:
                self.nrows = self.ncols = shape[0]
            else:
                self.nrows, self.ncols = shape[0:2]
        else:
            raise ValueError(f"Invalid shape parameter: {shape}")

        _tile = np.resize(
            [(i + 1) % self.npieces for i in range(0, self.npieces)],
            (self.nrows, self.ncols)
        )
        _coordinate0 = Coordinate(self.nrows - 1, self.ncols - 1)
        self.state = TileGameState(_tile, _coordinate0)
        self.goal_state = self.init_state = self.state

        self.MAX_INIT_NSTEPS = MAX_INIT_NSTEPS
        self.initialize_randomly()
        print("initial state\n"
              "=============")
        print(self.state)

    @property
    def npieces(self):
        return self.nrows * self.ncols

    def initialize_randomly(self):
        # nsteps = np.random.randint(MAX_INIT_NSTEPS)
        nsteps = self.MAX_INIT_NSTEPS

        actions = []

        for i in range(nsteps):
            succ = self.state.successors
            new_state, new_action, _ = succ[np.random.randint(len(succ))]
            self.state = new_state
            actions.append(new_action)

        self.init_state = self.state

        return actions

    def play(self, actions):
        import time
        for action in actions:
            # 清屏
            print("\033[H\033[J")
            self.state = self.state.move(action)
            print(self.state)
            time.sleep(1)

        print("\n"
              "Game finished!")


def heuristic_tilegame(state: TileGameState, game: TileGame):
    return np.count_nonzero(state.tile - game.goal_state.tile)


if __name__ == "__main__":
    tilegame = TileGame(shape=(4, 4), MAX_INIT_NSTEPS=30)
    actions = AStarAgent(tilegame).search(heuristic_tilegame)
    print(actions)
    print("\n")

    tilegame.play(actions)
