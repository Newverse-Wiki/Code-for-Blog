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

        # 定义组件的响应外观类别
        self.reactions = ['disable', 'normal', 'active']
        # 定义组件的响应状态
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
        # 为部件显示内容添加内边距 padding
        size = (inner_surf.get_width()  + 2 * self.padding, 
                inner_surf.get_height() + 2 * self.padding)
        surf = pygame.Surface(size)
        surf.set_colorkey('black')
        surf.blit(inner_surf, ((self.padding, self.padding), inner_surf.get_size()))

        return surf

    def arrange_surfs(self, surfs, active_id = -1):
        """ 将所有部件水平排列，竖直居中绘制到组件平面上

        arrange_surfs(surfs, active_id)

        surfs: 所有部件平面的列表
        active_id: 鼠标响应部件序号，-1 为整个组件
        """

        # 确定组件高度，部件上下边缘间距最小为 margin
        height = max([surf.get_height() for surf in surfs]) + 2 * self.margin
        
        # 确定所有部件位置
        x = self.margin
        rects = []
        for surf in surfs:
            # 竖直居中对齐
            rects.append(surf.get_rect(midleft = (x, height / 2)))
            # 水平间距为 margin
            x = rects[-1].right + self.margin
        # 确定组件宽度
        width = x
        
        surf = pygame.Surface((width, height))
        surf.set_colorkey('black')
        # 同时绘制所有部件
        surf.blits(zip(surfs, rects))

        # 返回组件平面以及鼠标响应区域
        if active_id < 0:
            # 默认鼠标响应区域为整个组件
            return surf, surf.get_rect().copy()
        else:
            # 可指定鼠标响应区域为某个部分
            return surf, rects[active_id]

    def align_active(self, offset):
        # 将响应区域与组件在屏幕上的绘制位置对齐
        self.active_rect.x += self.rect.x
        self.active_rect.y += self.rect.y
        # 消除响应区域的内外边距
        self.active_rect.inflate_ip(-2 * offset, -2 * offset)

    def update(self, pos, pressed):
        # 当组件绑定的快捷键被按下或鼠标掠过组件的响应区域
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

        # 定义开关状态
        self.states = ['off', 'on']

        # 定义不同开关状态以及响应状态下组件的配色
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

        # 绘制不同状态下组件的外观
        self.images = {}
        for state in self.states:
            self.images[state] = {}
            for react in self.reactions:
                self.images[state][react] = self.init_image(state, react)

        self.rect = self.image.get_rect(topleft = position)
        self.align_active(self.padding)

    # 根据组件的响应状态，渲染不同的组件外观
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

        # 定义组件的响应外观类别对应的颜色
        self.color = {'disable': 'gray',
                      'normal':  'gray', 
                      'active':  'white'}

        # 生成不同响应状态下的组件外观
        self.images = {}
        for react in self.reactions:
            self.images[react] = self.init_image(react)

        self.rect = self.image.get_rect(topleft = position)
        self.align_active(self.margin)

    # 根据组件的响应状态，渲染不同的组件外观
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
