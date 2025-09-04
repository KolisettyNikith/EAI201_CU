from collections import deque

# Graph A–L
graph = {
    'a': ['l', 'c'],
    'b': [],
    'c': ['e'],
    'd': ['e'],
    'e': ['h', 'f', 'k'],
    'f': ['g'],
    'g': [],
    'h': ['j'],
    'i': ['d'],
    'j': [],
    'k': [],
    'l': ['a', 'i', 'd', 'b']
}

start = 'a'   # Rat starts at A
goal = input("Enter where to keep the cheese (a–l): ").lower()

queue = deque()
queue.append([start])
visited = set()
path = None

while queue:
    current_path = queue.popleft()
    node = current_path[-1]

    if node == goal:
        path = current_path
        break

    if node not in visited:
        visited.add(node)
        for neighbor in graph[node]:
            new_path = list(current_path)
            new_path.append(neighbor)
            queue.append(new_path)

if path:
    print("\n Rat starts at:", start.upper())
    print(" Cheese is at:", goal.upper())
    print(" Fastest path:", " -> ".join(path).upper())
    print(" Junctions visited:", len(visited))

    print("\nStep by step movement:")
    for step in path:
        print("️ Rat goes to", step.upper())
else:
    print("\nNo path found to the cheese!")
