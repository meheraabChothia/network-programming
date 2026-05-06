## Attempting to build something using Network Programming:
In my last blog, I sort of figured out how to use sockets in python. Now I want to actually build something with it. I'm going to ignore any sort of a chat or messaging interface because that is easy to build(ish) and not something I'm too interested in. Instead I want to build something a little more meaningful. But since I have no ideas in my mind let's build something stupid.  

## How do I use sockets?
Now apart from just sending messages back and forth between a server and a client, the first thing that came to my mind was being able to control a client using the server, or vice versa. To be honest the most generic use case would be to just build applications that just need to take and send data to and from our server. And the complexity of the code would mainly come from making it all work under load. But again that's not something I want to use it for today.  
So using my server as a sort of a remote control device will be interesting. Practically I'm sure there are a lot of potential use cases for this but just for now, just to try things out I want to build a system that will play an alarm on my clients device.  

## Why?
Now even though this is a pretty stupid idea (apart from being funny it doesn't really help anyone, unless you want to be able to wake someone up, or some sort of global alarm system, okay now the ideas are flowing) implementing this should help me experience some application development, pushing out software that can be distributed and maintaining and managing connections to actually be usable. In our previous examples, it was a hassle to connect clients to the server, mainly because of the way the code was written. Being able to actually make this better will be a fun challenge.

## Consistent Connections
Now the first thing I want to do is to improve all of the connection logic. We were hard coding clients, which is not an ideal way to manage connections for a server. So on the server's end to connect to a client we run:
~~~python
(client, address)=server.accept()
~~~
Now once a client connects that connection line is done running which means that no other connections will be accepted until we hit another accept line. Now this means that to have a new connection established to my server I would need to run the server code again.  
This is obviously pretty inefficient. What we need is the server to keep accepting connections. Now we will have to use some sort of concurrency here, because until the accept line is able to accept a connection it halts the program. So if we want to have a client connect and do something with the server but also be able to wait for other clients then we will have to run them concurrently.  

This now also brings me to my next problem and that is being able to interact with a particular client that is connected. So if I have 5 clients connected to my server how do I choose which client to interact with?  

Let's think about this.  

Now what we ended up doing last time was this:
We had two different loops that needed to be run simultaneously, one of the loops would wait for the user to enter something and send it to the receiving socket, and the other would wait for sent message and print it to the console.  We ended up running the receive loop on another thread and the send loop running in our main program because the receiving function was something I did not have to really pay attention to so we could push it to the background. Now we need to do something a little different.  

Let's assume we have a server application that hold some data. A client can connect to the server and read some of this data, but this can only happen if the server sends the data to the client. Now if I only want one client to connect to my server at a time just having the send and recv loops would be fine, with each loop running on its own thread. But if we want to make it possible to have multiple clients connect at the same time, we need to run each client on their own thread while the server trying to loop over it's accept statement will run on the main thread (I don't really know what to call this so I'll call it the main thread for now).

So let's give this a shot, we'll make a server app that should be able to connect to multiple clients and take some string from each client and send the reversed string back to them.  

Now how do I spawn different client objects using the same line of code? Normally to create a client socket I need to run:
~~~python
(client,addr)=server.accept()
~~~
But now we need to create a client socket and then throw it at another thread, and then wait to make a new one and throw that at another thread. So I need some sort of method to create different client socket each time we run accept. So let's make a class, whose constructor will run the accept statement for us.
After some debugging I end up with this:
~~~python
#server.py
import socket
import threading

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("", 8000))
server.listen()

class client_maker():
    def __init__(self, server):
        (self.client, self.addr) = server.accept()
        self.client.send(b"Connected to the server.")

    def reverse(self):
        while (True):
            print(f"Interacting with client {self.addr}")
            message = self.client.recv(999_999).decode()
            print(f"Received this message: {
                  message}\nFrom client: {self.addr}")
            rev = message[::-1]
            self.client.send(rev.encode())
            print(f"Sent a reversed message to client {self.addr}")


clients_list = []
threads_list = []
index = 0
while (True):
    clients_list.append(client_maker(server))
    print(
        f"{"="*70}\nConnected to a client with the address: {clients_list[index].addr}\n{"="*70}")
    threads_list.append(threading.Thread(target=clients_list[index].reverse))
    threads_list[index].start()
    print("Pushed the client to another thread.")
    index += 1

~~~
~~~python
#client.py
import socket

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 8000))
print(client.recv(999_999))

while (True):
    message = input("What do you want to see reversed? ")
    client.send(message.encode())
    response = client.recv(999_999)
    print(response.decode())
~~~

And this is what the output was:
~~~
$ python server.py
======================================================================
Connected to a client with the address: ('127.0.0.1', 42534)
======================================================================
Interacting with client ('127.0.0.1', 42534)
Pushed the client to another thread.
Received this message: test
From client: ('127.0.0.1', 42534)
Sent a reversed message to client ('127.0.0.1', 42534)
Interacting with client ('127.0.0.1', 42534)
======================================================================
Connected to a client with the address: ('127.0.0.1', 56114)
======================================================================
Interacting with client ('127.0.0.1', 56114)
Pushed the client to another thread.
Received this message: hello
From client: ('127.0.0.1', 56114)
Sent a reversed message to client ('127.0.0.1', 56114)
Interacting with client ('127.0.0.1', 56114)
Received this message: sup
From client: ('127.0.0.1', 42534)
Sent a reversed message to client ('127.0.0.1', 42534)
Interacting with client ('127.0.0.1', 42534)

$ python client.py
b'Connected to the server.'
What do you want to see reversed? test
tset
What do you want to see reversed? sup
pus
What do you want to see reversed?

$ python client.py
b'Connected to the server.'
What do you want to see reversed? hello
olleh
What do you want to see reversed?
~~~
Damn it's hard to believe this worked on the first try. I thought that the whole logic behind the way I'm creating threads won't work out as it should but it did. And since we're storing the client details in a list we can also theoretically use them to interact with a particular client. We just need to make it more readable, so the client could send over a name that we can assign to their address and store that in a dictionary.  
Another thing I want to look into is finding out a way to know who is connected to our server, beyond what we have already. Mainly I'm going to look for some inbuilt functions that might workout that way, and if they don't make my own that do.  

Now both the client instances were run on my laptop, so let me try running them on different devices that are on the same network.
