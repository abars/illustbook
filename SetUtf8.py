import sys

class SetUtf8:
	@staticmethod
	def set():
		stdin = sys.stdin
		stdout = sys.stdout
		reload(sys)
		sys.setdefaultencoding('utf-8')
		sys.stdin = stdin
		sys.stdout = stdout