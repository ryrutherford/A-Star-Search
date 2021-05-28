import math

class PointSingleton:

    _instance_dict = dict()
    
    def __init__(self, decorated):
        self._decorated = decorated

    def instance(self, x, y):
        try:
            return self._instance_dict[f"{str(x)},{str(y)}"]
        except Exception:
            self._instance_dict[f"{str(x)},{str(y)}"] = self._decorated(x, y)
            return self._instance_dict[f"{str(x)},{str(y)}"]

    def __call__(self, x, y):
        raise TypeError('Singletons must be accessed through `instance()`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self._decorated)

@PointSingleton
class Point:
    def __init__(self, x, y):
        self._x, self._y = x, y
        self._f_score = math.inf
        self._g_score = math.inf

    def __str__(self):
        return "({}, {})".format(self._x, self._y)

    def __lt__(self, other):
        return self._f_score < other._f_score

    def get_x(self):
        return self._x
    
    def get_y(self):
        return self._y
    
    def get_f_score(self):
        return self._f_score
    
    def get_g_score(self):
        return self._g_score
    
    def set_f_score(self, new_score):
        self._f_score = new_score
    
    def set_g_score(self, new_score):
        self._g_score = new_score