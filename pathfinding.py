import pygame
import sys
import time
from collections import deque

import algorithms
from constants import *

pygame.init()
pygame.display.set_caption('Pathfinding Simulation')


class Cell(object):
    def __init__(self, x_idx, y_idx):
        self.pos = x_idx, y_idx  # 셀의 위치 값(튜플)
        self.color = COLOR_WHITE  # 셀의 색깔 겸 시작점/끝점/벽/빈공간의 역할
        self.trace = list()  # 셀의 자취, 최단경로(Simulator.path) 계산할 때 사용

    def __lt__(self, other):  # 힙정렬 시 에러 방지용 메서드
        return False
        
    def __repr__(self):  # print 될 때 색 출력
        return str(self.color)


class Simulator(object):
    data_structure = None

    def __init__(self):
        # 알고리즘 선택 가능 모드
        self.modes = ['BFS', 'A*', 'Dijkstra']
        self.mode = DEFAULT_MODE

        # 보드 크기
        self.cell_size = CELL_SIZE
        self.width_cnt = WIDTH_CNT
        self.height_cnt = HEIGHT_CNT
        self.width_board = self.cell_size * self.width_cnt
        self.height_board = self.cell_size * self.height_cnt

        # 패널 크기
        self.width_panel = WIDTH_PANEL
        self.margin_panel = MARGIN_PANEL
        # 알고리즘 선택 버튼 크기
        self.mode_size = self.width_panel - 2 * self.margin_panel, MODE_HEIGHT
        self.mode_interval = self.mode_size[1] + self.margin_panel

        # 화면 크기
        self.width = self.width_board + self.width_panel
        self.height = self.height_board
        self.screen = pygame.display.set_mode((self.width, self.height))

        # 셀 초기화
        self.cells_plane = [[Cell(x_idx, y_idx) for x_idx in range(self.width_cnt)] for y_idx in range(self.height_cnt)]
        self.cells_flatten = [cell for column in self.cells_plane for cell in column]  # 인덱스 상관없이 모든 요소 순환할 때 요긴함

        # 변수 초기화
        self.queue = deque()
        self.heap = list()
        self.path = list()
        self.start_cell = self.cells_plane[1 - 1][1 - 1]
        self.end_cell = self.cells_plane[self.width_cnt - 1][self.height_cnt - 1]
        self.delta = WITHOUT_DIAGONAL
        # self.delta = WITH_DIAGONAL
        self.status = 'wait'
        self.debug_list = list()

        # 시간
        self.clock = pygame.time.Clock()
        self.start_time = 0.
        self.end_time = 0.
        self.pause_time = 0.

        # 마우스 / 키 입력
        self.dragging = None

    def handle_event(self):
        '''
        마우스 / 키보드 입력 받기
        '''
        for event in pygame.event.get():
            e_type = event.type
            e_dict = event.dict

            # 키보드 F4 도는 우측 상단 X 버튼
            if e_type == QUIT:
                sys.exit()

            # 스페이스 바
            elif e_type == KEYUP and e_dict['key'] == K_SPACE:
                if self.status == 'wait':  # 대기상태 - 준비상태
                    self.status = 'ready'
                elif self.status == 'run':  # 실행 중 - 일시정지
                    self.pause_time = time.time()
                    self.status = 'pause'
                elif self.status == 'pause':  # 일시정지 - 실행 중
                    self.start_time += time.time() - self.pause_time
                    self.status = 'run'
                elif self.status == 'complete':  # 실행 후 - 대기상태 및 초기화
                    self.status = 'wait'
                    for cell in self.cells_flatten:
                        if cell.color in {COLOR_LIGHT_GREEN, COLOR_LIGHT_BLUE}:
                            cell.color = COLOR_WHITE
                            cell.trace = list()
                    self.path.clear()

            # 대기상태 일 때 ESC
            elif self.status == 'wait' and e_type == KEYUP and e_dict['key'] == K_ESCAPE:
                for cell in self.cells_flatten:
                    if cell.color == COLOR_GRAY:  # 벽 없애기
                        cell.color = COLOR_WHITE
            
            # 대기상태 일 때 마우스 입력
            elif self.status == 'wait' and e_type in {MOUSEBUTTONDOWN, MOUSEMOTION, MOUSEBUTTONUP}:
                x, y = e_dict['pos']
                x_idx, y_idx = x // self.cell_size, y // self.cell_size

                # 마우스가 보드 안
                if x < self.width_board:
                    cell = self.cells_plane[y_idx][x_idx]

                    # 마우스 좌클릭
                    if e_type == MOUSEBUTTONDOWN and e_dict['button'] == 1:

                        # 클릭 / 드래그 동안의 상태 self.dragging에 저장
                        if not self.dragging: 
                            if cell.color == COLOR_WHITE:
                                self.dragging = 'create wall'
                            elif cell.color == COLOR_GRAY:
                                self.dragging = 'remove wall'
                            elif cell.color == COLOR_GREEN:
                                self.dragging = 'move start'
                            elif cell.color == COLOR_RED:
                                self.dragging = 'move end'

                        # 벽 / 빈 공간 클릭 시 토글
                        if self.dragging == 'create wall':
                            cell.color = COLOR_GRAY
                        elif self.dragging == 'remove wall':
                            cell.color = COLOR_WHITE

                    # 마우스 드래그(좌클릭)
                    elif e_type == MOUSEMOTION and e_dict['buttons'] == LEFT_CLICK:
                        # 벽 / 빈 공간 드래그 시 토글
                        if self.dragging == 'create wall':
                            cell.color = COLOR_GRAY
                        elif self.dragging == 'remove wall':
                            cell.color = COLOR_WHITE
                        # 시작점 / 끝 점 드래그 시 이동
                        elif self.dragging == 'move start':
                            self.start_cell.color = COLOR_WHITE
                            self.start_cell = self.cells_plane[y_idx][x_idx]
                        elif self.dragging == 'move end':
                            self.end_cell.color = COLOR_WHITE
                            self.end_cell = self.cells_plane[y_idx][x_idx]

                    elif e_type == MOUSEBUTTONUP:
                        self.dragging = None

                # 마우스가 패널 안
                elif x >= self.width_board:
                    # 마우스 좌클릭
                    if e_type == MOUSEBUTTONDOWN and e_dict['button'] == 1:
                        for num, mode in enumerate(self.modes):

                            mode_left = self.width_board + self.margin_panel
                            mode_right = self.width - self.margin_panel
                            mode_top = self.margin_panel + num * self.mode_interval
                            mode_bottom = (num + 1) * self.mode_interval

                            # 알고리즘 선택 버튼 안
                            if mode_left < x < mode_right and mode_top < y < mode_bottom:
                                self.mode = mode  # 모드 설정
                                print('Mode: {}'.format(mode))

            elif self.status in ('pause', 'complete') and e_type in {MOUSEBUTTONDOWN, MOUSEMOTION, MOUSEBUTTONUP}:
                x, y = e_dict['pos']
                x_idx, y_idx = x // self.cell_size, y // self.cell_size
                self.debug_list.clear()

                # 마우스가 보드 안
                if x < self.width_board:
                    cell = self.cells_plane[y_idx][x_idx]

                    if self.mode == 'A*':
                        self.debug_list.append(((x, y), 'F', cell.f))
                        self.debug_list.append(((x, y), 'G', cell.g))
                        self.debug_list.append(((x, y), 'H', cell.h))

    def ready(self):
        '''
        알고리즘 실행 전 설정
        '''
        if self.mode == 'BFS':
            self.data, self.func = algorithms.BFS_init(self.cells_plane)
            # self.queue.append(self.start_cell)
            
        elif self.mode == 'A*':
            for cell in self.cells_flatten:
                cell.g, cell.h, cell.f = 0, 0, 0  #  A* 알고리즘을 위한 g, h, f 값 초기화
            self.heap.append((self.start_cell.g, self.start_cell))

        elif self.mode == 'Dijkstra':
            for cell in self.cells_flatten:
                cell.dist = 0 if cell == self.start_cell else float('inf')  # Dijkstra 알고리즘을 위한 dist 값 초기화
                cell.prev = None                                            # Dijkstra 알고리즘을 위한 prev 값 초기화
            self.heap.append((self.start_cell.dist, self.start_cell))

        self.status = 'run'
        self.start_time = time.time()  # 시간 측정 시작

    def run(self):
        '''
        알고리즘 실행
        '''
        if self.mode == 'BFS':
            # args = self.queue, self.cells_plane, self.start_cell, self.end_cell, self.delta
            args = self.cells_plane, self.start_cell, self.end_cell, self.delta
            # self.status, self.path = algorithms.BFS(*args)
            self.status, self.path = self.func(*args)
            
        elif self.mode == 'A*':
            # args = self.heap, self.cells_plane, self.start_cell, self.end_cell, self.delta
            args = self.cells_plane, self.start_cell, self.end_cell, self.delta
            self.status, self.path = algorithms.A_star(*args)

        elif self.mode == 'Dijkstra':
            args = self.heap, self.cells_plane, self.start_cell, self.end_cell, self.delta
            self.status, self.path = algorithms.dijkstra(*args) 

    def complete(self):
        '''
        알고리즘 실행 후 처리
        '''
        if self.start_time:  # 알고리즘 실행 끝난 후 한 번만 통과
            self.end_time = time.time()  # 시간 측정 종료
            print('Time: {:.2f} s'.format(self.end_time - self.start_time))
            self.start_time = 0.
            self.end_time = 0.

            self.queue.clear()  # 자료구조 초기화
            self.heap.clear()  # 자료구조 초기화

            # self.path의 인덱스 값을 실제 픽셀단위 위치로 변환
            idx_to_len = lambda idx: self.cell_size * idx + self.cell_size // 2
            self.path = [tuple(map(idx_to_len, (idx_x, idx_y))) for idx_x, idx_y in self.path]

    def draw(self):
        '''
        화면에 띄우기
        '''
        # 시작점 / 끝점 칠하기
        self.start_cell.color = COLOR_GREEN
        self.end_cell.color = COLOR_RED

        # 배경 칠하기
        self.screen.fill(COLOR_BLACK)

        # 각 셀들 흰 색으로 칠하기
        rect_size = self.cell_size - 1
        for y_idx, row in enumerate(self.cells_plane):
            for x_idx, cell in enumerate(row):
                rect_pos = tuple(self.cell_size * idx for idx in (x_idx, y_idx))
                rect = pygame.Rect(*rect_pos, rect_size, rect_size) 
                pygame.draw.rect(self.screen, cell.color, rect)

        # 최단 경로선 칠하기
        if self.status == 'complete':
            if self.path and len(self.path) > 1:
                pygame.draw.lines(self.screen, COLOR_YELLOW, False, self.path, 2)

        # 알고리즘 선택버튼 상자 칠하기 / 텍스트 설정
        font = pygame.font.Font(PATH_FONT, 20)
        for num, mode in enumerate(self.modes):
            # 상자 칠하기
            rect_left = self.width_board + self.margin_panel
            rect_top = self.margin_panel + num * (self.mode_size[1] + self.margin_panel)
            rect = pygame.Rect(rect_left, rect_top, *self.mode_size)
            pygame.draw.rect(self.screen, COLOR_GRAY, rect)
            if mode == self.mode:
                pygame.draw.rect(self.screen, COLOR_ORANGE, rect, 2)

            # 텍스트 설정
            font_surface = font.render(mode, True, COLOR_BLACK)
            font_size = font_surface.get_size()
            font_left = self.width_board + (self.width_panel - font_size[0]) / 2
            font_top = self.margin_panel + num * (self.mode_size[1] + self.margin_panel) + (self.mode_size[1] - font_size[1]) / 2
            self.screen.blit(font_surface, (font_left,font_top))

        # 디버그 변수 텍스트 설정
        if self.status in ('pause', 'complete'):
            font = pygame.font.Font(PATH_FONT, 15)
            for num, debug_v in enumerate(self.debug_list): 
            # while self.debug_list:
            #     (debug_x, debug_y), debug_name, debug_value = self.debug_list.pop()
                (debug_x, debug_y), debug_name, debug_value = debug_v
                font_surface = font.render('{}: {}'.format(debug_name, debug_value), True, COLOR_BLACK)
                font_size = font_surface.get_size()
                font_left = debug_x + 15
                font_top = debug_y + num * 15
                self.screen.blit(font_surface, (font_left,font_top))
        
        # 화면에 띄우기
        pygame.display.flip()
        # pygame.display.update()

    def exec(self):
        '''
        시뮬레이터 실행
        '''
        while True:
            self.handle_event()  # 마우스 / 키보드 입력 받기

            if self.status == 'ready':  # 알고리즘 실행 전 설정
                self.ready()
            if self.status == 'run':  # 알고리즘 실행
                self.run()
            if self.status == 'complete':  # 알고리즘 실행 후 처리
                self.complete()

            self.draw()  # 화면에 띄우기

            self.clock.tick(FPS)  # FPS 일정하게 조절

    # 알고리즘 함수 데코레이터
    @classmethod
    def test(cls, ds, ds_name):
        def decorator(f):
            def wrapper(*args):
                # 함수 내 자료구조 초기화
                _, start, _, _ = args
                if not getattr(wrapper, ds_name, None):
                    setattr(wrapper, ds_name, ds([start]))

                # 함수 리턴 값 초기화
                wrapper.status = 'run'
                wrapper.path = []

                # 함수 실행
                f(getattr(wrapper, ds_name), *args)

                # 함수 자료구조 변화에 따라 파란색/초록색 칠하기
                if not getattr(wrapper, 'prev_cells', None):
                    setattr(wrapper, 'prev_cells', {})
                prev_cells = set(getattr(wrapper, 'prev_cells', '{}'))
                next_cells = set(getattr(wrapper, ds_name))

                blue = prev_cells - next_cells
                green = next_cells - prev_cells
                for cell in blue:
                    cell.color = COLOR_LIGHT_BLUE
                for cell in green:
                    cell.color = COLOR_LIGHT_GREEN
                wrapper.prev_cells = next_cells

                # 완료 시 함수 변수 초기화
                if wrapper.status == 'complete':
                    setattr(wrapper, ds_name, None)
                    setattr(wrapper, 'prev_cells', None)
                return wrapper.status, wrapper.path
            return wrapper
        return decorator


if __name__ == '__main__':
    simulator = Simulator()

    simulator.exec()  # 시뮬레이터 실행
