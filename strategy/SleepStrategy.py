import time
from BaseStrategy import BaseStrategy

class SleepStrategy(BaseStrategy):
    def calculate(self, disk):
        time.sleep(301) # sleep 5 min + 1 sec to force timeout
        return disk
    
