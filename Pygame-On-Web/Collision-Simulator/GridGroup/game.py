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

    def generate(self, max_radius, groups, grid):

        """ 生成一个随机粒子

        generate(groups)

        生成粒子的 位置、速度、半径、密度均随机。

        """

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

        debug = Debug(screen)

        # 初始化游戏时钟（clock），由于控制游戏帧率
        clock = pygame.time.Clock()

        max_radius = 5

        particles = pygame.sprite.Group()
        grid = GridGroup(max_radius * 2)
        self.generate(max_radius, [particles, grid], grid)
        total_num = 1

        # 游戏运行控制变量（gamen_running）
        # True：游戏运行
        # False：游戏结束
        game_running = True
        gridding = False
        # 游戏主循环
        while game_running:
            # 按照给定的 FPS 刷新游戏
            # clock.tick() 函数返回上一次调用该函数后经历的时间，单位为毫秒 ms
            # dt 记录上一帧接受之后经历的时间，单位为秒 m
            # 使用 dt 控制物体运动可以使游戏物理过程与帧率无关
            dt = clock.tick(self.FPS) / 1000.0
            # 使用 asyncio 同步
            # 此外游戏主体代码中不需要再考虑 asyncio
            await asyncio.sleep(0)

            # 游戏事件处理
            # 包括键盘、鼠标输入等
            for event in pygame.event.get():
                # 点击关闭窗口按钮或关闭网页
                if event.type == pygame.QUIT:
                    game_running = False
                # 按 P 键添加一个随机粒子
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        total_num += 100
                        for i in range(100):
                            self.generate(max_radius, [particles, grid], grid)
                    if event.key == pygame.K_g:
                        gridding = not gridding

            # 以背景色覆盖刷新游戏界面
            screen.fill(screen_color)

            if gridding or total_num > 801:
                grid.update(dt)
                grid.draw(screen)
                debug.debug("Gridding", 'red', 'topright')
            else:
                list_particles = particles.sprites()
                # 每对粒子都进行碰撞检测
                for i, p1 in enumerate(list_particles):
                    # 每对粒子仅进行一次碰撞检测
                    for p2 in list_particles[i+1:]:
                        p1.collide(p2)

                # 调用 Group 类的 update() 函数，更新粒子状态
                particles.update(dt)
                # 调用 Group 类的 draw() 函数，绘制粒子
                particles.draw(screen)

            # 调用 debug 函数在游戏界面上方中间显示粒子个数
            debug.debug(total_num, 'white', 'midtop')
            # 调用 debug 函数在游戏界面左上角显示游戏帧率
            debug.debug(f"{clock.get_fps():.1f}", 'green')

            # 将游戏界面内容输出至屏幕
            pygame.display.update()

        # 当 game_running 为 False 时，
        # 跳出游戏主循环，退出游戏
        pygame.quit()
