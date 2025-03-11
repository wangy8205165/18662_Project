import gym
from gym import spaces
import numpy as np
import curses  # 用于实现键盘控制
import pygame
import sys
import time

class MultiAgentResourceEnv(gym.Env):
    metadata = {"render.modes": ["human"]}

    def __init__(self):
            super(MultiAgentResourceEnv, self).__init__()

            # 地图大小
            self.grid_size = 20
            
            # 状态空间 (agent位置)
            self.observation_space = spaces.Dict({
                "agent_1": spaces.Box(low=0, high=self.grid_size - 1, shape=(2,), dtype=np.int32),
                "agent_2": spaces.Box(low=0, high=self.grid_size - 1, shape=(2,), dtype=np.int32)
            })
            # 动作空间 (上下左右)
            self.action_space = spaces.Discrete(4)

            png_size = 30
            self.assets = {
                "agent_1": pygame.transform.scale(pygame.image.load("assets/player.png"), (png_size, png_size)),
                "agent_2": pygame.transform.scale(pygame.image.load("assets/zombie.png"), (png_size, png_size)),
                "wood": pygame.transform.scale(pygame.image.load("assets/wood.png"), (png_size, png_size)),
                "stone": pygame.transform.scale(pygame.image.load("assets/stone.png"), (png_size, png_size)),
                "iron": pygame.transform.scale(pygame.image.load("assets/iron.png"), (png_size, png_size)),
                "diamond": pygame.transform.scale(pygame.image.load("assets/diamond.png"), (png_size, png_size)),
            }

            # Resources location
            self.resources = {
            "wood": np.random.randint(0, self.grid_size, size=(2,)),
            "stone": np.random.randint(0, self.grid_size, size=(2,)),
            "iron": np.random.randint(0, self.grid_size, size=(2,)),
            "diamond": np.random.randint(0, self.grid_size, size=(2,))
            }

            self.collected_resources = {"agent_1": set(), "agent_2": set()}

            # 初始化环境
            self.reset()
    
    def reset(self):
        # 重置智能体到左上角
        self.agent_positions = {
            "agent_1": np.array([0, 0]),
            "agent_2": np.array([self.grid_size - 1, self.grid_size - 1])
        }
        
        for resource in self.resources:
            while True:
                position = np.random.randint(0, self.grid_size, size=(2,))
                if not any(np.array_equal(position, pos) for pos in self.agent_positions.values()):
                    self.resources[resource] = position
                    break

        self.collected_resources = {"agent_1": set(), "agent_2": set()}

        return self.agent_positions
    
    def step(self, agent, action):
        movement = {
            0: np.array([0, 1]),
            1: np.array([0, -1]),
            2: np.array([1, 0]),
            3: np.array([-1, 0])
        }

        self.agent_positions[agent] += movement[action]
        self.agent_positions[agent] = np.clip(self.agent_positions[agent], 0, self.grid_size - 1)

        reward = 0
        done = False
        message = ""

        for resource, position in self.resources.items():
            if np.array_equal(self.agent_positions[agent], position):
                if self._can_collect(agent, resource):
                    self.collected_resources[agent].add(resource)
                    reward = 10
                    message = f"{agent} 成功收集了 {resource}!"
                else:
                    message = f"⚠️ {agent} 未满足收集 {resource} 的条件!"

        # 检查是否完成全部资源收集
        all_resources = {"wood", "stone", "iron", "diamond"}
        if all_resources.issubset(self.collected_resources[agent]):
            done = True
            message = f"🎯 {agent} 收集了所有资源，游戏胜利！"

        return self.agent_positions, reward, done, message


    def _can_collect(self, agent, resource):
        """资源依赖规则"""
        required_resources = {
            "wood": set(),
            "stone": {"wood"},
            "iron": {"wood", "stone"},
            "diamond": {"wood", "stone", "iron"}
        }

        return required_resources[resource].issubset(self.collected_resources[agent])


    def render(self, screen):
        # 清屏
        cell_size = 30
        window_size = self.grid_size * cell_size
        screen = pygame.display.set_mode((window_size, window_size))
        screen.fill((255, 255, 255))  # 黑色背景

        # 绘制网格
        
        for x in range(self.grid_size):
            for y in range(self.grid_size):
                pygame.draw.rect(screen, (200, 200, 200), 
                                 (y * cell_size, x * cell_size, cell_size, cell_size), 1)


            # 绘制资源
        for resource, pos in self.resources.items():
            screen.blit(self.assets[resource], (pos[1] * cell_size, pos[0] * cell_size))

        # 绘制智能体
        screen.blit(self.assets["agent_1"], 
                    (self.agent_positions["agent_1"][1] * cell_size, 
                    self.agent_positions["agent_1"][0] * cell_size))

        screen.blit(self.assets["agent_2"], 
                    (self.agent_positions["agent_2"][1] * cell_size, 
                    self.agent_positions["agent_2"][0] * cell_size))

        # 刷新画面
        pygame.display.flip()

    def close(self):
        pygame.quit()

# ======================= 主程序 =======================
def main():
    pygame.init()
    env = MultiAgentResourceEnv()
    screen = pygame.display.set_mode((env.grid_size * 30, env.grid_size * 30))
    pygame.display.set_caption("🌳 资源收集游戏")

    
    state = env.reset()
    done = False

    move_flag = False  # 防止连续触发

    clock = pygame.time.Clock()
    env.render(screen)

    while not done:
        # env.render(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                print("keyboard pressed down!")
                move_flag = True

            if event.type == pygame.KEYUP and move_flag:
                print("ok, let's move!")
                agent = "agent_1"  # 默认操作 agent_1
                action = None
                print(f"current pressed key is {event.key}")
                print(type(event.key))
                # 控制 agent_1
                if event.key == pygame.K_w:
                    action = 3  # 上
                elif event.key == pygame.K_s:
                    action = 2  # 下
                elif event.key == pygame.K_a:
                    action = 1  # 左
                elif event.key == pygame.K_d:
                    action = 0  # 右

                # 控制 agent_2
                elif event.key == pygame.K_UP:
                    agent = "agent_2"
                    action = 3
                elif event.key == pygame.K_DOWN:
                    agent = "agent_2"
                    action = 2
                elif event.key == pygame.K_LEFT:
                    agent = "agent_2"
                    action = 1
                elif event.key == pygame.K_RIGHT:
                    agent = "agent_2"
                    action = 0
                else:
                    print("Nothing to move!")
                    action = None


                if action is not None:
                    state, reward, done, message = env.step(agent, action)
                    move_flag = False
                    print(message)
                    env.render(screen)

                    print(f"Agent 1 is now at {env.agent_positions["agent_1"]}")
                    print(f"Agent 2 is now at {env.agent_positions["agent_2"]}")

            if event.type == pygame.KEYUP:
                move_flag = False
        clock.tick(30)

if __name__ == "__main__":
    main()
