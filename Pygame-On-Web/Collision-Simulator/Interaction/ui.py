import pygame

class UIGroup(pygame.sprite.Group):
    def __init(self, *sprites):
        super().__init__(*sprites)

    def on_click(self, pos, *args, **kwargs):
        # 依次调用所有 UI 组件的 on_click() 命令，
        # 判断鼠标点击坐标是否位于组件响应区域之内
        for sprite in self.sprites():
            sprite.on_click(pos, *args, **kwargs)

class Widget(pygame.sprite.Sprite):
    def __init__(self, info, keys, groups):
        super().__init__(groups)

        self.info = str(info)
        self.pykey = eval("pygame.K_" + keys.lower())

        self.reactions = ['disable', 'normal', 'active']
        self.is_available = True
        self.is_active = False

        self.font = pygame.font.Font(None, 30)
        
        self.padding = 2
        self.margin  = 2

    def func(self, *args, **kwargs):
        pass

    def text_surf(self, text, color):
        surf = self.font.render(text, True, color)
        return self.pad_surf(surf)

    def pad_surf(self, inner_surf):
        size = (inner_surf.get_width()  + 2 * self.padding, 
                inner_surf.get_height() + 2 * self.padding)
        surf = pygame.Surface(size)
        surf.set_colorkey('black')
        surf.blit(inner_surf, ((self.padding, self.padding), inner_surf.get_size()))

        return surf

    def arrange_surfs(self, surfs, active_id = -1):
        height = max([surf.get_height() for surf in surfs]) + 2 * self.margin
        
        x = 0
        rects = []
        for surf in surfs:
            x += self.margin
            # 竖直居中对齐
            rects.append(surf.get_rect(midleft = (x, height / 2)))
            x = rects[-1].right + self.margin
        width = x
        
        surf = pygame.Surface((width, height))
        surf.set_colorkey('black')
        surf.blits(zip(surfs, rects))

        if active_id < 0:
            return surf, surf.get_rect().copy()
        else:
            return surf, rects[active_id]

    def align_active(self, offset):
        self.active_rect.x += self.rect.x
        self.active_rect.y += self.rect.y
        self.active_rect.inflate_ip(-2 * offset, -2 * offset)

    def update(self, pos, pressed):
        if pressed[self.pykey] or self.active_rect.collidepoint(pos):
            self.is_active = True
        else:
            self.is_active = False

    def on_click(self, pos, *args, **kwargs):
        if self.active_rect.collidepoint(pos):
            self.func(*args, **kwargs)

class Switch(Widget):
    def __init__(self, info, position, keys, groups):
        super().__init__(info, keys, groups)

        self.is_on = False

        self.radius = int(self.font.get_height() / 2)

        self.states = ['off', 'on']

        self.color_text   = {'off': 'gray', 'on': 'white'}
        self.color_switch = {'off': 'red',  'on': 'green'}

        self.color_border = {'off': {'disable': 'gray', 
                                     'normal':  'red', 
                                     'active':  'white'}, 
                             'on':  {'disable': 'gray', 
                                     'normal':  'green', 
                                     'active':  'white'}}
        self.color_slider = {'off': {'disable': 'red', 
                                     'normal':  'gray', 
                                     'active':  'white'}, 
                             'on':  {'disable': 'green', 
                                     'normal':  'gray', 
                                     'active':  'white'}}

        self.images = {}
        for state in self.states:
            self.images[state] = {}
            for react in self.reactions:
                self.images[state][react] = self.init_image(state, react)

        self.rect = self.image.get_rect(topleft = position)
        self.align_active(self.padding)

    @property
    def image(self):
        if self.is_available:
            if self.is_active:
                react = 'active'
            else:
                react = 'normal'
        else:
            react = 'disable'

        if self.is_on:
            state = 'on'
        else:
            state = 'off'

        return self.images[state][react]

    def init_image(self, state, react):
        surfs = []
        surfs.append(self.text_surf(self.info, self.color_text[state]))
        surfs.append(self.init_switch(state, react))

        surf, self.active_rect = self.arrange_surfs(surfs, 1)

        return surf

    def init_switch(self, state, react):
        switch_size = (4 * self.radius, 2 * self.radius)
        switch_surf = pygame.Surface(switch_size)
        switch_surf.set_colorkey('black')
        pygame.draw.rect(switch_surf, self.color_switch[state],        ((0, 0), switch_size), 0, self.radius)
        pygame.draw.rect(switch_surf, self.color_border[state][react], ((0, 0), switch_size), 2, self.radius)

        slider_size = ((self.radius - 1) * 2, (self.radius - 1) * 2)
        slider_surf = pygame.Surface(slider_size)
        slider_surf.set_colorkey('black')
        pygame.draw.ellipse(slider_surf, self.color_slider[state][react], ((0, 0), slider_size))

        slider_rect = slider_surf.get_rect()
        # on: left slider
        if state == 'on':
            slider_rect.midright = (switch_size[0] - 2, switch_size[1] / 2)
        # off: right slider
        else:
            slider_rect.midleft = (2, switch_size[1] / 2)

        switch_surf.blit(slider_surf, slider_rect)

        return self.pad_surf(switch_surf)

    def switch(self):
        if self.is_available:
            self.is_on = not self.is_on

    def func(self, *args, **kwargs):
        self.switch()

class Button(Widget):
    def __init__(self, info, position, func, keys, groups):
        super().__init__(info, keys, groups)

        self.func = func

        self.border_width = 2

        self.color = {'disable': 'gray',
                      'normal':  'gray', 
                      'active':  'white'}

        self.images = {}
        for react in self.reactions:
            self.images[react] = self.init_image(react)

        self.rect = self.image.get_rect(topleft = position)
        self.align_active(self.margin)

    @property
    def image(self):
        if self.is_available:
            if self.is_active:
                react = 'active'
            else:
                react = 'normal'
        else:
            react = 'disable'

        return self.images[react]

    def border_surf(self, inner_surf, color):
        radius = int(inner_surf.get_height() / 2) + self.border_width

        size = (inner_surf.get_width() + 2 * radius, inner_surf.get_height() + 2 * self.border_width)
        surf = pygame.Surface(size)
        surf.set_colorkey('black')

        pygame.draw.rect(surf, color, ((0, 0), size), self.border_width, radius)

        surf.blit(inner_surf, ((radius, self.border_width), inner_surf.get_size()))

        return surf

    def init_image(self, react):
        text_surf = self.text_surf(self.info, self.color[react])
        border_surf = self.border_surf(text_surf, self.color[react])

        surfs = [border_surf]
        surf, self.active_rect = self.arrange_surfs(surfs)

        return surf
