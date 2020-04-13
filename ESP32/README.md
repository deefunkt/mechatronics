# ESP 32

This folder contains code relating to experiments in micropython.
 - main.py contains the main startup code that gets executed after boot
 - myutils.py is a custom module providing convenience functions for networking, and logging to stdio
 - transpile.py lives on the development system, and is designed to convert python source code into code that can be sent to the micropython REPL. The end result is a copy of the source file gets created in the micropython system.