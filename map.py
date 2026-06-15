# map.py
"""
B팀 담당: 맵 설계 및 벽 배치
이 모듈은 게임의 2D 그리드 맵을 절차적으로 생성하고, 벽 배치 상태 조회, 충돌 판정용 유틸리티,
그리고 플레이어 및 적의 스폰 위치를 관리합니다.

매 실행마다 재귀 백트래킹(DFS) 알고리즘을 사용하여 완전히 새로운 미로 구조를 생성합니다.
모든 빈 공간은 서로 연결되어 있음이 보장됩니다.

다른 팀원(A팀: 엔진, C팀: 시스템)과 연동할 수 있도록 인터페이스를 제공합니다.
"""

import random


class Map:
    def __init__(self, width=21, height=21, seed=None):
        """
        절차적으로 미로 맵을 생성합니다.

        Parameters:
            width (int): 맵 가로 크기 (홀수 권장, 짝수면 +1 자동 보정)
            height (int): 맵 세로 크기 (홀수 권장, 짝수면 +1 자동 보정)
            seed (int|None): 랜덤 시드. None이면 매번 다른 맵 생성
        """
        # 미로 생성은 홀수 크기에서 가장 깔끔하게 동작
        if width % 2 == 0:
            width += 1
        if height % 2 == 0:
            height += 1

        self.cols = width
        self.rows = height

        if seed is not None:
            random.seed(seed)

        # 1. 미로 생성
        self.grid = self._generate_maze()

        # 2. 추가 통로 뚫기 (미로가 너무 좁지 않도록 루프 생성)
        self._add_extra_passages(chance=0.3)

        # 3. 스폰 위치 결정 (빈 공간에서 골고루 배치)
        open_cells = self._get_open_cells()

        # 플레이어 스폰: 좌상단 근처의 빈 공간
        self.player_spawn = self._find_spawn_near(open_cells, 1, 1)

        # 적 스폰: 플레이어로부터 충분히 떨어진 5개 위치
        self.enemy_spawns = self._place_enemy_spawns(open_cells, num=5, min_dist=5)

    # ─── 미로 생성 (재귀 백트래킹 / DFS) ─────────────────────────────────────
    def _generate_maze(self):
        """
        재귀 백트래킹 알고리즘으로 미로를 생성합니다.
        모든 벽(1)로 채운 뒤, DFS로 빈 공간(0)을 파서 통로를 만듭니다.
        """
        grid = [[1] * self.cols for _ in range(self.rows)]

        # 미로 시작점 (1, 1) - 반드시 홀수 좌표
        start_col, start_row = 1, 1
        grid[start_row][start_col] = 0

        # 스택 기반 DFS (재귀 깊이 제한 회피)
        stack = [(start_col, start_row)]
        directions = [(0, -2), (0, 2), (-2, 0), (2, 0)]  # 2칸씩 이동

        while stack:
            col, row = stack[-1]
            # 이동 가능한 방향 찾기 (2칸 뒤가 아직 벽인 방향)
            neighbors = []
            for dc, dr in directions:
                nc, nr = col + dc, row + dr
                if 0 < nc < self.cols - 1 and 0 < nr < self.rows - 1:
                    if grid[nr][nc] == 1:  # 아직 방문 안 한 셀
                        neighbors.append((dc, dr, nc, nr))

            if neighbors:
                dc, dr, nc, nr = random.choice(neighbors)
                # 현재 셀과 목표 셀 사이의 벽도 뚫기
                grid[row + dr // 2][col + dc // 2] = 0
                grid[nr][nc] = 0
                stack.append((nc, nr))
            else:
                stack.pop()

        return grid

    def _add_extra_passages(self, chance=0.3):
        """
        미로의 일부 벽을 추가로 뚫어서 루프(순환 경로)를 생성합니다.
        이렇게 하면 FPS 게임에 적합한 넓은 통로와 우회 경로가 만들어집니다.
        """
        for row in range(2, self.rows - 2):
            for col in range(2, self.cols - 2):
                if self.grid[row][col] == 1:
                    # 상하 또는 좌우가 모두 빈 공간이면 뚫을 수 있는 벽
                    if (self.grid[row - 1][col] == 0 and self.grid[row + 1][col] == 0 and
                            self.grid[row][col - 1] == 1 and self.grid[row][col + 1] == 1):
                        if random.random() < chance:
                            self.grid[row][col] = 0
                    elif (self.grid[row][col - 1] == 0 and self.grid[row][col + 1] == 0 and
                            self.grid[row - 1][col] == 1 and self.grid[row + 1][col] == 1):
                        if random.random() < chance:
                            self.grid[row][col] = 0

    # ─── 스폰 위치 결정 ──────────────────────────────────────────────────────
    def _get_open_cells(self):
        """벽이 아닌 모든 빈 셀 좌표를 반환합니다."""
        cells = []
        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col] == 0:
                    cells.append((col, row))
        return cells

    def _find_spawn_near(self, open_cells, target_col, target_row):
        """target 좌표에 가장 가까운 빈 셀의 중앙 월드 좌표를 반환합니다."""
        best = None
        best_dist = float('inf')
        for col, row in open_cells:
            d = abs(col - target_col) + abs(row - target_row)
            if d < best_dist:
                best_dist = d
                best = (col, row)
        if best:
            return (best[0] + 0.5, best[1] + 0.5)
        return (1.5, 1.5)  # 폴백

    def _place_enemy_spawns(self, open_cells, num=5, min_dist=5):
        """
        플레이어 스폰으로부터 최소 min_dist 이상 떨어진 빈 셀 중에서
        서로 충분히 분산된 num개의 스폰 위치를 선정합니다.
        """
        px, py = self.player_spawn

        # 플레이어로부터의 거리순 정렬 (먼 곳 우선)
        candidates = []
        for col, row in open_cells:
            dist = abs(col + 0.5 - px) + abs(row + 0.5 - py)
            if dist >= min_dist:
                candidates.append((col, row, dist))

        # 랜덤하게 골고루 분산 선택하기 위해 셔플
        random.shuffle(candidates)

        spawns = []
        for col, row, _ in candidates:
            # 이미 선정된 스폰과 최소 3칸 이상 떨어져야 함
            too_close = False
            for sx, sy in spawns:
                if abs(col + 0.5 - sx) + abs(row + 0.5 - sy) < 3:
                    too_close = True
                    break
            if not too_close:
                spawns.append((col + 0.5, row + 0.5))
            if len(spawns) >= num:
                break

        # 부족하면 남은 후보에서 채우기
        if len(spawns) < num:
            for col, row, _ in candidates:
                pos = (col + 0.5, row + 0.5)
                if pos not in spawns:
                    spawns.append(pos)
                if len(spawns) >= num:
                    break

        return spawns

    def generate_enemy_spawns(self, num, min_dist=5):
        """
        요청된 개수(num)만큼 새로운 적 스폰 위치를 생성하고 저장합니다.
        """
        open_cells = self._get_open_cells()
        self.enemy_spawns = self._place_enemy_spawns(open_cells, num=num, min_dist=min_dist)
        return self.enemy_spawns

    # ─── 외부 인터페이스 (A팀/C팀 연동) ──────────────────────────────────────
    def get_width(self):
        """맵 그리드의 가로(열) 크기를 반환합니다."""
        return self.cols

    def get_height(self):
        """맵 그리드의 세로(행) 크기를 반환합니다."""
        return self.rows

    def is_out_of_bounds(self, col, row):
        """그리드 좌표가 맵 경계를 벗어났는지 검사합니다."""
        return col < 0 or col >= self.cols or row < 0 or row >= self.rows

    def is_wall(self, x, y):
        """
        월드 좌표 (x, y)가 벽 내부인지 검사합니다.
        A팀원(플레이어 이동 및 레이캐스팅 충돌 판정)이 호출하는 인터페이스입니다.
        """
        col = int(x)
        row = int(y)
        if self.is_out_of_bounds(col, row):
            return True  # 경계 밖은 벽으로 간주
        return self.grid[row][col] > 0

    def get_wall_type(self, col, row):
        """특정 그리드 좌표의 벽 유형(숫자)을 반환합니다. 0은 빈 공간입니다."""
        if self.is_out_of_bounds(col, row):
            return 1
        return self.grid[row][col]

    def get_neighbors(self, col, row):
        """
        경로 탐색(A*)에서 사용하기 위해 특정 그리드 셀의 이동 가능한 (상, 하, 좌, 우) 이웃 셀 리스트를 반환합니다.
        """
        neighbors = []
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        for dc, dr in directions:
            ncol, nrow = col + dc, row + dr
            if not self.is_out_of_bounds(ncol, nrow):
                if self.grid[nrow][ncol] == 0:
                    neighbors.append((ncol, nrow))
        return neighbors

    def print_map(self):
        """디버깅용: 맵을 콘솔에 출력합니다. P=플레이어, E=적 스폰 위치"""
        # 스폰 위치를 그리드 좌표로 변환
        p_col, p_row = int(self.player_spawn[0]), int(self.player_spawn[1])
        e_positions = set()
        for ex, ey in self.enemy_spawns:
            e_positions.add((int(ex), int(ey)))

        for row in range(self.rows):
            line = ""
            for col in range(self.cols):
                if (col, row) == (p_col, p_row):
                    line += "P "
                elif (col, row) in e_positions:
                    line += "E "
                elif self.grid[row][col] == 1:
                    line += "██"
                else:
                    line += "  "
            try:
                print(line)
            except UnicodeEncodeError:
                print(line.replace("██", "##"))
