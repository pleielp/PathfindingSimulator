import pygame
import sys
import time
from collections import deque
import heapq

pygame.init()
pygame.display.set_caption('Pathfinding Simulation')

COLOR_BLACK = 0, 0, 0
COLOR_RED = 255, 0, 0
COLOR_ORANGE = 255, 127, 0
COLOR_YELLOW = 255, 255, 0
COLOR_LIGHT_GREEN = 127, 255, 127
COLOR_GREEN = 0, 255, 0
COLOR_LIGHT_BLUE = 127, 255, 255
COLOR_WHITE = 255, 255, 255
COLOR_GRAY = 127, 127, 127

MOUSEBUTTONDOWN = pygame.MOUSEBUTTONDOWN
MOUSEMOTION = pygame.MOUSEMOTION
MOUSEBUTTONUP = pygame.MOUSEBUTTONUP
KEYUP = pygame.KEYUP
QUIT = pygame.QUIT
K_ESCAPE = pygame.K_ESCAPE 
K_SPACE = pygame.K_SPACE
LEFT_CLICK = (1, 0, 0)


class Cell(object):
    def __init__(self, x_idx, y_idx):
        self.pos = x_idx, y_idx
        self.color = COLOR_WHITE
        self.trace = list()
        self.v = 0

    def __lt__(self, other):
        return self.v < other.v
        
    def __repr(self):
        return str(self.color)


class Simulator(object):
    def __init__(self, mode=''):
        self.modes = ['BFS', 'A*', 'Dijkstra']
        self.mode = mode if mode else self.modes[0]

        self.cell_size = 30
        self.width_cnt = 20
        self.height_cnt = 20
        self.width_board = self.cell_size * self.width_cnt
        self.height_board = self.cell_size * self.height_cnt
        self.width_panel = 150
        self.width = self.width_board + self.width_panel
        self.height = self.height_board
        self.screen = pygame.display.set_mode((self.width, self.height))

        self.cells_plane = [[Cell(x_idx, y_idx) for x_idx in range(self.width_cnt)] for y_idx in range(self.height_cnt)]
        self.cells_flatten = [cell for column in self.cells_plane for cell in column]

        self.start_cell = self.cells_plane[4 - 1][4 - 1]
        self.end_cell = self.cells_plane[17 - 1][17 - 1]
        self.queue = deque()
        self.heap = list()
        self.path = list()
        self.status = 'wait'

        self.clock = pygame.time.Clock()
        self.start_time = 0.
        self.end_time = 0.

        self.dragging = None

        self.delta = ((0, -1), (-1, 0), (0, 1), (1, 0))
        self.delta_diagonal = ((0, -1), (-1, 0), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, 1), (1, -1))

        self.mode_margin = 20
        self.mode_size = self.width_panel - 2 * self.mode_margin, 40
        self.mode_interval = self.mode_size[1] + self.mode_margin

    def handle_event(self):
        for event in pygame.event.get():
            e_type = event.type
            e_dict = event.dict

            if e_type == QUIT:
                sys.exit()

            elif e_type == KEYUP and e_dict['key'] == K_SPACE:
                if self.status == 'wait':
                    self.status = 'ready'
                elif self.status == 'run':
                    self.status = 'pause'
                elif self.status == 'pause':
                    self.status = 'run'
                elif self.status == 'complete':
                    self.status = 'wait'
                    for cell in self.cells_flatten:
                        if cell.color in {COLOR_LIGHT_GREEN, COLOR_LIGHT_BLUE}:
                            cell.color = COLOR_WHITE
                    self.path.clear()

            elif self.status == 'wait' and e_type == KEYUP and e_dict['key'] == K_ESCAPE:
                for cell in self.cells_flatten:
                    if cell.color == COLOR_GRAY:
                        cell.color = COLOR_WHITE
            
            elif self.status == 'wait' and e_type in {MOUSEBUTTONDOWN, MOUSEMOTION, MOUSEBUTTONUP}:
                x, y = e_dict['pos']

                if x < self.width_board:
                    cell = self.cells_plane[y // self.cell_size][x // self.cell_size]

                    if e_type == MOUSEBUTTONDOWN and e_dict['button'] == 1:

                        if not self.dragging: 
                            if cell.color == COLOR_WHITE:
                                self.dragging = 'create wall'
                            elif cell.color == COLOR_GRAY:
                                self.dragging = 'remove wall'
                            elif cell.color == COLOR_GREEN:
                                self.dragging = 'move start'
                            elif cell.color == COLOR_RED:
                                self.dragging = 'move end'

                        if self.dragging == 'create wall':
                            cell.color = COLOR_GRAY
                        elif self.dragging == 'remove wall':
                            cell.color = COLOR_WHITE

                    elif e_type == MOUSEMOTION and e_dict['buttons'] == LEFT_CLICK:

                        if self.dragging == 'create wall':
                            cell.color = COLOR_GRAY
                        elif self.dragging == 'remove wall':
                            cell.color = COLOR_WHITE
                        elif self.dragging == 'move start':
                            self.start_cell.color = COLOR_WHITE
                            self.start_cell = self.cells_plane[y // self.cell_size][x // self.cell_size]
                        elif self.dragging == 'move end':
                            self.end_cell.color = COLOR_WHITE
                            self.end_cell = self.cells_plane[y // self.cell_size][x // self.cell_size]

                    elif e_type == MOUSEBUTTONUP:
                        self.dragging = None

                elif x >= self.width_board:
                    if e_type == MOUSEBUTTONDOWN and e_dict['button'] == 1:
                        for num, mode in enumerate(self.modes):
                            if self.width_board + self.mode_margin < x < self.width - self.mode_margin \
                                and self.mode_margin + num * self.mode_interval < y < (num + 1) * self.mode_interval:
                                self.mode = mode
                                print('Mode: {}'.format(mode))
                                break

    def run(self):
        if self.mode == 'BFS':
            self.BFS()
        elif self.mode == 'A*':
            self.A_star()
        elif self.mode == 'Dijkstra':
            self.dijkstra()

    def BFS(self):
        if self.status == 'ready':
            self.queue.append(self.start_cell)
            self.status = 'run'
            self.start_time = time.time()

        around = self.delta
        cell = self.queue.popleft()
        x, y = cell.pos
        cell.color = COLOR_LIGHT_BLUE

        for dx, dy in around:
            new_x = x + dx
            new_y = y + dy

            if -1 < new_x < self.width_cnt and -1 < new_y < self.height_cnt:
                new_cell = self.cells_plane[new_y][new_x]
                if new_cell.color == COLOR_WHITE:
                    new_cell.color = COLOR_LIGHT_GREEN
                    self.queue.append(new_cell)
                    new_cell.trace = cell.trace + [(new_x, new_y)]
                elif new_cell.color == COLOR_RED:
                    self.status = 'complete'
                    self.path = [self.start_cell.pos] + cell.trace + [self.end_cell.pos]

        if not self.queue:
            self.status = 'complete'

    def A_star(self):
        if self.status == 'ready':
            for cell in self.cells_flatten:
                cell.g, cell.h, cell.f = 0, 0, 0
            self.heap.append((self.start_cell.g, self.start_cell))
            self.status = 'run'
            self.start_time = time.time()

        around = self.delta
        _, cell = heapq.heappop(self.heap)
        x, y = cell.pos
        cell.color = COLOR_LIGHT_BLUE

        for dx, dy in around:
            new_x = x + dx
            new_y = y + dy

            if -1 < new_x < self.width_cnt and -1 < new_y < self.height_cnt:
                new_cell = self.cells_plane[new_y][new_x]
                if new_cell.color == COLOR_WHITE:
                    if all([(new_x, new_y) != other_cell.pos for _, other_cell in self.heap]):
                        new_cell.color = COLOR_LIGHT_GREEN
                        new_cell.g = cell.g + 1
                        new_cell.h = (new_x - self.end_cell.pos[0]) ** 2 + (new_y - self.end_cell.pos[1]) ** 2
                        new_cell.f = new_cell.g + new_cell.h
                        heapq.heappush(self.heap, (new_cell.f, new_cell))
                        new_cell.trace = cell.trace + [(new_x, new_y)]
                elif new_cell.color == COLOR_RED:
                    self.status = 'complete'
                    self.path = [self.start_cell.pos] + cell.trace + [self.end_cell.pos]

        if not self.heap:
            self.status = 'complete'

    def dijkstra(self):
        if self.status == 'ready':
            for cell in self.cells_flatten:
                cell.dist = 0 if cell == self.start_cell else float('inf')
                cell.prev = None
                # self.heap.append((cell.dist, cell))
            self.heap.append((self.start_cell.dist, self.start_cell))
            self.status = 'run'
            self.start_time = time.time()

        around = self.delta
        heapq.heapify(self.heap)
        _, cell = heapq.heappop(self.heap)
        x, y = cell.pos
        cell.color = COLOR_LIGHT_BLUE

        for dx, dy in around:
            new_x = x + dx
            new_y = y + dy

            if -1 < new_x < self.width_cnt and -1 < new_y < self.height_cnt:
                new_cell = self.cells_plane[new_y][new_x]
                if new_cell.color == COLOR_WHITE:
                    new_cell.color = COLOR_LIGHT_GREEN
                    alt = cell.dist + 1
                    if alt < new_cell.dist:
                        new_cell.dist = alt
                        new_cell.prev = cell
                        heapq.heappush(self.heap, (new_cell.dist, new_cell))
                elif new_cell.color == COLOR_RED:
                    target = self.end_cell
                    target.prev = cell
                    while target:
                        self.path.append(target.pos)
                        target = target.prev
                    self.status = 'complete'

        if not self.heap:
            self.status = 'complete'

    def complete(self):
        if self.start_time:
            self.end_time = time.time()
            print('Time: {:.2f} s'.format(self.end_time - self.start_time))
            self.start_time = 0
            self.end_time = 0

            self.queue.clear()
            self.heap.clear()
            idx_to_len = lambda idx: self.cell_size * idx + self.cell_size // 2
            self.path = [tuple(map(idx_to_len, (idx_x, idx_y))) for idx_x, idx_y in self.path]

    def draw(self):
        self.start_cell.color = COLOR_GREEN
        self.end_cell.color = COLOR_RED

        self.screen.fill(COLOR_BLACK)

        rect_size = self.cell_size - 1
        for y_idx, row in enumerate(self.cells_plane):
            for x_idx, cell in enumerate(row):
                rect_pos = tuple(self.cell_size * idx for idx in (x_idx, y_idx))
                rect = pygame.Rect(*rect_pos, rect_size, rect_size) 
                pygame.draw.rect(self.screen, cell.color, rect)

        if self.status == 'complete':
            if self.path and len(self.path) > 1:
                pygame.draw.lines(self.screen, COLOR_YELLOW, False, self.path, 2)

        font = pygame.font.Font('font/gulim.ttf', 20)
        for num, mode in enumerate(self.modes):
            rect_left = self.width_board + self.mode_margin
            rect_top = self.mode_margin + num * (self.mode_size[1] + self.mode_margin)
            rect = pygame.Rect(rect_left, rect_top, *self.mode_size)
            pygame.draw.rect(self.screen, COLOR_GRAY, rect)
            if mode == self.mode:
                pygame.draw.rect(self.screen, COLOR_ORANGE, rect, 2)

            font_surface = font.render(mode, True, COLOR_BLACK)
            font_size = font_surface.get_size()
            font_left = self.width_board + (self.width_panel - font_size[0]) / 2
            font_top = self.mode_margin + num * (self.mode_size[1] + self.mode_margin) + (self.mode_size[1] - font_size[1]) / 2
            self.screen.blit(font_surface, (font_left,font_top))

        pygame.display.flip()

    def exec(self):
        while True:
            self.handle_event()

            if self.status in {'ready', 'run'}:
                self.run()
            if self.status == 'complete':
                self.complete()

            self.draw()

            self.clock.tick(120)


if __name__ == '__main__':
    simulator = Simulator()

    simulator.exec()
