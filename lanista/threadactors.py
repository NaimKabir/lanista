from lanista.core import Arena, Agent, Game
from threading import Thread
from Queue import Queue

# Various utilities for dealing with messages and threads

def start_thread(function, name = None, as_daemon = True):
    thread = Thread(target = function)
    thread.setDaemon(daemonic= as_daemon) #Sets job to run on non-main thread if daemonic
    thread.start()
    return thread

class HandlerRegistry(dict):
    """
    This class be used as a decorator on any functions that you'd like to handle
    specific message types.

    Usage:

    class Example(object):

        function_handlers = HandlerRegistry()

        @function_handlers(str)
        def onString(string_input):
            print "Handled String: " + string_input

    Effect:

    Allows you to very simply change various handlers for different message types in your class.

    """
    def __call__(self, typ):
        def register(func):
            self[typ] = func
            return func

        return register

class ArenaThread(Arena):

    """
    This version of the Arena uses python.threading to spawn actors on various threads.
    This means that each actor lives within the same process under the same PID, and share some memory.
    However, this also means that the actors are not truly parallel and subject to the Global Interpreter Lock,
    which means things will be slower than they can possibly be on a true parallel multi-core actor system.
    """

    def __init__(self):
        super(ArenaThread, self).__init__()
        self.mailbox = Queue()

    @classmethod
    def spawn(cls, *args, **kwargs):
        self = cls(*args, **kwargs)
        start_thread(function = self.live, name = self.name)
        return self

    def live(self):
        self.begin()
        self.handleMessages()




