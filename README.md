# Math TCP Server

This is a simple math tcp server which can compute math expressions.
It supports only +, -, *, /, (, ) also operations can be nested in parenthesis.

It uses Shunting-Yard and Reverse Polish notation algorithms to compute
the proper order of execution of operators.

This is a result of a test task given to me by probably my future employer :)

Although it's a huge overkill I have a couple of points that I have to implement myself,
so I decided to write everything by myself.

A simplest solution to this problem is to use python's `asyncio` and `ast` modules,
which yields the same result in about 100 lines of code and it's incredibly simple.

# Architecture

Whole thing is written in pure python without any third-party libraries, there are
a couple of modules which are used to glue everything together.
 
## loop.py

This is a simple loop implementation which helps reduce complexity when having a nested 
object relations one of which have to be executed regularly.
  
It consists of `Loop` and `Tickable` classes.

Simplest explanation how in general this works is:

```python
def loop(tickables):
    while True:
        for tickable in tickables:
            tickable.tick()
```

Each `Tickable` object have a reference to it's loop so it can add
another tickables if needed.

For example the TCP server in it's tick method accepts new connections,
if there is new connection it creates a Connection object and adds it to the loop.
Then each Connection object is ticked so it can read from it's socket.

## server.py

This module basically consist of 2 classes Server, Connection.

`Server` is used to bind a socket to given host:port and starts waiting for new connections.
When new connection is made it instantiates a new `Connection` object which is responsible
for reading, writing, encoding, decoding of messages through the socket.

To implement some kind of useful behavior you should sub-class `Connection` class and 
implement `on_message(message: str)` method.

For example:

```python
from mathcp.server import Connection

class Hello(Connection):
    
    def on_message(self, message:str):
        self.socket.print("Hello %s" % message)
```

## parallel.py

This module is a wrapper to pythons multiprocessing.Pool and its used to
offload CPU intensive tasks to a pool of sub-processes.
 
This is required in our case so we are not blocking our server loop when math expression is evaluated.

## math.py

This module holds Shunting-Yard and RPN implementations and also comes
with `calculate` function which combines them to produce an answer to
provided math expression.

## __main__.py

This is the main script of the server.
Here we implement our `MathSolver` class which takes care of receiving new messages and delegates the
execution to the `Pool`

# Install and run

## Install
To install the script run from source:

`python setup.py install`

To install the script from git with pip:

`pip install git+https://github.com/avladev/mathcp.git`

This will create an executable script called `mathcp` which you can use to run the server.

## Run

`mathcp` - This will bind the server to `0.0.0.0:8000`

`mathcp 127.0.0.1 9000` - Specifying host and port

`mathcp -v` - For more verbose output add `-v` flag


If you don't want to install the project you can run it from the root directory with:

`python -m matchcp`


# Thanks

I hope you like it and thanks for the interesting task it was a huge fun for me to write it.

`exit()`

