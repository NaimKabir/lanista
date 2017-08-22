class HandlerRegistry(dict):
    def __call__(self, typ):
        def register(func):
            self[typ] = func
            return func

        return register

class moop(object):

    meep = 33

    def __repr__(self):
        return str(self.__class__.meep)

    handles = HandlerRegistry()

    @handles(str)
    def onString(self, input):
        print "meep"