from setuptools import setup

setup(name='gym_zmq',
      version='0.0.1',
      install_requires=['gym>=0.10.9',
                        'pyzmq>=17.1.2'] # libzmq5 v4.1.4
)
