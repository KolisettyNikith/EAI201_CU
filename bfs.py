
graph = {
    0: [1, 2],
    1: [0, 3, 4],
    2: [0, 5],
    3: [1],
    4: [1, 5],
    5: [2, 4]
}

N = 6                 

visited = [0]*N        
queue = [0]            
visited[0] = 1         

print("BFS Traversal:")


while queue:
    node = queue.pop(0)          
    print(node, end=" ")     

    
    for neighbor in graph[node]:
        if visited[neighbor] == 0:   
            visited[neighbor] = 1  
            queue.append(neighbor)  
