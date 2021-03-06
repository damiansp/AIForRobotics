# Define a function, search() that returns a list in the form of:
# [optimal path length, row, col].
# For the grid shown below, function should output [11, 4, 5].
#
# If there is no valid path from the start point to the goal, function returns
# 'fail'
# ----------

# Grid format:
#   0 = Navigable space
#   1 = Occupied space (wall/barrier)

grid = [[0, 0, 1, 0, 0, 0],
        [0, 0, 1, 0, 0, 0],
        [0, 0, 0, 0, 1, 0],
        [0, 0, 1, 1, 1, 0],
        [0, 0, 0, 0, 1, 0]]
init = [0, 0]
goal = [len(grid) - 1, len(grid[0]) - 1]
cost = 1 # per movement

# Moves
delta = [[-1,  0], # go up
         [ 0, -1], # go left
         [ 1,  0], # go down
         [ 0,  1]] # go right

delta_name = ['^', '<', 'v', '>']

def search(grid, init, goal, cost):
    closed = [[0 for row in range(len(grid[0]))] for col in range(len(grid))]
    closed[init[0]][init[1]] = 1

    x = init[0]
    y = init[1]
    g = 0

    open = [[g, x, y]]

    found = False # True if goal reached
    resign = False # True if no reachable state is the goal state

    while not found and not resign:
        # check if still elements in open
        if len(open) == 0:
            resign = True
            print 'fail'
            return

        # remove node from list
        open.sort()
        open.reverse()
        next = open.pop()
        x = next[1]
        y = next[2]
        g = next[0]

        # Check if goal
        if x == goal[0] and y == goal[1]:
            found == True
            print next
            return next

        # Expand current best element andd add to open
        for i in range(len(delta)):
            x2 = x + delta[i][0]
            y2 = y + delta[i][1]

            # check that position is in bounds
            if x2 >= 0 and x2 < len(grid) and y2 >= 0 and y2 < len(grid[0]):
                # check that state not already visited and not a barrier
                if closed[x2][y2] == 0 and grid[x2][y2] == 0:
                    g2 = g + cost
                    open.append([g2, x2, y2])
                    closed[x2][y2] = 1

search(grid, init, goal, cost)
