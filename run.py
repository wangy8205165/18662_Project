import gym

# 导入自定义环境 (前提是已注册)
env = gym.make('CustomMultiAgentEnv-v0')

# 重置环境
state = env.reset()
done = False

while not done:
    # 随机选择动作
    actions = {
        "agent_1": env.action_space["agent_1"].sample(),
        "agent_2": env.action_space["agent_2"].sample()
    }

    # 执行动作
    state, rewards, done, _ = env.step(actions)

    # 可视化
    env.render()

    # 打印奖励
    print(f"Rewards: {rewards}")
