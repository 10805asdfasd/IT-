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
width, height = 640, 480

inventory = {"도끼" : 1, "가위": 1, "목재": 0, "호박": 0, "조각난 호박": 0, "보트": 0}
item_order = ["도끼", "가위", "목재", "호박", "조각난 호박", "보트"] 
selected_slot = 0
crafting_open = False

MAX_SLOTS = 8
SLOT_SIZE = 50
GAP = 5

BAR_WIDTH = (SLOT_SIZE + GAP) * MAX_SLOTS + GAP
BAR_HEIGHT = SLOT_SIZE + (GAP * 2)
BAR_X = (width - BAR_WIDTH) // 2
BAR_Y = height - BAR_HEIGHT - 10

def draw_item_icon(screen, item_name, rect):
    if item_name == "도끼":
        pygame.draw.rect(screen, brown, [rect.centerx - 2, rect.centery - 10, 4, 20])
        pygame.draw.rect(screen, (180, 180, 180), [rect.centerx - 8, rect.centery - 12, 10, 6])
    elif item_name == "가위":
        # 두 개의 타원형 손잡이와 날
        pygame.draw.circle(screen, (200, 200, 200), (rect.centerx-5, rect.centery+5), 5, 2)
        pygame.draw.circle(screen, (200, 200, 200), (rect.centerx+5, rect.centery+5), 5, 2)
        pygame.draw.line(screen, (200, 200, 200), (rect.centerx-3, rect.centery+2), (rect.centerx+8, rect.centery-8), 3)
        pygame.draw.line(screen, (200, 200, 200), (rect.centerx+3, rect.centery+2), (rect.centerx-8, rect.centery-8), 3)
    elif item_name == "조각난 호박":
        # 기본 호박 모양에 눈/입 추가
        pygame.draw.circle(screen, orange, rect.center, 12)
        # 검은색 눈과 입
        pygame.draw.rect(screen, (0, 0, 0), [rect.centerx-5, rect.centery-4, 3, 3])
        pygame.draw.rect(screen, (0, 0, 0), [rect.centerx+2, rect.centery-4, 3, 3])
        pygame.draw.line(screen, (0, 0, 0), (rect.centerx-4, rect.centery+4), (rect.centerx+4, rect.centery+4), 2)
    elif item_name == "목재":
        inner_rect = pygame.Rect(0, 0, 20, 10)
        inner_rect.center = rect.center
        pygame.draw.rect(screen, brown, inner_rect)
    elif item_name == "호박":
        pygame.draw.circle(screen, orange, rect.center, 12)
        pygame.draw.rect(screen, (0, 200, 0), [rect.centerx-2, rect.centery-15, 4, 6])
    elif item_name == "보트":
        pygame.draw.arc(screen, brown, [rect.x+5, rect.y+10, 40, 30], 3.14, 6.28, 20)
        pygame.draw.line(screen, brown, (rect.x+5, rect.centery+5), (rect.x+45, rect.centery+5), 3)

class Player(pygame.sprite.Sprite):
    def __init__(self, color, width, height):
        super().__init__()
        self.base_color = color
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.speed = 4
        self.is_wearing_pumpkin = False # 호박 착용 여부

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
            
    def update_appearance(self):
        """호박 착용 여부에 따라 플레이어의 외형을 바꿉니다."""
        self.image.fill(self.base_color) # 기본 몸 색상
        if self.is_wearing_pumpkin:
            # 머리 부분에 호박 씌우기 (주황색 바탕 + 눈/입)
            # 플레이어 상단 2/3 지점에 호박 그리기
            pygame.draw.ellipse(self.image, orange, [2, 0, 26, 20])
            # 눈 그리기
            pygame.draw.rect(self.image, (0, 0, 0), [8, 6, 3, 3])
            pygame.draw.rect(self.image, (0, 0, 0), [19, 6, 3, 3])
            # 입 그리기
            pygame.draw.line(self.image, (0, 0, 0), (10, 14), (20, 14), 2)

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, obs_type):
        super().__init__()
        self.obs_type = obs_type 
        
        if obs_type == "tree":
            self.max_hp = random.randint(3, 5)
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

    def hit(self):
        self.hp -= 1
        if self.obs_type == "tree":
            pygame.draw.circle(self.image, (100, 255, 100), (15, 15), 15)
        return self.hp <= 0

class Entity(pygame.sprite.Sprite):
    def __init__(self, health_point, speed, drop_item, stance):
        super().__init__()
        self.health_point = health_point
        self.speed = speed
        self.drop_item = drop_item
        self.stance = stance


class Enderman(Entity):
    def __init__(self):
        # 엔티티 속성
        super().__init__(
            health_point=40,
            speed=8,
            drop_item="ender_pearl",
            stance=1
        )
        # 엔더맨 그리기
        self.image = pygame.Surface([30, 80], pygame.SRCALPHA)
        # 몸통
        pygame.draw.rect(self.image, (20, 20, 20), [10, 20, 10, 60])
        # 머리
        pygame.draw.rect(self.image, (30, 30, 30), [5, 0, 20, 20])
        # 눈
        pygame.draw.rect(self.image, (150, 0, 150), [7, 5, 5, 5])
        pygame.draw.rect(self.image, (150, 0, 150), [18, 5, 5, 5])
        # 팔
        pygame.draw.rect(self.image, (20, 20, 20), [0, 20, 5, 60])
        pygame.draw.rect(self.image, (20, 20, 20), [25, 20, 5, 60])
        # 위치를 화면 밖으로 랜덤 배치
        self.rect = self.image.get_rect()
        side = random.randint(0, 3)
        if side == 0:  # 위쪽
            self.rect.x = random.randint(0, width - self.rect.width)
            self.rect.y = -self.rect.height
        elif side == 1:  # 아래쪽
            self.rect.x = random.randint(0, width - self.rect.width)
            self.rect.y = height
        elif side == 2:  # 왼쪽
            self.rect.x = -self.rect.width
            self.rect.y = random.randint(0, height - self.rect.height)
        else:  # 오른쪽
            self.rect.x = width
            self.rect.y = random.randint(0, height - self.rect.height)


class CraftingTable(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([40, 40])
        self.image.fill((101, 67, 33)) 
        
        pygame.draw.rect(self.image, (40, 20, 0), [0, 0, 40, 40], 3)
        pygame.draw.line(self.image, (40, 20, 0), (20, 0), (20, 40), 2)
        pygame.draw.line(self.image, (40, 20, 0), (0, 20), (40, 20), 2)

        self.rect = self.image.get_rect()
        self.rect.center = (width // 2, height // 2)

all_sprites_list = pygame.sprite.Group()
obstacles = pygame.sprite.Group()
endermen = pygame.sprite.Group()

player = Player((167, 255, 100), 30, 30)
craft_table = CraftingTable()
enderman_spawn_counter = 0  # 엔더맨 스폰 카운터

def reset_game():
    global inventory, selected_slot, crafting_open, boat_crafted, is_night, message_timer, show_tutorial, enderman_spawn_counter
    
    # 1. 변수 초기화
    inventory = {"도끼": 1, "가위": 1, "목재": 0, "호박": 0, "조각난 호박": 0, "보트": 0}
    selected_slot = 0
    crafting_open = False
    boat_crafted = False
    is_night = False
    message_timer = 0
    show_tutorial = True # 재시작 시 튜토리얼부터 다시 보여줄지 선택
    enderman_spawn_counter = 0
    
    # 2. 스프라이트 그룹 비우기
    all_sprites_list.empty()
    obstacles.empty()
    endermen.empty()
    
    # 3. 플레이어 재생성
    player.rect.center = (200, 300)
    player.is_wearing_pumpkin = False
    player.update_appearance()
    all_sprites_list.add(player)
    
    # 4. 제작대 및 오브젝트 재배치
    all_sprites_list.add(craft_table)
    obstacles.add(craft_table)
    
    # 나무 생성 로직
    for i in range(10):
        tree = Obstacle("tree")
        while pygame.sprite.collide_rect(player, tree) or pygame.sprite.spritecollideany(tree, obstacles):
            tree.rect.x = random.randint(0, width - 30)
            tree.rect.y = random.randint(0, height - 40)
        all_sprites_list.add(tree)
        obstacles.add(tree)

    # 호박 생성 로직
    for i in range(random.randint(3, 5)):
        pumpkin = Obstacle("pumpkin")
        while pygame.sprite.collide_rect(player, pumpkin) or pygame.sprite.spritecollideany(pumpkin, obstacles):
            pumpkin.rect.x = random.randint(0, width - 20)
            pumpkin.rect.y = random.randint(0, height - 20)
        all_sprites_list.add(pumpkin)
        obstacles.add(pumpkin)
        
def draw_tutorial(screen, font):
    # 배경을 약간 어둡게 덮기
    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))

    # 조작법 텍스트 리스트
    instructions = [
        "=== 조작 방법 & 플레이 순서 ===",
        "이동: W, A, S, D",
        "아이템 선택: 숫자키 1~8",
        "채집(도끼): 대상 클릭 (좌클릭)",
        "제작대 열기/닫기: 제작대 우클릭",
        "호박 조각(가위): 호박 우클릭",
        "전체화면: F / 종료: X",
        "",
        "1. 도끼로 목재 5개를 캐세요.",
        "2. 가위로 호박을 조각하세요.",
        "3. 목재 5개로 보트를 제작하세요.",
        "",
        "[ ESC ] 키를 눌러 게임 시작"
    ]

    # [수정] 시작 높이(start_y)와 줄 간격(line_spacing)
    start_y = 50 
    line_spacing = 30 

    for i, line in enumerate(instructions):
        color = white
        if i == 0 or i == len(instructions) - 1:
            color = yellow
        elif "1." in line or "2." in line or "3." in line:
            color = (200, 255, 200) # 플레이 순서는 연한 녹색
            
        text_surf = font.render(line, True, color)
        # y 위치 계산식 수정
        text_rect = text_surf.get_rect(center=(width // 2, start_y + i * line_spacing))
        screen.blit(text_surf, text_rect)

def draw_hotbar(screen, inventory, font):
    bar_surface = pygame.Surface((BAR_WIDTH, BAR_HEIGHT), pygame.SRCALPHA)
    pygame.draw.rect(bar_surface, (0, 0, 0, 180), [0, 0, BAR_WIDTH, BAR_HEIGHT], border_radius=10)
    screen.blit(bar_surface, (BAR_X, BAR_Y))

    for i in range(MAX_SLOTS):
        slot_x = BAR_X + GAP + (SLOT_SIZE + GAP) * i
        slot_y = BAR_Y + GAP
        slot_rect = pygame.Rect(slot_x, slot_y, SLOT_SIZE, SLOT_SIZE)

        if i == selected_slot:
            pygame.draw.rect(screen, yellow, slot_rect, 3, border_radius=5)
        else:
            pygame.draw.rect(screen, (100, 100, 100), slot_rect, 1, border_radius=5)

        if i < len(item_order):
            name = item_order[i]
            count = inventory[name]
            if count > 0:
                draw_item_icon(screen, name, slot_rect)
                count_surf = font.render(str(count), True, white)
                screen.blit(count_surf, (slot_x + SLOT_SIZE - 15, slot_y + SLOT_SIZE - 18))
        
def draw_crafting_ui(screen, font):
    ui_surface = pygame.Surface((300, 200), pygame.SRCALPHA)
    pygame.draw.rect(ui_surface, (0, 0, 0, 200), [0, 0, 300, 200], border_radius=15)
    
    title = font.render("=== 제작대 ===", True, white)
    recipe = font.render("보트 만들기", True, yellow)
    cost_text = font.render("필요: 목재 5개", True, orange)
    
    if boat_crafted:
        status = font.render("보트 제작 완료!", True, (100, 200, 255))
    elif inventory["목재"] >= 5:
        status = font.render("[SPACE] 눌러서 제작", True, (100, 255, 100))
    else:
        status = font.render("목재가 부족합니다", True, (255, 100, 100))

    ui_surface.blit(title, (100, 20))
    ui_surface.blit(recipe, (100, 70))
    ui_surface.blit(cost_text, (100, 100))
    ui_surface.blit(status, (80, 150))

    screen.blit(ui_surface, (width//2 - 150, height//2 - 100))
    
# 초기화
pygame.init()
font = pygame.font.SysFont("malgungothic", 15)
bold_font = pygame.font.SysFont("malgungothic", 18, bold=True)
screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN | pygame.DOUBLEBUF)
pygame.display.set_caption("Survival Game")

reset_game()

running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == QUIT: running = False
        if event.type == KEYDOWN:
            if show_tutorial:
                if event.key == K_ESCAPE:
                    show_tutorial = False
                continue
            if event.key == K_r:
                reset_game()
            if event.key == K_x: running = False
            if K_1 <= event.key <= K_8:
                selected_slot = event.key - K_1

            if crafting_open and event.key == K_ESCAPE:
                crafting_open = False
                if boat_crafted:
                    is_night = True
                    message_timer = 90
                    boat_crafted = False # 한 번만 실행되도록 리셋

            if crafting_open and event.key == K_SPACE:
                if inventory["목재"] >= 5:
                    inventory["목재"] -= 5
                    inventory["보트"] += 1
                    boat_crafted = True
                else:
                    print("목재가 부족합니다.")
                
        if event.type == MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            player_pos = pygame.math.Vector2(player.rect.center)
            
            if event.button == 3: 
                # 1. 제작대 상호작용 체크
                if craft_table.rect.collidepoint(mouse_pos):
                    dist = player_pos.distance_to(craft_table.rect.center)
                    if dist <= 100:
                        if crafting_open: # 열려있으면 닫기
                            crafting_open = False
                            if boat_crafted: # 여기서도 체크!
                                is_night = True
                                message_timer = 90
                                boat_crafted = False
                        else: # 닫혀있으면 열기
                            crafting_open = True
                        continue
                    
                elif not crafting_open and item_order[selected_slot] == "조각난 호박":
                    if inventory["조각난 호박"] > 0 and not player.is_wearing_pumpkin:
                        inventory["조각난 호박"] -= 1
                        player.is_wearing_pumpkin = True
                        player.update_appearance() # 외형 업데이트
                        

                # 2. 가위를 들고 호박 우클릭 (조각하기)
                if item_order[selected_slot] == "가위":
                    for obj in obstacles:
                        # [중요] obs_type 속성이 있는지 먼저 확인 (제작대 에러 방지)
                        if hasattr(obj, 'obs_type') and obj.obs_type == "pumpkin":
                            if obj.rect.collidepoint(mouse_pos):
                                dist = player_pos.distance_to(obj.rect.center)
                                if dist <= 100:
                                    obj.kill()
                                    inventory["조각난 호박"] += 1
                                    break
                            
            elif event.button == 1:
                 if not crafting_open and item_order[selected_slot] == "도끼":
                    INTERACTION_RANGE = 100
                    for obj in obstacles:
                        if obj.rect.collidepoint(mouse_pos):
                            obj_pos = pygame.math.Vector2(obj.rect.center)
                            distance = player_pos.distance_to(obj_pos)
                            
                            if distance <= INTERACTION_RANGE:
                                if obj.obs_type == "pumpkin":
                                    obj.kill()
                                    inventory["호박"] += 1
                                    break
                                elif obj.obs_type == "tree":
                                    if obj.hit(): 
                                        obj.kill()
                                        inventory["목재"] += random.randint(3, 5)
                                    break
    if not show_tutorial:
        keys = pygame.key.get_pressed()
        player.update(keys, obstacles)
        
        # 밤에 엔더맨 스폰 로직
        if is_night:
            enderman_spawn_counter += 1
            # 300프레임마다 (약 5초마다) 확률적으로 엔더맨 스폰
            if enderman_spawn_counter >= 300:
                # 엔더맨이 2마리 이하일 때만 스폰
                if len(endermen) < 2 and random.randint(1, 100) <= 30:  # 30% 확률
                    enderman = Enderman()
                    all_sprites_list.add(enderman)
                    endermen.add(enderman)
                enderman_spawn_counter = 0
            
            # 엔더맨 이동 (플레이어 방향으로)
            for enderman in endermen:
                player_pos = pygame.math.Vector2(player.rect.center)
                enderman_pos = pygame.math.Vector2(enderman.rect.center)
                direction = (player_pos - enderman_pos)
                if direction.length() > 0:
                    direction = direction.normalize()
                    enderman.rect.x += direction.x * enderman.speed
                    enderman.rect.y += direction.y * enderman.speed

    screen.fill(grass)
    all_sprites_list.draw(screen)

    if is_night:
        night_overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        night_overlay.fill((0, 0, 40, 160)) # 진한 남색 계열로 어둡게 (R, G, B, Alpha)
        screen.blit(night_overlay, (0, 0))

    if crafting_open:
        draw_crafting_ui(screen, font)
    
    draw_hotbar(screen, inventory, font)

    if selected_slot < len(item_order):
        current_item = item_order[selected_slot]
        msg = bold_font.render(f"선택됨: {current_item}", True, white)
        screen.blit(msg, (BAR_X, BAR_Y - 30))

    if message_timer > 0:
        # 텍스트 렌더링
        msg_surf = bold_font.render("밤이 되었습니다", True, yellow)
        # 중앙 정렬 계산
        msg_rect = msg_surf.get_rect(center=(width // 2, 50))
        
        # 가독성을 위한 검은색 배경 박스 (선택 사항)
        bg_rect = msg_rect.inflate(20, 10)
        pygame.draw.rect(screen, (0, 0, 0, 150), bg_rect, border_radius=5)
        
        # 메시지 출력
        screen.blit(msg_surf, msg_rect)
        
        # 타이머 감소 (매 프레임마다 1씩 줄어듦)
        message_timer -= 1

    if show_tutorial:
        draw_tutorial(screen, bold_font)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
