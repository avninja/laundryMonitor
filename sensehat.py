from blessings import Terminal

term = Terminal()
location = (0,1)
with term.location(location[0], location[1]):
    print 'This is', term.bold('pretty!')