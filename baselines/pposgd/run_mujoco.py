#!/usr/bin/env python
from baselines.common import set_global_seeds, tf_util as U
from baselines import bench
import os.path as osp
import gym, logging
from baselines import logger
import sys
import datetime

def train(env_id, num_timesteps, seed):
    from baselines.pposgd import mlp_policy, pposgd_simple
    U.make_session(num_cpu=1).__enter__()
    set_global_seeds(seed)
    env = gym.make(env_id)
    def policy_fn(name, ob_space, ac_space):
        return mlp_policy.MlpPolicy(name=name, ob_space=ob_space, ac_space=ac_space,
            hid_size=64, num_hid_layers=2)
    logger.configure(dir = osp.join("/home/hermannl/master_project/git/baselines/baselines/pposgd/logs/",
        datetime.datetime.now().strftime("openai-%Y-%m-%d-%H-%M-%S-%f")))
    if logger.get_dir():
        env = bench.Monitor(env, osp.join(logger.get_dir(), "monitor.json"))
    env.seed(seed)
    gym.logger.setLevel(logging.WARN)
    pposgd_simple.learn(env, policy_fn,
            max_timesteps=num_timesteps,
            timesteps_per_batch=2048,
            clip_param=0.2, entcoeff=0.0,
            optim_epochs=10, optim_stepsize=3e-4, optim_batchsize=64,
            gamma=0.99, lam=0.95,
        )
    env.close()

def main():
    train('Jaco-v1', num_timesteps=1e8, seed=0)


if __name__ == '__main__':
    main()
