from gym.envs.registration import register

register(
    id='CustomMultiAgentEnv-v0',
    entry_point='your_module_name:CustomMultiAgentEnv'
)
