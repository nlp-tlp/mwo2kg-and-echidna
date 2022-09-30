''' logger '''
import logging
from time import localtime, strftime
from colorama import Fore, Back, Style

class LoggingFormatter(logging.Formatter):	

	"""A loggingFormatter that looks a bit nicer than the default Flask one.
	This one prints out logs in colours.
	Doesn't work in PowerShell but does work in Cmder or a linux/mac terminal.
	"""
	
	def format(record):
		color_map = {
			'DEBUG': Fore.GREEN,
			'INFO': Fore.CYAN,
			'WARNING': Fore.YELLOW,
			'ERROR': Fore.MAGENTA,
			'CRITICAL': Fore.RED
		}

		return "[%s] %s%s %s%s" % (strftime("%H:%M:%S", localtime()), color_map[record.levelname], record.levelname.ljust(5), Style.RESET_ALL,  record.msg)

# class LogToFile(logging.Formatter):
# 	def format(self, record):

# 		# Break the message nicely onto multiple lines so the file looks a bit better.
# 		def break_lines(msg):
# 			def get_chunks(msg, n=80):
# 				chunks = []
# 				for i in range(0, len(msg), n):
# 					chunks.append(msg[i: i + n])
# 				return chunks
# 			lines = get_chunks(msg.strip())
# 			for i in range(1, len(lines)):
# 				lines[i] = (" " * 28) + lines[i]
# 			return "\n".join(lines)

# 		message = record.msg.replace(Fore.GREEN, "")
# 		message = message.replace(Fore.RED, "")
# 		message = message.replace(Fore.YELLOW, "")
# 		message = message.replace(Style.RESET_ALL, "")

# 		return "%s %s %s" % (datetime.now().strftime('%d-%m-%Y %H:%M:%S'), record.levelname.ljust(7), message)


logging_handler = logging.StreamHandler()
logging_handler.setFormatter(LoggingFormatter)


