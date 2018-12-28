**Status:** Prealpha (code is provided as-is, only tested on Ubuntu 16.04)

# gym-zmq
OpenAI Gym environment adapter using ZeroMQ

Supports messaging connections to live environments

# Installation

Install the [OpenAI gym](https://gym.openai.com/docs/).

Then install this package via

```bash
git clone https://github.com/wilbown/gym-zmq.git
cd gym-zmq
pip install -e .
```

# Usage

```
import gym
import gym_zmq

env = gym.make('Zmq-v0')
```