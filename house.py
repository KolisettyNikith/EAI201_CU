import heapq

# 10x10 grid (1 = wall, 0 = open, S = start, G = goal)
grid = [
    ['S',0,0,1,0,0,0,0,0,0],
    [0,1,0,1,0,1,1,1,1,0],
    [0,1,0,0,0,0,0,1,0,0],
    [0,1,1,1,1,1,0,1,0,1],
    [0,0,0,0,0,1,0,1,0,0],
    [1,1,1,1,0,1,0,1,1,0],
    [0,0,0,1,0,0,0,0,1,0],
    [0,1,0,1,1,1,1,0,1,0],
    [0,1,0,0,0,0,0,0,1,'G'],
    [0,0,0,1,1,1,1,0,0,0]
]

# Find start and goal
for i in range(10):
    for j in range(10):
        if grid[i][j]=='S': start=(i,j); grid[i][j]=0
        if grid[i][j]=='G': goal=(i,j); grid[i][j]=0

# ---------------- Greedy BFS ----------------
open_set=[(abs(start[0]-goal[0])+abs(start[1]-goal[1]),start)]
came_from={}
visited=set()

while open_set:
    _,cur=heapq.heappop(open_set)
    if cur==goal: break
    visited.add(cur)
    for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
        nx,ny=cur[0]+dx,cur[1]+dy
        if 0<=nx<10 and 0<=ny<10 and grid[nx][ny]!=1 and (nx,ny) not in visited:
            came_from[(nx,ny)]=cur
            h=abs(nx-goal[0])+abs(ny-goal[1])
            heapq.heappush(open_set,(h,(nx,ny)))

# Reconstruct path
path=[goal]
while path[-1] in came_from: path.append(came_from[path[-1]])
path.reverse()
print("Greedy BFS Path:",path)

# ---------------- A* ----------------
open_set=[(abs(start[0]-goal[0])+abs(start[1]-goal[1]),0,start)]
came_from={}
g_cost={start:0}

while open_set:
    f,g,cur=heapq.heappop(open_set)
    if cur==goal: break
    for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
        nx,ny=cur[0]+dx,cur[1]+dy
        if 0<=nx<10 and 0<=ny<10 and grid[nx][ny]!=1:
            new_g=g+1
            if new_g<g_cost.get((nx,ny),9999):
                came_from[(nx,ny)]=cur
                g_cost[(nx,ny)]=new_g
                h=abs(nx-goal[0])+abs(ny-goal[1])
                heapq.heappush(open_set,(new_g+h,new_g,(nx,ny)))

# Reconstruct path
path=[goal]
while path[-1] in came_from: path.append(came_from[path[-1]])
path.reverse()
print("A* Path:",path)
