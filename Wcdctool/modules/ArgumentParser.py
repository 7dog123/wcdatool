#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# Module Argument Parser
# Copyright (c) 2015 by Fonic (https://github.com/fonic)
#
# Date started:  10/05/2015
# Date modified: 10/06/2015
#
# NOTE 07/12/19 07/28/19:
# - added maxlen logic to print_help for prettier output
# - added support for default values for wcdtool
# - added special handling of nargs == 1 to not produce a list; if nargs=1 is passed to ArgumentParser, the result is a list with one item;
#   to get only the item, one must pass nargs=None (very confusing...) -> https://stackoverflow.com/a/37868918
# - changes should maintain compatibility with older projects (not tested yet)
#
# TODO:
# - use templates for usage message instead of %s to allow applications to decide if executable, positionals and options should be displayes (required for medials!)
#   -> Templates (1): https://docs.python.org/3/library/string.html#string-formatting: str.format("Usage: {exec} Options: {options}", exec="...", options="...")
#		-> built-in, also works if some ids are missing in first string
#   -> Templates (2): https://docs.python.org/3/library/string.html#template-strings
#   -> Support {executable} {arguments} {options}
# - measure max length of options syntax -> prettier output
# - probably support different nargs for option type 'normal'; would affect syntax as well as usage display
# - probably add parameter for options type 'positional' for usage display so that e.g. 'files' can be used as name while 'FILE' is being displayed
#
# DONE:
# - check if there's is way to evaluate the error (e.g. to many arguments, missing arguments, unknown arguments etc.)
#   -> not possible due to error handling in parent class
#


# ------------------------------
# - Exports
# ------------------------------

# Auto-generated by generate-all.py
__all__ = [ "ArgumentParser" ]



# ------------------------------
# - Imports
# ------------------------------

import os
import sys
import argparse



# ------------------------------
# - Globals
# ------------------------------

# Message that get's displayed in case of an error
MSG_SYNTAX_ERROR = "Invalid command line. Use --help to display available options."

# Message that get's displayed if help is requested
MSG_USAGE_HELP   = "Usage: %s [OPTION]... %s\n\nOptions:"

# Default 'help' option
OPT_DEFAULT_HELP = {
	"type":   "help",
	"name":   "help",
	"short":  "-h",
	"long":   "--help",
	"help":   "Display this message"
}

# Exitcode in case of an error
EXITCODE_ERROR = 2

# Exitcode if help was requested
EXITCODE_USAGE = 0



# ------------------------------
# - Class ArgumentParser
# ------------------------------

# Wrapper class for argparse.ArgumentParser
class ArgumentParser(argparse.ArgumentParser):
	
	# Constructor
	def __init__(self, options, msg_error=MSG_SYNTAX_ERROR, exc_error=EXITCODE_ERROR, msg_usage=MSG_USAGE_HELP, exc_usage=EXITCODE_USAGE):
		
		# Call constructor of parent class
		super(ArgumentParser, self).__init__(add_help=False)

		# Store parameters
		self.options   = options
		self.msg_error = msg_error
		self.exc_error = exc_error
		self.msg_usage = msg_usage
		self.exc_usage = exc_usage

		# Check if 'help' option is provided
		self.opt_help = None
		for option in self.options:
			if (option["type"] == "help"):
				self.opt_help = option
				break
		
		# Add 'help' option if not provided
		if (not self.opt_help):
			self.opt_help=OPT_DEFAULT_HELP
			self.options.append(self.opt_help)
		
		# Add provided options to parser
		for option in self.options:
			if (option["type"] == "normal"):
				option["syntax"] = "%s, %s=%s" % (option["short"], option["long"], option["arg"])
				self.add_argument(option["short"], option["long"], nargs="?", action="store", dest=option["name"], default=option["default"] if ("default" in option) else None)
			elif (option["type"] == "switch"):
				option["syntax"] = "%s, %s" % (option["short"], option["long"])
				self.add_argument(option["short"], option["long"], action="store_true", dest=option["name"], default=False)
			elif (option["type"] == "positional"):
				option["syntax"] = "%s" % (option["name"])
				self.add_argument(option["name"], nargs=None if (isinstance(option["nargs"], int) and option["nargs"] == 1) else option["nargs"], action="store")
			elif (option["type"] == "help"):
				option["syntax"] = "%s, %s" % (option["short"], option["long"])
				self.add_argument(option["short"], option["long"], action="help")
			else:
				raise Exception
	
	
	# Print usage help (overwrites method of parent class)
	# TODO: generate output, then apply to template and print as a whole; this way, the template may decide how/what is printed
	def print_help(self):
		
		# Print usage line
		positional = ""
		for option in self.options:
			if (option["type"] == "positional"):
				if (option["nargs"] == "?"):
					#positional += "[%s]" % option["name"].upper()
					positional += "[%s]" % (option["display"].upper() if "display" in option else option["name"].upper())
				elif (option["nargs"] == "+"):
					#positional += "%s..." % option["name"].upper()
					positional += "%s..." % (option["display"].upper() if "display" in option else option["name"].upper())
				elif (option["nargs"] == "*"):
					#positional += "[%s]..." % option["name"].upper()
					positional += "[%s]..." % (option["display"].upper() if "display" in option else option["name"].upper())
				else:
					for i in range(0, option["nargs"]):
						#positional += "%s " % option["name"].upper()
						positional += "%s " % (option["display"].upper() if "display" in option else option["name"].upper())
				positional += " "
		print(self.msg_usage % (os.path.basename(sys.argv[0]), positional))
		
		# Print options
		maxlen = 0
		for option in self.options:
			if (len(option["syntax"]) > maxlen):
				maxlen = len(option["syntax"])
		template = "  %-" + str(maxlen+2) + "s%s"
		for option in self.options:
			if (option["type"] != "positional"):
				print(template % (option["syntax"], option["help"]))
				
		# Terminate program
		sys.exit(self.exc_usage)
	
	
	# Handle errors (overwrites method of parent class)
	def error(self, message):
		self.exit(self.exc_error, self.msg_error % self.opt_help["long"] + "\n")



# ------------------------------
# - Example
# ------------------------------

# This function demonstrates some of the module's abilities.
# It is only executed if the script is run directly
def example():

	# Define command line options
	cmdoptions = [
			{
				"type":   "switch",
				"name":   "pretend",
				"short":  "-p",
				"long":   "--pretend",
				"help":   "No changes (dry run)"
			},
			{
				"type":   "normal",
				"name":   "logfile",
				"short":  "-l",
				"long":   "--logfile",
				"arg":    "file",
				"help":   "Log file to write to"
			},
			{
				"type":   "help",
				"name":   "help",
				"short":  "-h",
				"long":   "--help",
				"help":   "Display this message"
			},
			{
				"type":   "positional",
				"name":   "infile",
				"nargs":  "+",
				"help":   "Input files"
			},
			{
				"type":   "positional",
				"name":   "outfile",
				"nargs":  1,
				"help":   "Output file"
			}
		     ]
	
	# Define messages
	msg_error = "Invalid or insufficient command line. Use %s for detailed usage information."
	msg_usage = "Usage: %s [OPTION]... %s\n\nExample for Python module Argument Parser. The options\nspecified below are for demonstration purposes only.\n\nOptions:"
	
	# Define exitcodes
	exc_error = 2
	exc_usage = 0
	
	# Process command line
	parser = ArgumentParser(cmdoptions, msg_error, exc_error, msg_usage, exc_usage)
	args   = parser.parse_args()
	
	# Print given arguments
	print("\nCommand line arguments:\n")
	print("Pretend:", args.pretend)
	print("Logfile:", args.logfile)
	print("Input:  ", args.infile)
	print("Output: ", args.outfile)
	print("")


# Execute example function only if script is run directly
# as an application, not when imported as a module
if (__name__ == "__main__"):
	example()
