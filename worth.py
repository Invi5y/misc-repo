import datetime as dt
import numpy as np

class Person(object):
    def __init__(self, name):
        self.name = name
        self.today = dt.date.today()
    def last_day(self, y, m, d):
        #should return an array with date of expected death and number of days to live
        #based on date of birth
        #need a function to read birth dates >> string to dt object
        self.date_of_birth = dt.date(y,m,d)
        self.last_day = np.random.normal(73,10)
