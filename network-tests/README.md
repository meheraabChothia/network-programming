# Why am I even doing this??
At work one of the things I have been extensively working with are APIs. Now to be quite honest before I started working I never really looked into what APIs are, instead I just understood how I can use them and moved on (a serious plot hole in my learning).  
Once I started using it, a part of me kept wondering how this works. I mean I have two different processes and I can communicate between them while both of them exist on different devices, the concept baffled me. Anytime I wanted to have any sort of communication between two codes I never really searched up how it's done, instead in my laziness I just wrote everything I wanted to send into a common file and let the other program read from it, but that is pretty slow and stupid, and there are a whole other slew of problems that can come out of this.  
So here existed a completely new way of communication and while I could make APIs, debug them and use them I had no idea what was really going on in the background.  
Now in college my only experience with network programming was coding sockets in C++ and Python and sending `Hello World` between my codes. And unfortunately I never really gave this a second thought either, never used it even though I always wanted to build some sort of software that I can use to communicate between two different systems.  
Now before I dive into `REST` and `HTTP` protocols I thought I'd revisit sockets.  
Honestly I'm not really sure why but there's just this burning sensation in me to just try to understand what they are.  
Maybe I'll have a more concrete reason when I progress.


# The Learning Process:

So I started by just searching about sockets. Literally just a google search for sockets in python, and I came across this blog post: [Sockets for dummies](https://mathspp.com/blog/sockets-for-dummies). The author starts by talking about his own motivations on learning socket programming and what his end goals are, and they align with my current goals with socket programming as well, basically being able to understand and explain what sockets are to others and to be able to use them in Python to have my programs communicate with each other.  
We start by going through the official [HOWTO](https://docs.python.org/3/howto/sockets.html) on sockets. I did go through it myself and things are not too complicated. They talk about server and client processes and sockets, with an example of how our browser was able to access the page we're currently reading.  
So a server socket will bind itself to an address and wait till a client socket connects to it and then they can transfer data between each other. 

Next in the blog the author starts by making his own server socket and trying to connect his browser to it and sending data to the browser from his server code.  
He starts by making a socket, and using `bind()` to bind it to his `localhost`. And then he decides to just try to connect his browser to it as it is a client after all. He faced a whole slew of issues while trying to do this however and what interested me was his flow of solving the issues and trying things out. Made a server? Lets try to connect to it with the browser. Can't seem to send the data, maybe the browser is trying to send some data first so let's try to read that data. No `read()` method? Lets list all methods using `dir()`. Found a method called `recv()` but don't know how to use it? Use the `help()` method to understand the syntax. That was pretty cool and another goal of sorts it to be able to learn like this. Keep iterating over things to try and do.  

## Creating a server:
So I tried out the whole browser communication thingy the blog was trying out as well but then I wanted to make my own client socket in another code and try to communicate with my server code.  

From what I understood about sockets, the creation process for both the server and client sockets stays the same. The difference between the two comes from what we do with the sockets. For server sockets we start with `bind()` which binds them to an address and port. For a client socket it's using the `connect()` function to connect to an address and port. So I just created another socket in another REPL and used `connect()` to connect to my localhost which already had the server socket bound to it.  
Now we can use `send()` and `recv()` between the 2 codes to talk to each other. And adding these sections to a loop will make it an infinitely looping chat until we close the connection.  

Now this is great, but I'm still communicating between codes on the same device. So let me try to connect between codes on different devices but on the same network.  

So I started building the server side program first:
~~~python
import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Binding to localhost at port 8000
server.bind(('localhost', 8000))
server.listen()

(client_socket, address) = server.accept()
print("Connection established.")
client_socket.send(b'Connected to the server, what do you want to say?')

while (True):
    response = client_socket.recv(999_999)
    print(f"Client: {response}")
    message = input("Server: ")
    client_socket.send(message.encode())
~~~

Since you can only send bytes in `socket.send()` I needed to convert the string into bytes but I could not just use `b'string'` here as we were dealing with a variable. So I used `encode()` which will work just fine for now.

Now I'll make the client's code:
~~~python
import socket

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client.connect(('localhost', 8000))
print(client.recv(999_999))

while (True):
    message = input("Client: ")
    client.send(message.encode())
    response = client.recv(999_999)
    print(f"Server: {response}")
~~~

Testing these codes on the same device worked as expected:
~~~
$ python testserver.py
Connection established.
Client: b'Something'
Server: Test
Client: b'I need to figure out how to remove that damn b'
Server: Maybe use decode? Does that even exist lmao?

$ python testclient.py
b'Connected to the server, what do you want to say?'
Client: Something
Server: b'Test'
Client: I need to figure out how to remove that damn b
Server: b'Maybe use decode? Does that even exist lmao?'
Client:
~~~

So two things bother me with these codes, the first one is mentioned in the messages, the `b` in python printing the raw byte data will also print the `b` in front of it so I need to figure out how to remove that.  
Since we used `encode()` to convert the message into bytes, I assumed that there should be a function called `decode()` that does the opposite, and I was right. I added `.decode()` to any line that's printing the response received from the other code and that fixed the `b`.  
The other thing bothering me is that until we receive a response to our message we cannot send another message. I'll work on improving this later but being able to send multiple messages in a go is possible, they keep getting added to the network buffer on the receiving end until the buffer is flushed, but I need to just code this better for my sample application here.  

But we know that this works on the same system, so let's load the client code onto another device that is connected to the same network as my laptop and let's see if this works.

I ran the server code on my own system, changed the client code to connect to my IP address and ran it on a colleagues laptop and.....  

It failed.  

Naturally, it's very rare for something to work on the first run for me so let's try to understand why it did not work.  
First the error: The error pointed to the `client.connect()` line with a `ConnectionRefusedError`, basically telling me that that connection was refused.  

I realised that while I had changed the client code to connect to my IP address, I had forgotten to change the code on the server's end. So the server was still bound to the localhost. I changed that to bind to ('',8000) which will bind to all available addresses the machine seems to have. (This is mentioned in the HOWTO).  

While using `''` binds every address, if I want to just allow connections on my WiFi network I can just bind the socket to my IP address on the network. If I want to let devices connected to my VPN connect to my server I can use my IP address on my VPN instead. But using `''` let's anybody that can connect to my laptop in. At least that's what I understand from this.  

# Trying to add more clients

So now I can connect python codes that are on different devices (that can connect to each other) I need to try to utilise this in an actual use case.  

So this communication is happening between a server and client. But what if I want there to be 2 clients connected to the server and make them talk to each other?  

Let me try to make some adjustments to our server code to connect to 2 clients and just pass on messages between them. The server code now looks like this:
~~~python
import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind(('', 8000))
server.listen()

# Client 1:
client1, address1 = server.accept()
print("Connection to client 1 established.")
client1.send(b'Connected to the server, what do you want to say?')

client2, address2 = server.accept()
print("Connection to client 2 established.")
client2.send(b'Connected to the server, please wait for the first message.')

while (True):
    response = client1.recv(999_999)
    client2.send(response)
    response = client2.recv(999_999)
    client1.send(response)
~~~

It's not pretty but we're just trying to test things out. So this should accept 2 different connections and just pass the messages from one connection to another. Now I'll create a new client side code that will connect and wait for a message instead of sending one:
~~~python
import socket

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client.connect(('localhost', 8000))
print(client.recv(999_999))

while (True):
    response = client.recv(999_999)
    print(f"Sender : {response.decode()}")
    message = input("You : ")
    client.send(message.encode())
~~~

After running our server and clients and sending some messages between this is what it looks like:

~~~
$ python test-multi-client.py
Connection to client 1 established.
Connection to client 2 established.

$ python client1.py
b'Connected to the server, what do you want to say?'
You : Test
Sender : Test confirmed
You : mhmm

$ python client2.py
b'Connected to the server, please wait for the first message.'
Sender : Test
You : Test confirmed
Sender : mhmm
You :
~~~

# Threading and concurrent `send` and `recv` loops

So it works, and that's great but I now I want to figure out a way to just send without having to wait for a response. Basically right now when we send a message we then wait for the recv function to get some data from the sender. And until that's done we cannot move ahead with the rest of our code.  

I need to figure out a way to separate the sending and receiving sections. If I can make 2 different loops that are running simultaneously, one for receiving and displaying what it received and one for sending messages whenever the user wants to, I don't have to wait to until I can receive anything from another connection.

The two loops themselves are not going to be a problem to make, I can create 2 sockets per connection, one for receiving and one for sending. Basically both of them will be one way connections between the client and the server. But running them parallelly is a problem. So if I want to run them in the same file I can't run one loop while the other one is running.  

So I need to find a way to concurrently run 2 loops and that's exactly what I googled. That helped me find two different libraries in python, [`multiprocessing`](https://docs.python.org/3/library/multiprocessing.html) and ['threading'](https://docs.python.org/3/library/threading.html).  

When trying to understand the differences between the two, I kept coming across this statement:
~~~txt
If your code has I/O or Network usage, use Threading.
If your code is CPU bound, use Multiprocessing.
~~~

Case number 1 is clearly what we're trying to do so let's use `threading`.  
I want to first understand how threading works in a program so let's try it out. I need a loop that will be printing to the terminal every once in while. And another loop that will be ready to take an input from the user at any time. For now we can ignore the sending and receiving parts cause I just want to see how this would work with threading.  
So I made this code:
~~~python
import threading
import time


def inputLoop():
    while (True):
        msg = input("Input something: ")


def outputLoop():
    while (True):
        time.sleep(5)
        print('\nStuff\n')


t = threading.Thread(target=outputLoop)
t.start()

inputLoop()
~~~

And the output looked a little something like this:
~~~
$ python con-test.py
Input something: Test
Input something:
Stuff


Stuff
~~~

Uhhh, it's weird but it works the way I expected it to.  
So the program does not stop and wait for me to input my message before printing the response, but the problems I can see right now are mainly graphical ones. Every iteration of the output loop, will print over the input prompt, in a GUI, you'll normally have 2 different elements, the pane where you can see the entire chat history, and a text box both of which will be independent of each other in the application. However since we're printing everything to the same terminal window this is bound to happen, we'll look into making it look better later on.  

Now that we have a slight understanding of using threading let's try to use it for our socket codes.  

I ended up writing this:

~~~python
# Server Code
import socket
import threading

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind(("", 8000))
server.listen()


class custom_socket:
    def __init__(self, server):
        (self.client, self.address) = server.accept()
        self.name = self.client.recv(999_999).decode()  # For debugging
        print(f"We got a client named: {self.name}")

    def transfer(self, recipient):
        while (True):
            message = recipient.client.recv(999_999)
            print(f"Received a message from {self.name}.")
            self.client.send(message)


client1 = custom_socket(server)
client2 = custom_socket(server)

t = threading.Thread(target=client1.transfer, args=(client2,))
t.start()

client2.transfer(client1)
~~~

~~~python
#Client Code
import socket
import threading

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('localhost', 8000))

name = input("Name: ")
client.send(name.encode())


def recv_loop():
    while (True):
        response = client.recv(999_999).decode()
        print(f"Sender: {response}\nYou: ")


def send_loop():
    while (True):
        message = input("You: ")
        client.send(message.encode())


t = threading.Thread(target=recv_loop)
t.start()

send_loop()
~~~

Now when I run the server code and 2 separate instances of the client code this is what we get:
~~~
$ python server.py
We got a client named: client1
We got a client named: client2
Received a message from client2.
Received a message from client1.
Received a message from client2.
Received a message from client2.

$ python client.py
Name: client1
You: Test message
You: Sender: Hola
You: Hi
You: Let's see if this works
You:

$ python client.py
Name: client2
You: Sender: Test message
You: Hola
You: Sender: Hi
You: Sender: Let's see if this works
You:
~~~

AND IT WORKED!! Well not really, my first attempt to run the codes returned an infinite loop on each of the client's sides. Turns out the server was breaking the connection with the clients because of this line right here:
~~~python
            message = recipient.client.recv(999_999)
~~~

Which used to look like this:
~~~python
            message = recipient.recv(999_999)
~~~

So since I was passing an object of `custom_socket` directly to the function instead of the client variable the sockets were breaking their connections and when that happens `recv` returns 0 which and kept printing `b''` which signals that the connection to the sender is broken.

The next problem I faced was when I tried to run the thread. I was getting this error:
~~~
TypeError: __main__.custom_socket.transfer() argument after * must be an iterable, not custom_socket
~~~
This one confused me at first but when I looked at the help section of `threading.Thread` this is what I saw, "*args* is a list or tuple of arguments for the target invocation. Defaults to ()". So I ended up changing this line:
~~~python
t = threading.Thread(target=client1.transfer, args=client2)
~~~
To this line:
~~~python
t = threading.Thread(target=client1.transfer, args=(client2))
~~~
And it still failed. After a little digging I found a stack overflow page where someone mentioned adding the argument with a trailing comma at the end if you have a single arguments to pass. So the code you see above contains those changes.  

Post all of that, the most noticeable problem is the "graphical" one, since we're printing everything to one common terminal page stuff looks messed up. We'll care about that later on.  
The important thing is that using threading and sockets we've made this weird chat interface. Now this is not all I wanted to do with sockets, ideally I should be able to use this to send data between programs that are on different devices, this whole chat interface was just a nice way for me to see the whole data sending aspect in action. My next course of action will be to think of something interesting to build, which will probably be a separate post.


