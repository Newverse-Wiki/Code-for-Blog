""" 调试模块

debug(info, x = 10, y = 10, color = 'white')

将调试信息 info，以字符串格式输出至游戏界面 (x, y) 位置
可以自定义字体颜色 color

"""

# 引入 pygame 模块
import pygame
# 初始化pygame，预定义各种常量
pygame.init()
# 调用 pygame 内置默认字体
font = pygame.font.Font(None, 30)

def debug(info, x = 10, y = 10, color = 'white'):
    # 获取游戏界面
    screen = pygame.display.get_surface()

    # 渲染调试信息
    debug_surf = font.render(str(info), True, color)
    # 给定调试信息输出位置
    debug_rect = debug_surf.get_rect(topleft = (x, y))
    # 将调试信息背景设置为黑色，以覆盖游戏界面中的其他元素
    pygame.draw.rect(screen, 'black', debug_rect)
    # 将调试信息输出至游戏界面
    screen.blit(debug_surf, debug_rect)
