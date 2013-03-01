#!/usr/bin/python
from urlfetch import Link

ERROR_KEY = 'error'
ERR_MESSAGE_KEY = 'message'
OK_KEY = 'ok'
ERROR_CODE = {
		'LINK_DUPLICATE': 1000,
		'UNDEFINED_LINK': 1021,
	}

class DuplicateLinkException(Exception):
	"""
	TODO
	"""

	def __init__(self, link):
		self.link = link

	def __str__(self):
		return 'Warning: Link '+ self.link.strUrl() +' already exists'

class LinkGetException(Exception):
	"""
	TODO
	"""

	def __init__(self, link):
		self.link = link

	def __str__(self):
		return 'ERROR: Unable to retrieve link data in database for "'+ self.link.strUrl() +'"'

class AddLinkHistoryException(Exception):
	"""
	TODO
	"""

	def __init__(self, link):
		self.link = link

	def __str__(self):
		return 'ERROR: Unable to write in "link_history" for the link "'+ self.link.strUrl() +'"'

class WTFException(Exception):
	"""
	TODO
	"""
	def __init__(self, m=None):
		self.message = m

	def __str__(self):
		if self.message is None:
			return 'Error: An imprevisible error occured. Exiting program.'
		else:
			return self.message

