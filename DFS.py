
graph = {
    0: [1, 2],
    1: [0, 6, 4],
    2: [0, 5],
    3: [1],
    4: [1, 5],
    5: [2, 4],
    6: [3 ,4 ,1]
}

N = 7                 



visited = [0]*N
stack = [0]  # start from node 0
visited[0] = 1

print("\nDFS Traversal:")

while stack:
    current = stack.pop()
    print(current, end=" ")  # visit node

    # push neighbors in reverse order for predictable traversal
    for neighbor in reversed(graph[current]):
        if visited[neighbor] == 0:
            visited[neighbor] = 1
            stack.append(neighbor)

