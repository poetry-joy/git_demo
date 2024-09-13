import pygame
import sys
import random

pygame.init()

countdown_duration = 70000

WINDOW_WIDTH, WINDOW_HEIGHT = 420, 750
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('抓肥羊')

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# 加载背景和装饰图像
background_image = pygame.image.load('imgs/ba.jpg')
background_image = pygame.transform.scale(background_image, (WINDOW_WIDTH, WINDOW_HEIGHT))

decorative_image = pygame.image.load('imgs/cute.png')
decorative_image1 = pygame.transform.scale(decorative_image, (200, 200))
decorative_image2 = pygame.transform.scale(decorative_image, (150, 150))
decorative_image3 = pygame.transform.scale(decorative_image, (100, 100))
decorative_image4 = pygame.transform.scale(decorative_image, (120, 120))
decorative_image5 = pygame.transform.scale(decorative_image, (160, 160))
decorative_image6 = pygame.transform.scale(decorative_image, (100, 100))
decorative_image7 = pygame.transform.scale(decorative_image, (90, 90))

pygame.mixer.music.load("imgs/sheep1.mp3")
pygame.mixer.music.set_volume(0.2)  # 设置音乐音量（范围从 0.0 到 1.0）
pygame.mixer.music.play(-1)  # -1 表示循环播放音乐

font_path = 'imgs/ZCOOLKuaiLe-Regular.ttf'
FONT = pygame.font.Font(font_path, 35)

ROWS, COLS = 6, 6
TILE_SIZE = 70

# 加载道具图像
power_up_icon = pygame.image.load('imgs/cute.png')
power_up_icon = pygame.transform.scale(power_up_icon, (50, 50))

original_patterns = [pygame.image.load(f"imgs/{i}.jpg") for i in range(1, 11)]
original_patterns = [pygame.transform.scale(p, (TILE_SIZE, TILE_SIZE)) for p in original_patterns]

MAIN_MENU = 0
GAME = 1
GAME_OVER = 2
VICTORY = 3


class PowerUp:
    def __init__(self):
        self.image = power_up_icon
        self.position = (WINDOW_WIDTH - 70, WINDOW_HEIGHT - 70)
        self.rect = pygame.Rect(self.position, self.image.get_size())
        self.active = False
        self.animation_start_time = None
        self.animation_duration = 3000  # 动画持续时间，单位为毫秒
        self.victory_triggered = False
        self.game_over = False  # 游戏结束标志

    def draw(self, surface):
        surface.blit(self.image, self.position)

    def activate(self):
        if not self.active:
            self.active = True
            self.animation_start_time = pygame.time.get_ticks()  # 记录动画开始时间

    def update(self, layers):
        if self.active:
            current_time = pygame.time.get_ticks()
            elapsed_time = current_time - self.animation_start_time

            if elapsed_time >= self.animation_duration:
                self.deactivate()
                if not self.victory_triggered:
                    self.check_victory_condition(layers)
            else:
                progress = min(elapsed_time / self.animation_duration, 1)
                self.perform_effect(progress, layers)

    def deactivate(self):
        self.active = False
        self.animation_start_time = None

    def perform_effect(self, progress=1, layers=None):
        if not self.active or layers is None:
            return

        colored_tiles = []
        for layer in layers:
            for row in range(ROWS):
                for col in range(COLS):
                    tile = layer.get_tile_at_position(row, col)
                    if tile and not tile['is_gray']:
                        colored_tiles.append((layer, row, col))

        if len(colored_tiles) == 0:
            return

        tiles_to_remove = int((len(colored_tiles) + 1) * progress)
        for i in range(tiles_to_remove):
            layer, row, col = colored_tiles[i]
            layer.remove_tile(row, col)

    def check_victory_condition(self, layers):
        for layer in layers:
            for row in range(ROWS):
                for col in range(COLS):
                    tile = layer.get_tile_at_position(row, col)
                    if tile and not tile['is_gray']:
                        return

        self.trigger_victory_animation()

    def trigger_victory_animation(self):
        if self.victory_triggered:
            return
        self.victory_triggered = True
        victory_animation = VictoryAnimation()
        while not victory_animation.draw(window):
            pygame.display.flip()
            pygame.time.delay(10)

        pygame.time.wait(1000)  # 等待1秒钟
        self.game_over = True  # 设置游戏结束标志

class Layer:
    def __init__(self, images, position, is_top_layer):
        self.images = images
        self.position = position
        self.is_top_layer = is_top_layer

        even_images = self.generate_even_image_list(images, ROWS * COLS)

        self.board = [[{"image": even_images.pop(), "is_gray": False} for _ in range(COLS)] for _ in range(ROWS)]

    def generate_even_image_list(self, images, total_tiles):
        image_list = []
        num_images = len(images)

        if total_tiles % 2 != 0:
            raise ValueError("总图块数必须为偶数！")

        for i in range(total_tiles // 2):
            image = images[i % num_images]
            image_list.append(image)
            image_list.append(image)

        random.shuffle(image_list)
        return image_list

    def draw(self, surface, above_layer=None):
        for row in range(ROWS):
            for col in range(COLS):
                tile = self.board[row][col]
                if tile is not None:
                    x = col * TILE_SIZE + self.position[0]
                    y = row * TILE_SIZE + self.position[1]

                    if tile['is_gray']:
                        image_to_draw = convert_to_gray(tile["image"])
                    else:
                        image_to_draw = tile["image"]

                    if above_layer:
                        above_tile = above_layer.get_tile_at_position(row, col)
                        if above_tile and above_tile["image"] is not None:
                            above_x = col * TILE_SIZE + above_layer.position[0]
                            above_y = row * TILE_SIZE + above_layer.position[1]

                            if not (
                                    x + TILE_SIZE <= above_x or x >= above_x + TILE_SIZE or y + TILE_SIZE <= above_y or y >= above_y + TILE_SIZE):
                                image_to_draw = convert_to_gray(tile["image"])
                                tile['is_gray'] = True
                            else:
                                tile['is_gray'] = False
                        else:
                            tile['is_gray'] = False
                    surface.blit(image_to_draw, (x, y))

    def get_tile_at_position(self, row, col):
        if 0 <= row < ROWS and 0 <= col < COLS:
            return self.board[row][col]
        return None

    def remove_tile(self, row, col):
        self.board[row][col] = None

    def is_tile_fully_uncovered(self, row, col, above_layer):
        if above_layer:
            above_tile = above_layer.get_tile_at_position(row, col)
            return above_tile is None or above_tile["image"] is None
        return True

    def is_empty(self):
        # Check if all tiles in the layer have been removed
        return all(tile is None for row in self.board for tile in row)

def convert_to_gray(image):
    gray_image = pygame.Surface(image.get_size())
    gray_image.fill((128, 128, 128))
    gray_image.blit(image, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
    return gray_image

class VictoryAnimation:
    def __init__(self):
        self.image = pygame.image.load('imgs/victory_end.jpg')
        self.image = pygame.transform.scale(self.image, (WINDOW_WIDTH, WINDOW_HEIGHT))
        self.start_time = pygame.time.get_ticks()
        self.duration = 2000  # 动画持续时间，单位为毫秒

    def draw(self, surface):
        elapsed_time = pygame.time.get_ticks() - self.start_time
        if elapsed_time < self.duration:
            surface.blit(self.image, (0, 0))
        else:
            return True
        return False

class VictoryAnimation1:
    def __init__(self):
        self.image = pygame.image.load('imgs/mo2.jpg')
        self.image = pygame.transform.scale(self.image, (WINDOW_WIDTH, WINDOW_HEIGHT))
        self.start_time = pygame.time.get_ticks()
        self.duration = 3000  # 动画持续时间，单位为毫秒

    def draw(self, surface):
        elapsed_time = pygame.time.get_ticks() - self.start_time
        if elapsed_time < self.duration:
            surface.blit(self.image, (0, 0))
        else:
            return True
        return False

def draw_main_menu():
    window.blit(background_image, (0, 0))  # 绘制背景图像

    title_text = FONT.render('抓 肥 羊 啦 ~', True, BLACK)
    start_text = FONT.render('开始游戏', True, BLACK)
    quit_text = FONT.render('退出游戏', True, BLACK)

    # 绘制标题
    window.blit(title_text, (WINDOW_WIDTH // 2 - title_text.get_width() // 2, 100))

    # 绘制按钮
    start_button_rect = pygame.Rect(WINDOW_WIDTH // 2 - 100, 300, 200, 50)
    quit_button_rect = pygame.Rect(WINDOW_WIDTH // 2 - 100, 400, 200, 50)
    pygame.draw.rect(window, (213, 243, 191), start_button_rect)  # 按钮背景
    pygame.draw.rect(window, (0, 0, 0), start_button_rect, 2)
    pygame.draw.rect(window, (213, 243, 191), quit_button_rect)  # 按钮背景
    pygame.draw.rect(window, (0, 0, 0), quit_button_rect, 2)

    # 绘制按钮文本
    window.blit(start_text, (WINDOW_WIDTH // 2 - start_text.get_width() // 2, 310))
    window.blit(quit_text, (WINDOW_WIDTH // 2 - quit_text.get_width() // 2, 410))

    # 绘制装饰图像
    # window.blit(decorative_image4, (WINDOW_WIDTH - 420, WINDOW_HEIGHT - 80))
    # window.blit(decorative_image3, (WINDOW_WIDTH - 320, WINDOW_HEIGHT - 10))
    window.blit(decorative_image5, (WINDOW_WIDTH - 100, WINDOW_HEIGHT - 520))
    window.blit(decorative_image4, (WINDOW_WIDTH - 180, WINDOW_HEIGHT - 620))
    # window.blit(decorative_image2, (WINDOW_WIDTH - 280, WINDOW_HEIGHT - 120))

def draw_game():
    window.fill(WHITE)
    window.blit(background_image, (0, 0))  # 添加背景图像

def draw_game_over():
    window.fill(WHITE)
    window.blit(background_image, (0, 0))  # 添加背景图像
    game_over_text = FONT.render('游戏结束!!!', True, BLACK)
    restart_text = FONT.render('下一关', True, BLACK)
    quit_text = FONT.render('退出游戏', True, BLACK)

    restart_button_rect = pygame.Rect(WINDOW_WIDTH // 2 - 100, 300, 200, 50)
    quit_button_rect = pygame.Rect(WINDOW_WIDTH // 2 - 100, 400, 200, 50)
    pygame.draw.rect(window, (213, 243, 191), restart_button_rect)  # 按钮背景
    pygame.draw.rect(window, (0, 0, 0), restart_button_rect, 2)
    pygame.draw.rect(window, (213, 243, 191), quit_button_rect)  # 按钮背景
    pygame.draw.rect(window, (0, 0, 0), quit_button_rect, 2)

    window.blit(game_over_text, (WINDOW_WIDTH // 2 - game_over_text.get_width() // 2, 100))
    window.blit(restart_text, (WINDOW_WIDTH // 2 - restart_text.get_width() // 2, 310))
    window.blit(quit_text, (WINDOW_WIDTH // 2 - quit_text.get_width() // 2, 410))

    window.blit(decorative_image1, (WINDOW_WIDTH - 120, WINDOW_HEIGHT - 120))
    window.blit(decorative_image2, (WINDOW_WIDTH - 220, WINDOW_HEIGHT - 220))
    window.blit(decorative_image3, (WINDOW_WIDTH - 320, WINDOW_HEIGHT - 300))
    window.blit(decorative_image4, (WINDOW_WIDTH - 420, WINDOW_HEIGHT - 80))
    window.blit(decorative_image3, (WINDOW_WIDTH - 320, WINDOW_HEIGHT - 10))
    window.blit(decorative_image5, (WINDOW_WIDTH - 100, WINDOW_HEIGHT - 520))
    window.blit(decorative_image4, (WINDOW_WIDTH - 180, WINDOW_HEIGHT - 620))
    window.blit(decorative_image2, (WINDOW_WIDTH - 280, WINDOW_HEIGHT - 120))

def check_match(selected, layers):
    if len(selected) == 2:
        r1, c1, layer0 = selected[0]
        r2, c2, layer1 = selected[1]

        if (r1, c1) == (r2, c2):
            selected.clear()
            return

        tile1_layer0 = layer0.get_tile_at_position(r1, c1)
        tile2_layer0 = layer0.get_tile_at_position(r2, c2)
        tile1_layer1 = layer1.get_tile_at_position(r1, c1)
        tile2_layer1 = layer1.get_tile_at_position(r2, c2)

        if tile1_layer0 and not tile1_layer0['is_gray'] and tile2_layer1 and not tile2_layer1['is_gray']:
            if tile1_layer0["image"] == tile2_layer1["image"]:
                #print(f"消除 ({r1}, {c1}) in layer {layers.index(layer0)} 和 ({r2}, {c2}) in layer {layers.index(layer1)}")
                layer0.remove_tile(r1, c1)
                layer1.remove_tile(r2, c2)
        elif tile1_layer0 and not tile1_layer0['is_gray'] and tile2_layer0 and not tile2_layer0['is_gray']:
            if tile1_layer0["image"] == tile2_layer0["image"]:
                #print(f"消除 ({r1}, {c1}) in layer {layers.index(layer0)} 和 ({r2}, {c2}) in layer {layers.index(layer0)}")
                layer0.remove_tile(r1, c1)
                layer0.remove_tile(r2, c2)
        elif tile1_layer1 and not tile1_layer1['is_gray'] and tile2_layer1 and not tile2_layer1['is_gray']:
            if tile1_layer1["image"] == tile2_layer1["image"]:
                #print(f"消除 ({r1}, {c1}) in layer {layers.index(layer1)} 和 ({r2}, {c2}) in layer {layers.index(layer1)}")
                layer1.remove_tile(r1, c1)
                layer1.remove_tile(r2, c2)
        elif tile1_layer1 and not tile1_layer1['is_gray'] and tile2_layer0 and not tile2_layer0['is_gray']:
            if tile1_layer1["image"] == tile2_layer0["image"]:
                #print(f"消除 ({r1}, {c1}) in layer {layers.index(layer1)} 和 ({r2}, {c2}) in layer {layers.index(layer0)}")
                layer1.remove_tile(r1, c1)
                layer0.remove_tile(r2, c2)

        selected.clear()

        if all(layer.is_empty() for layer in layers):
            print("游戏胜利！")
            # 显示胜利动画
            victory_animation = VictoryAnimation()
            while not victory_animation.draw(window):
                pygame.display.flip()
                pygame.time.delay(10)

            pygame.time.wait(1000)  # 等待1秒钟
            return True  # 返回 True 表示胜利动画完成

def reset_game():
    global countdown_duration

    layers = [
        Layer(original_patterns, (0, 0), is_top_layer=False),
        Layer(original_patterns, (0, 0), is_top_layer=True)
    ]
    power_up = PowerUp()  # 初始化道具
    countdown_duration = max(0, countdown_duration - 10000)  # 确保游戏时长不会变为负数
    return layers, power_up,countdown_duration

def over_all_game(countdown_duration):
    if countdown_duration == 0:
        victory_animation1 = VictoryAnimation1()
        while not victory_animation1.draw(window):
            pygame.display.flip()
            pygame.time.delay(5000)
            pygame.quit()
            sys.exit()

def draw_timer(time_left):
    timer_text = FONT.render(f"剩余时间: {time_left//1000}秒", True, BLACK)
    window.blit(timer_text, (WINDOW_WIDTH - timer_text.get_width() - 100, WINDOW_HEIGHT - timer_text.get_height() - 20))

def update_game_time(start_time, current_time):
    elapsed_time = current_time - start_time
    countdown_duration1=countdown_duration
    return countdown_duration1 - elapsed_time


def test_main_menu_interaction():
    # 模拟游戏初始化
    pygame.init()
    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

    # 模拟主菜单绘制
    draw_main_menu()
    pygame.display.flip()

    # 模拟点击开始游戏按钮
    start_button = pygame.Rect(WINDOW_WIDTH // 2 - 100, 300, 200, 50)
    assert start_button.collidepoint((250, 325)), "Start button interaction failed"

    # 模拟点击退出游戏按钮
    quit_button = pygame.Rect(WINDOW_WIDTH // 2 - 100, 400, 200, 50)
    assert quit_button.collidepoint((250, 425)), "Quit button interaction failed"


def main():
    state = MAIN_MENU
    clock = pygame.time.Clock()
    layers = []  # 初始化为空
    power_up = None  # 初始化为空
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if state == MAIN_MENU:
                    if 200 < mouse_pos[0] < 275 and 300 < mouse_pos[1] < 350:
                        state = GAME
                        layers, power_up,countdown_duration = reset_game()  # 重新初始化游戏
                    elif 200 < mouse_pos[0] < 275 and 400 < mouse_pos[1] < 450:
                        pygame.quit()
                        sys.exit()
                elif state == GAME_OVER:
                    if 200 < mouse_pos[0] < 275 and 300 < mouse_pos[1] < 350:
                        state = GAME
                        layers, power_up,countdown_duration = reset_game()  # 重新初始化游戏
                        print(countdown_duration)
                        over_all_game(countdown_duration)
                    elif 200 < mouse_pos[0] < 275 and 400 < mouse_pos[1] < 450:
                        pygame.quit()
                        sys.exit()

        if state == MAIN_MENU:
            draw_main_menu()
        elif state == GAME:
            running = True
            selected = []
            start_time = pygame.time.get_ticks()  # 游戏开始时间


            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        state = GAME_OVER
                        running = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if power_up.rect.collidepoint(event.pos):  # 判断是否点击了道具图标
                            power_up.activate()
                        mouse_pos = pygame.mouse.get_pos()
                        x, y = mouse_pos
                        col = x // TILE_SIZE
                        row = y // TILE_SIZE

                        # 检查是否点击了图块
                        if len(layers) >= 2:  # 确保 layers 有足够的元素
                            for layer in reversed(layers):
                                tile_image = layer.get_tile_at_position(row, col)
                                if tile_image and not tile_image.get("is_gray"):
                                    is_fully_uncovered = True
                                    for above_layer in layers[:layers.index(layer)]:
                                        if not layer.is_tile_fully_uncovered(row, col, above_layer):
                                            is_fully_uncovered = False
                                            break

                                    if is_fully_uncovered:
                                        # print(f"Clicked tile at ({row}, {col}) in layer {layers.index(layer)}")
                                        selected.append((row, col, layer))
                                        if len(selected) == 2:
                                            if check_match(selected, layers):
                                                state = GAME_OVER
                                                running = False
                                            break
                # 倒计时
                current_time = pygame.time.get_ticks()
                time_left = update_game_time(start_time, current_time)

                if time_left <= 0:
                    state = GAME_OVER
                    running = False
                else:
                    # 绘制游戏画面
                    window.fill(WHITE)
                    window.blit(background_image, (0, 0))

                    # 绘制图层
                    if len(layers) >= 2:  # 确保有足够的图层
                        layers[1].draw(window, above_layer=layers[0])
                        layers[0].draw(window)

                    # 绘制道具
                    if power_up:
                        power_up.update(layers)
                        power_up.draw(window)
                        if power_up.game_over:
                            state = GAME_OVER
                            running = False


                    #绘制装饰
                    window.blit(decorative_image7, (WINDOW_WIDTH - 120, WINDOW_HEIGHT - 180))
                    window.blit(decorative_image6, (WINDOW_WIDTH - 220, WINDOW_HEIGHT - 250))
                    window.blit(decorative_image6, (WINDOW_WIDTH - 320, WINDOW_HEIGHT - 250))
                    window.blit(decorative_image6, (WINDOW_WIDTH - 420, WINDOW_HEIGHT - 250))

                    #绘制时间
                    draw_timer(time_left)

                    pygame.display.flip()
                    clock.tick(60)


        elif state == GAME_OVER:
            draw_game_over()

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    # main()
    test_main_menu_interaction()
