import platform
import abce
import filecmp as fc
import difflib as dl
import pandas as pd
import numpy as np


class Agent(abce.Agent):
    def go(self):
        self.create('money', 0.1)
        self.i = self.id
        self.r = self.round
        self.log('li', self.i)
        self.log('lr', self.r)
        self.log('l', {'i': self.i, 'r': self.r})


def compare(to_compare, path, message):
    should_be_full = pd.read_csv(to_compare).sort_index(axis=1)
    the_path = (path + '/' + to_compare)
    if platform.system() == 'Windows':  # windows compatibility
        the_path = the_path[the_path.find('/') + 1:]
    really_is_full = pd.read_csv(the_path).sort_index(axis=1)
    if 'id' in should_be_full.columns:
        should_be_full = (should_be_full
                          .sort_values(by=['id', 'round'], axis=0)
                          .reset_index(drop=True))
        really_is_full = (really_is_full
                          .sort_values(by=['id', 'round'], axis=0)
                          .reset_index(drop=True))
        del should_be_full['index']
        del really_is_full['index']
    assert(should_be_full.shape == really_is_full.shape)
    if not np.isclose(should_be_full, really_is_full).all():
        # finds all lines which are different
        should_be = should_be_full[np.logical_not(
                                   np.min(np.isclose(should_be_full,
                                                     really_is_full),
                                          axis=1))]
        really_is = really_is_full[np.logical_not(
                                   np.min(np.isclose(should_be_full,
                                                     really_is_full),
                                          axis=1))]

        print(to_compare)
        raise Exception(pd.concat([should_be, really_is], axis=1))
    else:
        print(to_compare + ' ' + message + '\tOK')


def main(processes):
    simulation = abce.Simulation(processes=processes)


    agents = simulation.build_agents(Agent, 'agent', 10, parameters='')

    for r in range(100):
        simulation.advance_round(r)
        agents.go()
        agents.agg_log(variables=['i', 'r'], possessions=['money'])
        agents.panel_log(variables=['i', 'r'], possessions=['money'])
    simulation.finalize()

    if platform.system() == 'Windows':
        simulation.path = simulation.path.replace('/', '\\')

    compare('aggregate_agent.csv',
            simulation.path, 'aggregate logging test\t\t')
    compare('agent.csv',
            simulation.path, 'aggregate logging test mean\t')


if __name__ == '__main__':
    main(processes=1)
    main(processes=4)
