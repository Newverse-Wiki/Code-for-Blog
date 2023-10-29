"""pygbag 打包游戏内容时要求游戏以 main.py 为入口

将涉及到与 asyncio 相关的代码均放置在 main.py 中，
后续代码中无序考虑 asyncio 异步处理、等待等问题。

"""

# 网页运行 python 需要引入 asyncio
import asyncio

# 游戏主代码存放在 game.py 中，作为模块引入
from game import Game

# main() 主函数需要由 async 定义
async def main():
    # 游戏主体为 Game 类的实例
    # 初始化时确定游戏界面的尺寸、刷新率
    game = Game((800, 600), FPS = 60)
    # 游戏的主循环（while True）所在函数的调用需有 await
    # 相应的游戏主循环所在函数也需要由 async 定义
    await game.start()

if __name__ == "__main__":
    # 经由 asyncio.run() 调用 main() 主函数
    asyncio.run(main())
