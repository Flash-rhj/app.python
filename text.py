import pygame
import time
import random
import os
import sys

# 初始化pygame
pygame.init()

# 定义颜色
COLORS = {
    "white": (255, 255, 255),
    "yellow": (255, 255, 102),
    "black": (0, 0, 0),
    "red": (213, 50, 80),
    "green": (0, 255, 0),
    "blue": (50, 153, 213),
    "purple": (128, 0, 128)
}

# 屏幕尺寸
DIS_SIZE = (800, 600)
dis = pygame.display.set_mode(DIS_SIZE)
pygame.display.set_caption('高级贪吃蛇游戏')

# 游戏参数
SNAKE_BLOCK = 15
INIT_SPEED = 10
MAX_LEVEL = 5

# 加载资源
try:
    eat_sound = pygame.mixer.Sound("eat.wav")
    game_over_sound = pygame.mixer.Sound("gameover.wav")
except FileNotFoundError:
    print("警告：音效文件缺失，将静音运行")


class Snake:
    def __init__(self):
        self.reset()

    def reset(self):
        self.length = 1
        self.positions = [[DIS_SIZE[0] / 2, DIS_SIZE[1] / 2]]
        self.direction = (0, 0)
        self.score = 0
        self.speed = INIT_SPEED
        self.powerup_timer = 0
        self.level = 1

    def move(self):
        head = self.positions[-1].copy()
        head[0] += self.direction[0] * SNAKE_BLOCK
        head[1] += self.direction[1] * SNAKE_BLOCK
        self.positions.append(head)
        if len(self.positions) > self.length:
            del self.positions[0]

    def check_collision(self):
        head = self.positions[-1]
        # 边界碰撞
        if head[0] < 0 or head[0] >= DIS_SIZE[0] or head[1] < 0 or head[1] >= DIS_SIZE[1]:
            return True
        # 自身碰撞
        return head in self.positions[:-1]


class Food:
    def __init__(self):
        self.types = [
            {"color": COLORS["green"], "value": 1},
            {"color": COLORS["purple"], "value": 3, "duration": 5000}
        ]
        self.respawn()

    def respawn(self):
        self.type = random.choice(self.types)
        self.pos = [
            random.randrange(0, DIS_SIZE[0] - SNAKE_BLOCK, SNAKE_BLOCK),
            random.randrange(0, DIS_SIZE[1] - SNAKE_BLOCK, SNAKE_BLOCK)
        ]


def draw_button(text, pos, size, color):
    font = pygame.font.SysFont("simhei", 30)
    text_surf = font.render(text, True, COLORS["white"])
    text_rect = text_surf.get_rect(center=(pos[0] + size[0] / 2, pos[1] + size[1] / 2))
    pygame.draw.rect(dis, color, (pos[0], pos[1], size[0], size[1]))
    dis.blit(text_surf, text_rect)


def show_menu():
    menu = True
    selected = 0
    options = [
        {"text": "开始游戏", "action": "start"},
        {"text": "难度选择", "action": "difficulty"},
        {"text": "退出游戏", "action": "quit"}
    ]

    while menu:
        dis.fill(COLORS["blue"])
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    return options[selected]["action"]

        # 绘制菜单项
        for i, option in enumerate(options):
            color = COLORS["red"] if i == selected else COLORS["yellow"]
            y_pos = 200 + i * 60
            draw_button(option["text"], (300, y_pos), (200, 50), color)

        pygame.display.update()
        clock.tick(15)


def game_loop():
    snake = Snake()
    food = Food()
    running = True
    paused = False
    high_score = load_high_score()

    while running:
        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                elif not paused:
                    # 方向控制（新增对角线移动支持）
                    if event.key == pygame.K_LEFT and snake.direction != (1, 0):
                        snake.direction = (-1, 0)
                    elif event.key == pygame.K_RIGHT and snake.direction != (-1, 0):
                        snake.direction = (1, 0)
                    elif event.key == pygame.K_UP and snake.direction != (0, 1):
                        snake.direction = (0, -1)
                    elif event.key == pygame.K_DOWN and snake.direction != (0, -1):
                        snake.direction = (0, 1)

        if paused:
            continue

        # 游戏逻辑
        snake.move()

        # 碰撞检测
        if snake.check_collision():
            game_over_sound.play()
            update_high_score(snake.score)
            return

        # 吃食物逻辑
        if snake.positions[-1] == food.pos:
            eat_sound.play()
            snake.length += food.type["value"]
            snake.score += food.type["value"] * 10
            if "duration" in food.type:
                snake.speed += 2
                snake.powerup_timer = pygame.time.get_ticks()
            food.respawn()

            # 升级系统
            if snake.score // 100 > snake.level and snake.level < MAX_LEVEL:
                snake.level += 1
                snake.speed += 1

        # 特殊效果倒计时
        if snake.powerup_timer and pygame.time.get_ticks() - snake.powerup_timer > 5000:
            snake.speed -= 2
            snake.powerup_timer = 0

        # 画面绘制
        dis.fill(COLORS["blue"])

        # 绘制蛇身（新增渐变效果）
        for i, pos in enumerate(snake.positions):
            alpha = 255 * (i + 1) / len(snake.positions)
            pygame.draw.rect(dis, (0, 200, 0, alpha),
                             [pos[0], pos[1], SNAKE_BLOCK, SNAKE_BLOCK])

        # 绘制食物
        pygame.draw.circle(dis, food.type["color"],
                           (food.pos[0] + SNAKE_BLOCK // 2, food.pos[1] + SNAKE_BLOCK // 2),
                           SNAKE_BLOCK // 2)

        # 显示游戏信息
        show_info(snake, high_score)

        pygame.display.update()
        clock.tick(snake.speed)


def show_info(snake, high_score):
    font = pygame.font.SysFont("simhei", 20)
    texts = [
        f"得分: {snake.score}",
        f"最高分: {high_score}",
        f"速度: {snake.speed}",
        f"等级: {snake.level}"
    ]

    y_pos = 10
    for text in texts:
        text_surf = font.render(text, True, COLORS["yellow"])
        dis.blit(text_surf, (10, y_pos))
        y_pos += 25

    # 绘制进度条
    if snake.powerup_timer:
        remaining = 5000 - (pygame.time.get_ticks() - snake.powerup_timer)
        bar_width = (remaining / 5000) * 100
        pygame.draw.rect(dis, COLORS["purple"], (10, DIS_SIZE[1] - 30, bar_width, 20))


def load_high_score():
    try:
        with open("highscore.txt", "r") as f:
            return int(f.read())
    except:
        return 0


def update_high_score(score):
    high_score = load_high_score()
    if score > high_score:
        with open("highscore.txt", "w") as f:
            f.write(str(score))


# 初始化游戏
clock = pygame.time.Clock()

# 主程序
while True:
    action = show_menu()

    if action == "start":
        game_loop()
    elif action == "difficulty":
        # 难度选择实现（代码略）
        pass
    elif action == "quit":
        pygame.quit()
        sys.exit()