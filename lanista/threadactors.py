from lanista.core import Arena, Agent, Game
from threading import Thread
from Queue import Queue
import time

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

class UnregisteredMessage(object):
    pass

class ThreadActor():

    """
    This version of the Arena uses python.threading to spawn actors on various threads.
    This means that each actor lives within the same process under the same PID, and share some memory.
    However, this also means that the actors are not truly parallel and subject to the Global Interpreter Lock,
    which means things will be slower than they can possibly be on a true parallel multi-core actor system.
    """

    message_handlers = HandlerRegistry()


    def __init__(self):
        """
        This is a factory method that actually creates a thread actor.
        To instantiate an ArenaThread object you must use it like so:

        new_arena_thread = ArenaThreadChild.spawn(arguments)

        """
        self.mailbox = Queue()
        start_thread(function = self.live, name = self.name)

    @message_handlers(UnregisteredMessage)
    def onUnregisteredMessage(self, sender, message):
        print("%s is sending an unregistered message to %s. "
              "This will likely cause a blocked cycle." % (sender, self))

    @message_handlers(PoisonPill)
    def onPoisonPill(self, sender, message):
        """
        This poison pill handler kills the Arena and all sub Agents.
        """
        raise message # This, in concert with the live() method causes thread completion.

    def live(self):
        """
        Override this with a message-listening control flow.
        """
        raise NotImplementedError


    def handleMessage(self, sender, message):
        """
        Example of how to use the handler registry.
        It's not used in this protoclass.
        """
        registry = self.__class__.message_handlers
        handler_function = registry.get(message.__class__) or registry.get(UnregisteredMessage)
        if handler_function is not None:
            handler_function(self, sender, message)


#GAME ACTOR RECIPES

class ArenaThread(Arena, ThreadActor):

    """
    This mixes all the sweet parallelism of the Threaded actor class
    with all the reinforcement learning contracts of an Arena.
    """

    message_handlers = HandlerRegistry()

    def __init__(self):
        Arena.__init__(self)
        ThreadActor.__init__(self)

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
                self.publish(agent, self, PoisonPill())
            for name, game in self.games.iteritems():
                self.publish(game, self, PoisonPill())
            pass



class AgentThread(Agent, ThreadActor):

    """
    This mixes all the sweet parallelism of the Threaded actor class
    with all the reinforcement learning contracts of an Agent.
    """

    message_handlers = HandlerRegistry()

    def __init__(self):
        Agent.__init__(self)
        ThreadActor.__init__(self)

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
            pass


class GameThread(Game, ThreadActor):

    """
    This mixes all the sweet parallelism of the Threaded actor class
    with all the reinforcement learning contracts of a Game.
    """

    message_handlers = HandlerRegistry()

    def __init__(self, name, arena_array, agent_array):
        Game.__init__(self, name, arena_array, agent_array)
        ThreadActor.__init__(self)

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
            pass
