## Motivation
During the development of a website, [notesnook.pl](https://www.notesnook.pl), I encountered a feature that I wanted to optimize. On the subpage [notesnook.pl/notes-search](https://www.notesnook.pl/notes-search), users always start with a list of the most liked notes. These are always fetched from the PostgreSQL database and, as long as not many users like different notes, it always returns a similar result. It would be beneficial not to call the database every time a user enters the page, and this is where the idea of implementing an in-memory data store comes in handy. 

I'm aware of Redis or Next.js's built-in cache functions `getServerSideProps` and `getStaticProps`. I decided to leave my website as it is since it's not worth optimizing for a dozen users. However, my curiosity about how these types of solutions work under the hood led to this project.

## Goal  
The goal is to implement a simple datastore solution, or rather a simulation of its features:
- [x] Data storage - users should be able to store data in a key-value format
- [x] Support for SET, GET, DELETE, EXISTS, KEYS operations
- [x] Concurrency - handle concurrent access and modification to data
- [x] Persistence - write current data to disk or file
- [x] Backup / import
- [x] LRU implementation and adding max size limitation / TTL
- [ ] Pipelining (where the client sends multiple requests to the server without waiting for each response) 
- [x] Transactions
- [ ] ACID
- [ ] Logging user operations
- [ ] Pub/sub notifications that some client modified the data (not working, I think I should have a separate thread handling subscriptions)
- [x] Equivalent of Redis' `INCR` and `DECR`

## Initial Research
- [Building a simple Redis server with Python](https://charlesleifer.com/blog/building-a-simple-redis-server-with-python/)
- [Codecrafters Redis Course](https://app.codecrafters.io/courses/redis/overview)
- [Miniredis on GitHub](https://github.com/rcarmo/miniredis)

- I learned a couple of magic words such as socket server, event loop. 
- I should have a server and a client app. 
- I'll implement TTL instead of LRU so it's not as trivial as just using OrderedDict. 
- I also learned how to implement multi-client communication via TCP from [Real Python's guide on Python Sockets](https://realpython.com/python-sockets/).

## Questions and Answers:
- **What if there are more clients than threads?**
  ```python
  client_thread = threading.Thread(target ...
  client_thread.start()
  ```
In Python, when you create a new thread using threading.Thread, it doesn't actually create a new operating system thread, but a lightweight process within the Python interpreter itself. This is due to Python's Global Interpreter Lock (GIL), which allows only one thread to execute at a time in a single process.

- **Should I use a request-response model or a persistent connection model?** <br>
  It depends (obviously). As Redis uses a persistent connection model and it's more suitable for the use case I have in mind, I'll stick with it.  <br>
- **Why should I use a reader-writer lock, when I could simply apply a standard lock for write operations and leave read operations without any lock?** <br>
 A reader-writer lock solves this problem by allowing multiple reads to occur concurrently until a write comes along. When a write operation starts, it waits for all current read operations to finish and then locks out new read and write operations until it's done.
