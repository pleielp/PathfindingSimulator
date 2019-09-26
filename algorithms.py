from pathfinding import Simulator
from collections import deque
import heapq

from constants import *


def BFS_init(cells, start, end):
    BFS_queue = deque(start)

    @Simulator.test(deque, 'BFS_queue')
    def BFS(BFS_queue, cells, start, end, delta):
        height, width = len(cells), len(cells[0])
        cell = BFS_queue.popleft()
        x, y = cell.pos

        for dx, dy in delta:
            new_x = x + dx
            new_y = y + dy

            if -1 < new_x < width and -1 < new_y < height:
                new_cell = cells[new_y][new_x]
                if new_cell.color == COLOR_WHITE:
                    BFS_queue.append(new_cell)
                    new_cell.trace = cell.trace + [(new_x, new_y)]
                elif new_cell.color == COLOR_RED:
                    BFS.status = 'complete'
                    BFS.path = [start.pos] + cell.trace + [end.pos]

        if not BFS_queue:
            BFS.status = 'complete'

    return BFS_queue, BFS


@Simulator.test(list, 'Astar_heap')
def A_star(Astar_heap, cells, start, end, delta):
    height, width = len(cells), len(cells[0])
    # _, cell = heapq.heappop(heap)
    _, cell = heapq.heappop(Astar_heap)
    x, y = cell.pos
    # cell.color = COLOR_LIGHT_BLUE

    for dx, dy in delta:
        new_x = x + dx
        new_y = y + dy

        if -1 < new_x < width and -1 < new_y < height:
            new_cell = cells[new_y][new_x]
            if new_cell.color == COLOR_WHITE:
                if all([(new_x, new_y) != other_cell.pos for _, other_cell in Astar_heap]):
                    new_cell.color = COLOR_LIGHT_GREEN
                    new_cell.g = cell.g + 1
                    new_cell.h = (new_x - end.pos[0]) ** 2 + (new_y - end.pos[1]) ** 2  # euclidian
                    # new_cell.h = abs(new_x - end.pos[0]) + abs(new_y - end.pos[1])  # manhathan
                    new_cell.f = 10 * new_cell.g + new_cell.h
                    heapq.heappush(Astar_heap, (new_cell.f, new_cell))
                    new_cell.trace = cell.trace + [(new_x, new_y)]
            elif new_cell.color == COLOR_RED:
                A_star.status = 'complete'
                A_star.path = [start.pos] + cell.trace + [end.pos]
                # return status, path

    if not Astar_heap:
        A_star.status = 'complete'
        # path = []
        # return status, path

    # status = 'run'
    # path = []
    # return status, path


def dijkstra(heap, cells, start, end, delta):
    height, width = len(cells), len(cells[0])
    heapq.heapify(heap)
    _, cell = heapq.heappop(heap)
    x, y = cell.pos
    cell.color = COLOR_LIGHT_BLUE

    for dx, dy in delta:
        new_x = x + dx
        new_y = y + dy

        if -1 < new_x < width and -1 < new_y < height:
            new_cell = cells[new_y][new_x]
            if new_cell.color == COLOR_WHITE:
                new_cell.color = COLOR_LIGHT_GREEN
                alt = cell.dist + 1
                if alt < new_cell.dist:
                    new_cell.dist = alt
                    new_cell.prev = cell
                    heapq.heappush(heap, (new_cell.dist, new_cell))
            elif new_cell.color == COLOR_RED:
                target = end
                target.prev = cell
                path = list()
                while target:
                    path.append(target.pos)
                    target = target.prev
                status = 'complete'
                return status, path

    if not heap:
        status = 'complete'
        path = []
        return status, path

    status = 'run'
    path = []
    return status, path