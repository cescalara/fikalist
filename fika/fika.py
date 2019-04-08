"""
Automatic fika list generator.

@author Francesca Capel 
@email capel.francesca@gmail.com
@date April 2018
"""

import numpy as np
import pandas as pd
from datetime import date, timedelta
import holidays

__all__ = ['FikaProviders', 'FikaList']

# keywords used
KW_HOLIDAY = 'HOLIDAY'
KW_NAN = 'nan'


class FikaProviders():
    """
    A container to store the generous fika providers of PAP.
    """


    def __init__(self, name_list, couple_list):
        """
        A container to store the generous fika providers of PAP.
        
        @TODO: tidy up add and remove methods for better code
               coverage

        :param name_list: a list of first names of people in the group.
        """

        self.names = name_list
        self.oldcouples = couple_list
        self.couples = []
        
    def show(self):
        """
        Print the info.
        """

        for name in self.names:
            print(name)


    def add(self, name):
        """
        Add a new name to the list.

        Names are added to the beginning of the chronological 
        list as new people have never made fika before. 
        
        :param name: The name to be added, can be a string or 
                     a list
        """

        # is name a string or list?
        if isinstance(name, str):
            self.names.insert(0, name)
            print ('Welcome,', name + '!')
        else:
            for n in name:
                self.names.insert(0, n)
                print ('Welcome,', n + '!')

                
    def remove(self, name):
        """
        Remove a name from the list.
        """

        # is name a string or list?
        if isinstance(name, str):
            try:
                self.names.remove(name)
            except ValueError:
                print (name, 'is not in the list of providers...')
            else:
                print ('Farewell,', name + '!')

            # check if they were in a couple
            # if yes, replace with 'nan' keyword
            for c in self.oldcouples:
                if name in c:
                    c[c.index(name)] = KW_NAN
        else:
            for n in name:
                try:
                    self.names.remove(n)
                except ValueError:
                    print (n, 'is not in the list of providers...')
                else:
                    print ('Farewell,', n + '!')
                    
                    # check if they were in a couple
                    # if yes, replace with 'nan' keyword
                    for c in self.oldcouples:
                        if n in c:
                            c[c.index(n)] = KW_NAN


class FikaConstraints():
    """
    Handles contraints on the fika schedule.
    """

    def __init__(self):
        """
        Handles contraints on the fika schedule.
        """

        # allowed constraints
        self._possible_constraints = ['leaving soon', 'together', 'holiday', 'just arrived']

        self.leaving_soon = []
        self.just_arrived = []
        self.together = []
        #self.fikaholidays = self._define_holidays()
        self.fikafridays = []

        
    def add(self, name, constraint):
        """
        Add a new constraint.

        :param name: name(s) of people affected
        :param constraint: the constraint, must be from 
                           the defined possible options listed in
                           self._possible_constraints
        """

        if constraint not in self._possible_constraints:
            print ('ERROR:', constraint, 'is not a defined constraint')

        if constraint == self._possible_constraints[0]:
            # is name a string or list?
            if isinstance(name, str):
                self.leaving_soon.append(name)
            else:
                for n in name:
                    self.leaving_soon.append(n)

        if constraint == self._possible_constraints[3]:
            # is name a string or list?
            if isinstance(name, str):
                self.just_arrived.append(name)
            else:
                for n in name:
                    self.just_arrived.append(n)
                    
        if constraint == self._possible_constraints[1]:
            # require a couple  
            if len(name) != 2:
                print ('ERROR:','first argument to add() must be a couple if constraint is `together`')
            else:
                self.together.append(name)
                

    def _get_fridays(self, N, start_date = None):
        """
        Get a list of the Fika Fridays.

        If a start date is not supplied, the current date
        is assumed

        Holidays are also defined here for now, due to a bug in
        the holidays package.

        :param N: the number of Fridays that you need
        :param start_date: the starting date
        """

        if not start_date:
            # get current date
            start_date = date.today()
        
        self.fikaholidays = holidays.Sweden()

        # DEFINE HOLIDAYS
        month = start_date.month
        if month <= 9:
            summer_year = start_date.year
            winter_year = start_date.year
        else:
            summer_year = start_date.year + 1
            winter_year = start_date.year
            
        # add summer for the coming midsummer and August
        day = date(summer_year, 6, 20)
        while day.month < 9:
            if day not in holidays.Sweden():
                self.fikaholidays.append(day)
            day = day + timedelta(days = 1)
            
        # add winter for the coming Christmas period
        day = date(winter_year, 12, 20)
        weeks_off = 3
        end_day = day + timedelta(weeks = 3)
        while day < end_day:
            if day not in holidays.Sweden():
                self.fikaholidays.append(day)
            day = day + timedelta(days = 1)
        
        # GET FRIDAYS
        # index of week
        friday_index = 4

        # Find the next Friday after the start date
        while start_date.weekday() != friday_index:
            start_date = start_date + timedelta(days = 1)

            
        friday = start_date
        while len(self.fikafridays) < N:
            # check for holidays (also on the thursday before)
            thursday = friday - timedelta(days = 1)
            if (friday not in self.fikaholidays
                and thursday not in self.fikaholidays):
            #if friday not in holidays.Sweden() and thursday not in holidays.Sweden():
                self.fikafridays.append(friday)

            # go to the next week
            friday = friday + timedelta(days = 7)


            
class FikaList():
    """
    Fikalist wrapper class and generator. 
    """

    def __init__(self):
        """
        Fikalist wrapper class and generator.
        """

        # names of columns in the fikalist .txt file
        self._file_layout = ['Week', 'Friday', 'Person 1', 'Person 2']
        self.constraints = FikaConstraints()
        self.providers = None
    
        
    def input_list(self, filename):
        """
        Input the old fikalist in .txt format.

        :param filename: the name of the fikalist file.
        """

        self._input_filename = filename
        
        self._parsed_output = pd.read_csv(self._input_filename, comment = '#',
                             delim_whitespace = True,
                             names = self._file_layout)
        
        name_list = []
        couple_list = []
        for index, row in self._parsed_output.iterrows():

            # convert to string to handle nan checks smoothly
            person1 = str(row['Person 1'])
            person2 = str(row['Person 2'])
    
            # check for parsing keywords
            if (KW_HOLIDAY not in person1) and (KW_NAN not in person1):
                name_list.append(person1)
            if (KW_HOLIDAY not in person2) and (KW_NAN not in person2):    
                name_list.append(person2)

            # store the couples, where one can be nan
            if (KW_HOLIDAY not in person1) and (KW_HOLIDAY not in person2):
                fika_couple = [person1, person2]
                couple_list.append(fika_couple)
            
        self.providers = FikaProviders(name_list, couple_list)
        

    def _apply_constraints(self):
        """
        Apply the constraints.
        """

        # Bump up people leaving soon to the top of the list
        # This makes it more likely for them to get picked
        for name in self.constraints.leaving_soon:
            self.providers.names.remove(name)
            self.providers.names.insert(0, name)

        # Bump up people that have just arrived to the top of the list
        # This makes it more likely for them to get picked
        # Separate out from leaving soon in case you want some separate behaviour
        for name in self.constraints.just_arrived:
            self.providers.names.remove(name)
            self.providers.names.insert(0, name)    
        
        # remove exjobbare from list, if they are there
        #exjobb = 'Exjobbare'
        #if exjobb in self.providers.names:
        #    self.providers.names.remove(exjobb)

            
    def generate(self, start_date = None):
        """
        Generate a new fikalist.
        
        The order is determined by random sampling without replacement, 
        with people who made fika a long time ago weighted preferentially. 
        Also, people are put in a couple with someone who they have not 
        been with before. 
        """

        # apply any constraints
        self._apply_constraints()

        # get couples
        self._get_random_couples()
        couples = self.providers.couples
        person1 = np.asarray([c[0] for c in couples])
        person2 = np.asarray([c[1] for c in couples])
        
        # get fridays and convert to string dates
        N = len(self.providers.couples)
        self.constraints._get_fridays(N, start_date)
        fridays = self.constraints.fikafridays
        fridays_string = np.asarray([d.strftime("%d/%m/%Y") for d in fridays])
        
        # get week number
        week_num = np.asarray([d.isocalendar()[1] for d in fridays])

        # make a dataframe
        data_array = np.transpose([week_num, fridays_string, person1, person2])
        self.fikalist = pd.DataFrame(data_array, columns = self._file_layout)
        

    def save(self, filename):
        """
        Save the fikalist in .txt format.

        :param filename: the name of the file to save to.
        """

        with open(filename, 'w') as f:
            text = self.fikalist.to_string(index = False)
            f.write(text)

            
    def show(self):
        """
        Display the fikalist dataframe.
        """
        
        display(self.fikalist)
            
            
    def _get_random_couples(self):
        """
        Select couples from a weighted probability distribution,
        under the given constraints.
        
        @TODO: add treatment of Exjobbare as alone or paired based 
               on group number being even/odd.
        """

        # initialise a list of names
        names = self.providers.names
        
        # deal with odd number of names
        N = len(names)
        # check odd, as exjobb is special case
        if N % 2 != 0:
            names.append(KW_NAN)
        
        while names != []:

            # the fikalist is in chronological order
            # convert this into a probability between 0 and 1
            N = len(names)
            
            # from 1 to N + 1 to avoid zero probability
            weights = np.flipud(range(1, N + 1))/N

            # normalise
            probabilities = (weights/sum(weights)).tolist()

            # make 2 random draws from the name list
            draws = np.random.choice(names, 2, p = probabilities, replace = False)
            
            # check if they are part of a set pair
            together = False
            for c in self.constraints.together:
                for draw in draws:
                    if draw in c:
                        # pair them with who they live with instead
                        i_draw = next((i for i, x in enumerate(draws) if x != draw), None)
                        i_c = next((i for i, x in enumerate(c) if x != draw), None)
                        draws[i_draw] = c[i_c]
                        together = True
                        
            # check if they have been a couple
            # if yes, discard this draw
            # ignore if together!
            old_couple = False
            if not together:
                for c in self.providers.oldcouples:
                    if (draws[0] in c and draws[1] in c):
                        old_couple = True
                

            # avoid old couples unless it is the last option
            if not old_couple or N == 2:
                # remove from the names list
                for draw in draws:
                    del probabilities[names.index(draw)]
                    names.remove(draw)

                # append to new list
                self.providers.couples.append(draws)

        # add exjobbare's on the end, as they are always alone
        # Remove this for now as odd number of people - should automate
        #self.providers.couples.append(['Exjobbare', KW_NAN])



        
            
            
        
