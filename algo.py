import pygame
from queue import PriorityQueue

W = 800
win = pygame.display.set_mode((W, W))
pygame.display.set_caption("Pathfinder Visualizer")

white = (255, 255, 255)
blk = (0, 0, 0)
red = (255, 0, 0)         
green = (0, 255, 0)      
blue = (0, 0, 255)        
yellow = (255, 255, 0)    
gray = (128, 128, 128)  
purple = (128, 0, 128)    

class Node:
    def __init__(self, r, c, w, total_r):
        self.r = r
        self.c = c
        self.x = self.c * w    
        self.y = self.r * w
        self.color = white
        self.neighs = []
        self.w = w
        self.total_r = total_r

    def get_pos(self):
        return self.r, self.c

    def is_closed(self):
        return self.color == red

    def is_open(self):
        return self.color == green

    def is_barrier(self):
        return self.color == blk

    def is_start(self):
        return self.color == blue

    def is_end(self):
        return self.color == yellow

    def reset(self):
        self.color = white

    def make_start(self):
        self.color = blue

    def make_closed(self):
        self.color = red

    def make_open(self):
        self.color = green

    def make_barrier(self):
        self.color = blk

    def make_end(self):
        self.color = yellow

    def make_path(self):
        self.color = purple

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.w, self.w))

    def update_neighbors(self, grid):
        self.neighs = []

        if self.r < self.total_r - 1 and not grid[self.r + 1][self.c].is_barrier():
            self.neighs.append(grid[self.r + 1][self.c])
        if self.r > 0 and not grid[self.r - 1][self.c].is_barrier():
            self.neighs.append(grid[self.r - 1][self.c])
        if self.c < self.total_r - 1 and not grid[self.r][self.c + 1].is_barrier():
            self.neighs.append(grid[self.r][self.c + 1])
        if self.c > 0 and not grid[self.r][self.c - 1].is_barrier():
            self.neighs.append(grid[self.r][self.c - 1])

        if self.r < self.total_r - 1 and self.c < self.total_r - 1 and not grid[self.r + 1][self.c + 1].is_barrier():
            self.neighs.append(grid[self.r + 1][self.c + 1])

        if self.r < self.total_r - 1 and self.c > 0 and not grid[self.r + 1][self.c - 1].is_barrier():
            self.neighs.append(grid[self.r + 1][self.c - 1])

        if self.r > 0 and self.c < self.total_r - 1 and not grid[self.r - 1][self.c + 1].is_barrier():
            self.neighs.append(grid[self.r - 1][self.c + 1])

        if self.r > 0 and self.c > 0 and not grid[self.r - 1][self.c - 1].is_barrier():
            self.neighs.append(grid[self.r - 1][self.c - 1])

    def __lt__(self, other):
        return False


def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    dx = abs(x1 - x2)
    dy = abs(y1 - y2)
   
    return max(dx, dy)

def reconstruct_path(came_from, curr, draw):
    while curr in came_from:
        curr = came_from[curr]
        curr.make_path()
        draw()

def algo(draw, grid, start, end):
    cnt = 0
    open_set = PriorityQueue()
    open_set.put((0, cnt, start))
    came_from = {}

    g_score = {node: float("inf") for row in grid for node in row}
    g_score[start] = 0

    f_score = {node: float("inf") for row in grid for node in row}
    f_score[start] = h(start.get_pos(), end.get_pos())

    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return 

        curr = open_set.get()[2]
        open_set_hash.remove(curr)

        if curr == end:
            reconstruct_path(came_from, end, draw)
            end.make_end()
            return True

        for neighbor in curr.neighs:
            temp_g_score = g_score[curr] + 1

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = curr
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())

                if neighbor not in open_set_hash:
                    cnt += 1
                    open_set.put((f_score[neighbor], cnt, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()

        draw()

        if curr != start:
            curr.make_closed()

    return False

def make_grid(r, w):
    grid = []
    gap = w // r 

    for i in range(r):
        grid.append([])
        for j in range(r):
            node = Node(i, j, gap, r)
            grid[i].append(node)

    return grid

def draw_grid(win, r, w):
    gap = w // r

    for i in range(r):
        pygame.draw.line(win, gray, (0, i * gap), (w, i * gap))
        for j in range(r):
            pygame.draw.line(win, gray, (j * gap, 0), (j * gap, w))

def draw(win, grid, r, w):
    win.fill(white)

    for row in grid:
        for node in row:
            node.draw(win)

    draw_grid(win, r, w)
    pygame.display.update()

def get_clicked_pos(pos, r, w):
    gap = w // r
    x, y = pos

    col = x // gap
    row = y // gap

    return row, col

def main(win, w):
    r = 50
    grid = make_grid(r, w)

    start = None
    end = None

    run = True
    while run:
        draw(win, grid, r, w)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if pygame.mouse.get_pressed()[0]:  
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, r, w)
                node = grid[row][col]

                if not start and node != end:
                    start = node
                    start.make_start()

                elif not end and node != start:
                    end = node
                    end.make_end()

                elif node != end and node != start:
                    node.make_barrier()

            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, r, w)
                node = grid[row][col]
                node.reset()

                if node == start:
                    start = None
                elif node == end:
                    end = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid)

                    algo(lambda: draw(win, grid, r, w), grid, start, end)

                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(r, w)

    pygame.quit()

if __name__ == "__main__":
    main(win, W)
