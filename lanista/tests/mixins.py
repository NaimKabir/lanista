
# Testing trait mixing with a spawn method.

class A():

    def doA(self):

        print("A")

class N():

    @classmethod
    def spawn(cls):
        print(cls)
        self = cls()
        cls.test_attribute = []

        return self

class Mix(A, N):

    @classmethod
    def create(cls):
        self = cls.spawn()
        self.m = []

        return self


m = Mix.create()
m.doA()
m.test_attribute
m.m

