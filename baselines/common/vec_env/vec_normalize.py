from baselines.common.vec_env import VecEnvWrapper
from baselines.common.running_mean_std import RunningMeanStd
import numpy as np
from gym.spaces import Dict
from os.path import join as p_join
import pickle


class VecNormalize(VecEnvWrapper):
    """
    Vectorized environment base class
    """
    def __init__(self, venv, ob=True, ret=True, clipob=10., cliprew=10., gamma=0.99, epsilon=1e-8):
        VecEnvWrapper.__init__(self, venv)
        self.ob_rms = RunningMeanStd(shape=self.observation_space.shape) if ob else None
        self.ret_rms = RunningMeanStd(shape=()) if ret else None
        self.clipob = clipob
        self.cliprew = cliprew
        self.ret = np.zeros(self.num_envs)
        self.gamma = gamma
        self.epsilon = epsilon

    def save_norm(self, path):
        with open(path + '_vecnorm', 'wb') as f:
            pickle.dump([self.ob_rms, self.ret_rms, self.clipob, self.cliprew, self.ret, self.gamma,
                         self.epsilon], f)

    def load_norm(self, path):
        with open(path + '_vecnorm', 'rb') as f:
            self.ob_rms, self.ret_rms, self.clipob, self.cliprew, self.ret, self.gamma, \
            self.epsilon = pickle.load(f)

    def step_wait(self):
        """
        Apply sequence of actions to sequence of environments
        actions -> (observations, rewards, news)

        where 'news' is a boolean vector indicating whether each element is new.
        """
        obs, rews, news, infos = self.venv.step_wait()
        self.ret = self.ret * self.gamma + rews
        obs = self._obfilt(obs)
        if self.ret_rms:
            self.ret_rms.update(self.ret)
            rews = np.clip(rews / np.sqrt(self.ret_rms.var + self.epsilon), -self.cliprew, self.cliprew)
        return obs, rews, news, infos

    def _obfilt(self, obs):
        if self.ob_rms:
            self.ob_rms.update(obs)
            obs = np.clip((obs - self.ob_rms.mean) / np.sqrt(self.ob_rms.var + self.epsilon), -self.clipob, self.clipob)
            return obs
        else:
            return obs

    def reset(self):
        """
        Reset all environments
        """
        obs = self.venv.reset()
        return self._obfilt(obs)

class ImVecNormalize(VecEnvWrapper):
    """
    Vectorized environment base class
    """
    def __init__(self, venv, ob=True, ret=True, clipob=10., cliprew=10., gamma=0.99, epsilon=1e-8):
        VecEnvWrapper.__init__(self, venv)
        if isinstance(self.observation_space, Dict):
            self.ob_robot_rms = RunningMeanStd(
                shape=self.observation_space.spaces["robot_state"].shape) if ob else None
            self.ob_task_rms = RunningMeanStd(
                shape=self.observation_space.spaces["task_state"].shape) if ob else None
        else:
            self.ob_rms = RunningMeanStd(
                shape=self.observation_space.shape) if ob else None
        self.ret_rms = RunningMeanStd(shape=()) if ret else None
        self.clipob = clipob
        self.cliprew = cliprew
        self.ret = np.zeros(self.num_envs)
        self.gamma = gamma
        self.epsilon = epsilon

    def save_norm(self, path):
        with open(path + '_vecnorm', 'wb') as f:
            pickle.dump([self.ob_robot_rms,self.ob_task_rms, self.ret_rms, self.clipob, self.cliprew, self.ret, self.gamma,
                         self.epsilon], f)

    def load_norm(self, path):
        with open(path + '_vecnorm', 'rb') as f:
            self.ob_robot_rms, ob_task_rms, self.ret_rms, self.clipob, self.cliprew, self.ret, self.gamma, \
                self.epsilon = pickle.load(f)

    def step_wait(self):
        """
        Apply sequence of actions to sequence of environments
        actions -> (observations, rewards, news)

        where 'news' is a boolean vector indicating whether each element is new.
        """
        obs, rews, news, infos = self.venv.step_wait()
        self.ret = self.ret * self.gamma + rews
        obs = self._obfilt(obs)
        if self.ret_rms:
            self.ret_rms.update(self.ret)
            rews = np.clip(rews / np.sqrt(self.ret_rms.var + self.epsilon), -self.cliprew, self.cliprew)
        return obs, rews, news, infos

    def _obfilt(self, obs):
        if isinstance(obs, dict):
            if self.ob_robot_rms:
                self.ob_robot_rms.update(obs['robot_state'])
                obs['robot_state'] = np.clip((obs['robot_state'] - self.ob_robot_rms.mean) / np.sqrt(self.ob_robot_rms.var + self.epsilon), -self.clipob,
                              self.clipob)
                self.ob_task_rms.update(obs['task_state'])
                obs['task_state'] = np.clip(
                    (obs['task_state'] - self.ob_task_rms.mean) / np.sqrt(self.ob_task_rms.var + self.epsilon),
                    -self.clipob,
                    self.clipob)
                return obs
        else:
            if self.ob_rms:
                self.ob_rms.update(obs)
                obs = np.clip((obs - self.ob_rms.mean) / np.sqrt(self.ob_rms.var + self.epsilon), -self.clipob, self.clipob)
                return obs
            else:
                return obs

    def reset(self):
        """
        Reset all environments
        """
        obs = self.venv.reset()
        obs = self._obfilt(obs)
        return obs

