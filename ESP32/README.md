# ESP 32

This folder contains code relating to experiments in micropython.
 - The **filesystem** folder contains a replica of the local filesystem on the ESP32 board. 
 - transpile.py lives on the development system, and is designed to convert python source code into code that can be sent to the micropython REPL. The end result is a copy of the source file gets created in the micropython system.
 - socket-client.py is a work in progress of a python tcp client to interact with the onboard tcp server.