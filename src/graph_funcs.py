def addEdge(graph,u,v): 
    graph[u].append(v) 
  
def deleteEdge(graph,u,v): 
    graph[u].remove(v) 
  
# definition of function 
def generate_edges(graph): 
    edges = [] 
  
    # for each node in graph 
    for node in graph: 
          
        # for each neighbour node of a single node 
        for neighbour in graph[node]: 
              
            # if edge exists then append 
            edges.append((node, neighbour)) 
    return edges 

# function to generate all possible paths 
def find_all_paths(graph, start, end, path =[]): 
  path = path + [start] 
  if start == end: 
    return [path] 
  paths = [] 
  for node in graph[start]: 
    if node not in path: 
      newpaths = find_all_paths(graph, node, end, path) 
    for newpath in newpaths: 
      paths.append(newpath) 
  return paths

# function to find the shortest path 
def find_shortest_path(graph, start, end, path =[]): 
        path = path + [start] 
        if start == end: 
            return path 
        shortest = None
        for node in graph[start]: 
            if node not in path: 
                newpath = find_shortest_path(graph, node, end, path) 
                if newpath: 
                    if not shortest or len(newpath) < len(shortest): 
                        shortest = newpath 
        return shortest
