#!/usr/bin/env python3
import argparse
from baselines.common.cmd_util import mujoco_arg_parser
from baselines import bench, logger
import datetime
import os.path as osp
import os


def train(env_id, num_timesteps, seed):
    from baselines.common import set_global_seeds
    from baselines.common.vec_env.vec_normalize import VecNormalize, ImVecNormalize
    from baselines.ppo2 import ppo2
    from baselines.ppo2.policies import AsyncCombiPolicy, CombiPolicy
    import gym
    import tensorflow as tf
    from baselines.common.vec_env.dummy_vec_env import DummyVecEnv
    from gym_grasping.envs.grasping_env import GraspingEnv
    ncpu = 1
    config = tf.ConfigProto(allow_soft_placement=True,
                            intra_op_parallelism_threads=ncpu,
                            inter_op_parallelism_threads=ncpu)
    config.gpu_options.allow_growth = True  # pylint: disable=E1101
    tf.Session(config=config).__enter__()

    def make_env():
        env = gym.make(env_id)
        env = bench.Monitor(env, logger.get_dir())
        return env

    env = DummyVecEnv([make_env])
    env = ImVecNormalize(env)

    set_global_seeds(seed)
    policy = CombiPolicy
    ppo2.learn(policy=policy, env=env, nsteps=2048, nminibatches=32,
               lam=0.95, gamma=0.99, noptepochs=4, log_interval=1,
               ent_coef=0.0,
               lr=1e-4,  # changed
               cliprange=0.2,
               total_timesteps=num_timesteps,
               save_interval=100)
    # try: noptepochs 2 /4
    #
    #
    #
    #


def main():
    os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"  # see issue #152
    os.environ["CUDA_VISIBLE_DEVICES"] = "1"
    logger.configure(dir=osp.join("/home/kuka/lang/baselines/baselines/ppo2/logs/combi/",
                                  datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")),
                     format_strs=["tensorboard", "stdout", "csv", "log"])
    train(env_id='kuka_block_cont_combi-v0', num_timesteps=10e7, seed=1)


if __name__ == '__main__':
    main()
