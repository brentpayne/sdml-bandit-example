import random
import requests

__author__ = 'brent'


class IndexedArm(object):
    def __init__(self, index, count=0, average_reward=0.):
        self.index = index
        self.count = count
        self.average_reward = float(average_reward)

    def update(self, reward):
        self.count += 1
        self.average_reward = ((self.count - 1.) / self.count) * self.average_reward + (1. / self.count) * reward


def accumulate(values):
    """
    Given an iterable yields sum total of the list at each iteration
    :param values: an iterable whose elements can be added
    :yields: accumulated subtotals for each element
    :return: None
    """
    # TODO: replace usage with numpy.cumsum(values) after adding numpy
    accumulation = None
    for i, value in enumerate(values):
        if i == 0:
            # making no assumptions about the type of items in the list
            accumulation = value
        else:
            accumulation += value
        yield accumulation


class EpsilonGreedyBandit(object):

    def __init__(self, number_arms=0, epsilon=0.20):
        self.arms = [IndexedArm(index=i) for i in range(number_arms)]
        self.epsilon = epsilon
        if self.epsilon < 0. or self.epsilon > 1.:
            raise ValueError("self.epsilon should be a decimal between 0.0 and 1.0, received {0}".format(self.epsilon))

    def select_arm(self):
        best_arm = max(self.arms, key=lambda x: x.average_reward)
        if random.random() <= self.epsilon:
            rv = best_arm
        else:
            rv = self.arms[random.randrange(len(self.arms))]
        return rv

    def probability_distribution(self):
        """
        This function returns the probability of each arm being choosen
        :return: an array of tuples [(<probability to choose this arm>, <the arm class>), ...]
        """
        if not len(self.arms):
            return []
        best_arm = max(self.arms, key=lambda x: x.average_reward)
        exploring_an_arm_probability = (1 - self.epsilon)/len(self.arms)
        exploting_or_exploring_best_arm = self.epsilon + exploring_an_arm_probability


        return [exploring_an_arm_probability if arm != best_arm else exploting_or_exploring_best_arm for arm in self.arms]


    def cumulative_probability_distribution(self):
        """
        Returns the cumulative probability distribution for the bandit's arms
        :return: list of cumulative probabilities in the same order as this bandit's arms
        """
        return list(accumulate(self.probability_distribution()))

    @staticmethod
    def update(arm, reward):
        arm.update(reward)


if __name__ == "__main__":
    bandit = EpsilonGreedyBandit(number_arms=10, epsilon=0.20)
    while True:
        for i in xrange(10):
            arm = bandit.select_arm()
            url = 'http://bandit-server.elasticbeanstalk.com/{type}?k={arm}&u={username}'.format(type="0", arm=arm.index, username="Ruby")
            r = requests.get(url)
            reward = float(r.text)
            bandit.update(arm, reward)
        print bandit.probability_distribution()