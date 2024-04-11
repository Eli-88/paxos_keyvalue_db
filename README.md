## Description
This is an implementation of distributed key value database with paxos algorithm with replicated logs.

## Usage
- pip install -r requirements.txt
- run `python paxos_kv/main.py paxo
s_kv/config/config1.json`
- do the same for `config2`, `config3` and `config4`
- put request: post to url: `http://0.0.0.0:8081/propose_request_put` msg: `{"key": "id", "value": "1234"}`
- get request: post to url: `http://0.0.0.0:8080/propose_request_get`
msg: `{"key": "id"}`


## Design

### Sequence Diagram
```mermaid
sequenceDiagram
  Client->>Proposer: request
  Proposer->>Acceptor_1: prepare 
  Proposer->>Acceptor_2: prepare
  Acceptor_1-->>Proposer: promise 
  Acceptor_2-->>Proposer: promise
  Proposer->>Acceptor_1: propose 
  Proposer->>Acceptor_2: propose
  Acceptor_1-->>Proposer: accept 
  Acceptor_2-->>Proposer: accept
  Proposer->>Learner: learn
```

### API
- **/proposer/request**: {value: string}
proposer will call the following api
 1. /acceptor/prepare
 2. /acceptor/propose

- **/acceptor/prepare**: {number: int}
prepare number must be higher than highest promise number

- **/acceptor/propose**: {number: int}
propose number must be higher than highest accept proposal number

- **/learner/accept**: {number: int, value: string}
number must be higher than accepted number

- **/learner/retrieve**: {number: int}
to retrieved the learned values

### Consensus
minimum votes: N/2 + 1 where N is total number of nodes