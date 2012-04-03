# Package:  events
# Date:     11th April 2010
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Events

This module define the basic Event object and common events.
"""


from .utils import uncamel


class EventMetaClass(type):

    def __init__(cls, name, bases, ns):
        super(EventMetaClass, cls).__init__(name, bases, ns)

        setattr(cls, "name", ns.get("name", uncamel(cls.__name__)))


class BaseEvent(object):

    channels = ()
    "The channels this message is send to."

    success = False
    failure = False
    complete = False
    alert_done = False
    waitingHandlers = 0

    @classmethod
    def create(cls, name, *args, **kwargs):
        return type(cls)(name, (cls,), {})(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        """Base Event

        An Event is a message send to one or more channels. It is eventually
        dispatched to all components that have handlers for one
        of the channels and the event type.

        All normal arguments and keyword arguments passed to the constructor
        of an event are passed on to the handler. When declaring a
        handler, its argument list must therefore match the arguments
        used for creating the event.

        Every event has a :attr:`name` attribute that is used for matching
        the event with the handlers. By default, the name is the uncameled
        class name of the event.

        :cvar channels: An optional attribute that may be set before firing
            the event. If defined (usually as a class variable), the attribute
            specifies the channels that the event should be delivered
            to as a tuple. This overrides the default behavior
            of sending the event to the firing component's channel.

            When an event is fired, the value in this attribute
            is replaced for the instance with the channels that
            the event is actually sent to. This information may be used
            e.g. when the event is passed as a parameter to a handler.

        :ivar value: This is a :class:`circuits.core.values.Value`
            object that holds the results returned by the handlers invoked
            for the event.

        If the optional attribute ":attr:`success`" of an event is set to
        ``True``, an associated event ``EventSuccess`` (original name
        with "Success" appended) will automatically be fired when all
        handlers for the event have been invoked successfully.

        The success event is, by default, delivered to same channels
        as the successfully dispatched event itself. This may be
        overridden by specifying an alternative list of destinations
        in the optional attribute ":attr:`success_channels`"
        """

        self.args = list(args)
        self.kwargs = kwargs

        self.value = None
        self.future = False
        self.handler = None
        self.notify = False

    def __repr__(self):
        "x.__repr__() <==> repr(x)"

        name = self.name
        type = self.__class__.__name__
        if len(self.channels) > 1:
            channels = repr(self.channels)
        elif len(self.channels) == 1:
            channels = str(self.channels[0])
        else:
            channels = ""

        data = "%s %s" % (
                ", ".join(repr(arg) for arg in self.args),
                ", ".join("%s=%s" % (k, repr(v)) for k, v in
                    self.kwargs.items()
                )
        )

        return "<%s[%s.%s] (%s)>" % (type, channels, name, data)

    def __getitem__(self, x):
        """x.__getitem__(y) <==> x[y]

        Get and return data from the Event object requested by "x".
        If an int is passed to x, the requested argument from self.args
        is returned index by x. If a str is passed to x, the requested
        keyword argument from self.kwargs is returned keyed by x.
        Otherwise a TypeError is raised as nothing else is valid.
        """

        if type(x) is int:
            return self.args[x]
        elif type(x) is str:
            return self.kwargs[x]
        else:
            raise TypeError("Expected int or str, got %r" % type(x))

    def __setitem__(self, i, y):
        """x.__setitem__(i, y) <==> x[i] = y

        Modify the data in the Event object requested by "x".
        If i is an int, the ith requested argument from self.args
        shall be changed to y. If i is a str, the requested value
        keyed by i from self.kwargs, shall by changed to y.
        Otherwise a TypeError is raised as nothing else is valid.
        """

        if type(i) is int:
            self.args[i] = y
        elif type(i) is str:
            self.kwargs[i] = y
        else:
            raise TypeError("Expected int or str, got %r" % type(i))

Event = EventMetaClass("Event", (BaseEvent,), {})

class LiteralEvent(Event):
    """
    An event whose name is not uncameled when looking for a handler.
    """
    @staticmethod
    def create(cls, name, *args, **kwargs):
        """
        Utility method to create an event that inherits from
        a base event class (passed in as *cls*) and from
        LiteralEvent.
        """
        return type(cls)(name, (cls, LiteralEvent),
                         {"name": name})(*args, **kwargs)


class DerivedEvent(Event):
    
    @classmethod
    def create(cls, topic, event, *args, **kwargs):
        if isinstance(event, LiteralEvent):
            name = "%s%s" % (event.__class__.__name__, uncamel("_%s" % topic))
            return type(cls)(name, (cls,), 
                             {"name": name})(event, *args, **kwargs)
        else:
            name = "%s_%s" % (event.__class__.__name__, topic)
            return type(cls)(name, (cls,), {})(event, *args, **kwargs)
    

class Error(Event):
    """Error Event

    This Event is sent for any exceptions that occur during the execution
    of an Event Handler that is not SystemExit or KeyboardInterrupt.

    :param type: type of exception
    :type  type: type

    :param value: exception object
    :type  value: exceptions.TypeError

    :param traceback: traceback of exception
    :type  traceback: traceback

    :param kwargs: (Optional) Additional Information
    :type  kwargs: dict
    """

    def __init__(self, type, value, traceback, handler=None):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(Error, self).__init__(type, value, traceback, handler)


class Done(DerivedEvent):
    """Done Event

    This Event is sent when an event is done. It is used by the wait and call
    primitives to know when to stop waiting. Don't use this for application
    development, use :class:`Success` instead.
    """


class Success(DerivedEvent):
    """Success Event

    This Event is sent when all handlers (for a particular event) have been
    executed successfully, see :class:`~.manager.Manager`.

    :param event: The event that has completed.
    :type  event: Event
    """


class Complete(DerivedEvent):
    """Complete Event

    This Event is sent when all handlers (for a particular event) have been
    executed and (recursively) all handlers for all events fired by those
    handlers etc., see :class:`~.manager.Manager`.

    :param event: The event that has completed.
    :type  event: Event
    """


class Failure(DerivedEvent):
    """Failure Event

    This Event is sent when an error has occurred with the execution of an
    Event Handlers.

    :param event: The event that failed
    :type  event: Event
    """


class Started(Event):
    """Started Event

    This Event is sent when a Component has started running.

    :param component: The component that was started
    :type  component: Component or Manager
    """

    def __init__(self, component):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(Started, self).__init__(component)


class Stopped(Event):
    """Stopped Event

    This Event is sent when a Component has stopped running.

    :param component: The component that has stopped
    :type  component: Component or Manager
    """

    def __init__(self, component):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(Stopped, self).__init__(component)


class Signal(Event):
    """Signal Event

    This Event is sent when a Component receives a signal.

    :param signal: The signal number received.
    :type  int:    An int value for the signal

    :param stack:  The interrupted stack frame.
    :type  object: A stack frame
    """

    def __init__(self, signal, stack):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(Signal, self).__init__(signal, stack)


class Registered(Event):
    """Registered Event

    This Event is sent when a Component has registered with another Component
    or Manager. This Event is only sent iif the Component or Manager being
    registered with is not itself.

    :param component: The Component being registered
    :type  component: Component

    :param manager: The Component or Manager being registered with
    :type  manager: Component or Manager
    """

    def __init__(self, component, manager):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(Registered, self).__init__(component, manager)


class Unregister(Event):
    """Unregister Event

    This Event ask for a Component to unregister from its
    Component or Manager.
    """

    def __init__(self, component=None):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(Unregister, self).__init__(component)


class Unregistered(Event):
    """Unregistered Event

    This Event is sent when a Component has been unregistered from its
    Component or Manager.
    """

    def __init__(self, component, manager):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(Unregistered, self).__init__(component, manager)
