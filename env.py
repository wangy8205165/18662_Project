import gym
from gym import spaces
import numpy as np
import curses  # 用于实现键盘控制


class DiamondCollectorEnv(gym.Env):
    metadata = {"render.modes": ["human"]}

    def __init__(self):
            super(DiamondCollectorEnv, self).__init__()

            # 地图大小
            self.grid_size = 10
            
            # 状态空间 (agent位置)
            self.observation_space = spaces.Box(low=0, high=self.grid_size - 1, shape=(2,), dtype=np.int32)

            # 动作空间 (上下左右)
            self.action_space = spaces.Discrete(4)

            # 钻石位置
            self.diamond_pos = None

            # 初始化环境
            self.reset()
    
    def reset(self):
        # 重置智能体到左上角
        self.agent_pos = np.array([0, 0])

        # 随机生成一个钻石位置
        self.diamond_pos = np.random.randint(0, self.grid_size, size=(2,))
        
        # 确保钻石不会和智能体初始位置重合
        while np.array_equal(self.diamond_pos, self.agent_pos):
            self.diamond_pos = np.random.randint(0, self.grid_size, size=(2,))

        return self.agent_pos
    
    def step(self, action):
        # 定义移动规则
        movement = {
            0: np.array([0, 1]),   # 向右
            1: np.array([0, -1]),  # 向左
            2: np.array([1, 0]),   # 向下
            3: np.array([-1, 0])   # 向上
        }

        # 更新智能体的位置
        self.agent_pos += movement[action]

        # 边界处理
        self.agent_pos = np.clip(self.agent_pos, 0, self.grid_size - 1)

        # 检查是否收集到钻石
        done = np.array_equal(self.agent_pos, self.diamond_pos)

        # 奖励机制
        reward = 10 if done else -0.1  # 鼓励尽快找到钻石，避免无效移动

        return self.agent_pos, reward, done, {}

    def render(self, stdscr=None):
        grid = np.full((self.grid_size, self.grid_size), '⬜️')

        # 标记智能体的位置
        grid[tuple(self.agent_pos)] = '🟦'

        # 标记钻石的位置
        if not np.array_equal(self.agent_pos, self.diamond_pos):
            grid[tuple(self.diamond_pos)] = '💎'

        # 打印地图
        if stdscr:
            stdscr.clear()
            for row in grid:
                stdscr.addstr(' '.join(row) + '\n')
            stdscr.refresh()
        else:
            for row in grid:
                print(' '.join(row))
            print('\n' + '-' * 30 + '\n')

    def close(self):
        pass

def main(stdscr):
    env = DiamondCollectorEnv()

    # 初始化环境
    state = env.reset()
    done = False

    stdscr.clear()
    stdscr.addstr("使用键盘控制:\n")
    stdscr.addstr(" ↑ : 上移\n ↓ : 下移\n ← : 左移\n → : 右移\n Q : 退出\n")

    # 游戏循环
    print("Game starts!")
    while not done:
        env.render(stdscr)

        # 等待用户输入
        key = stdscr.getch()

        # 将键盘按键映射为环境动作
        if key == curses.KEY_UP:
            action = 3  # 上
        elif key == curses.KEY_DOWN:
            action = 2  # 下
        elif key == curses.KEY_LEFT:
            action = 1  # 左
        elif key == curses.KEY_RIGHT:
            action = 0  # 右
        elif key == ord('q') or key == ord('Q'):
            break
        else:
            continue  # 无效按键，跳过

        # 执行动作
        state, reward, done, _ = env.step(action)

        # 显示奖励信息
        stdscr.addstr(f"奖励: {reward}\n")

    stdscr.addstr("🎯 恭喜！成功收集到钻石！\n")
    stdscr.addstr("按 Q 键退出...\n")
    while True:
        if stdscr.getch() in [ord('q'), ord('Q')]:
            break

if __name__ == "__main__":
    print("let's play the game!")
    curses.wrapper(main)
