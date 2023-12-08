# Shopping Lists on The Cloud

## Overview

Shopping Lists on The Cloud is a large-scale distributed system designed for managing shopping lists in a collaborative and distributed environment. This project implements a local-first approach, ensuring data accessibility and persistence on the client's machine. The system supports concurrent read/write operations, scalability, and fault tolerance, making it suitable for real-world distributed scenarios.

## Authors

- Ricardo Inácio (up2023027421@up.pt)
- Diogo Lemos (up2020034842@up.pt)
- Tomás Maciel (up2020068453@up.pt)

## Description

Distributed solutions over the internet can be complex, requiring mechanisms for concurrent control of data, replication, and fault tolerance. The Shopping Lists on The Cloud project presents a simplistic yet effective approach for a large-scale distributed shopping list system. The key features include:

- **Local-First Implementation:** Data is always accessible and persistent on the client's machine.
- **Concurrent Read/Write Operations:** The system supports simultaneous data operations.
- **JSON Objects:** Shopping lists are represented as JSON objects with unique IDs (uuid4).
- **ZeroMQ Messaging Library:** Communication is facilitated using the ZeroMQ messaging library.
- **Last-Writer-Wins CRDT:** Versioning is handled using a Last-Writer-Wins Convergent Replicated Data Type (CRDT) supporting add, remove, compare, lookup, and merging functions.
- **Consistent Hash Ring:** Distribution is managed by a consistent hash ring, ensuring uniform mapping of nodes and efficient data storage and replication.

For more informtion and detail, refer to the project's report: [Final Report PDF](./final-report.pdf)


## Keywords

Collaborative, Distributed, Replication, Concurrency, CRDT, LWW, Local-First, Hash Ring

## How to Run

### Prerequisites

Before running the project, ensure that you have the ZeroMQ Python module installed. You can install it using:

```bash
pip install pyzmq
```

## Running the Servers and Proxy

> Open a terminal and navigate to the project directory.
> Run the service.py script to start the servers and the proxy:

```bash
python service.py
```

This script initializes five servers and a proxy, which together form the backbone of the distributed system.
Running the Client

> Open another terminal window (or multiple terminals for multiple clients).
> Run the client.py script to start the client:

```bash
python client.py
```

The client script is designed for academic purposes and is intended to work on a local single machine. Multiple local clients can be run simultaneously, as intended.
Note for Online Deployment

If you intend to deploy the system online, follow these steps:

> Modify the service.py script and replace the localhost (or 127.0.0.1) addresses with real functional IP addresses in the classes' instantiations for servers and the proxy.

> Similarly, modify the client.py script and replace the localhost addresses with the corresponding real IP addresses for each server and the proxy.

**Important:** Do not change the PORT ADDRESSES while modifying the scripts. The system relies on specific port configurations for communication.

By following these steps, you can run the Shopping Lists on The Cloud project on your local machine or adapt it for online deployment with real IP addresses.