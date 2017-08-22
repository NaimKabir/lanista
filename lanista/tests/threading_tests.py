from lanista.threadactors import start_thread, PoisonPill
# from Queue import Queue
from Queue import Queue

# Testing message passing loop between different actors

class BasicActor():

    @classmethod
    def spawn(cls, *args, **kwargs):
        self = cls(*args, **kwargs)
        self.inbox = Queue()
        start_thread(function = self.live, name = self.name)
        print("leep")
        return self

    def __init__(self, name):
        self.name = name

    def live(self):
        try:
            while True:
                if not self.inbox.empty():
                    message, sender = self.inbox.get()
                    print(message)
                    if type(message) == type(PoisonPill()):
                        raise message
                    sender.inbox.put((self.name, self))
        except PoisonPill:
            print("Dying.")
            pass

meep = BasicActor.spawn(name = "meep")
moop = BasicActor.spawn(name = "moop")

#Kicking off an eternal cycle
meep.inbox.put((moop.name, moop))

#Poisoning an actor to stop the cycle.
import time
time.sleep(0.2)
pill = PoisonPill()
meep.inbox.put((pill, moop))







