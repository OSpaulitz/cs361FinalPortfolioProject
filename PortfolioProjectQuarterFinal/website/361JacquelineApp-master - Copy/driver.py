#py -m pip install pyzmq
import zmq
debug = 1

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")

#send notification to admin that user added recipe

if debug == 1:
    print("sending test string")
socket.send_string("TEST")
message = socket.recv()
if debug == 1:
    print("received response "+str(message))

if debug == 1:
    print("sending admin message command")
socket.send_string("TYPE: admin; CONTACT: paulitzj@oregonstate.edu; RECIPE NAME: avocado toast; RECIPE: ingredients:\
 bread, avocado. instructions: mash avocado, toast bread, spread avocado on toast; USER: jacqueline.o.84@gmail.com")  # gouldai@oregonstate.edu
message = socket.recv()
if debug == 1:
    print("received response "+str(message))

if debug == 1:
    print("sending user message command")
socket.send_string("TYPE: user; CONTACT: paulitzj@oregonstate.edu; RECIPE NAME: avocado toast")  #gouldai@oregonstate.edu
message = socket.recv()
if debug == 1:
    print("received response "+str(message))