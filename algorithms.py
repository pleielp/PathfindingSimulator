from collections import deque
import heapq

import constants


def BFS_init(cells, start, end, delta):
    BFS_queue = deque([start])

    def BFS():
        height, width = len(cells), len(cells[0])
        cell = BFS_queue.popleft()
        x, y = cell.pos

        for dx, dy in delta:
            new_x = x + dx
            new_y = y + dy

            if -1 < new_x < width and -1 < new_y < height:
                new_cell = cells[new_y][new_x]
                if new_cell.color == constants.COLOR_WHITE:
                    BFS_queue.append(new_cell)
                    new_cell.prev = cell
                elif new_cell.color == constants.COLOR_RED:
                    new_cell.prev = cell
                    return "complete"

        if not BFS_queue:
            return "complete"

    return BFS_queue, BFS


def Astar_init(cells, start, end, delta):
    #  A* 알고리즘을 위한 g, h, f 값 초기화
    for column in cells:
        for cell in column:
            cell.g, cell.h, cell.f = 0, 0, 0
    Astar_heap = [(start.g, start)]

    def Astar():
        height, width = len(cells), len(cells[0])
        _, cell = heapq.heappop(Astar_heap)
        x, y = cell.pos

        for dx, dy in delta:
            new_x = x + dx
            new_y = y + dy

            if -1 < new_x < width and -1 < new_y < height:
                new_cell = cells[new_y][new_x]
                if new_cell.color == constants.COLOR_WHITE:
                    if all(
                        [
                            (new_x, new_y) != other_cell.pos
                            for _, other_cell in Astar_heap
                        ]
                    ):
                        new_cell.g = cell.g + 1
                        new_cell.h = (new_x - end.pos[0]) ** 2 + (
                            new_y - end.pos[1]
                        ) ** 2  # euclidian
                        new_cell.f = new_cell.g + new_cell.h
                        heapq.heappush(Astar_heap, (new_cell.f, new_cell))
                        new_cell.prev = cell
                elif new_cell.color == constants.COLOR_RED:
                    new_cell.prev = cell
                    return "complete"

        if not Astar_heap:
            return "complete"

    return Astar_heap, Astar


def dijkstra_init(cells, start, end, delta):
    for column in cells:
        for cell in column:
            cell.dist = (
                0 if cell == start else float("inf")
            )  # Dijkstra 알고리즘을 위한 dist 값 초기화
            cell.prev = None  # Dijkstra 알고리즘을 위한 prev 값 초기화
    dijkstra_heap = [(start.dist, start)]

    def dijkstra():
        height, width = len(cells), len(cells[0])
        heapq.heapify(dijkstra_heap)
        _, cell = heapq.heappop(dijkstra_heap)
        x, y = cell.pos

        for dx, dy in delta:
            new_x = x + dx
            new_y = y + dy

            if -1 < new_x < width and -1 < new_y < height:
                new_cell = cells[new_y][new_x]
                if new_cell.color == constants.COLOR_WHITE:
                    alt = cell.dist + 1
                    if alt < new_cell.dist:
                        new_cell.dist = alt
                        new_cell.prev = cell
                        heapq.heappush(dijkstra_heap, (new_cell.dist, new_cell))
                elif new_cell.color == constants.COLOR_RED:
                    target = end
                    target.prev = cell
                    dijkstra.path = list()
                    while target:
                        dijkstra.path.append(target.pos)
                        target = target.prev
                    return "complete"

        if not dijkstra_heap:
            return "complete"

    return dijkstra_heap, dijkstra
