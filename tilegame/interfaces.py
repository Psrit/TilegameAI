class GameState(object):
    @property
    def successors(self):
        """
        返回后继状态节点的信息三元组 (state, action, cost).

        :return: tuple

        """
        return NotImplemented


class Game(object):
    def __init__(self):
        self.goal_state = None
        self.init_state = None

    def is_goal_state(self, state: GameState):
        """
        判断某状态节点是否是目标状态.

        :param state: GameState
        :return: boolean

        """
        return state == self.goal_state


class Agent(object):
    def search(self, *args):
        """
        返回完成游戏所需要采取的动作序列.

        :return: list
        """
        return NotImplemented
