# 引入 pygame 模块
import pygame
# 引入 asyncio 模块，game.py 中仅需 2 行与之相关的代码
import asyncio
import random
import math

# 引入 debug 模块，方便在游戏界面上输出调试信息
from debug import Debug
from particle import Particle
from group import NebulaGroup
from ui import UIGroup, Button, MouseMove
from camera import Camera

class Game:

    """Game 类承载游戏主循环

    Game(dims, FPS)

    定义游戏界面的尺寸 dims，游戏帧数 FPS，控制游戏流程

    """

    def __init__(self, dims, FPS = 60):
        self.dims = dims
        self.FPS  = FPS

        self.time_shift = 3
        self.time_speeds = (0.125, 0.25, 0.5, 1, 2, 4, 8)

        # 初始化pygame，预定义各种常量
        pygame.init()
        # 初始化游戏界面（screen）：尺寸、背景色等
        pygame.display.set_mode(self.dims)
        self.screen_color = 'Black'

        # 屏幕显示控制和图形绘制
        self.camera = Camera(self.dims)

        self.game_paused = False

        self.total_num = 0

    def generate(self, num, groups):

        """ 生成 num 个随机粒子

        generate(groups)

        生成粒子的 位置、速度、半径、密度均随机。

        """

        for i in range(num):
            # 在当前屏幕范围内随机位置生成粒子
            x = random.randint(5, self.dims[0] - 5)
            y = random.randint(5, self.dims[1] - 5)
            position = pygame.Vector2(x, y)
            # 将屏幕位置投影到实际物理位置
            pos_real = self.camera.project2real(position)

            # 速度大小随机
            speed = random.randint(10, 20)
            # 速度方向随机
            angle = random.random() * 2.0 * math.pi
            velocity = (speed * math.cos(angle), speed * math.sin(angle))

            Particle(pos_real, velocity, 2000, groups)

    def time_control(self, shift):
        self.time_shift += shift
        self.time_shift = max(0, min(self.time_shift, len(self.time_speeds) - 1))

    def game_pause(self):
        self.game_paused = not self.game_paused

    # 游戏主循环所在函数需要由 async 定义
    async def start(self):
        screen = pygame.display.get_surface()
        screen_width, screen_height = screen.get_size()

        debug = Debug(screen, 8)

        # 初始化游戏时钟（clock），用于控制游戏帧率
        clock = pygame.time.Clock()

        nebula = NebulaGroup()
        groups = [nebula, self.camera]
        self.generate(1, groups)
        self.total_num += 1

        uis = UIGroup()
        # 初始化按钮控件
        button_plus  = Button("+10", (screen_width / 2, 60),  
                              self.generate,     'P',      uis, 10, groups)
        button_fast  = Button(">>",  (screen_width / 2 + 80, screen_height - 20), 
                              self.time_control, 'PERIOD', uis, 1)
        button_slow  = Button("<<",  (screen_width / 2 - 80, screen_height - 20), 
                              self.time_control, 'COMMA',  uis, -1)
        button_pause = Button("Run", (screen_width / 2, screen_height - 20), 
                              self.game_pause,   'SPACE',  uis)

        mousemove = MouseMove((1120, 750), uis)
        # 初始化鼠标位置
        mouse_pos = pygame.mouse.get_pos()

        # 游戏运行控制变量（gamen_running）
        # True：游戏运行
        # False：游戏结束
        game_running = True
        # 游戏主循环
        while game_running:
            # 按照给定的 FPS 刷新游戏
            # clock.tick() 函数返回上一次调用该函数后经历的时间，单位为毫秒 ms
            # dt 记录上一帧接受之后经历的时间，单位为秒 m
            # 使用 dt 控制物体运动可以使游戏物理过程与帧率无关
            dt = clock.tick(self.FPS) / 1000.0
            pygame.display.set_caption(f"Nebula Simulator [FPS={clock.get_fps():.1f}]")
            # 使用 asyncio 同步
            # 此外游戏主体代码中不需要再考虑 asyncio
            await asyncio.sleep(0)

            # 游戏事件处理
            # 包括键盘、鼠标输入等
            for event in pygame.event.get():
                # 点击关闭窗口按钮或关闭网页
                if event.type == pygame.QUIT:
                    game_running = False
                elif event.type == pygame.KEYDOWN:
                    # 按 P 键添加随机粒子
                    if event.key == pygame.K_p:
                        self.generate(10, groups)
                    elif event.key == pygame.K_c:
                        self.camera.center_target()
                    elif event.key == pygame.K_COMMA:
                        self.time_control(-1)
                    elif event.key == pygame.K_PERIOD:
                        self.time_control(1)
                    elif event.key == pygame.K_SPACE:
                        self.game_pause()
                elif event.type == pygame.MOUSEMOTION:
                    # 当鼠标移动时更新鼠标所在位置
                    mouse_pos = event.pos
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button < 3:
                        pygame.mouse.get_rel()
                        uis.on_click(event.pos)
                        self.camera.on_click(event.pos)
                elif event.type == pygame.MOUSEWHEEL:
                    self.camera.zoom(dt, event.y)
            pressed_keys = pygame.key.get_pressed()
            pressed_buttons = pygame.mouse.get_pressed(3)

            # 以背景色覆盖刷新游戏界面
            screen.fill(self.screen_color)

            # 调用 NebulaGroup 类的 update() 函数，更新粒子状态
            if not self.game_paused:
                button_pause.is_available = False
                button_fast.is_available = True
                button_slow.is_available = True

                time_speed = self.time_speeds[self.time_shift]
                if time_speed > 1:
                    for i in range(int(time_speed / 2)):
                        nebula.update(dt * 2)
                else:
                    nebula.update(dt * time_speed)
            else:
                button_pause.is_available = True
                button_fast.is_available = False
                button_slow.is_available = False

            # 调用 Camera 类的 update() 和 draw() 函数，绘制粒子
            self.camera.update(dt, mouse_pos, pressed_keys, pressed_buttons)
            self.camera.draw(screen)

            # 根据鼠标位置和键盘按键信息更新组件的外观渲染
            uis.update(mouse_pos, pressed_keys, pressed_buttons)
            uis.draw(screen)

            # 调用 debug 函数在游戏界面上方中间显示粒子个数
            self.total_num = len(nebula.sprites())
            debug.debug(self.total_num, 'white', 'midtop')
            # 调用 debug 函数在游戏界面左上角显示游戏帧率
            debug.debug(f"{clock.get_fps():.1f}", 'green')
            # 调用 debug 函数在游戏界面下方中间显示程序运行速度
            if not self.game_paused:
                debug.debug(f"x {self.time_speeds[self.time_shift]}", 'white', 'midbottom')

            # 将游戏界面内容输出至屏幕
            pygame.display.update()

        # 当 game_running 为 False 时，
        # 跳出游戏主循环，退出游戏
        pygame.quit()
