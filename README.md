##### Requirements

The program uses python 3.7. Python 3.6 should also work fine.

##### Setting up

1. Create the virtualenv:
`python3 -m venv venv`

2. Activate the venv:
`source venv/bin/activate`

##### Running the server

Having activated the venv, run:
`PYTHONPATH=. python socket_server/server.py <PORT> <DATAPATH>`

Note: The way this project is set up, the datapath should be ./data if running the server from the top level path.

##### Running tests

Having activated the venv: 
`python -m unittest -v`

