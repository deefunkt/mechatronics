# Filesystem
This folder contains a replica of the filesystem on the board.
 - boot.py gets executed first on boot
 - main.py contains the main startup code that gets executed after boot.py
 - myutils.py is a custom module providing convenience functions. Currently includes functionality for networking, logging to stdio, an implementation of the linux 'cat', and a dirty file comparator using sha1 hashes
 - socket_server.py is a tcp server implemented using micropython's implementation of the asyncio library for an asynchronous, single threaded approximation of multithreading. Currently supports file upload with specifically formatted files.

 The idea behind creating a folder replica is to write a 'differential sync' like program over the onboard wifi interface. Though microppython provides a rich webREPL it seemed a bit overkill to have a full web browser REPL for single purpose applications. Online upload of python files and soft reboots offer adequate functionality with the benefit of being able to use a dedicated development machine with a fully featured IDE like VS Code.

