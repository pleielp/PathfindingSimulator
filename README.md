# Pathfinding Simulator

## 업데이트 (v0.2.2)

- 알고리즘 함수 구조 일부 개선
- 디버그 모드 추가
- 실행파일 이름 변경 (pathfinder.py -> simulator.py)
- 실행 중지 기능 추가

## 설치 / 실행

```sh
pip3 install pygame

python3 simulator.py
```

- 버전 정보
    - OS: Linux Mint 19.1 Cinnamon
    - python: 3.7, 3.6
    - pygame: 1.9.4

__Mac 에서 호환 안되는 경우가 있음__

## 사용 매뉴얼

### 스크린

- 빈 상자(흰색)를 좌클릭 하거나 드래그하면 벽(회색)이 생깁니다.
- 벽(회색)을 다시 좌클릭 하거나 드래그하면 벽이 없어집니다.
- 시작점(초록색)이나 끝점(빨간색)을 드래그 하면 이동시킬 수 있습니다.
- 대기 상태에서 ESE 키를 누르면 칠한 벽이 모두 사라집니다.

- 시작점과 끝점과 벽을 설정 후 스페이스 바를 누르면 길찾기가 시작됩니다.
- 길찾기가 성공적으로 완료되면 노란색 선이 가장 빠른 경로를 알려줍니다.
- 길찾기에 실패하면 더이상 진행되지 않습니다.
- 길 찾기 완료 후 스페이스바를 누르면 대기 상태로 진입하고 다시 설정을 할 수 있습니다.
- 길 찾기 중 스페이스바를 누르면 일시정지 상태로 들어가고 마우스로 각 셀 위를 움직여 셀의 각 변수 상태를 확인할 수 있습니다.
- 길 찾기 중 ESC 키를 누르면 대기 중으로 바로 진입합니다.

### 모듈 활용

- pathfinding.py 의 Cell, Simulator 객체를 임포트합니다.
- Simulator를 상속받아 새로운 시뮬레이터 객체를 정의하고 초기화 합니다.
- 시뮬레이터 객체에 run 메서드를 재정의하여 다른 길찾기 알고리즘을 적용합니다.
- 상세한 변수 설명은 추후 업데이트 하겠습니다.

## 업데이트 예정

- 알고리즘 추가 (IDA*, Jump Point Search...)
- 패널 UI 개선
- 화면에 시간 표시
- 대각선 탐색 추가
- 양방향 탐색 추가
- 디버그 모드 추가
- 알고리즘 함수 구조 추가 개선
- 패키지 계층화

## 참고 링크

[pygame docs](https://www.pygame.org/docs/)

[PathFinding.js](https://qiao.github.io/PathFinding.js/visual/)

[Easy A* (star) Pathfinding](https://medium.com/@nicholas.w.swift/easy-a-star-pathfinding-7e6689c7f7b2)

[위키백과: 데이크스트라 알고리즘](https://ko.wikipedia.org/wiki/%EB%8D%B0%EC%9D%B4%ED%81%AC%EC%8A%A4%ED%8A%B8%EB%9D%BC_%EC%95%8C%EA%B3%A0%EB%A6%AC%EC%A6%98)