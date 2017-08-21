from lanista.threadactors import start_thread, HandlerRegistry
from Queue import Queue
# import visdom
#
# vis = visdom.Visdom()

# Testing message passing loop between different actors

class BasicActor():

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "Basic Actor"

    @classmethod
    def spawn(cls, *args, **kwargs):
        print cls
        self = cls(*args, **kwargs)
        self.inbox = Queue()
        start_thread(function = self.live, name = self.name)
        return self

    handles = HandlerRegistry()

    def live(self):

        while True:
            if not self.inbox.empty():
                message, sender = self.inbox.get()
                print message
                sender.inbox.put((self.name, self))

meep = BasicActor.spawn(name = "meep")
moop = BasicActor.spawn(name = "moop")

#Kicking off the eternal cycle
meep.inbox.put((moop.name, moop))






