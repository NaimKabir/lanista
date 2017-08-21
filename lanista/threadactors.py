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

class PoisonPill(Exception):
    """
    This is a special message that can be used to kill an actor and all related actors.
    """
    pass

class ArenaThread(Arena):

    """
    This version of the Arena uses python.threading to spawn actors on various threads.
    This means that each actor lives within the same process under the same PID, and share some memory.
    However, this also means that the actors are not truly parallel and subject to the Global Interpreter Lock,
    which means things will be slower than they can possibly be on a true parallel multi-core actor system.
    """

    message_handlers = HandlerRegistry()

    def __init__(self):
        super(ArenaThread, self).__init__()
        self.mailbox = Queue()

    @classmethod
    def spawn(cls, *args, **kwargs):
        """
        This is a factory method that actually creates a thread actor.
        To instantiate an ArenaThread object you must use it like so:

        new_arena_thread = ArenaThreadChild.spawn(arguments)

        """
        self = cls(*args, **kwargs)
        self.begin()
        start_thread(function = self.live, name = self.name)
        return self

    @message_handlers(PoisonPill)
    def onPoisonPill(self, sender, message):
        """
        This poison pill handler kills the Arena and all sub Agents.
        """
        for name, agent in self.agents.iteritems():
            self.publish(agent, PoisonPill())

        raise message # This, in concert with the live() method causes thread completion.

    def live(self):
        """
        Override this if you want to involve another stop message,
        or have a different listening control flow.
        """

        try:
            while True:
                if not self.mailbox.empty():
                    sender, message = self.mailbox.get()
                    self.receive(sender, message)
        except PoisonPill:
            for name, agent in self.agents.iteritems():
                self.publish(agent, PoisonPill())

    def handleMessage(self, sender, message):
        """
        Example of how to use the handler registry.
        It's not used in this protoclass.
        """

        registry = self.__class__.message_handlers
        handler_function = registry.get(message.__class__)
        if handler_function is not None:
            handler_function(self, sender, message)


class AgentThread(Agent):

    message_handlers = HandlerRegistry()

    def __init__(self):
        super(ArenaThread, self).__init__()
        self.mailbox = Queue()








