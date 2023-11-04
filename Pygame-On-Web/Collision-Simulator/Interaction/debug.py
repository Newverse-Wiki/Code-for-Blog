# 引入 pygame 模块
import pygame

class Debug:

    """ 调试类：方便在游戏界面输出调试信息

    Debug(screen)

    将调试信息输出至游戏界面 screen

    """

    def __init__(self, screen, padding = 10):
        # 获取游戏界面及其尺寸
        self.screen = screen
        self.width, self.height = screen.get_size()
        
        self.padding = padding

        self.map = {
                'topleft':     (self.padding,              self.padding),
                'midtop':      (self.width / 2,            self.padding),
                'topright':    (self.width - self.padding, self.padding),
                'midleft':     (self.padding,              self.height / 2),
                'center':      (self.width / 2,            self.height / 2),
                'midright':    (self.width - self.padding, self.height / 2),
                'bottomleft':  (self.padding,              self.height - self.padding),
                'midbottom':   (self.width / 2,            self.height - self.padding),
                'bottomright': (self.width - self.padding, self.height - self.padding)}
        
        # 调用 pygame 内置默认字体
        self.font = pygame.font.Font(None, 30)

    def debug(self, info, color = 'white', anchor = 'topleft'):

        """ debug 函数

        debug(info, color = 'white', anchor = 'topleft')

        将调试信息 info，以字符串格式输出至游戏界面
        可以自定义字体颜色 color 和输出位置 anchor

        可选的 anchor 位置有：
        'topleft',    'midtop',    'topright',
        'midleft',    'center',    'midright',
        'bottomleft', 'midbottom', 'bottomright'

        """

        # 渲染调试信息
        debug_surf = self.font.render(str(info), True, color)
        # 给定调试信息输出位置
        anchor_pos = {anchor: self.map[anchor]}
        debug_rect = debug_surf.get_rect(**anchor_pos)
        # 将调试信息背景设置为黑色，以覆盖游戏界面中的其他元素
        pygame.draw.rect(self.screen, 'black', debug_rect)
        # 将调试信息输出至游戏界面
        self.screen.blit(debug_surf, debug_rect)
