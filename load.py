#!/usr/bin/python2.6
"""This script imports text substitutions into OS X preferences."""
import json
import sys
import time
from Foundation import (
    NSUserDefaults,
    NSMutableDictionary,
    NSDistributedNotificationCenter
)
from CoreFoundation import (
    CFPropertyListCreateDeepCopy,
    kCFPropertyListMutableContainersAndLeaves
)

if len(sys.argv) < 2:
    sys.exit("Usage: load.py [map.json]")

# Using the same JSON format as
# https://github.com/dwaite/mac-text-substitutions
f = open(sys.argv[1], 'r')
importedData = json.load(f)
f.close()

updated = added = 0 # reset counters

# This code reads and modifies OS X preferences.
prefs = NSUserDefaults.standardUserDefaults()
globalPrefs = prefs.persistentDomainForName_('.GlobalPreferences')

# Since NSUserDefaults returns immutable objects, we create
# a deep(!) mutable copy, and then assign this copy
# at the end of the script.
globalPrefs = CFPropertyListCreateDeepCopy(
    None, globalPrefs, kCFPropertyListMutableContainersAndLeaves)

# Before 10.8, this was called NSUserReplacementItems.
# From 10.8, this is called NSUserDictionaryReplacementItems.
itemsName = 'NSUserReplacementItems'
items = globalPrefs.objectForKey_(itemsName)
if items == None:
    itemsName = 'NSUserDictionaryReplacementItems'
    items = globalPrefs.objectForKey_(itemsName)
    if items == None:
        sys.exit('Error: The global preferences do not contain '
                 'a replacement items list. '
                 'Is this OS version supported?')

# Update entries that already exist
for item in items:
    replace = item.valueForKey_('replace')
    if importedData.has_key(replace):
        importedItem = importedData[replace]
        item.setObject_forKey_(importedItem['enabled'], 'on')
        item.setObject_forKey_(importedItem['replacement'], 'with')
        del importedData[replace]
        updated += 1

# Add new entries
for key, importedItem in importedData.iteritems():
    item = NSMutableDictionary.dictionary()
    item.setObject_forKey_(importedItem['enabled'], 'on')
    item.setObject_forKey_(key, 'replace')
    item.setObject_forKey_(importedItem['replacement'], 'with')
    items.addObject_(item)
    added += 1

# Update the preferences
prefs.setPersistentDomain_forName_(globalPrefs, '.GlobalPreferences')
prefs.synchronize()

# Release the preferences from memory
NSUserDefaults.resetStandardUserDefaults()

# Build notification userInfo object
userInfo = {}
userInfoEntries = []
for item in items:
    userInfoEntries.append({
                           'shortcut': item.valueForKey_('replace'),
                           'phrase': item.valueForKey_('with'),
                           'timestamp': int(time.time())
                           })
userInfo = {
    'IMKUserDictionaryUserInfoCurrentEntriesKey': userInfoEntries
}

# Makes our changes to apply immediately on running processes.
# It's undocumented but this is the notification that the prefpane
# sends out when you make changes.
nc = NSDistributedNotificationCenter.defaultCenter()
nc.postNotificationName_object_('NSSpellServerReplacementsChanged', None)
nc.postNotificationName_object_userInfo_(
   'IMKUserDictionaryDidChangeNotification', None, userInfo)

print repr(added) + " substitutions added."
print repr(updated) + " substitutions updated."
