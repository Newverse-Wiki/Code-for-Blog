import pygame

class GridGroup(pygame.sprite.Group):
    def __init__(self, box_size, *sprites):
        super().__init__(*sprites)

        self.width, self.height = pygame.display.get_window_size()
        self.size = box_size
        self.Nrow = int(self.width  / self.size) + 1
        self.Ncol = int(self.height / self.size) + 1

        self.grid = []
        for row in range(self.Nrow):
            self.grid.append([])
            for col in range(self.Ncol):
                self.grid[row].append([])

    def add2grid(self, sprite):
        row = int(sprite.position.x / self.size)
        col = int(sprite.position.y / self.size)
        self.grid[row][col].append(sprite)

    def in_grid(self, row, col):
        if (row < 0) or (col < 0) or (row >= self.Nrow) or (col >= self.Ncol):
            return False
        else:
            return True

    def regrid(self):
        for row in range(self.Nrow):
            for col in range(self.Ncol):
                box = self.grid[row][col]
                outside = []
                for sprite in box:
                    now_row = int(sprite.position.x / self.size)
                    now_col = int(sprite.position.y / self.size)
                    if (now_row != row) or (now_col != col):
                        outside.append(sprite)
                        self.grid[now_row][now_col].append(sprite)
                for sprite in outside:
                    box.remove(sprite)

    def collide(self):
        adjoin = ((1, -1), (1, 0), (1, 1), (0, 1))
        for row in range(self.Nrow):
            for col in range(self.Ncol):
                box = self.grid[row][col]

                for i, p1 in enumerate(box):
                    for p2 in box[i+1:]:
                        p1.collide(p2)

                    for (drow, dcol) in adjoin:
                        next_row = row + drow
                        next_col = col + dcol
                        if self.in_grid(next_row, next_col):
                            next_box = self.grid[next_row][next_col]
                            for p2 in next_box:
                                p1.collide(p2)

    def update(self, dt):
        for sprite in self.sprites():
            sprite.update(dt)

        self.regrid()
        self.collide()

