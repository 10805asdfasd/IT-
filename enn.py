import pygame
import random
from pygame.locals import *

# 전역 변수 설정
grass = (0, 178, 0)
white = (255, 255, 255)
brown = (139, 69, 19)
orange = (255, 165, 0)
dark_green = (0, 100, 0)
yellow = (255, 255, 0)
COLOR_KEY = (255, 100, 98)
width, height = 640, 480
# 시간 변수 추가
time_of_day = 0
DAY_LENGTH = 2000
is_night = False

sky_day = (135, 206, 235) # 낮 하늘 색깔
sky_night = (25, 25, 112) # 밤 하늘 색깔



# [수정 1] 집합({})이 아니라 리스트([])여야 순서대로 접근 가능
inventory = {"도끼" : 1, "목재": 0, "호박": 0}
item_order = ["도끼", "목재", "호박"] 
selected_slot = 0
MAX_SLOTS = 8
SLOT_SIZE = 50
GAP = 5

BAR_WIDTH = (SLOT_SIZE + GAP) * MAX_SLOTS + GAP
BAR_HEIGHT = SLOT_SIZE + (GAP * 2)
BAR_X = (width - BAR_WIDTH) // 2
BAR_Y = height - BAR_HEIGHT - 10

class Entity(pygame.sprite.Sprite):
    def __init__(self, health_point, speed, drop_item, stance):
        super().__init__()
        self.health_point = health_point
        self.speed = speed
        self.drop_item = drop_item
        self.stance = stance


def draw_item_icon(screen, item_name, rect):
    if item_name == "도끼":
        # 손잡이
        pygame.draw.rect(screen, brown, [
            rect.centerx - 2,
            rect.centery - 10,
            4, 20
        ])
        # 날
        pygame.draw.rect(screen, (180, 180, 180), [
            rect.centerx - 8,
            rect.centery - 12,
            10, 6
        ])

    elif item_name == "목재":
        inner_rect = pygame.Rect(0, 0, 20, 10)
        inner_rect.center = rect.center
        pygame.draw.rect(screen, brown, inner_rect)

    elif item_name == "호박":
        pygame.draw.circle(screen, orange, rect.center, 12)
        pygame.draw.rect(
            screen,
            (0, 200, 0),
            [rect.centerx-2, rect.centery-15, 4, 6]
        )


class Player(pygame.sprite.Sprite):
    def __init__(self, color, width, height):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.speed = 4
        self.hp = 20

    def update(self, keys, obstacles):
        old_x, old_y = self.rect.x, self.rect.y
        if keys[K_a]: self.rect.x -= self.speed
        if keys[K_d]: self.rect.x += self.speed
        if self.rect.left < 0 or self.rect.right > width or pygame.sprite.spritecollideany(self, obstacles):
            self.rect.x = old_x
        if keys[K_w]: self.rect.y -= self.speed
        if keys[K_s]: self.rect.y += self.speed
        if self.rect.top < 0 or self.rect.bottom > height or pygame.sprite.spritecollideany(self, obstacles):
            self.rect.y = old_y

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, obs_type):
        super().__init__()
        # [수정 2] 종류를 기억해야 나중에 인벤토리에 넣을 수 있음
        self.obs_type = obs_type 
        
        if obs_type == "tree":
            self.max_hp = random.randint(3, 5) # 테스트 쉽게 체력 조금 낮춤
            self.hp = self.max_hp
            self.image = pygame.Surface([30, 40], pygame.SRCALPHA)
            pygame.draw.rect(self.image, brown, [10, 20, 10, 20])
            pygame.draw.circle(self.image, dark_green, (15, 15), 15)
        elif obs_type == "pumpkin":
            self.max_hp = 1
            self.hp = 1
            self.image = pygame.Surface([20, 20], pygame.SRCALPHA)
            pygame.draw.ellipse(self.image, orange, [0, 5, 20, 15])
            pygame.draw.rect(self.image, (0, 200, 0), [8, 0, 4, 7])
        
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, width - self.rect.width)
        self.rect.y = random.randint(0, height - self.rect.height)

    # [수정 3] hit 함수는 __init__ 밖으로 나와야 함 (들여쓰기 수정)
    def hit(self):
        self.hp -= 1
        if self.obs_type == "tree":
            # 타격 효과 (잠시 밝게)
            pygame.draw.circle(self.image, (100, 255, 100), (15, 15), 15)
        return self.hp <= 0


class Enderman(Entity):
    def __init__(self):
        # 엔티티 속성
        super().__init__(
            health_point = 40,
            speed = 8,
            drop_item = "ender_pearl",
            stance = 1
        )
        # 엔더맨 그리기
        self.image = pygame.Surface([30, 80], pygame.SRCALPHA)
        # 몸통
        pygame.draw.rect(self.image, (20, 20, 20), [10, 20, 10, 60])
        # 머리
        pygame.draw.rect(self.image, (30, 30, 30), [5, 0, 20, 20])
        #눈
        pygame.draw.rect(self.image, (150, 0, 150), [7, 5, 5, 5])
        pygame.draw.rect(self.image, (150, 0, 150), [18, 5, 5, 5])
        # 팔
        pygame.draw.rect(self.image, (20, 20, 20), [0, 20, 5, 60])
        pygame.draw.rect(self.image, (20, 20, 20), [25, 20, 5, 60])
        #위치 랜덤 배치
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, width - self.rect.width)
        self.rect.y = random.randint(0, height - self.rect.height)
        




def draw_hotbar(screen, inventory, font):
    # 배경
    bar_surface = pygame.Surface((BAR_WIDTH, BAR_HEIGHT), pygame.SRCALPHA)
    pygame.draw.rect(bar_surface, (0, 0, 0, 180), [0, 0, BAR_WIDTH, BAR_HEIGHT], border_radius=10)
    screen.blit(bar_surface, (BAR_X, BAR_Y))

    for i in range(MAX_SLOTS):
        slot_x = BAR_X + GAP + (SLOT_SIZE + GAP) * i
        slot_y = BAR_Y + GAP
        slot_rect = pygame.Rect(slot_x, slot_y, SLOT_SIZE, SLOT_SIZE)

        # 테두리 그리기
        if i == selected_slot:
            pygame.draw.rect(screen, yellow, slot_rect, 3, border_radius=5)
        else:
            pygame.draw.rect(screen, (100, 100, 100), slot_rect, 1, border_radius=5)

        # 아이템 그리기
        if i < len(item_order):
            name = item_order[i]
            count = inventory[name]
            if count > 0:
                draw_item_icon(screen, name, slot_rect)
                count_surf = font.render(str(count), True, white)
                # [수정 4] 텍스트 위치 잡는 코드 완성
                screen.blit(count_surf, (slot_x + SLOT_SIZE - 15, slot_y + SLOT_SIZE - 18))

# 초기화
pygame.init()
font = pygame.font.SysFont("malgungothic", 15)
bold_font = pygame.font.SysFont("malgungothic", 18, bold=True)
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Survival Game")

all_sprites_list = pygame.sprite.Group()
obstacles = pygame.sprite.Group()

player = Player((167, 255, 100), 30, 30)
player.rect.center = (200, 300)
all_sprites_list.add(player)

# 나무 생성
for i in range(10):
    tree = Obstacle("tree")
    while pygame.sprite.collide_rect(player, tree):
        tree.rect.x = random.randint(0, width - 30)
        tree.rect.y = random.randint(0, height - 40)
    all_sprites_list.add(tree)
    obstacles.add(tree)

# 호박 생성
for i in range(random.randint(3, 5)):
    pumpkin = Obstacle("pumpkin")
    while pygame.sprite.collide_rect(player, pumpkin):
        pumpkin.rect.x = random.randint(0, width - 20)
        pumpkin.rect.y = random.randint(0, height - 20)
    all_sprites_list.add(pumpkin)
    obstacles.add(pumpkin)

running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == QUIT: running = False
        if event.type == KEYDOWN:
            if event.key == K_x: running = False
            if K_1 <= event.key <= K_8:
                selected_slot = event.key - K_1

        # [핵심 수정] 마우스 클릭 로직
    if event.type == MOUSEBUTTONDOWN and event.button == 1:
    # 도끼를 선택한 상태인지 확인
     if item_order[selected_slot] == "도끼":

        mouse_pos = pygame.mouse.get_pos()

        for obj in obstacles:
            # 클릭한 위치에 호박이 있고
            if obj.obs_type == "pumpkin" and obj.rect.collidepoint(mouse_pos):
                obj.kill()                 # 맵에서 제거
                inventory["호박"] += 1     # 인벤토리에 추가
                break  # 한 번 클릭에 하나만 캐기


    keys = pygame.key.get_pressed()
    player.update(keys, obstacles)

    screen.fill(grass)
    all_sprites_list.draw(screen)
    
    draw_hotbar(screen, inventory, font)

    if selected_slot < len(item_order):
        current_item = item_order[selected_slot]
        msg = bold_font.render(f"선택됨: {current_item}", True, white)
        screen.blit(msg, (BAR_X, BAR_Y - 30))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()


