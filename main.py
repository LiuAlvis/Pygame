#sprite
from tkinter import W
from turtle import Screen
import pygame
import random
import os

FPS = 60
WIDTH = 500
HEIGHT = 600

BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLUE = (0, 191, 255)

#遊戲初始化與創建視窗
pygame.init()
pygame.mixer.init() #音效初始化
screen = pygame.display.set_mode((WIDTH , HEIGHT)) #畫面高度與寬度
pygame.display.set_caption("SeaWar")
clock = pygame.time.Clock()

#載入圖片
background_img = pygame.image.load(os.path.join("img", "72.png")).convert()
player_img = pygame.image.load(os.path.join("img", "36.png")).convert()
shark_img = pygame.image.load(os.path.join("img", "shark.png")).convert()
bullet_img = pygame.image.load(os.path.join("img", "bullet.png")).convert()
# shark_imgs = []
# for i in range(7):                                                                          動畫加入
#     shark_imgs.append(pygame.image.load(os.path.join("img", f"shark{i}.png")).convert()

expl_anim = {}
expl_anim['lg'] = []
expl_anim['sm'] = []
for i in range(7):
    expl_img = pygame.image.load(os.path.join("img", f"expl{i}.png")).convert()
    expl_img.set_colorkey(WHITE)
    expl_anim['lg'].append(pygame.transform.scale(expl_img, (75, 75)))
    expl_anim['sm'].append(pygame.transform.scale(expl_img, (30, 30)))

#載入音樂
shoot_sound = pygame.mixer.Sound(os.path.join("sound", "shoot.mp3"))
expl_sounds = [
    pygame.mixer.Sound(os.path.join("sound", "bigexplosion.mp3")),
    pygame.mixer.Sound(os.path.join("sound", "smallexplosion.mp3"))
]
pygame.mixer.music.load(os.path.join("sound", "background.mp3"))
pygame.mixer.music.set_volume(0.5)

font_name = pygame.font.match_font('arial') #引入字體
def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE) #是否啟用反鋸齒
    text_rect = text_surface.get_rect()
    text_rect.centerx = x
    text_rect.top = y
    surf.blit(text_surface, text_rect)

def new_shark():
    shark = Shark()
    all_sprites.add(shark)
    sharks.add(shark)

def draw_health(surf, hp, x, y):
    if hp < 0:
        hp = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (hp/100)*BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, GREEN, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = player_img #pygame.transfrom.scale(player_img, (50, 38)) 可以改變圖片大小
        self.image.set_colorkey(BLACK ) #將圖片某色變成透明
        self.rect = self.image.get_rect()
        self.radius = self.rect.width / 2
       # pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 8
        self.health = 100

    def update(self):
        key_pressed = pygame.key.get_pressed() #鍵盤上按鍵是否有被按下
        if key_pressed[pygame.K_RIGHT]:
            self.rect.x += self.speedx
        if key_pressed[pygame.K_LEFT]:
            self.rect.x -= self.speedx   

        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        all_sprites.add(bullet)
        bullets.add(bullet)
        shoot_sound.play()
 
class Shark(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_ori = pygame.transform.scale(shark_img, (80, 80)) #可以改變圖片大小
        #self.image_ori = random.choice(shark_imgs) 加入隨機敵人圖片
        self.image_ori.set_colorkey(WHITE) #將圖片某色變成透明 
        self.image = self.image_ori.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width / 2)
        #pygame.draw.circle(self.image_ori, RED, self.rect.center, self.radius)
        self.rect.centerx = random.randrange(0, WIDTH - self.rect.width)
        self.rect.bottom = random.randrange(-180, -100)
        self.speedy = random.randrange(2, 5)
        self.speedx = random.randrange(-3, 3)
        self.total_degree = 0
        self.rot_degree = random.randrange(-3, 3)

    def rotate(self):
        self.total_degree += self.rot_degree
        self.total_degree = self.total_degree % 360
        self.image = pygame.transform.rotate(self.image_ori, self.total_degree)
        center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = center

    def update(self):
        self.rotate()
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        if self.rect.top > HEIGHT or self.rect.left > WIDTH or self.rect.right < 0:
            self.rect.centerx = random.randrange(0, WIDTH - self.rect.width)
            self.rect.bottom = random.randrange(-100, -40)
            self.speedy = random.randrange(2, 10)
            self.speedx = random.randrange(-3, 3)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.image.set_colorkey(WHITE)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = expl_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50 #設定延遲

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(expl_anim[self.size]):
                self.kill()
            else:
                self.image = expl_anim[self.size][self.frame]
                center = self.rect.center
                self.rect = self.image.get_rect()
                self.rect.center = center



all_sprites = pygame.sprite.Group()
sharks = pygame.sprite.Group()
bullets = pygame.sprite.Group()
player = Player()
all_sprites.add(player)
for i in range(8):
    new_shark()
score = 0
pygame.mixer.music.play(-1) #音樂部分的無限重複撥放

#遊戲迴圈
running = True
while running:
    clock.tick(FPS)
    #取得輸入
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot()

    #更新遊戲
    all_sprites.update()
    hits = pygame.sprite.groupcollide(sharks, bullets, True, True) #判定子彈碰觸後是否消失
    for hit in hits:
        random.choice(expl_sounds).play()
        score += hit.radius
        expl = Explosion(hit.rect.center, 'lg')
        all_sprites.add(expl)
        new_shark()

    hits = pygame.sprite.spritecollide(player, sharks, True, pygame.sprite.collide_circle) #判定鯊魚是否碰觸到烏龜
    for  hit in hits:
        new_shark()
        player.health -= hit.radius
        if player.health <= 0:
            running = False
 

    #畫面顯示
    screen.fill((BLUE))
    screen.blit(background_img, (0,0))
    all_sprites.draw(screen)
    draw_text(screen, str(score), 18, WIDTH/2, 10)
    draw_health(screen, player.health, 5, 10)
    pygame.display.update()




pygame.quit()