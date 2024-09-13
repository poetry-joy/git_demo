import pygame
import sys

pygame.init()

WINDOW_WIDTH, WINDOW_HEIGHT = 475, 750
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('抓懒羊羊')

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# 加载背景和装饰图像
background_image = pygame.image.load('background.jpg')
background_image = pygame.transform.scale(background_image, (WINDOW_WIDTH, WINDOW_HEIGHT))

decorative_image = pygame.image.load('cute.png')
decorative_image1 = pygame.transform.scale(decorative_image, (200, 200))
decorative_image2 = pygame.transform.scale(decorative_image, (150, 150))
decorative_image3 = pygame.transform.scale(decorative_image, (100, 100))
decorative_image4 = pygame.transform.scale(decorative_image, (120, 120))
decorative_image5 = pygame.transform.scale(decorative_image, (160, 160))
decorative_image6 = pygame.image.load('menu.jpg')
font_path = 'ZCOOLKuaiLe-Regular.ttf'
FONT = pygame.font.Font(font_path, 35)


def draw_main_menu():
    window.blit(background_image, (0, 0))  # 绘制背景图像

    title_text = FONT.render('抓 懒 羊 羊', True, BLACK)
    start_text = FONT.render('开始游戏', True, BLACK)
    quit_text = FONT.render('退出游戏', True, BLACK)

    # 绘制标题
    window.blit(title_text, (WINDOW_WIDTH // 2 - title_text.get_width() // 2, 100))

    # 绘制按钮
    start_button_rect = pygame.Rect(WINDOW_WIDTH // 2 - 100, 300, 200, 50)
    quit_button_rect = pygame.Rect(WINDOW_WIDTH // 2 - 100, 400, 200, 50)
    pygame.draw.rect(window, (213,243,191), start_button_rect)  # 按钮背景
    pygame.draw.rect(window, (213,243,191), quit_button_rect)  # 按钮背景

    # 绘制按钮文本
    window.blit(start_text, (WINDOW_WIDTH // 2 - start_text.get_width() // 2, 310))
    window.blit(quit_text, (WINDOW_WIDTH // 2 - quit_text.get_width() // 2, 410))

    # 绘制装饰图像
    window.blit(decorative_image1, (WINDOW_WIDTH - 120, WINDOW_HEIGHT - 120))
    window.blit(decorative_image2, (WINDOW_WIDTH - 220, WINDOW_HEIGHT - 220))
    window.blit(decorative_image3, (WINDOW_WIDTH - 320, WINDOW_HEIGHT - 300))
    window.blit(decorative_image4, (WINDOW_WIDTH - 420, WINDOW_HEIGHT - 80))
    window.blit(decorative_image3, (WINDOW_WIDTH - 320, WINDOW_HEIGHT - 10))
    window.blit(decorative_image5, (WINDOW_WIDTH - 100, WINDOW_HEIGHT - 520))
    window.blit(decorative_image4, (WINDOW_WIDTH - 180, WINDOW_HEIGHT - 620))
    window.blit(decorative_image2, (WINDOW_WIDTH - 280, WINDOW_HEIGHT - 120))
def main_menu():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if 175 < mouse_pos[0] < 275 and 300 < mouse_pos[1] < 350:
                    return 'game'
                elif 175 < mouse_pos[0] < 275 and 400 < mouse_pos[1] < 450:
                    pygame.quit()
                    sys.exit()

        draw_main_menu()
        pygame.display.flip()


if __name__ == "__main__":
    state = main_menu()
