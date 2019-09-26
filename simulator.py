import pygame
import sys
import time

import algorithms
from constants import *

pygame.init()
pygame.display.set_caption('Pathfinding Simulation')


class Cell(object):
    def __init__(self, x_idx, y_idx):
        self.pos = x_idx, y_idx  # 셀의 위치 값(튜플)
        self.color = COLOR_WHITE  # 셀의 색깔 겸 시작점/끝점/벽/빈공간의 역할
        self.prev = None  # # 이전 셀의 위치 값, 최단경로(Simulator.path) 계산할 때 사용

    def __lt__(self, other):  # 힙정렬 시 에러 방지용 메서드
        return False
        
    def __repr__(self):  # print 될 때 색 출력
        return str(self.pos)


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
        self.path = list()
        self.start_cell = self.cells_plane[1 - 1][1 - 1]
        self.end_cell = self.cells_plane[self.width_cnt - 1][self.height_cnt - 1]
        self.delta = WITHOUT_DIAGONAL
        # self.delta = WITH_DIAGONAL
        self.status = 'wait'
        self.prev_cells = set()
        self.next_cells = set()
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
                            cell.prev = None
                    self.path.clear()
                    self.debug_list.clear()

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

                    # 마우스 좌클릭 해체
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

            # 일시정지 중이거나 완료됐을 때
            elif self.status in ('pause', 'complete') and e_type in {MOUSEBUTTONDOWN, MOUSEMOTION, MOUSEBUTTONUP}:
                x, y = e_dict['pos']
                x_idx, y_idx = x // self.cell_size, y // self.cell_size
                self.debug_list.clear()

                # 마우스가 보드 안
                if x < self.width_board:
                    cell = self.cells_plane[y_idx][x_idx]

                    # 디버그 정보 추가
                    if self.mode == 'BFS':
                        self.debug_list.append(((x, y), 'pos', cell.pos))
                        self.debug_list.append(((x, y), 'prev', cell.prev))
                    elif self.mode == 'A*':
                        self.debug_list.append(((x, y), 'pos', cell.pos))
                        self.debug_list.append(((x, y), 'prev', cell.prev))
                        self.debug_list.append(((x, y), 'F', cell.f))
                        self.debug_list.append(((x, y), 'G', cell.g))
                        self.debug_list.append(((x, y), 'H', cell.h))
                    elif self.mode == 'Dijkstra':
                        self.debug_list.append(((x, y), 'pos', cell.pos))
                        self.debug_list.append(((x, y), 'prev', cell.prev))
                        self.debug_list.append(((x, y), 'dist', cell.dist))

            # 실행 중일 때 ESC
            elif self.status == 'run' and e_type == KEYUP and e_dict['key'] == K_ESCAPE:
                # 대기 중 상태로 전환 및 초기화
                self.status = 'wait'
                for cell in self.cells_flatten:
                    if cell.color in {COLOR_LIGHT_GREEN, COLOR_LIGHT_BLUE}:
                        cell.color = COLOR_WHITE
                        cell.trace = list()
                self.path.clear()
                self.debug_list.clear()

    def ready(self):
        '''
        알고리즘 실행 전 설정
        '''
        args = self.cells_plane, self.start_cell, self.end_cell, self.delta

        if self.mode == 'BFS':
            init_func = algorithms.BFS_init
        elif self.mode == 'A*':
            init_func = algorithms.Astar_init
        elif self.mode == 'Dijkstra':
            init_func = algorithms.dijkstra_init

        self.data, self.func = init_func(*args)
        self.status = 'run'
        self.start_time = time.time()  # 시간 측정 시작

    def run(self):
        '''
        알고리즘 실행
        '''
        # 알고리즘 함수의 자료구조에서 Cell 인스턴스 찾기
        # 자료구조 요소가 iterable 이면 Cell 인스턴스가 있는 인덱스 찾기
        if hasattr(self.data[0], '__iter__'):
            for idx, element in enumerate(self.data[0]):
                if isinstance(element, Cell):
                    break
        # 자료구조 요소가 iterable이 아니면 idx를 None으로 초기화
        else:
            idx = None

        # prev_cells 에 함수 실행 전 자료구조 상태 저장
        # next_cells 에 함수 실행 후 자료구조 상태 저장
        if idx is None:
            self.prev_cells = set(self.data)
            status = self.func()
            self.next_cells = set(self.data)
        else:
            self.prev_cells = {data[idx] for data in self.data}
            status = self.func()
            self.next_cells = {data[idx] for data in self.data}

        # 자료구조에서 제거된(확인된) cell 은 파란 색으로 색칠
        for cell in self.prev_cells - self.next_cells:
            cell.color = COLOR_LIGHT_BLUE
        # 자료구조에 추가된(확인할) cell 은 초록 색으로 색칠
        for cell in self.next_cells - self.prev_cells:
            cell.color = COLOR_LIGHT_GREEN
        self.prev_cells = self.next_cells

        # 상태 업데이트
        if status:
            self.status = status

        # 최단 경로 계산
        self.path = []
        target = self.end_cell
        while target:
            self.path.append(target.pos)
            target = target.prev

    def complete(self):
        '''
        알고리즘 실행 후 처리
        '''
        if self.start_time:  # 알고리즘 실행 끝난 후 한 번만 통과
            self.end_time = time.time()  # 시간 측정 종료
            print('Time: {:.2f} s'.format(self.end_time - self.start_time))
            self.start_time = 0.
            self.end_time = 0.

            # self.path의 인덱스 값을 실제 픽셀단위 위치로 변환
            idx_to_len = lambda idx: self.cell_size * idx + self.cell_size // 2
            self.path = [tuple(map(idx_to_len, (idx_x, idx_y))) for idx_x, idx_y in self.path]

            self.prev_cells, self.next_cells = {}, {}

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


if __name__ == '__main__':
    simulator = Simulator()

    simulator.exec()  # 시뮬레이터 실행
