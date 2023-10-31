import pygame

class GridGroup(pygame.sprite.Group):
    # 初始化网格群组，网格大小为 box_size
    def __init__(self, box_size, *sprites):
        super().__init__(*sprites)

        self.width, self.height = pygame.display.get_window_size()
        self.size = box_size
        # 计算网格行列数
        self.Nrow = int(self.width  / self.size) + 1
        self.Ncol = int(self.height / self.size) + 1

        self.grid = []
        # 二维网格，每个网格为一个存放粒子的列表
        for row in range(self.Nrow):
            self.grid.append([])
            for col in range(self.Ncol):
                self.grid[row].append([])

    def add2grid(self, sprite):
        # 根据粒子的位置，将粒子放入相应的网格中
        row = int(sprite.position.x / self.size)
        col = int(sprite.position.y / self.size)
        self.grid[row][col].append(sprite)

    def in_grid(self, row, col):
        # 判断行列坐标是否超出网格上下限
        if (row < 0) or (col < 0) or (row >= self.Nrow) or (col >= self.Ncol):
            return False
        else:
            return True

    def regrid(self):
        # 粒子移动之后，进行碰撞检测之前，更新粒子所处的网格
        for row in range(self.Nrow):
            for col in range(self.Ncol):
                box = self.grid[row][col]
                # outside 列表存放离开网格的粒子
                outside = []
                for sprite in box:
                    now_row = int(sprite.position.x / self.size)
                    now_col = int(sprite.position.y / self.size)
                    # 判断粒子是否离开原先的网格
                    if (now_row != row) or (now_col != col):
                        # 不要在 for 循环中增删循环列表中的元素
                        outside.append(sprite)
                        # 更新粒子所处的网格
                        self.grid[now_row][now_col].append(sprite)
                # for 循环结束之后删除离开网格的粒子
                for sprite in outside:
                    box.remove(sprite)

    def collide(self):
        # 只需检测右下方向网格中的粒子
        adjoin = ((1, -1), (1, 0), (1, 1), (0, 1))
        for row in range(self.Nrow):
            for col in range(self.Ncol):
                box = self.grid[row][col]

                for i, p1 in enumerate(box):
                    # 检测同一网格中的粒子
                    for p2 in box[i+1:]:
                        p1.collide(p2)

                    # 检测相邻网格中的粒子
                    for (drow, dcol) in adjoin:
                        next_row = row + drow
                        next_col = col + dcol
                        # 判断行列坐标是否超出网格上下限
                        if self.in_grid(next_row, next_col):
                            next_box = self.grid[next_row][next_col]
                            for p2 in next_box:
                                p1.collide(p2)

    def update(self, dt):
        # 更新粒子位置
        for sprite in self.sprites():
            sprite.update(dt)
        # 更新粒子所处的网格
        self.regrid()
        # 进行碰撞检测和处理
        self.collide()

