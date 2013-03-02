#!/usr/bin/python
#from urlfetch import Link

class DuplicateLinkException(Exception):
	"""
	TODO
	"""

	def __init__(self, link):
		self.link = link

	def __str__(self):
		return 'Warning: Link ID '+ str(self.link.id) +' already exists'

class NothingUpdateException(Exception):
	"""
	TODO
	"""

	def __init__(self, link):
		self.link = link

	def __str__(self):
		return 'ERROR: Link ID "'+ str(self.link.id) +'": Nothing updated'

class WTFException(Exception):
	"""
	TODO
	"""
	def __init__(self, m=None):
		self.message = m

	def __str__(self):
		if self.message is None:
			return 'ERROR: An imprevisible error occured. Exiting program.'
		else:
			return self.message

