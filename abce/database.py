# Copyright 2012 Davoud Taghawi-Nejad
#
# Module Author: Davoud Taghawi-Nejad
#
# ABCE is open-source software. If you are using ABCE for your research you are
# requested the quote the use of this software.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License and quotation of the
# author. You may obtain a copy of the License at
#       http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
"""
The :class:`abceagent.Agent` class is the basic class for creating your agent.
It automatically handles the possession of goods of an agent. In order to
produce/transforme goods you need to also subclass
the :class:`abceagent.Firm` [1]_ or to create a consumer the
:class:`abceagent.Household`.

For detailed documentation on:

Trading:
    see :class:`abceagent.Trade`

Logging and data creation:
    see :class:`abceagent.Database` and :doc:`simulation_results`

Messaging between agents:
    see :class:`abceagent.Messaging`.

.. autoexception:: abce.NotEnoughGoods

.. [1] or :class:`abceagent.FirmMultiTechnologies` for simulations with
complex technologies.
"""
from collections import OrderedDict

class Database(object):
    """ The database class """

    def log(self, action_name, data_to_log):
        """ With log you can write the models data. Log can save variable
        states and and the working of individual functions such as production,
        consumption, give, but not trade(as its handled automatically).

        Args:
            'name'(string):
                the name of the current action/method the agent executes

            data_to_log:
                a variable or a dictionary with data to log in the the
                database

        Example::

            self.log('profit', profit)

            self.log('employment_and_rent',
                     {'employment': self.possession('LAB'),
                      'rent': self.possession('CAP'),
                      'composite': self.composite})

            self.log('production', self.produce_use_everything())

        See also:
            :meth:`~abecagent.Database.log_change`:
                loges the change from last round

            :meth:`~abecagent.Database.observe_begin`:

        """
        try:
            data_to_write = {'%s_%s' % (str(action_name), str(
                key)): data_to_log[key] for key in data_to_log}
        except TypeError:
            data_to_write = {str(action_name): data_to_log}
        self.database_connection.put(["snapshot_panel",
                                      str(self.round),
                                      self.group,
                                      self.id,
                                      data_to_write])

    def _common_log(self, variables, possessions, functions, lengths):
        ret = OrderedDict()
        for var in variables:
            ret[var] = self.__dict__[var]
        for pos in possessions:
            ret[pos] = self._haves[pos]
        for name, func in functions.items():
            ret[name] = func(self)
        for length in lengths:
            ret['len_' + length] = len(self.__dict__[length])
        return ret


    def _agg_log(self, variables, possessions, functions, lengths):
        data_to_write = self._common_log(variables, possessions, functions, lengths)
        self.database_connection.put(["snapshot_agg",
                                      str(self.round),
                                      self.group,
                                      data_to_write])


    def _panel_log(self, variables, possessions, functions, lengths):
        data_to_write = self._common_log(variables, possessions, functions, lengths)
        self.database_connection.put(["snapshot_panel",
                                      str(self.round),
                                      self.group,
                                      self.id,
                                      data_to_write])

