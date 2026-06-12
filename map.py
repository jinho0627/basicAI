# map.py
"""
B팀 담당: 맵 설계 및 벽 배치
이 모듈은 게임의 2D 그리드 맵을 설계하고, 벽 배치 상태 조회, 충돌 판정용 유틸리티,
그리고 플레이어 및 적의 스폰 위치를 관리합니다.

다른 팀원(A팀: 엔진, C팀: 시스템)과 연동할 수 있도록 인터페이스를 제공합니다.
"""

class Map:
    def __init__(self):
        # 2D 그리드 맵 정의 (1 이상은 벽 종류 번호, 0은 빈 공간)
        # 16 x 16 크기의 예시 맵 구성
        self.grid = [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1],
            [1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1],
            [1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1],
            [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1],
            [1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1],
            [1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1],
            [1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 1, 0, 1],
            [1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 0, 0, 0, 1, 0, 1],
            [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 1, 0, 1, 0, 1],
            [1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1],
            [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        ]
        
        self.rows = len(self.grid)
        self.cols = len(self.grid[0])
        
        # 플레이어 초기 스폰 월드 좌표 (x, y) - 타일의 중심 부근
        self.player_spawn = (1.5, 1.5)
        
        # 적 스폰 월드 좌표 (x, y) 리스트
        self.enemy_spawns = [
            (3.5, 3.5),
            (14.5, 1.5),
            (14.5, 14.5),
            (9.5, 7.5),
            (1.5, 14.5)
        ]

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
            return True # 경계 밖은 벽으로 간주
        return self.grid[row][col] > 0

    def get_wall_type(self, col, row):
        """특정 그리드 좌표의 벽 유형(숫자)을 반환합니다. 0은 빈 공간입니다."""
        if self.is_out_of_bounds(col, row):
            return 1
        return self.grid[row][col]

    def get_neighbors(self, col, row):
        """
        경로 탐색(A*)에서 사용하기 위해 특정 그리드 셀의 이동 가능한 (상, 하, 좌, 우) 이웃 셀 리스트를 반환합니다.
        대각선 이동을 허용하고 싶다면 대각선 셀도 포함시킬 수 있습니다. 여기서는 4방향 이동을 기준으로 합니다.
        """
        neighbors = []
        # 상, 하, 좌, 우 오프셋
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        for dc, dr in directions:
            ncol, nrow = col + dc, row + dr
            if not self.is_out_of_bounds(ncol, nrow):
                if self.grid[nrow][ncol] == 0:  # 벽이 아닌 경우만 통과 가능
                    neighbors.append((ncol, nrow))
        return neighbors
