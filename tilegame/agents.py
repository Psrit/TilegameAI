from tilegame.interfaces import Agent, Game
from tilegame.utils import PriorityQueue


class AStarAgent(Agent):
    def __init__(self, game: Game):
        self.game = game

    def search(self, heuristic: callable):
        # 求解出来的动作序列, 被返回
        actions = []

        # 游戏初始态
        init_state = self.game.init_state

        # 状态树目前的叶节点
        fringe_states = PriorityQueue()

        # 状态树目前的内部节点
        tree_states = [init_state, ]

        # 标记节点在 `tree_states` 中的下标
        index = -1

        # 目前已访问到的节点
        # { state: (action from parent, parent's index in `tree_states`,
        # total cost g from the initial state, f = g + h for the state) }
        visited_states = {
            init_state: (None, index, 0, heuristic(init_state, self.game))
        }

        # 刚被从叶节点队列中弹出的状态节点
        # 可以认为初始态经过一次压入之后立马弹出
        popped_state = init_state
        index = 0

        while True:
            if self.game.is_goal_state(popped_state):
                action, parent_index, _, _ = visited_states.get(popped_state)
                while action:
                    actions.insert(0, action)
                    parent_state = tree_states[parent_index]
                    action, parent_index, _, _ = visited_states.get(parent_state)

                return actions

            # 获取 popped_state 的相关信息
            _, _, total_cost_popped, _ = visited_states.get(popped_state)

            for state, action, cost in popped_state.successors:
                # state 已被加入状态树内部
                if state in tree_states:
                    continue

                # 查看 state 是否已被访问到 (是否已被纳入叶节点)
                former_record = visited_states.get(state, None)

                # 若 state 已是叶节点
                if former_record:
                    former_action, former_parent, former_g, former_f = former_record
                    new_g = total_cost_popped + cost

                    if former_g <= new_g:
                        continue
                    # 若选取 popped_state 作为父节点使得 g 值更小,
                    # 更新 state 在 visited_states 中的信息
                    else:
                        new_f = former_f - former_g + new_g

                else:
                    new_g = total_cost_popped + cost
                    new_f = new_g + heuristic(state, self.game)

                visited_states.update({
                    state: (action, index, new_g, new_f)
                })

                fringe_states.update(state, new_f)

            # 弹出一个叶节点, 并入状态树内部, 在下一次循环中将其展开 (访问其后继, 作为新的叶子)
            try:
                popped_state = fringe_states.pop()
            except IndexError:
                # Goal state is inaccessible
                return None

            tree_states.append(popped_state)
            index += 1
            print(index)
