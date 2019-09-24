# Pathfinding Simulator

## 업데이트

- Cell.trace 초기화 안되던 버그 수정
- 일시정지 시 생기던 시간 측정 오류 개선

- pathfinding.py 에서 알고리즘 함수들 분리해 algorithms.py 에 저장
- 각종 상수들 constants.py 에 저장
- 주석 처리

## 설치 / 실행

```sh
pip3 install pygame

python3 pathfinding.py
```

## 소스 설명

/ Pathfinding_Simulator

... [pathfinding.py](pathfinding.py)

## 사용 매뉴얼

### 스크린

- 빈 상자(흰색)를 좌클릭 하거나 드래그하면 벽(회색)이 생깁니다.
- 벽(회색)을 다시 좌클릭 하거나 드래그하면 벽이 없어집니다.
- 시작점(초록색)이나 끝점(빨간색)을 드래그 하면 이동시킬 수 있습니다.
- ESE 키를 누르면 칠한 벽이 모두 사라집니다.

- 시작점과 끝점과 벽을 설정 후 스페이스 바를 누르면 길찾기가 시작됩니다.
- 길찾기가 성공적으로 완료되면 노란색 선이 가장 빠른 경로를 알려줍니다.
- 길찾기에 실패하면 더이상 진행되지 않습니다.
- 다시 스페이스바를 누르면 리셋되고 다시 설정을 할 수 있습니다.

### 모듈 활용

- pathfinding.py 의 Cell, Simulator 객체를 임포트합니다.
- Simulator를 상속받아 새로운 시뮬레이터 객체를 정의하고 초기화 합니다.
- 시뮬레이터 객체에 run 메서드를 재정의하여 다른 길찾기 알고리즘을 적용합니다.
- 상세한 변수 설명은 추후 업데이트 하겠습니다.

## 업데이트 예정

- 알고리즘 추가 (Best-First-Search, IDA*, Jump Point Search...)
- 패널 UI 개선
- 화면에 시간 표시
- 대각선 탐색 추가

## 참고 링크

[pygame docs](https://www.pygame.org/docs/)

[PathFinding.js](https://qiao.github.io/PathFinding.js/visual/)