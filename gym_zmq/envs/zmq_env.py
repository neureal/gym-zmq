import gym
import numpy as np

try:
    import zmq
except ImportError as e:
    raise gym.error.DependencyNotInstalled("{}. (HINT: you can install dependencies with 'pip install')".format(e))

context = zmq.Context(1)

class ZmqEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    # TODO make this work with multiple threaded agents
    def __init__(self):
        """
        action_space: The Space object corresponding to valid actions
        observation_space: The Space object corresponding to possible observations
        reward_range: A tuple corresponding to the min and max possible rewards
        Note: a default reward range set to [-inf,+inf] already exists. Set it if you want a narrower range.
        """

		self.REQUEST_TIMEOUT = 2500
		self.SERVER_ENDPOINT = "tcp://127.0.0.1:5558"

        # self.context = zmq.Context(1) # breaks threading, zmq.Context needs to be one instance and global
        self.poll = zmq.Poller()
        self._connect_server()

        # TODO get these from zmq-server
        self.action_space = self._action_space()
        self.observation_space = self._observation_space()

    def __del__(self):
        self._disconnect_server()

    def step(self, action):
        """
        Get current state of the environment's dynamics.

        Args:
            action (object): an action provided by the agent
        Returns:
            observation (object): agent's observation of the current environment
            reward (float) : amount of reward returned after previous action
            done (boolean): whether the environment wants to end the agent's eposode, in which case further step() calls will return undefined results
            info (dict): contains auxiliary diagnostic information (helpful for debugging, and sometimes learning)
        """
        return self._request(action)

    def reset(self):
        """
        Resets the state of the environment and returns an initial observation.
        When the agent wants to end it's episode, they are responsible for calling this.

        Returns: observation (object): the initial observation of the episode
        """
        return self._request(None)[0]

    def render(self, mode='human', close=False):
        """ These are live environments, so the agent doesn't get to control their rendering """
        return
        # if close:
        # else:

    # def close(self):
    #     """Override close in your subclass to perform any necessary cleanup."""
    #     self._disconnect_server()

    # def seed(self, seed):
    #     random.seed(seed)
    #     np.random.seed


    def _action_space(self):
        return spaces.Discrete(18)
        # low = [0.0, 0.0, 0.0]
        # high = [1.0, 1.0, 1.0]
        # return spaces.Box(np.array(low), np.array(high), dtype=np.float32)
        # return spaces.Box(low=0.0, high=1.0, shape=(3,), dtype=np.float32)

    def _observation_space(self):
        # low = [-1.0, -1.0, -1.0, -1.0]
        # high = [1.0, 1.0, 1.0, 1.0]
        # return spaces.Box(np.array(low), np.array(high), dtype=np.float32)
        return spaces.Box(low=0, high=255, shape=(4,4,3), dtype=np.uint8)

    def _connect_server(self):
        print("zmq_env: Connecting to server...")
        self.client = context.socket(zmq.REQ)
        self.client.connect(self.SERVER_ENDPOINT)
        self.poll.register(self.client, zmq.POLLIN)

    def _disconnect_server(self):
        print("zmq_env: Disconnecting from server...")
        self.client.setsockopt(zmq.LINGER, 0)
        self.client.close()
        self.poll.unregister(self.client)


    def _request(self, action):
        observation = np.zeros(shape=self.observation_space.shape, dtype=self.observation_space.dtype)
        reward = np.float32(0.0)
        done = True
        info = {}
        
        # print("zmq_env: action {}".format(action))
        request = "reset"
        if (action is not None):
            action = np.asarray(action)
            if (action.ndim == 0):
                request = action
            elif (action.ndim == 1):
                request = " ".join(map(str, action))
        request = str(request).encode()
        # print("zmq_env: Sending {}".format(request))

        self.client.send(request)

        socks = dict(self.poll.poll(self.REQUEST_TIMEOUT))
        # print("zmq_env: connected??? {}".format(socks.get(self.client)))
        if socks.get(self.client) == zmq.POLLIN:
            reply = self.client.recv()
            if reply:
                # print("zmq_env: Server replied {}".format(reply))
                reply_list = reply.split()
                done = (np.float32(reply_list[0]) == 1)
                reward = np.float32(reply_list[1])

                observation = np.fromiter(map(np.uint8,reply_list[2:]), np.uint8)
                observation.resize(self.observation_space.shape)
                # info = {}
        else:
            print("zmq_env: No response from server")
            # Socket is confused. Close and remove it.
            self._disconnect_server()
            self._connect_server()

        return observation, reward, done, info