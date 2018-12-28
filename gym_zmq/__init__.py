from gym.envs.registration import register

register(
    id='Zmq-v0',
    entry_point='gym_zmq.envs:ZmqEnv',
    # timestep_limit=1000,
    # reward_threshold=1.0,
    # nondeterministic = True,
)
