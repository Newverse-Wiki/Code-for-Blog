import pygame

class UIGroup(pygame.sprite.Group):
    def __init(self, *sprites):
        super().__init__(*sprites)

    def on_click(self, mouse_pos):
        # 依次调用所有 UI 组件的 on_click() 命令，
        # 判断鼠标点击坐标是否位于组件响应区域之内
        for sprite in self.sprites():
            sprite.on_click(mouse_pos)

class Widget(pygame.sprite.Sprite):
    def __init__(self, info, keys, groups, *args, **kwargs):
        super().__init__(groups)

        self.info = str(info)
        try:
            self.pykey = eval("pygame.K_" + keys.lower())
        except:
            self.pykey = eval("pygame.K_" + keys.upper())

        self.args = args
        self.kwargs = kwargs

        # 定义组件的响应外观类别
        self.reactions = ['disable', 'normal', 'active']
        # 定义组件的响应状态
        self.is_available = True
        self.is_wakeup = False
        self.is_active = False

        self.font = pygame.font.Font(None, 30)
        
        self.padding = 2
        self.margin  = 2

    def func(self, *args, **kwargs):
        pass

    def text_surf(self, text, color, background = 'black'):
        surf = self.font.render(text, True, color, background)
        return self.pad_surf(surf, background)

    def pad_surf(self, inner_surf, background = 'black'):
        # 为部件显示内容添加内边距 padding
        size = (inner_surf.get_width()  + 2 * self.padding, 
                inner_surf.get_height() + 2 * self.padding)
        surf = pygame.Surface(size)
        #surf.set_colorkey('black')
        surf.fill(background)
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

    def update(self, mouse_pos, pressed_keys, pressed_buttons):
        # 当组件绑定的快捷键被按下或鼠标掠过组件的响应区域
        self.is_wakeup = False
        self.is_active = False
        if pressed_keys[self.pykey]:
            self.is_active = True
        if self.active_rect.collidepoint(mouse_pos):
            self.is_wakeup = True
            if True in pressed_buttons:
                self.is_active = True

    def on_click(self, mouse_pos):
        if self.is_available and self.active_rect.collidepoint(mouse_pos):
            self.func(*self.args, **self.kwargs)

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

    def func(self):
        self.switch()

class Button(Widget):
    def __init__(self, info, position, func, keys, groups, *args, **kwargs):
        super().__init__(info, keys, groups, *args, **kwargs)

        self.func = func

        self.reactions = ['disable', 'normal', 'wakeup', 'active']
        # 定义组件的响应外观类别对应的颜色
        self.color = {'disable': ('black', 'black', 'black'),
                      'normal':  ('gray',  'black', 'gray'), 
                      'wakeup':  ('white', 'black', 'white'), 
                      'active':  ('black', 'white', 'white')}
        self.border = {'disable': 0,
                       'normal':  2,
                       'wakeup':  2,
                       'active':  0}

        # 生成不同响应状态下的组件外观
        self.images = {}
        for react in self.reactions:
            self.images[react] = self.init_image(react)

        self.rect = self.image.get_rect(center = position)
        self.align_active(self.margin)

    # 根据组件的响应状态，渲染不同的组件外观
    @property
    def image(self):
        if self.is_available:
            if self.is_active:
                react = 'active'
            elif self.is_wakeup:
                react = 'wakeup'
            else:
                react = 'normal'
        else:
            react = 'disable'

        return self.images[react]

    def border_surf(self, inner_surf, color, border_width):
        radius = int(inner_surf.get_height() / 2) + self.padding

        size = (inner_surf.get_width() + 2 * radius, inner_surf.get_height() + 2 * self.padding)
        surf = pygame.Surface(size)
        surf.set_colorkey('black')

        pygame.draw.rect(surf, color, ((0, 0), size), border_width, radius)

        surf.blit(inner_surf, (radius, self.padding))

        return surf

    def init_image(self, react):
        text_surf = self.text_surf(self.info, self.color[react][0], self.color[react][1])
        border_surf = self.border_surf(text_surf, self.color[react][2], self.border[react])

        surfs = [border_surf]
        surf, self.active_rect = self.arrange_surfs(surfs)

        return surf

class MouseMove(pygame.sprite.Sprite):
    def __init__(self, position, groups):
        super().__init__(groups)

        self.pos = position

        self.font = pygame.font.Font("VeraMoBd.ttf", 15)
        self.color0 = 'black'
        self.color  = 'gray'
        self.color1 = 'white'
        self.color_ = 'black'

        self.padding = 5

    def mouse_surf(self, pressed_buttons):
        surf = pygame.Surface((15, 19))
        surf.set_colorkey(self.color0)

        rect3 = (0, 7, 15, 12)
        pygame.draw.rect(surf, self.color, rect3, 1, 
                         border_bottom_left_radius  = 7, 
                         border_bottom_right_radius = 7)

        rect0 = (0, 0, 8, 8)
        if pressed_buttons[0]:
            pygame.draw.rect(surf, self.color1, rect0, 0, 
                             border_top_left_radius = 5)
        pygame.draw.rect(surf, self.color, rect0, 1, 
                         border_top_left_radius = 5)

        rect2 = (7, 0, 8, 8)
        if pressed_buttons[2]:
            pygame.draw.rect(surf, self.color1, rect2, 0, 
                             border_top_right_radius = 5)
        pygame.draw.rect(surf, self.color, rect2, 1, 
                         border_top_right_radius = 5)

        rect1 = (5, 4, 5, 8)
        if pressed_buttons[1]:
            pygame.draw.rect(surf, self.color1, rect1, 0, 2)
        else:
            pygame.draw.rect(surf, self.color0, rect1, 0, 2)
        pygame.draw.rect(surf, self.color, rect1, 1, 2)

        return surf

    def arrow_surf(self, key, pressed_keys):

        if pressed_keys[eval("pygame.K_" + key)]:
            color_foreground = self.color0
            color_background = self.color1
            color_border = self.color1
            border = 2
        else:
            color_foreground = self.color
            color_background = self.color0
            color_border = self.color
            border = 1
        surf0 = self.font.render('>', True, color_foreground, color_background)

        surf1 = pygame.Surface((10, 10))
        surf1.set_colorkey(self.color0)
        surf1.fill(color_background)
        surf1.blit(surf0, surf0.get_rect(center = surf1.get_rect().center))

        match key:
            case "RIGHT": angle = 0
            case "UP":    angle = 90
            case "LEFT":  angle = 180
            case "DOWN":  angle = 270
        surf1 = pygame.transform.rotate(surf1, angle)

        surf2 = pygame.Surface((14, 14))
        surf2.set_colorkey(self.color0)
        surf2.blit(surf1, (2, 2))
        pygame.draw.rect(surf2, color_border, surf2.get_rect(), border, 5)

        return surf2

    def arrows_surf(self, pressed_keys):
        sub_surfs = []
        for keys in ["UP", "DOWN", "LEFT", "RIGHT"]:
            sub_surfs.append(self.arrow_surf(keys, pressed_keys))

        sub_rects = [(12, 0), (12, 24), (0, 12), (24, 12)]

        surf = pygame.Surface((38, 38))
        surf.set_colorkey('black')
        surf.blits(zip(sub_surfs, sub_rects))

        return surf
        
    def update(self, mouse_pos, pressed_keys, pressed_buttons):
        surfs = [self.mouse_surf(pressed_buttons),
                 self.arrows_surf(pressed_keys)]

        height = max([surf.get_height() for surf in surfs]) + 2 * self.padding
        
        x = self.padding
        rects = []
        for surf in surfs:
            rects.append(surf.get_rect(midleft = (x, height / 2)))
            x = rects[-1].right + 10
        width = x
        
        self.image = pygame.Surface((width, height))
        self.image.set_colorkey('black')
        self.image.blits(zip(surfs, rects))
        self.rect = self.image.get_rect(topleft = self.pos)

    def on_click(self, mouse_pos):
        pass
