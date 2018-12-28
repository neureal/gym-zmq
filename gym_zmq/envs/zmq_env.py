import gym
from gym import error, spaces, utils
from gym.utils import seeding
import numpy as np

try:
    import zmq
except ImportError as e:
    raise error.DependencyNotInstalled("{}. (HINT: you can install dependencies with 'pip install')".format(e))

REQUEST_TIMEOUT = 2500
SERVER_ENDPOINT = "tcp://localhost:5558"

class ZmqEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):
        """
        action_space: The Space object corresponding to valid actions
        observation_space: The Space object corresponding to possible observations
        reward_range: A tuple corresponding to the min and max possible rewards
        Note: a default reward range set to [-inf,+inf] already exists. Set it if you want a narrower range.
        """
        self.context = zmq.Context(1)
        self.poll = zmq.Poller()
        self._connect_server()

        self.action_space = self._action_space()
        self.observation_space = self._observation_space()

    def __del__(self):
        self.context.term()

    def step(self, action):
        """
        Get current state of the environment's dynamics.

        Args:
            action (object): an action provided by the agent
            
        Returns:
            observation (object): agent's observation of the current environment
            reward (float) : amount of reward returned after previous action
            TODO set this when zmq-server disconnects, or if done recieved from zmq-server
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
        return self._request("reset")[0]

    def render(self, mode='human', close=False):
        """ These are live environments, so the agent doesn't get to control their rendering """
        return
        # if close:
        # else:

    # def close(self):
    #     """Override close in your subclass to perform any necessary cleanup."""

    # def seed(self, seed):
    #     random.seed(seed)
    #     np.random.seed


    def _action_space(self):
        # TODO get this from zmq-server
        # return spaces.Discrete(21)
        # low = [-1.0, -1.0, -1.0]
        # high = [1.0, 1.0, 1.0]
        # return spaces.Box(np.array(low), np.array(high), dtype=np.float32)
        return spaces.Box(low=-1.0, high=1.0, shape=(3,), dtype=np.float32)

    def _observation_space(self):
        # TODO get this from zmq-server
        # hit points, cooldown, ground range, is enemy, degree, distance (myself)
        # hit points, cooldown, ground range, is enemy (enemy)
        low = [0.0, 0.0, 0.0, 0.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        high = [100.0, 100.0, 1.0, 1.0, 1.0, 50.0, 100.0, 100.0, 1.0, 1.0]
        return spaces.Box(np.array(low), np.array(high), dtype=np.float32)

    def _connect_server(self):
        print("I: Connecting to server...")
        self.client = self.context.socket(zmq.REQ)
        self.client.connect(SERVER_ENDPOINT)
        self.poll.register(self.client, zmq.POLLIN)


    def _request(self, action):
        observation = np.zeros(self.observation_space.shape)
        reward = 0.0
        done = True
        info = {}

        socks = dict(self.poll.poll(REQUEST_TIMEOUT))
        print("I: Client??? (%s)" % socks.get(self.client))
        
        request = str(action).encode()
        print("I: Sending (%s)" % request)
        self.client.send(request)

        socks = dict(self.poll.poll(REQUEST_TIMEOUT))
        if socks.get(self.client) == zmq.POLLIN:
            reply = self.client.recv()
            if reply:
                print("I: Server replied OK (%s)" % reply)
                observation[0] = 0.25
                reward = 0.1
                done = False
        else:
            print("W: No response from server")
            # Socket is confused. Close and remove it.
            # self.client.setsockopt(zmq.LINGER, 0)
            # self.client.close()
            # self.poll.unregister(self.client)

        return observation, reward, done, info