
# FactoryOS: Distributed Self-Organizing Manufacturing OS

[Design Doc](https://docs.google.com/document/d/14D9z-c7i1_GU2eFmPw7M6nCwIaInTCtb14OPEwDR4mo/edit#)

## Overview

Supply-Chain management systems deal with massive amounts of data. In today's scenario, with numerous inventories to track, they're unable to work efficiently because 1. they are not fault-tolerant 2. their data is stored on a single database, and 3. they require manual reconfiguration in case of errors. We introduce **factoryOS**, a distributed and self-organizing planning system that can cope with these challenges. **factoryOS** is robust to network delays and fault-tolerant, partitions inventory data natively, and works without any manual intervention. Our novel design point is that we're able to guarantee uninterrupted production even with multiple failures. With **factoryOS**, partition shards are created natively and nodes handle their own processes individually. Our experimental results show that **factoryOS** can be easily scaled to a large number of nodes and is fault-tolerant to a high degree of failures.

## Demo

[![DEMO](http://i3.ytimg.com/vi/929uTIOhIUY/hqdefault.jpg)](https://www.youtube.com/watch?v=929uTIOhIUY)

### Running Project

#### Setup

```bash
python3.5 -m pip install -r requirements.txt
```

### Execution

To spawn multiple processes automatically, run the following commands. Number of types represents the items being produced, while nodes_per_type represents the duplication for the nodes.

```python
python main.py --num_types 5 --nodes_per_type 2 --complexity high
```

To run a dynamic GUI reflecting the cluster changes, run,
```python
python main.py --num_types 5 --nodes_per_type 2 --complexity high --run_plotter True
```
