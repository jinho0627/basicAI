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

        # 4. 특수 요소 배치 (비밀의 방, 자동문, 독 함정)
        self.doors = {}
        self.traps = []
        self.items = []
        self._place_special_elements()

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

    def _place_special_elements(self):
        # 1. 비밀의 방 및 비밀문 배치 (막다른 길 중 플레이어/적 스폰 위치가 아닌 곳을 밀폐)
        secret_candidates = []
        p_cell = (int(self.player_spawn[0]), int(self.player_spawn[1]))
        e_cells = [(int(ex), int(ey)) for ex, ey in self.enemy_spawns]
        
        for r in range(1, self.rows - 1):
            for c in range(1, self.cols - 1):
                if self.grid[r][c] == 0:
                    # 막다른 길인지 체크 (이웃한 0 셀이 정확히 1개인 경우)
                    corridor_neighbors = []
                    for dc, dr in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                        tc, tr = c + dc, r + dr
                        if not self.is_out_of_bounds(tc, tr) and self.grid[tr][tc] == 0:
                            corridor_neighbors.append((tc, tr))
                    
                    if len(corridor_neighbors) == 1:
                        room_pos = (c, r)
                        door_pos = corridor_neighbors[0]
                        # 스폰 셀 제외
                        if room_pos != p_cell and room_pos not in e_cells:
                            if door_pos != p_cell and door_pos not in e_cells:
                                secret_candidates.append((room_pos, door_pos))
        
        # 중복 방지를 위해 셔플 후 최대 3개 배치
        random.shuffle(secret_candidates)
        placed_secrets = 0
        for room_pos, door_pos in secret_candidates:
            if placed_secrets >= 3:
                break
            rc, rr = room_pos
            dc, dr = door_pos
            
            # 문이 될 위치가 다른 문이나 벽으로 막히지 않았는지 확인
            if self.grid[dr][dc] == 0:
                self.grid[dr][dc] = 5  # 비밀문 (닫힘)
                
                # 비밀의 방에 아이템 생성 (A+ 또는 학식 중 하나만!)
                item_type = random.choice(['A+', 'H'])
                self.items.append({
                    'x': rc + 0.5,
                    'y': rr + 0.5,
                    'type': item_type
                })
                
                # 문 정보 등록
                self.doors[door_pos] = {
                    'type': 'secret',
                    'state': 'closed',
                    'timer': 0.0,
                    'base_type': 5,
                    'progress': 0.0
                }
                placed_secrets += 1

        # 2. 자동문 배치
        door_candidates = []
        for r in range(2, self.rows - 2):
            for c in range(2, self.cols - 2):
                if self.grid[r][c] == 0:
                    # 플레이어/적 스폰 근처 피하기
                    if (c + 0.5, r + 0.5) == self.player_spawn or (c + 0.5, r + 0.5) in self.enemy_spawns:
                        continue
                    
                    # 통로인지 체크
                    is_passage = False
                    if (self.grid[r][c-1] == 1 and self.grid[r][c+1] == 1 and 
                        self.grid[r-1][c] == 0 and self.grid[r+1][c] == 0):
                        is_passage = True
                    elif (self.grid[r-1][c] == 1 and self.grid[r+1][c] == 1 and 
                          self.grid[r][c-1] == 0 and self.grid[r][c+1] == 0):
                        is_passage = True
                        
                    if is_passage:
                        door_candidates.append((c, r))

        random.shuffle(door_candidates)
        placed_doors = 0
        for c, r in door_candidates:
            if placed_doors >= 4:
                break
            # 문 정보 등록 및 그리드에 자동문(4) 마킹
            self.grid[r][c] = 4
            self.doors[(c, r)] = {
                'type': 'auto',
                'state': 'closed',
                'timer': 0.0,
                'base_type': 4,
                'progress': 0.0
            }
            placed_doors += 1

        # 3. 독 함정 배치
        trap_candidates = []
        for r in range(1, self.rows - 1):
            for c in range(1, self.cols - 1):
                if self.grid[r][c] == 0:
                    # 스폰 위치나 아이템 위치 피하기
                    pos = (c + 0.5, r + 0.5)
                    if pos == self.player_spawn or pos in self.enemy_spawns:
                        continue
                    if any(item['x'] == pos[0] and item['y'] == pos[1] for item in self.items):
                        continue
                    if (c, r) in self.doors:
                        continue
                    
                    # 이웃한 0 셀 개수 검사 (막다른 길이나 외길인지 확인)
                    corridor_neighbors = 0
                    for dc, dr in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                        tc, tr = c + dc, r + dr
                        if not self.is_out_of_bounds(tc, tr) and self.grid[tr][tc] == 0:
                            corridor_neighbors += 1
                    # 길이 하나밖에 없는 곳 (dead-end, corridor_neighbors <= 1) 제외
                    if corridor_neighbors <= 1:
                        continue
                        
                    trap_candidates.append(pos)

        random.shuffle(trap_candidates)
        for i in range(min(len(trap_candidates), 3)):  # 최대 3개 배치
            self.traps.append({
                'x': trap_candidates[i][0],
                'y': trap_candidates[i][1]
            })

    def update_doors(self, player_pos, enemy_manager, dt):
        """
        자동문과 비밀문의 개폐 상태를 업데이트합니다.
        """
        px, py = player_pos
        
        # 살아있는 적들의 위치 수집
        enemy_positions = []
        if enemy_manager:
            enemy_positions = [(e.x, e.y) for e in enemy_manager.get_active_enemies()]
            
        for (c, r), door in self.doors.items():
            door_x = c + 0.5
            door_y = r + 0.5
            
            # 플레이어와의 거리
            dist_to_player = ((door_x - px)**2 + (door_y - py)**2)**0.5
            
            # 적들과의 최소 거리
            dist_to_enemy = float('inf')
            for ex, ey in enemy_positions:
                d = ((door_x - ex)**2 + (door_y - ey)**2)**0.5
                if d < dist_to_enemy:
                    dist_to_enemy = d
                    
            if door['type'] == 'auto':
                # 자동문: 플레이어 또는 적이 사거리(1.5) 이내면 열림
                if dist_to_player < 1.5 or dist_to_enemy < 1.5:
                    if door['state'] == 'closed':
                        door['state'] = 'opening'
                        door['progress'] = 0.0
                    elif door['state'] == 'opening':
                        door['progress'] = min(1.0, door['progress'] + dt * 1.5)  # 약 0.67초 동안 열림
                        if door['progress'] >= 1.0:
                            door['state'] = 'open'
                            self.grid[r][c] = 0  # 통과 가능
                    elif door['state'] == 'open':
                        door['timer'] = 2.0  # 2초 동안 개방 유지
                else:
                    if door['state'] == 'open':
                        door['timer'] -= dt
                        if door['timer'] <= 0:
                            door['state'] = 'closed'
                            self.grid[r][c] = 4  # 다시 닫힘
                            door['progress'] = 0.0
                    elif door['state'] == 'opening':
                        # 문이 열리다 플레이어가 벗어나면 리셋
                        door['state'] = 'closed'
                        door['progress'] = 0.0
                            
            elif door['type'] == 'secret':
                # 비밀문: 플레이어가 아주 가까이(1.5 이내) 붙어야 열림
                if dist_to_player < 1.5:
                    if door['state'] == 'closed':
                        door['state'] = 'opening'
                        door['progress'] = 0.0
                        print("[SECRET] Secret Room Discovered! Door is opening...")
                    elif door['state'] == 'opening':
                        door['progress'] = min(1.0, door['progress'] + dt * 1.5)  # 약 0.67초 동안 열림
                        if door['progress'] >= 1.0:
                            door['state'] = 'open'
                            self.grid[r][c] = 0  # 통과 가능
