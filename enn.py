import pygame
import random
import math
from pygame.locals import *

# 전역 변수 설정
grass = (0, 178, 0)
white = (255, 255, 255)
brown = (139, 69, 19)
orange = (255, 165, 0)
dark_green = (0, 100, 0)
yellow = (255, 255, 0)
width, height = 640, 480
current_message = "조각된 호박을 착용했습니다!"
message_timer = 0
night_message_shown = False
last_attack_time = 0  # 마지막 공격 시간 (초 단위)
ATTACK_DELAY = 0.9  # 공격 딜레이

inventory = {"도끼" : 1, "가위": 1, "목재": 0, "호박": 0, "조각된 호박": 0, "보트": 0}
item_order = ["도끼", "가위", "목재", "호박", "조각된 호박", "보트"] 
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
    elif item_name == "조각된 호박":
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

    def update(self, keys, obstacles, endermen):
        old_x, old_y = self.rect.x, self.rect.y
        # X축 이동 및 충돌 검사
        if keys[K_a]: self.rect.x -= self.speed
        if keys[K_d]: self.rect.x += self.speed
        
        # 장애물 또는 엔더맨과 충돌 시 위치 복구
        if (self.rect.left < 0 or self.rect.right > width or 
            pygame.sprite.spritecollideany(self, obstacles) or 
            pygame.sprite.spritecollideany(self, endermen)):
            self.rect.x = old_x
            
        # Y축 이동 및 충돌 검사
        if keys[K_w]: self.rect.y -= self.speed
        if keys[K_s]: self.rect.y += self.speed
        
        # 장애물 또는 엔더맨과 충돌 시 위치 복구
        if (self.rect.top < 0 or self.rect.bottom > height or 
            pygame.sprite.spritecollideany(self, obstacles) or 
            pygame.sprite.spritecollideany(self, endermen)):
            self.rect.y = old_y
            
    def update_appearance(self):
        """호박 착용 여부에 따라 플레이어의 외형을 바꿉니다."""
        self.image.fill(self.base_color) # 기본 몸 색상
        
        if self.is_wearing_pumpkin:
            pygame.draw.rect(
                self.image,
                orange,
                [0, 0, self.rect.width, 16]
            )

            pygame.draw.rect(self.image, (0,0,0), [5,5,5,5])
            pygame.draw.rect(self.image, (0,0,0), [20,5,5,5])

            pygame.draw.line(self.image, (0,0,0), (7,13), (23,13), 2)
            

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

class DroppedItem(pygame.sprite.Sprite):
    def __init__(self, item_name, x, y):
        super().__init__()
        self.item_name = item_name
        self.image = pygame.Surface([20, 20], pygame.SRCALPHA)
        
        if item_name == "ender_eye":
            # ender_eye.png 로드 (없으면 기본 원 그리기)
            try:
                self.image = pygame.image.load("ender_eye.png")
                self.image = pygame.transform.scale(self.image, [20, 20])
            except:
                # 파일 없으면 기본 자주색 원 그리기
                pygame.draw.circle(self.image, (160, 80, 200), (10, 10), 8)
        elif item_name == "ender_pearl":
            pygame.draw.circle(self.image, (100, 200, 200), (10, 10), 8)
        else:
            # 기본 드롭 아이템 (흰색 사각형)
            pygame.draw.rect(self.image, (200, 200, 200), [2, 2, 16, 16])
        
        self.rect = self.image.get_rect(center=(x, y))
        self.vel = pygame.math.Vector2(random.uniform(-2, 2), random.uniform(-3, -0.5))
    
    def update(self):
        self.vel.y += 0.15  # 중력
        self.rect.x += self.vel.x
        self.rect.y += self.vel.y


class Entity(pygame.sprite.Sprite):
    def __init__(self, health_point, speed, drop_item, stance):
        super().__init__()
        self.health_point = health_point
        self.max_health = health_point
        self.speed = speed
        self.drop_item = drop_item
        self.stance = stance
        self.damage_cooldown = 0  # 피격 후 경직 시간
        self.knockback_vel = pygame.math.Vector2(0, 0)
        self.is_dead = False
        self.death_timer = 0
        self.death_tilt = 0  # 쓰러지는 각도
    
    def take_damage(self, amount, direction_from_x):
        """데미지를 입고 넉백과 피격 효과 적용"""
        if self.is_dead:
            return
        
        self.health_point -= amount
        self.damage_cooldown = 15  # 0.25초 경직
        
        # 넉백 방향 (반대 방향)
        knockback_direction = -1 if direction_from_x < self.rect.centerx else 1
        self.knockback_vel.x = knockback_direction * 6
        
        if self.health_point <= 0:
            self.is_dead = True
            self.death_timer = 30  # 사망 애니메이션 0.5초
    
    def update(self):
        """기본 엔티티 업데이트 (피격 효과, 넉백, 사망 처리)"""
        if self.damage_cooldown > 0:
            self.damage_cooldown -= 1
        
        # 넉백 감소
        self.knockback_vel.x *= 0.85
        self.rect.x += self.knockback_vel.x
        
        # 사망 상태
        if self.is_dead:
            self.death_timer -= 1
            self.death_tilt = min(90, (30 - self.death_timer) * 6)  # 쓰러지는 각도




class Enderman(Entity):
    def __init__(self):
        # 엔티티 속성
        super().__init__(
            health_point=40,
            speed=4,
            drop_item="ender_eye",
            stance=1
        )

        # 애니메이션 상태
        self.anim_tick = 0
        self.particle_timer = 0
        self.facing_right = True  # 좌우 방향 (True=오른쪽, False=왼쪽)

        # 기본 스프라이트 크기 고정
        self.image = pygame.Surface([30, 80], pygame.SRCALPHA)
        self.rect = self.image.get_rect()

        # 초기 랜더(애니메이션 오프셋 0)
        self.pose = 'front'  # 'front' or 'side' — 이동 방향에 따라 바뀜
        self._redraw(0, 0)

        # 위치를 화면 밖으로 랜덤 배치
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

    def _redraw(self, arm_offset, leg_offset):
        """이미지를 재생성합니다. arm_offset은 팔 흔들림(픽셀), leg_offset은 다리 분리/흔들림"""
        surf = pygame.Surface([30, 80], pygame.SRCALPHA)

        # 피격 효과 (손상 시 붉은 색으로 변함)
        tint_alpha = 0
        if self.damage_cooldown > 0:
            tint_alpha = int(150 * (self.damage_cooldown / 15))  # 최대 150 알파

        # 머리
        head_color = (12, 12, 12)
        if self.damage_cooldown > 0:
            head_color = (min(255, 12 + 100), 12, 12)  # 붉은 색 오버레이
        
        pygame.draw.rect(surf, head_color, [7, 0, 16, 14])
        pygame.draw.rect(surf, (min(255, 24 + 50), 24, 24) if self.damage_cooldown > 0 else (24, 24, 24), [8, 1, 14, 12])
        
        # 머리 텍스처
        for hx in range(9, 21, 5):
            for hy in range(2, 7, 5):
                pygame.draw.rect(surf, (4, 4, 4), [hx, hy, 2, 2])

        if self.pose == 'front':
            # 눈
            pygame.draw.rect(surf, (255, 210, 230), [7, 6, 6, 3])  # 왼쪽 베이스
            pygame.draw.rect(surf, (200, 50, 200), [9, 6, 2, 3])   # 왼쪽 중앙
            pygame.draw.rect(surf, (255, 230, 240), [8, 6, 1, 1])  # 하이라이트
            pygame.draw.rect(surf, (255, 210, 230), [17, 6, 6, 3]) # 오른쪽 베이스
            pygame.draw.rect(surf, (200, 50, 200), [19, 6, 2, 3])  # 오른쪽 중앙
            pygame.draw.rect(surf, (255, 230, 240), [19, 6, 1, 1]) # 하이라이트

            # 목
            pygame.draw.rect(surf, (16, 16, 16), [8, 14, 14, 2])

            # 몸통
            torso_x, torso_y, torso_w, torso_h = 9, 16, 12, 16
            torso_color = (min(255, 10 + 100), 10, 10) if self.damage_cooldown > 0 else (10, 10, 10)
            pygame.draw.rect(surf, torso_color, [torso_x, torso_y, torso_w, torso_h])
            # 몸통
            torso_spots = [(10, 19), (14, 23), (12, 28)]
            for sx, sy in torso_spots:
                pygame.draw.rect(surf, (2, 2, 2), [sx, sy, 2, 2])

            # 팔
            arm_h = 60
            arm_start_y = 16
            arm_color = (min(255, 10 + 100), 10, 10) if self.damage_cooldown > 0 else (10, 10, 10)
            pygame.draw.rect(surf, arm_color, [0 + arm_offset, arm_start_y, 3, arm_h])
            pygame.draw.rect(surf, arm_color, [27 - arm_offset, arm_start_y, 3, arm_h])
            for ay in range(arm_start_y, arm_start_y + arm_h, 10):
                pygame.draw.rect(surf, (3, 3, 3), [1 + arm_offset, ay, 2, 3])
                pygame.draw.rect(surf, (3, 3, 3), [28 - arm_offset, ay, 2, 3])

            # 다리
            leg_h = 48
            leg_start_y = torso_y + torso_h
            leg_color = (min(255, 10 + 100), 10, 10) if self.damage_cooldown > 0 else (10, 10, 10)
            pygame.draw.rect(surf, leg_color, [9 - leg_offset, leg_start_y, 4, leg_h])
            pygame.draw.rect(surf, leg_color, [17 + leg_offset, leg_start_y, 4, leg_h])
            pygame.draw.rect(surf, (3, 3, 3), [9 - leg_offset, leg_start_y + 12, 4, 2])
            pygame.draw.rect(surf, (3, 3, 3), [17 + leg_offset, leg_start_y + 14, 4, 2])

        else:  # side pose
            # 눈
            pygame.draw.rect(surf, (255, 210, 230), [10, 6, 8, 3])
            pygame.draw.rect(surf, (200, 50, 200), [12, 6, 4, 3])

            # 목/어깨
            pygame.draw.rect(surf, (16, 16, 16), [10, 14, 12, 3])

            # 몸통
            torso_x, torso_y, torso_w, torso_h = 12, 16, 8, 18
            torso_color = (min(255, 10 + 100), 10, 10) if self.damage_cooldown > 0 else (10, 10, 10)
            pygame.draw.rect(surf, torso_color, [torso_x, torso_y, torso_w, torso_h])

            # 팔
            arm_h = 44
            shoulder_x = torso_x + torso_w  # 오른쪽 어깨 쪽에서 내리는 형태
            arm_start_y = torso_y
            arm_color = (min(255, 10 + 100), 10, 10) if self.damage_cooldown > 0 else (10, 10, 10)
            # 그리기
            for i in range(arm_h // 6):
                dy = i * 6
                dx = int(i * 0.6) + int(arm_offset * 0.3)
                pygame.draw.rect(surf, arm_color, [shoulder_x + dx, arm_start_y + dy, 4, 5])
                pygame.draw.rect(surf, (3, 3, 3), [shoulder_x + dx + 1, arm_start_y + dy + 1, 2, 2])

            # 다리
            leg_h = 48
            leg_start_y = torso_y + torso_h
            leg_color = (min(255, 10 + 100), 10, 10) if self.damage_cooldown > 0 else (10, 10, 10)
            pygame.draw.rect(surf, leg_color, [torso_x + 1 + leg_offset, leg_start_y, 6, leg_h])
            pygame.draw.rect(surf, (3, 3, 3), [torso_x + 1 + leg_offset, leg_start_y + 14, 6, 2])

        # 어깨/허리 음영 (공통)
        pygame.draw.rect(surf, (18, 18, 18), [8, torso_y - 1, 14, 1])
        pygame.draw.rect(surf, (8, 8, 8), [8, leg_start_y - 1, 14, 1])

        self.image = surf

    def update(self, player):
        # 1. 부모 업데이트 (여기서 self.death_tilt가 계산됨)
        super().update()

        # 애니메이션 틱 계산
        self.anim_tick += 1
        arm_offset = int(math.sin(self.anim_tick * 0.16) * 3)
        leg_offset = int(math.sin(self.anim_tick * 0.18) * 2)

        # ----------------------------------------------------
        # [수정됨] 사망 처리 로직을 가장 먼저 수행합니다.
        # ----------------------------------------------------
        if self.is_dead:
            # 1. 기본 그림 그리기
            self._redraw(arm_offset, leg_offset)
            
            # 2. 기울기(death_tilt) 적용하여 이미지 회전시키기
            #    (중심축 기준 회전 시 위치가 틀어질 수 있어 rect 중심 보정)
            old_center = self.rect.center
            self.image = pygame.transform.rotate(self.image, -self.death_tilt)
            self.rect = self.image.get_rect(center=old_center)

            # 3. 사망 타이머 종료 시 아이템 드롭 및 소멸
            if self.death_timer <= 0:
                drop = DroppedItem(self.drop_item, self.rect.centerx, self.rect.centery)
                all_sprites_list.add(drop)
                dropped_items.add(drop)
                
                # 사망 이펙트 (파티클)
                for _ in range(8):
                    angle = random.uniform(0, math.tau)
                    speed = random.uniform(1, 3)
                    vx = math.cos(angle) * speed
                    vy = math.sin(angle) * speed
                    particles.append(Particle(self.rect.centerx, self.rect.centery, vx, vy, random.randint(20, 40), random.randint(1, 2), (255, 255, 255)))
                
                self.kill()
            
            # 죽었으면 아래 이동 코드는 실행하지 않고 리턴
            return

        # ----------------------------------------------------
        # [수정됨] 피격 경직 처리
        # ----------------------------------------------------
        if self.damage_cooldown > 0:
            self._redraw(arm_offset, leg_offset)
            return

        # ----------------------------------------------------
        # 이동 로직 (살아있고 경직이 아닐 때만 실행)
        # ----------------------------------------------------
        player_pos = pygame.math.Vector2(player.rect.center)
        enderman_pos = pygame.math.Vector2(self.rect.center)
        direction = (player_pos - enderman_pos)
        
        # 호박 착용 시 추격 중지
        if player.is_wearing_pumpkin:
            direction = pygame.math.Vector2(0, 0)

        if direction.length() > 0:
            direction = direction.normalize()
            
            # X축 이동
            self.rect.x += direction.x * self.speed
            if self.rect.colliderect(player.rect):
                self.rect.x -= direction.x * self.speed

            # Y축 이동
            self.rect.y += direction.y * self.speed
            if self.rect.colliderect(player.rect):
                self.rect.y -= direction.y * self.speed

            # 방향에 따른 포즈 설정
            if abs(direction.x) > abs(direction.y):
                self.pose = 'side'
                self.facing_right = direction.x > 0
            else:
                self.pose = 'front'
        else:
            self.pose = 'front'

        # 최종 그리기
        self._redraw(arm_offset, leg_offset)

        # 측면 반전
        if self.pose == 'side' and not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)

        # 생존 중 파티클 생성
        self.particle_timer += 1
        if self.particle_timer >= 6:
            self.particle_timer = 0
            if random.random() < 0.8:
                spawn_enderman_particle(self.rect.centerx + random.randint(-8, 8),
                                        self.rect.centery + random.randint(-20, 20))


class Particle:
    def __init__(self, x, y, vx, vy, life, size, color):
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(vx, vy)
        self.life = life
        self.max_life = life
        self.size = size
        self.color = color

    def update(self):
        self.pos += self.vel
        self.vel.y -= 0.02
        self.vel *= 0.995
        self.life -= 1

    def draw(self, surf):
        if self.life <= 0:
            return
        alpha = max(0, int(255 * (self.life / self.max_life)))
        s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (self.color[0], self.color[1], self.color[2], alpha), (self.size, self.size), self.size)
        surf.blit(s, (self.pos.x - self.size, self.pos.y - self.size))


def spawn_enderman_particle(x, y):
    for _ in range(random.randint(1, 3)):
        angle = random.uniform(0, math.tau)
        speed = random.uniform(0.2, 1.0)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed - 0.3
        life = random.randint(30, 60)
        size = random.randint(1, 3)
        color = (170, 100, 200)  # purple
        particles.append(Particle(x, y, vx, vy, life, size, color))


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
dropped_items = pygame.sprite.Group()
particles = []  # global particle list for enderman effects

player = Player((167, 255, 100), 30, 30)
craft_table = CraftingTable()
enderman_spawn_counter = 0  # 엔더맨 스폰 카운터

def reset_game():
    global inventory, selected_slot, crafting_open, boat_crafted, is_night, message_timer, show_tutorial, enderman_spawn_counter
    
    # 1. 변수 초기화
    inventory = {"도끼": 1, "가위": 1, "목재": 0, "호박": 0, "조각된 호박": 0, "보트": 0}
    selected_slot = 0
    crafting_open = False
    boat_crafted = False
    is_night = False
    message_timer = 0
    show_tutorial = True # 재시작 시 튜토리얼부터 다시 보여줄지 선택
    enderman_spawn_counter = 0
    
    all_sprites_list.empty()
    obstacles.empty()
    endermen.empty()
    dropped_items.empty()
    
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

night_message_shown = False

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
                if boat_crafted and not is_night:
                    is_night = True
                    boat_crafted = False

                    if not night_message_shown:
                        current_message = "밤이 되었습니다..."
                        message_timer = 120
                        night_message_shown = True

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
                if craft_table.rect.collidepoint(mouse_pos):
                    dist = player_pos.distance_to(craft_table.rect.center)
                    if dist <= 100:
                        if crafting_open:
                            crafting_open = False
                            if boat_crafted:
                                is_night = True
                                message_timer = 90
                                boat_crafted = False
                        else:
                            crafting_open = True
                        continue
                    
                elif (
                    not crafting_open
                    and item_order[selected_slot] == "조각된 호박"
                    and inventory["조각된 호박"] >0
                    and not player.is_wearing_pumpkin
                ):
                    inventory["조각된 호박"] -= 1
                    player.is_wearing_pumpkin = True
                    player.update_appearance()

                    current_message = "조각된 호박을 착용했습니다!"
                    message_timer = 120

                    continue
                elif (
                    not crafting_open
                    and item_order[selected_slot] == "조각된 호박"
                    and player.is_wearing_pumpkin
                ):
                    inventory["조각된 호박"] += 1
                    player.is_wearing_pumpkin = False
                    player.update_appearance()
                    current_message = "조각된 호박을 벗었습니다!"
                    message_timer = 120 #호박 벗기
                    continue                    
                        

                # 2. 가위를 들고 호박 우클릭 (조각하기)
                if item_order[selected_slot] == "가위":
                    for obj in obstacles:
                        if hasattr(obj, 'obs_type') and obj.obs_type == "pumpkin":
                            if obj.rect.collidepoint(mouse_pos):
                                dist = player_pos.distance_to(obj.rect.center)
                                if dist <= 100:
                                    obj.kill()
                                    inventory["조각된 호박"] += 1
                                    break
                            
            elif event.button == 1:
                 # 엔티티(엔더맨) 공격 로직
                 # 공격 데미지 계산 (선택 아이템에 따라)
                 attack_damage = 1  # 기본값 (빈 칸)
                 is_axe_attack = item_order[selected_slot] == "도끼"
                 if is_axe_attack:
                     attack_damage = 9
                 
                 # 도끼로 공격할 때만 딜레이 확인
                 current_time = pygame.time.get_ticks() / 1000.0
                 if is_axe_attack:
                     if current_time - last_attack_time >= ATTACK_DELAY:
                         last_attack_time = current_time
                         # 엔더맨 공격
                         for enderman in endermen:
                             if enderman.rect.collidepoint(mouse_pos):
                                 enderman.take_damage(attack_damage, mouse_pos[0])
                 else:
                     # 맨손 공격은 딜레이 없음
                     for enderman in endermen:
                         if enderman.rect.collidepoint(mouse_pos):
                             enderman.take_damage(attack_damage, mouse_pos[0])
                 
                 # 도끼로 장애물 채집
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
        player.update(keys, obstacles, endermen)
        
        # 밤에 엔더맨 스폰 로직
        if is_night:
            enderman_spawn_counter += 1
            # 300프레임마다 (약 5초마다) 확률적으로 엔더맨 스폰
            if enderman_spawn_counter >= 300:
                # 엔더맨이 2마리 이하일 때만 스폰
                if len(endermen) < 1 and random.randint(1, 100) <= 30:  # 30% 확률
                    enderman = Enderman()
                    all_sprites_list.add(enderman)
                    endermen.add(enderman)
                enderman_spawn_counter = 0
            
            # 엔더맨 이동 (플레이어 방향으로)
            # [수정 완료] 수동 이동 코드를 지우고, 클래스의 update 함수를 호출
            endermen.update(player)  # <-- 이 한 줄이 핵심입니다!

            # 파티클 업데이트 및 소거
            for p in particles[:]:
                p.update()
                if p.life <= 0:
                    particles.remove(p)
            
            # 드롭된 아이템 업데이트
            for item in dropped_items:
                item.update()

    screen.fill(grass)
    all_sprites_list.draw(screen)
    dropped_items.draw(screen)

    if is_night:
        night_overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        night_overlay.fill((0, 0, 40, 160))
        screen.blit(night_overlay, (0, 0))
        # 엔더맨 파티클 렌더링
        for p in particles:
            p.draw(screen)

    if crafting_open:
        draw_crafting_ui(screen, font)
    
    draw_hotbar(screen, inventory, font)

    if selected_slot < len(item_order):
        current_item = item_order[selected_slot]
        msg = bold_font.render(f"선택됨: {current_item}", True, white)
        screen.blit(msg, (BAR_X, BAR_Y - 30))

    if message_timer > 0:
        # 텍스트 렌더링
        msg_surf = bold_font.render(current_message, True, yellow)
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



