from lanista.threadactors import start_thread, PoisonPill
from Queue import Queue

# Testing message passing loop between different actors

class BasicActor():

    def __init__(self, name):
        self.name = name
        self.inbox = Queue()
        start_thread(function = self.live, name = self.name)


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

meep = BasicActor(name = "meep")
moop = BasicActor(name = "moop")

#Kicking off an eternal cycle
meep.inbox.put((moop.name, moop))

#Poisoning an actor to stop the cycle.
import time
time.sleep(0.2)
pill = PoisonPill()
meep.inbox.put((pill, moop))







