#!/usr/bin/python2.6
"""Listens to all notifications to determine undocumented
notification codes."""

from Foundation import (
    NSDistributedNotificationCenter,
    NSRunLoop
)

class GetNotifications(object):

    def __init__(self):
        nc = NSDistributedNotificationCenter.defaultCenter()
        nc.addObserver_selector_name_object_(self, 'gotIt:', None, None)

    def gotIt_(self, note):
        print 'Got: ', note

listener = GetNotifications()

loop = NSRunLoop.currentRunLoop()
loop.run()
