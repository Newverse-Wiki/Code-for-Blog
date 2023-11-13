# 引入 pygame 模块
import pygame
# 引入 asyncio 模块，game.py 中仅需 2 行与之相关的代码
import asyncio
import random
import math

# 引入 debug 模块，方便在游戏界面上输出调试信息
from debug import Debug
from particle import Particle
from grid import GridGroup
from ui import UIGroup, Button, Switch

class Game:

    """Game 类承载游戏主循环

    Game(dims, FPS)

    定义游戏界面的尺寸 dims，游戏帧数 FPS，控制游戏流程

    """

    def __init__(self, dims, FPS = 60):
        self.dims = dims
        self.FPS  = FPS

        # 初始化pygame，预定义各种常量
        pygame.init()

    def generate(self, num, max_radius, groups, grid):

        """ 生成 num 个随机粒子

        generate(groups)

        生成粒子的 位置、速度、半径、密度均随机。

        """

        for i in range(num):
            radius = random.randint(2, max_radius)
            x = random.randint(radius, self.dims[0] - radius)
            y = random.randint(radius, self.dims[1] - radius)

            speed = random.randint(100, 200)
            # 速度方向随机
            angle = random.random() * 2.0 * math.pi
            velocity = (speed * math.cos(angle), speed * math.sin(angle))

            density = random.randint(1, 20)

            grid.add2grid(Particle((x, y), velocity, radius, density, groups))

    # 游戏主循环所在函数需要由 async 定义
    async def start(self):
        # 初始化游戏界面（screen）：尺寸、背景色等
        screen = pygame.display.set_mode(self.dims)
        screen_width, screen_height = self.dims
        screen_color = 'Black'

        debug = Debug(screen, 10)

        # 初始化游戏时钟（clock），由于控制游戏帧率
        clock = pygame.time.Clock()

        max_radius = 5

        particles = pygame.sprite.Group()
        grid = GridGroup(max_radius * 2)
        self.generate(1, max_radius, [particles, grid], grid)

        uis = UIGroup()
        button_plus = Button("+100", (650, 4), self.generate, 'P', uis)
        switch_grid = Switch("Gridding", (1050, 6), 'G', uis)
        mouse_pos = pygame.mouse.get_pos()

        # 游戏运行控制变量（gamen_running）
        # True：游戏运行
        # False：游戏结束
        game_running = True
        switch_grid.is_on = False
        # 游戏主循环
        while game_running:
            # 按照给定的 FPS 刷新游戏
            # clock.tick() 函数返回上一次调用该函数后经历的时间，单位为毫秒 ms
            # dt 记录上一帧接受之后经历的时间，单位为秒 m
            # 使用 dt 控制物体运动可以使游戏物理过程与帧率无关
            dt = clock.tick(self.FPS) / 1000.0
            pygame.display.set_caption(f"Collision Simulation [FPS={clock.get_fps():.1f}]")
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
                        self.generate(100, max_radius, [particles, grid], grid)
                    # 按 G 键切换碰撞检测算法
                    if event.key == pygame.K_g:
                        switch_grid.switch()
                elif event.type == pygame.MOUSEMOTION:
                    # 当鼠标移动时更新鼠标所在位置
                    mouse_pos = event.pos
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    uis.on_click(event.pos, 100, max_radius, [particles, grid], grid)

            # 以背景色覆盖刷新游戏界面
            screen.fill(screen_color)
            
            list_particles = particles.sprites()
            total_num = len(list_particles)
            # 当粒子总数超过 801 时，启用网格算法，禁用算法切换功能
            if total_num > 801:
                switch_grid.is_on = True
                switch_grid.is_available = False
            else:
                switch_grid.is_available = True

            if switch_grid.is_on:
                # 调用 GridGroup 类的 update() 函数，更新粒子状态
                grid.update(dt)
                # 调用 GridGroup 类的 draw() 函数，绘制粒子
                grid.draw(screen)
            else:
                # 每对粒子都进行碰撞检测
                for i, p1 in enumerate(list_particles):
                    # 每对粒子仅进行一次碰撞检测
                    for p2 in list_particles[i+1:]:
                        p1.collide(p2)

                # 调用 Group 类的 update() 函数，更新粒子状态
                particles.update(dt)
                # 调用 Group 类的 draw() 函数，绘制粒子
                particles.draw(screen)

            # 根据鼠标位置和键盘按键信息更新组件的外观渲染
            uis.update(mouse_pos, pygame.key.get_pressed())
            uis.draw(screen)

            # 调用 debug 函数在游戏界面上方中间显示粒子个数
            debug.debug(total_num, 'white', 'midtop')
            # 调用 debug 函数在游戏界面左上角显示游戏帧率
            debug.debug(f"{clock.get_fps():.1f}", 'green')

            # 将游戏界面内容输出至屏幕
            pygame.display.update()

        # 当 game_running 为 False 时，
        # 跳出游戏主循环，退出游戏
        pygame.quit()
