import pygame

class Camera(pygame.sprite.Group):
    def __init__(self, size, *sprites):
        super().__init__(*sprites)

        self.width, self.height = size
        self.screen_center = pygame.Vector2(self.width / 2, self.height / 2)
        self.rect = pygame.Rect((-self.width, -self.height), (3 * self.width, 3 * self.height))

        self.move_speed = 300
        self.scale_speed = 0.6
        self.scale = 1.0

        self.offset = self.screen_center.copy()
        self.center = self.screen_center.copy()
        # 鼠标悬停对象
        self.hover = None
        # 鼠标锁定对象
        self.target = None

        self.color_hover  = 'green'
        self.color_target = 'red'
        self.border = 2

    def center_target(self):
        # 如果有锁定对象，将锁定对象固定到屏幕中央
        if sprite := self.target:
            self.center = sprite.position
            self.offset = self.screen_center.copy()

    def zoom(self, dt, factor):
        self.scale *= 1 + factor * self.scale_speed * dt
        
    def keyboard_control(self, dt, pressed_keys):
        if pressed_keys[pygame.K_UP]:
            self.offset.y -= self.move_speed * dt
        elif pressed_keys[pygame.K_DOWN]:
            self.offset.y += self.move_speed * dt
        if pressed_keys[pygame.K_LEFT]:
            self.offset.x -= self.move_speed * dt
        elif pressed_keys[pygame.K_RIGHT]:
            self.offset.x += self.move_speed * dt
        if pressed_keys[pygame.K_MINUS]:
            self.zoom(dt, -1)
        elif pressed_keys[pygame.K_EQUALS]:
            self.zoom(dt, 1)

    # 判断当前鼠标位置是否与游戏中某个对象重合
    def mouse_pick(self, mouse_pos):
        for sprite in self.sprites():
            pos = self.project2screen(sprite.position)
            rect = sprite.image.get_rect(center = pos)
            if rect.collidepoint(mouse_pos):
                return sprite

    def on_click(self, mouse_pos):
        # 当在游戏对象上点击鼠标时
        if sprite := self.mouse_pick(mouse_pos):
            # 将偏移向量设定为锁定目标当前在屏幕上的位置
            self.offset = self.project2screen(sprite.position)
            # 将摄像机锁定在目标对象上，center 随对象运动而改变
            self.center = sprite.position
            self.target = sprite
        # 当在游戏界面空白（无可选对象）处点击鼠标时
        else:
            # 将摄像机解锁，center 不随对象运动而改变
            self.center = self.center.copy()

    def mouse_control(self, dt, mouse_pos, pressed_buttons):
        # 刷新鼠标悬停对象
        if sprite := self.mouse_pick(mouse_pos):
            self.hover = sprite
        else:
            self.hover = None

        if True in pressed_buttons:
            # 鼠标拖拽
            self.offset += pygame.Vector2(pygame.mouse.get_rel())
        else:
            self.mouse_push(dt, mouse_pos)

    def mouse_push(self, dt, mouse_pos):
        padding = 5

        left = padding
        right = self.width - padding
        top = padding
        bottom = self.height - padding

        mouse_out = pygame.Vector2(mouse_pos)
        x_in = max(left, min(mouse_out.x, right))
        y_in = max(top,  min(mouse_out.y, bottom))
        mouse_in = pygame.Vector2(x_in, y_in)

        movement = mouse_out - mouse_in
        try:
            movement.scale_to_length(self.move_speed * dt)
        except:
            pass
        finally:
            self.offset -= movement

    def draw(self, screen):
        sequence = []
        for sprite in self.sprites():

            # 游戏对象进行相应缩放
            sprite.scale_image(self.scale)

            pos = self.project2screen(sprite.position)
            rect = sprite.image.get_rect(center = pos)
            if self.rect.colliderect(rect):
                sequence.append((sprite.image, rect))
        screen.blits(sequence)

        # 鼠标悬停对象周围绘制绿框
        if sprite := self.hover:
            pos = self.project2screen(sprite.position)
            rect = sprite.image.get_rect(center = pos)
            pygame.draw.ellipse(screen, self.color_hover, rect.inflate(self.border * 2, self.border * 2), self.border)

        # 鼠标锁定对象周围绘制红框
        if sprite := self.target:
            # 判断锁定对象是否被移除
            if sprite in self.sprites():
                pos = self.project2screen(sprite.position)
                rect = sprite.image.get_rect(center = pos)
                pygame.draw.ellipse(screen, self.color_target, rect.inflate(self.border * 2, self.border * 2), self.border)
            else:
                self.target = None

    def project2screen(self, pos):
        return (pos - self.center) * self.scale + self.offset

    def project2real(self, pos):
        pos = pygame.Vector2(pos)
        return (pos - self.offset) / self.scale + self.center

    def update(self, dt, mouse_pos, pressed_keys, pressed_buttons):
        self.keyboard_control(dt, pressed_keys)
        self.mouse_control(dt, mouse_pos, pressed_buttons)
