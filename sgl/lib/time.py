import math

class Interval():
    def __init__(self, interval, function, start_time=0):
        self.interval = interval
        self.function = function
        self.last_time_called = start_time
        self.stopped = False

    def stop(self):
        self.stopped = True

class TimeManager():
    def __init__(self):
        self.time = 0
        self.functions = {}
        self.intervals = []

    def add_function(self, delay, function):
        self.functions[self.time + delay] = function

    def add_interval(self, interval, function):
        self.intervals.append(Interval(interval, function, self.time))
        return self.intervals[-1]

    def update(self, dt):
        self.time += dt

        # handle delayed functions
        times = [time for time in self.functions if time <= self.time]
        for time in times:
            self.functions[time]()
            del self.functions[time]

        # handle interval functions
        for number, interval in enumerate(self.intervals):
            distance = self.time - interval.last_time_called
            amount = int(distance / float(interval.interval))

            if amount > 0:
                for i in range(amount):
                    interval.function()
                interval.last_time_called = self.time
               
            if interval.stopped:
                del self.intervals[number]

manager = TimeManager()

def set_timeout(delay, function):
    manager.add_function(delay, function)

def set_interval(interval, function):
    return manager.add_interval(interval, function)

def at_fps(fps, function):
    return manager.add_interval(1./fps, function)

def update(dt):
    manager.update(dt)






