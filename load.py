#!/usr/bin/python2.6
import json;
import sys;
from Foundation import NSUserDefaults, NSMutableDictionary

if len(sys.argv) < 2:
	sys.exit("Usage: load.py [map.json]")

# Using the same JSON format as https://github.com/dwaite/mac-text-substitutions
f = open(sys.argv[1], 'r');
importedData = json.load(f);
f.close();

# reset counters
updated = added = 0

# update entries that already exist
prefs = NSUserDefaults.standardUserDefaults();
dict = prefs.persistentDomainForName_('.GlobalPreferences');
items = dict.objectForKey_('NSUserReplacementItems');
for item in items:
	replace = item.valueForKey_('replace')
	if importedData.has_key(replace):
		importedItem = importedData[replace]
		item.setObject_forKey_(importedItem['enabled'], 'on');
		item.setObject_forKey_(importedItem['replacement'], 'with');
		del importedData[replace]
		updated += 1

# add new entries
for key, importedItem in importedData.iteritems():
	item = NSMutableDictionary.dictionary();
	item.setObject_forKey_(importedItem['enabled'], 'on');
	item.setObject_forKey_(key, 'replace');
	item.setObject_forKey_(importedItem['replacement'], 'with');
	items.addObject_(item);
	added += 1

prefs.setPersistentDomain_forName_(dict, '.GlobalPreferences');
prefs.synchronize();

print repr(added) + " substitutions added."
print repr(updated) + " substitutions updated."
