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

Now both the client instances were run on my laptop, so let me try running them on different devices that are on the same network. I ran one client on my phone and one client on my laptop and that worked as well, so connection wise it all works.  

## MEGA CLIENT
Now the next thing I want to try is interacting with a client of my choosing. So if I have 5 clients connected to my server, I need to be able to choose a client and send them some instructions.  

However after some thinking on how I want this work, I think I want to let the server just manage connections and messages. I want to avoid adding any hard coded logic on the server. So what if I create a mega client. Or some sort of admin client. This admin client should be able to see who is connected to the server, choose one dude and control it.  

And on top of that even though I wanted to avoid it we need to prepare the server for two different types of clients so we will need to hard code some logic for that.  

Let's start by preparing the server for a mega client. I also will now expect a name from each client and store their details in a dictionary instead of a list. This should make things a little easier to work with.  

Another thing to worry about is the buffer size. In the [HOWTO](https://docs.python.org/3/howto/sockets.html) they mention this problem here:
~~~
Now we come to the major stumbling block of sockets - send and recv operate on the network buffers. They do not necessarily handle all the bytes you hand them (or expect from them), because their major focus is handling the network buffers. In general, they return when the associated network buffers have been filled (send) or emptied (recv). They then tell you how many bytes they handled. It is your responsibility to call them again until your message has been completely dealt with.
~~~

Now since I am not actually sending messages 'per se' between the client and the server and I have full control over the communication between sockets, I don't think this is something I need to worry about right now, but maybe I should deal with an abstraction for now. Just make a custom function that will just forward send and recv functions. Later on when I want to change the internals of the abstract function we should not face any problems.

So we need to:
- Take a name from every client.
- Change the lists to dictionaries.
- Prepare the server to accept a mega client first before.

Before we start with preparing the server, I want to plan out what the mega client should actually do.
- When it connects to the server it should be given a list of connected clients.
- We'll also give the client the option to refresh the list.
- It should then choose a client, and then for our test case, we'll just send a message to the selected client.

So first the server needs to know that the client connected to it is the mega client, for that I'll make it check the name of the client (security wise this is horrible but this is just me trying stuff out and I do not want to make this any more complicated than it has to be).

~~~
Okay full refactor of the old code
Flow:
1. Create Server
2. Accept Connections
3. Check clients
4. Store non admin client sessions
5. Assign Thread
6. Store non admin client threads
7. Split Flow into normal and admin clients now

Flow - admin:
1. Give it a list of connected clients
2. Accept the client details (could be the name)
3. Send that client a message
4. For later:
    a. Possibility to get the list whenever I want it.
    b. Get choose another client and do the same.

Flow - client:
1. Connect to the server and wait for the admin to send a message
~~~


While writing this since I wanted to send the dictionary containing the client list to the mega client, I had to figure out a way to send a dictionary over sockets.  
Just using `socket.send(dict)` does not work so I searched up ways to send a dictionary over sockets. One of the more recommended methods was to use the `json` library and serialise the dictionary into a string using `json.dumps`, I can then use `encode` to convert it into bytes.

However I faced another issue with attempting to serialise the dictionary. The dictionary would store the client object as values. And the `json.dumps` function does not like that. So instead I'll be passing just the names of the connected clients, instead of the client object as well. Because we do not need the object.  
Later on we can also use the client's address. But since I'm running everything locally every client has the same IP address.

As I kept working on this, I kept making changes to the code. Trying to make it more abstract, mainly because as I was writing things it got really complicated and I was starting to get confused about what I had written. (This is a problem I definitely need to work on). I ended up consulting with a friend who told me what changes to make to prevent such confusion. And ended up splitting my code into a bunch of files and classes. I don't want to paste all the codes in this blog but I will add a `github` link at the end for the files of the referenced programs.  

### So let's talk about the flow of our new program
1. Server Code:
- Start the [server](https://github.com/meheraabChothia/network-programming/blob/main/signals/mega-client/refactored_server.py) and bind it to an address.
- Loop over looking for connections
  - When a client connects classify them as an admin client or a normal client.
- Assign the client to a thread and let it run in the background.
- Both the client and the thread are added to dictionaries.

- The normal client, will just wait to receive a message from the admin.
- The admin client's object on the server's end, waits for a command from the admin client.
  - It then checks if the command matches the ones in our utilities file [`util.py`](https://github.com/meheraabChothia/network-programming/blob/main/signals/mega-client/utils.py)
  - For the `list` command the server will send the list of connected clients to the admin.
  - For the `choose` command the server takes the name of the client from the admin and checks to see if it exists.
  - If it does, it returns a connection successful message along with a custom exception that we check on the clients end. All of these exceptions can be found in [`exceptions.py`](https://github.com/meheraabChothia/network-programming/blob/main/signals/mega-client/exceptions.py)
    - It then sends a sample message to the chosen client.
  - If the client is not found the relevant exception is sent to the client and checked.

Apart from the stuff that exists in `utils.py` and `exceptions.py` everything exists in one of two classes: `Server` and `Client`. The Server class, handles creating the server socket, the connection loop, sorting the clients and assigning their threads for them.  
The Client class handles the acceptance of the client socket, retrieving the client list both encoded and decoded, helping the mega client from selecting a client from the client list, and the interaction loop between the server and the admin client. It will also contain any functions that the server will require to control or communicate with the clients.

2. Client Code:
The [client code](https://github.com/meheraabChothia/network-programming/blob/main/signals/mega-client/client.py) has just one class called `Client`. This class deals with making the client socket and connecting it to the host, taking the name from the user and sending it to the server.  

It then has the flow loops for the admin client and the normal client. The normal client only waits for a message from the admin and prints it to the terminal.
The admin client flow meanwhile, let's the user input a command, checks the command and calls the necessary functions.  

The flow looks something like this:
- The user is asked to enter their name, then depending on that input the appropriate functions are called (admin_loop for admins and client_loop for normal clients).
- The normal client just runs a `recv` call and prints out what it gets.  
- The admin client will ask the user to enter commands.
- It will then take those commands process them and send them to the server.
- What the server does with that choice is mentioned in the server flow above.
- The server then returns a few status codes, for connecting to the client and to tell the admin if the communication was a success (I would like to explore this in more detail).
- The client then goes through the status codes and handles them (I should also look into how HTTP communication works with status codes).

That's basically it. The premise is pretty simple and it works. The normal client connects to the server and waits for the mega client to send it a message.
The mega client on the other hand can choose to see all connected clients at any moment and then choose one to 'activate'. In this case activation is sending it a message.

Here is a sample run of the code:
~~~
$ python refactored_server.py
Interacting with client ('127.0.0.1', 34884)
Pushed the client to another thread.
Pushed the client to another thread.
Interacting with the admin client.
Interacting with the admin client.
Interacting with the admin client.

$ python client.py
What's your name: admin
Successfully connected to the server.
Connected to the Server as an admin!
(/help for help) command: /list
1. dummy
2. admin
(/help for help) command: /connect
Name of the client: dummy
Connected to the client with the name: dummy
Communcation with the client was successful.
(/help for help) command:

$ python client.py
What's your name: dummy
Successfully connected to the server.
Waiting for communication from the admin:
Message from admin: Message from the Mega Client
Waiting for communication from the admin:
~~~

~~~
Slightly off topic, but while testing my server code, if I made a change and restarted it, I would get an OSError:
"OSError: [Errno 9] Address already in use"
This would last for a minute or two and I tried to figure out why.
Apparently the kernel holds the port open for a while after the connection closes. This is called the "TIME_WAIT" state.
The docs for sockets mention using this line to stop that:
"s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)"
I will try to figure out what the attributes mean some other time.
~~~

# Potential Issues
If someone logs in with a name that already exists in the dictionary, the previous session could be wiped.
Inactivity time out.
