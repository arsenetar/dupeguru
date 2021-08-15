# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from ..testutil import eq_
from ..notify import Broadcaster, Listener, Repeater


class HelloListener(Listener):
    def __init__(self, broadcaster):
        Listener.__init__(self, broadcaster)
        self.hello_count = 0

    def hello(self):
        self.hello_count += 1


class HelloRepeater(Repeater):
    def __init__(self, broadcaster):
        Repeater.__init__(self, broadcaster)
        self.hello_count = 0

    def hello(self):
        self.hello_count += 1


def create_pair():
    b = Broadcaster()
    listener = HelloListener(b)
    return b, listener


def test_disconnect_during_notification():
    # When a listener disconnects another listener the other listener will not receive a
    # notification.
    # This whole complication scheme below is because the order of the notification is not
    # guaranteed. We could disconnect everything from self.broadcaster.listeners, but this
    # member is supposed to be private. Hence, the '.other' scheme
    class Disconnecter(Listener):
        def __init__(self, broadcaster):
            Listener.__init__(self, broadcaster)
            self.hello_count = 0

        def hello(self):
            self.hello_count += 1
            self.other.disconnect()

    broadcaster = Broadcaster()
    first = Disconnecter(broadcaster)
    second = Disconnecter(broadcaster)
    first.other, second.other = second, first
    first.connect()
    second.connect()
    broadcaster.notify("hello")
    # only one of them was notified
    eq_(first.hello_count + second.hello_count, 1)


def test_disconnect():
    # After a disconnect, the listener doesn't hear anything.
    b, listener = create_pair()
    listener.connect()
    listener.disconnect()
    b.notify("hello")
    eq_(listener.hello_count, 0)


def test_disconnect_when_not_connected():
    # When disconnecting an already disconnected listener, nothing happens.
    b, listener = create_pair()
    listener.disconnect()


def test_not_connected_on_init():
    # A listener is not initialized connected.
    b, listener = create_pair()
    b.notify("hello")
    eq_(listener.hello_count, 0)


def test_notify():
    # The listener listens to the broadcaster.
    b, listener = create_pair()
    listener.connect()
    b.notify("hello")
    eq_(listener.hello_count, 1)


def test_reconnect():
    # It's possible to reconnect a listener after disconnection.
    b, listener = create_pair()
    listener.connect()
    listener.disconnect()
    listener.connect()
    b.notify("hello")
    eq_(listener.hello_count, 1)


def test_repeater():
    b = Broadcaster()
    r = HelloRepeater(b)
    listener = HelloListener(r)
    r.connect()
    listener.connect()
    b.notify("hello")
    eq_(r.hello_count, 1)
    eq_(listener.hello_count, 1)


def test_repeater_with_repeated_notifications():
    # If REPEATED_NOTIFICATIONS is not empty, only notifs in this set are repeated (but they're
    # still dispatched locally).
    class MyRepeater(HelloRepeater):
        REPEATED_NOTIFICATIONS = set(["hello"])

        def __init__(self, broadcaster):
            HelloRepeater.__init__(self, broadcaster)
            self.foo_count = 0

        def foo(self):
            self.foo_count += 1

    b = Broadcaster()
    r = MyRepeater(b)
    listener = HelloListener(r)
    r.connect()
    listener.connect()
    b.notify("hello")
    b.notify("foo")  # if the repeater repeated this notif, we'd get a crash on HelloListener
    eq_(r.hello_count, 1)
    eq_(listener.hello_count, 1)
    eq_(r.foo_count, 1)


def test_repeater_doesnt_try_to_dispatch_to_self_if_it_cant():
    # if a repeater doesn't handle a particular message, it doesn't crash and simply repeats it.
    b = Broadcaster()
    r = Repeater(b)  # doesnt handle hello
    listener = HelloListener(r)
    r.connect()
    listener.connect()
    b.notify("hello")  # no crash
    eq_(listener.hello_count, 1)


def test_bind_messages():
    b, listener = create_pair()
    listener.bind_messages({"foo", "bar"}, listener.hello)
    listener.connect()
    b.notify("foo")
    b.notify("bar")
    b.notify("hello")  # Normal dispatching still work
    eq_(listener.hello_count, 3)
