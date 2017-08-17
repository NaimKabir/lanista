import gevent
from gevent.queue import Queue

class Arena(gevent.Greenlet):
    """
    This is the superclass for environments that multiple learner agents may interact in.

    It is responsible for keeping track of the current state of the environment,
    dictating how states transition to other states based on actions (a set of game rules),
    and what rewards to deal to each participating agent depending on their unique attributes
    and/or their team alliegance.

    It also is the entry-point into the cycle of any multiplayer game:

    <publishing state to Agents --> receiving actions from Agents --> priming Agents with received actions
    --> stepping the environment forward in time according to game dynamics --> publishing state to Agents>

    Here are the attributes that any Arena must have:

    state: A serializable data object that keeps track of the current state of the game.
     This can be a graph, a vector, an image, etc.

    actions: A complete space of actions that can be taken by Agents. This is the union of all
     the Agents' individual action sets.

    agents: A registry of all the Agents that are live in the Arena. Is empty if no Agents are added.

    Here are the methods that are called by the user:

    start
    reset
    close
    register
    receive
    prime
    step
    publish
    seed

    These are wrappers over the core methods that should be implemented by the developer:

    _start
    _reset
    _close
    _register
    _receive
    _prime
    _step
    _publish
    _seed

    """
    def live(self):
        """
        You probably won't need to override this.
        This method readies the Greenlet object so it can receive and handle messages.
        It also has several checks to make sure the correct number of messages are received.
        """
        self.live = True
        while self.live:
            if not self.mailbox.empty():
                if len(self.mailbox) > len(self.agents) + len(self.games):
                    raise AssertionError("Agents are sending the Arena more than one message per step!"
                                         "This will cause thread slowdown and halting.")
                message = self.mailbox.get()
                self.receive(message)

    def __init__(self):
        super(Arena, self).__init__()
        self.agents = []
        self.games = []
        self.mailbox = Queue()

    def start(self):
        """
        This starts up the environment's dynamics and begins the cycle of
        publishing state -> receiving actions -> updating state -> publishing state
        """

        self._start()

    def reset(self):
        """
        Once some stopping condition is met, such as a game win or loss, then the environment
        should be reset to a starting state so that the game may begin anew.
        One start-to-reset cycle is an episode.
        """

        self._reset()

    def close(self):
        """
        Once the user is done with an environment, necessary wrap-up can be done here.
        """

        self._close()


    def register(self, agent):
        """
        When a new Agent enters the Arena, the necessary update to state and
        game dynamics should occur here. The Agent can (and probably should) be added to the Arena's
        'agents' attribute.
        """

        self._register(agent)

    def receive(self, *args):
        """
        Generic method for handling actions sent to the Arena.
        This can be configured for Agents and Arenas running on multiple cores or CPUs.
        """



        self._receive(*args)

    def prime(self, agent, action):
        """
        Before stepping forward the Arena in time, this method should be used to
        prime each Agent with actions that they have chosen. This way the Arena's state dynamics functions
        can handle any unique Agent-dynamics where events simultaneously unfold.

        For example, if a Murmillo agent is primed to <stab> a Retiarus, and the Retiarus
        is primed to <throw a net> on the Murmillo--then the Murmillo's <stab>
        action may be interrupted during the step function because he was netted first.
        """
        self._prime(agent, action)

    def step(self, *args):
        """
        This is the core method of an Arena, where all registered Agents, their actions, and the
        the current state are all used in order to determine the next state and the reward for each agent.
        """

        self._step(*args)

    def publish(self, agent, *args):
        """
        After new rewards and the latest state have been determined,
        these data must be published to each registered Agent.

        This should send states and rewards for each agent in self.agents.
        """

        self._publish(agent, *args)

    def seed(self, seed = None):
        """
        Random state dynamics will be based on some random seed.
        It's best to keep track of them to make sure there's no issues with multiple RNG
        producing correlated numbers.
        """
        self._seed(seed)

    def _start(self): raise NotImplementedError
    def _reset(self): raise NotImplementedError
    def _close(self): raise NotImplementedError
    def _register(self, agent): raise NotImplementedError
    def _receive(self, *args): raise NotImplementedError
    def _prime(self, agent, action): raise NotImplementedError
    def _step(self, *args): raise NotImplementedError
    def _publish(self, agent, *args): raise NotImplementedError
    def _seed(self, seed = None): raise NotImplementedError

class Agent(gevent.Greenlet):
    """
    This is a single decision-making entity placed in an Arena.

    Any Agent is responsible for forming a personal representation of the Arena's state,
    using this state in order to produce an action, and use rewards from the environment
    in order to update how it chooses actions.

    The Agent requires the following attributes:

    name: A unique identifier.
    actions: A subset of the actions made available by a particular Arena.
    representation: An Agent-specific representation of Arena state.
    model: An Agent's model for a state/action evaluation function.

    Depending on the type of game/agent the user may elect to grant attributes such as:

    teams: A set of group names with which this Agent shares a common cause.

    These are the methods called by the user:

    receive
    learn
    perceive
    policy
    publish

    Which are thin wrappers over these methods that must be implemented by the user:

    _receive
    _learn
    _perceive
    _policy
    _publish

    """

    def live(self):
        """
        You probably won't need to override this.
        This method readies the Greenlet object so it can receive and handle messages.
        It also has several checks to make sure the correct number of messages are received.
        """
        self.live = True
        while self.live:
            if not self.mailbox.empty():
                if len(self.mailbox) > len(self.arenas):
                    raise AssertionError("Arena is sending this agent more than one message!"
                                         "This will cause thread slowdown and halting.")
                message = self.mailbox.get()
                self.receive(message)

    def __init__(self):
        super(Agent, self).__init__()
        self.arenas = []
        self.mailbox = Queue()

    def receive(self, *args):
        """
        This method covers receipt of new state and reward signal from the Arena,
        for use in learning how to choose actions and for choosing the next action.

        It should end up calling the perceive, policy, and learn methods before publishing
        an action back to the Arena.
        """

        self._receive(*args)

    def learn(self, *args):
        """
        This method updates the Agent's internal model using a reward signal
        from the Arena.
        """

        self._learn(*args)

    def perceive(self, state):
        """
        Given some state from the Arena, the Agent should form
        an internal representation of that state. If the Agent is omniscient
        this may be identical to the input state, but otherwise
        the internal representation will only be a piece of the Arena state,
        or perhaps a distortion.
        """

        self._perceive(state)

    def policy(self, representation):
        """
        Given the model's internal representation, the Agent must choose a new action.
        """

        self._policy(representation)

    def publish(self, *args):
        """
        Once an action is committed to, it's published to the Arena for final
        use in stepping forward in time.
        """

        self._publish()

    def _receive(self, *args): raise NotImplementedError
    def _learn(self, *args): raise NotImplementedError
    def _perceive(self, state): raise NotImplementedError
    def _policy(self, representation): raise NotImplementedError
    def _publish(self): raise NotImplementedError

class Game(gevent.Greenlet):
    """
    This class allows you to place a group of Agents in an Arena and allow them
    to play out scenarios for a number of episodes.

    The developer must override the following methods:

    _receive
    _publish
    _reset_condition

    """

    def __init__(self, arena_array, agent_array):
        super(Game, self).__init__()
        self.mailbox = Queue()
        self.episodes = 0

        self.arenas = arena_array
        self.agents = agent_array

        #Adding a pointer to this Game to Arenas' internal state, for messaging purposes.
        for arena in self.arenas:
            arena.games.append(self)

            # Registering all agents with the Arena.
            for agent in self.agents:
                self.arena.register(agent)

    def live(self):
        """
        You probably won't need to override this.
        This method readies the Greenlet object so it can receive and handle messages.
        It also has several checks to make sure the correct number of messages are received.
        """
        self.live = True
        while self.live:
            if not self.mailbox.empty():
                message = self.mailbox.get()
                self.receive(message)

    def receive(self, *args):
        """
        This should receive some data about Arena state,
        and then should be able to enforce a stopping condition by publishing a specific message.
        """

        self._receive(*args)

    def publish(self, arena, *args):
        """
        This should publish a particular message to a specified Arena.
        This simplest way to do this is to simply put() something in the Arena's mailbox attribute.
        The publish method will mainly be used to send a stop signal, but can be useful in many other cases.
        """

    def reset_condition(self, state):
        """
        Specify whether or not some state of the Arena
        warrants a reset. If the Game is a Capture-the-Flag game, then this would be
        if one team captures the flag, for example. If it is a King of the Hill game,
        then an appropriate reset condition would be if one team has stayed on the Hill
        for a sufficient amount of time.

        This method returns a boolean.
        """

        return self._reset_condition(state)

    def run(self, episodes = 1):
        """
        This method starts up the cycle of
        <publishing state --> responding to state with actions -->
        publishing actions --> stepping forward Arena dynamics --> publishing state>

        For all the arenas belonging to a particular game type.
        """

        #Spin up the Game actor and have it listen for messages.
        self.live()

        #Subsequently spin up the Arenas, which in turn will spawn and/or register their Agent actors.
        self.arena.start()


    def _receive(self, *args): raise NotImplementedError
    def _publish(self, *args): raise NotImplementedError
    def _reset_condition(self, state): raise NotImplementedError
