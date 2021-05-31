import math

#Credit for Singleton structure: Paul Manta https://stackoverflow.com/questions/31875/is-there-a-simple-elegant-way-to-define-singletons
class EdgeSingleton:

    _instance_dict = dict()
    
    def __init__(self, decorated):
        self._decorated = decorated

    def instance(self, x, y):
        """
        Returns the singleton instance. Upon its first call, it creates a
        new instance of the decorated class and calls its `__init__` method.
        On all subsequent calls, the already created instance is returned.
        """
        try:
            return self._instance_dict[f"{str(x)},{str(y)}"]
        except Exception:
            try:
                return self._instance_dict[f"{str(y)},{str(x)}"]
            except Exception:
                self._instance_dict[f"{str(x)},{str(y)}"] = self._decorated(x, y)
                return self._instance_dict[f"{str(x)},{str(y)}"]

    def __call__(self, x, y):
        raise TypeError('Singletons must be accessed through `instance()`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self._decorated)

@EdgeSingleton
class Edge:
    def __init__(self, point1, point2):
        self._point1, self._point2 = point2, point2
        self._score = None
    
    def __str__(self):
        return "{} <-> {}".format(self._point1, self._point2)

    def add_score(self, scoreToAdd):
        if self._score is None:
            self._score = scoreToAdd
        #two playgrounds next to each other --> edge value is infinity
        elif self._score == 3 and scoreToAdd == 3:
            self._score = math.inf
        else:
            self._score = (self._score + scoreToAdd)/2

    def get_score(self):
        return self._score