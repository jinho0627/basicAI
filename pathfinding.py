# pathfinding.py
"""
B팀 담당: 적 추적 알고리즘 (A* 경로 탐색)
이 모듈은 2D 그리드 상에서 시작점(적의 그리드 위치)부터 목표점(플레이어의 그리드 위치)까지의
최단 경로를 찾기 위해 A* (A-Star) 알고리즘을 구현합니다.
"""

import heapq
import math

class Node:
    def __init__(self, col, row, g=0, h=0, parent=None):
        self.col = col
        self.row = row
        self.g = g  # 시작점에서 현재 노드까지의 실제 비용
        self.h = h  # 현재 노드에서 목표 노드까지의 예측 비용 (휴리스틱)
        self.f = g + h  # 총 비용 (F = G + H)
        self.parent = parent  # 경로 추적을 위한 부모 노드

    def __lt__(self, other):
        # 우선순위 큐에서 F 값을 기준으로 정렬하기 위한 비교 연산자 정의
        return self.f < other.f

    def __eq__(self, other):
        return self.col == other.col and self.row == other.row

    def __hash__(self):
        return hash((self.col, self.row))


def heuristic(p1, p2):
    """
    맨해튼 거리(Manhattan Distance)를 사용하여 휴리스틱을 계산합니다.
    그리드 맵에서 상하좌우 이동만 가능하므로 맨해튼 거리가 적절합니다.
    """
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])


def a_star(grid_map, start, goal):
    """
    A* 알고리즘을 사용하여 start (col, row)에서 goal (col, row)까지의 최적 경로를 찾습니다.
    
    Parameters:
        grid_map (Map): map.py의 Map 인스턴스 (is_out_of_bounds, get_neighbors 등을 활용)
        start (tuple): 시작 그리드 좌표 (col, row)
        goal (tuple): 목표 그리드 좌표 (col, row)
        
    Returns:
        list of tuple: 목표 지점까지의 그리드 좌표 경로 [(c1, r1), (c2, r2), ...]. 경로를 찾지 못하면 빈 리스트 []를 반환합니다.
    """
    start_col, start_row = start
    goal_col, goal_row = goal

    # 예외 처리: 시작점이나 목표점이 벽이거나 맵 범위를 벗어난 경우
    if grid_map.is_out_of_bounds(start_col, start_row) or grid_map.is_out_of_bounds(goal_col, goal_row):
        return []
    if grid_map.get_wall_type(start_col, start_row) > 0 or grid_map.get_wall_type(goal_col, goal_row) > 0:
        return []

    # 시작점과 목표점이 같으면 경로가 바로 있는 것
    if start == goal:
        return [start]

    # 우선순위 큐로 관리할 Open List
    open_list = []
    # 중복 검사를 위한 Open Set과 Closed Set
    open_set = {}
    closed_set = set()

    # 시작 노드 생성
    start_node = Node(start_col, start_row, g=0, h=heuristic(start, goal))
    heapq.heappush(open_list, start_node)
    open_set[(start_col, start_row)] = start_node

    while open_list:
        # F값이 가장 작은 노드를 큐에서 꺼냅니다.
        current_node = heapq.heappop(open_list)
        curr_pos = (current_node.col, current_node.row)
        
        # open_set에서 제거
        if curr_pos in open_set:
            del open_set[curr_pos]

        # 목표 노드에 도달했는지 확인
        if curr_pos == goal:
            # 부모 노드를 역추적하여 경로를 생성합니다.
            path = []
            curr = current_node
            while curr is not None:
                path.append((curr.col, curr.row))
                curr = curr.parent
            # 경로는 시작점에서 목적지 순이어야 하므로 역순으로 정렬하여 반환
            return path[::-1]

        closed_set.add(curr_pos)

        # 현재 노드의 이동 가능한 이웃 셀 목록을 가져옵니다.
        neighbors = grid_map.get_neighbors(current_node.col, current_node.row)
        
        for ncol, nrow in neighbors:
            n_pos = (ncol, nrow)

            # 이미 닫힌 목록에 있으면 패스
            if n_pos in closed_set:
                continue

            # 이웃으로 이동할 때의 비용 계산 (상하좌우 이동이므로 비용은 1씩 증가)
            tentative_g = current_node.g + 1

            # 이웃이 이미 열린 목록에 있는지 확인
            if n_pos in open_set:
                neighbor_node = open_set[n_pos]
                # 이미 열린 목록에 있는 경로보다 더 저렴한 경로를 발견하면 값 갱신
                if tentative_g < neighbor_node.g:
                    neighbor_node.g = tentative_g
                    neighbor_node.f = tentative_g + neighbor_node.h
                    neighbor_node.parent = current_node
                    # heapq의 최소 힙 정렬 상태가 흐트러질 수 있으므로 재정렬(heapify)을 유도하거나
                    # 그냥 heapq를 재정렬해 줍니다.
                    heapq.heapify(open_list)
            else:
                # 새로운 노드를 생성하여 열린 목록에 추가
                h_val = heuristic(n_pos, goal)
                new_node = Node(ncol, nrow, g=tentative_g, h=h_val, parent=current_node)
                heapq.heappush(open_list, new_node)
                open_set[n_pos] = new_node

    # 경로를 찾을 수 없는 경우 빈 리스트 반환
    return []
