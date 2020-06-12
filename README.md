
# FactoryOS: Distributed Self-Organizing Manufacturing OS

[Design Doc](https://docs.google.com/document/d/14D9z-c7i1_GU2eFmPw7M6nCwIaInTCtb14OPEwDR4mo/edit#)

## Overview

TODO

### Running Project

#### Setup

```bash
python3.5 -m pip install -r requirements.txt
```

### Execution

To spawn multiple processes automatically, run the following commands. Number of types represents the items being produced, while nodes_per_type represents the duplication for the nodes.
```
python main.py --num_types 5 --nodes_per_type 2 --complexity high
```

To run a dynamic GUI reflecting the cluster changes, run,
```
python main.py --num_types 5 --nodes_per_type 2 --complexity high --run_plotter True
```
