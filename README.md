
# Distributed Manufacturing operation system

Use cases:

- Convert the single SQL DB to shared data across sites.
- design choices
  - Central DB with replication?
  - Each site holding a DB? The data is replicated?
- smooth addition of new sites.

## Development

```bash
make setup
cd src && source bin/activate
python3 -m pip install -r requirements.txt

```

## APIs

- addNewSite POST/PUT
- transferInventory(id) PUT/POST
- getInventory(id) GET

## User Stories

1. A
2. B

## Skill sets

- Data science (python, TF, etc.)
- Golang (cloud application/concurrency performance)
- Systems programming (C, gRPC, protobuf, sockets, etc)??
