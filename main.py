import pygame
import random
import os


# 遊戲設定
FPS = 60
WIDTH = 500
HEIGHT = 600

BLACK = (0,0,0)
WHITE = (255,255,255)
GREEN = (0,255,0)
RED = (255,0,0)
YELLOW = (255,255,0)


# 遊戲初始化 & 創建視窗
pygame.init()
pygame.mixer.init()    #初始化音效部分
screen = pygame.display.set_mode((WIDTH, HEIGHT))  #畫面寬度, 高度
pygame.display.set_caption("Shooting game")   # 設定遊戲上方視窗名稱
clock = pygame.time.Clock()



# 載入圖片
background_img = pygame.image.load(os.path.join("img", "background.png")).convert()   #os.path => 目前python檔案位置  join => img資料夾中的background.png
player_img = pygame.image.load(os.path.join("img", "player.png")).convert()
player_mini_img = pygame.transform.scale(player_img, (25,19))       #顯示生命值的小飛船圖片
player_mini_img.set_colorkey(BLACK)
pygame.display.set_icon(player_mini_img)      #設定遊戲左上角小圖示
#rock_img = pygame.image.load(os.path.join("img", "rock.png")).convert()
rock_imgs = []
for i in range(7):
    rock_imgs.append(pygame.image.load(os.path.join("img", f"rock{i}.png")).convert())
bullet_img = pygame.image.load(os.path.join("img", "bullet.png")).convert()

font_name = pygame.font.match_font('arial')     #引入字體
def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)      #鋸齒(True)&反鋸齒(False)
    text_rect = text_surface.get_rect()
    text_rect.centerx = x
    text_rect.top = y
    surf.blit(text_surface, text_rect)

explosion_anime = {}                    #引入爆炸動畫 (多個圖片連續撥放=>動畫)
explosion_anime['lg'] = []
explosion_anime['sm'] = []
explosion_anime['player'] = []          #載入死亡爆炸動畫
for i in range(9):
    explosion_img = pygame.image.load(os.path.join("img", f"expl{i}.png")).convert()
    explosion_img.set_colorkey(BLACK)
    explosion_anime['lg'].append(pygame.transform.scale(explosion_img, (75,75)))
    explosion_anime['sm'].append(pygame.transform.scale(explosion_img, (30,30)))

    player_explosion_img = pygame.image.load(os.path.join("img", f"player_expl{i}.png")).convert()
    player_explosion_img.set_colorkey(BLACK)
    explosion_anime['player'].append(player_explosion_img)

power_imgs = {}
power_imgs['shield'] = pygame.image.load(os.path.join("img", "shield.png")).convert()
power_imgs['gun'] = pygame.image.load(os.path.join("img", "gun.png")).convert()






#載入音效
shoot_sound = pygame.mixer.Sound(os.path.join("sound", "shoot.wav"))
shoot_sound.set_volume(0.7)   #調整音量

explode_sounds = [
    pygame.mixer.Sound(os.path.join("sound", "expl0.wav")),
    pygame.mixer.Sound(os.path.join("sound", "expl1.wav"))
    ]
explode_sounds[0].set_volume(0.7)
explode_sounds[1].set_volume(0.7)

gun_sound = pygame.mixer.Sound(os.path.join("sound", "pow1.wav"))
shield_sound = pygame.mixer.Sound(os.path.join("sound", "pow0.wav"))


die_sound = pygame.mixer.Sound(os.path.join("sound", "rumble.ogg"))
die_sound.set_volume(1)

pygame.mixer.music.load(os.path.join("sound", "background.ogg"))
pygame.mixer.music.set_volume(0.5)



def addnew_rock():          #加入新石頭
    r = ROCK()
    all_sprites.add(r)
    rocks.add(r)


def draw_health(surf, hp, x, y):
    if hp < 0:
        hp = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (hp/100)*BAR_LENGTH
    #fill_percent = (hp/100)+"%"  => 之後再看看如何把血量剩餘幾%的部分加上去...?
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)  #白色外框
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)           #綠色矩形生命條
    pygame.draw.rect(surf, GREEN, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)            # 2像素 若沒寫則會被填滿


def draw_lives(surf, lives, img, x, y):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 30*i       #間隔30象素畫一個小飛船生命值圖
        img_rect.y = y
        surf.blit(img, img_rect)


def draw_init():
    screen.blit(background_img, (0,0))
    draw_text(screen, "Space fight", 64, WIDTH/2, HEIGHT/4)
    draw_text(screen, "Array key to move.", 22, WIDTH/2, HEIGHT/2)
    draw_text(screen, "space key to shoot bullet.", 22, WIDTH/2, HEIGHT/2+30)
    draw_text(screen, "Press any key to start the game", 18, WIDTH/2, HEIGHT*3/4)
    pygame.display.update()
    waiting = True      
    while waiting:      #判定玩家是否已按任意鍵開始遊戲
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return True
            elif event.type == pygame.KEYUP:  #當按鍵按下去後鬆開時  (KEYDOWN則是按鍵按下去時就判定)
                waiting = False
                return False




class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player_img, (50,40))  #轉換圖片大小
        self.image.set_colorkey(BLACK)    #消除圖片周圍的黑色框框  => 把黑色變成透明
        #self.image.fill(GREEN)
        self.rect = self.image.get_rect() #將圖片框起來後設定屬性(如x,y top, botton, topright, center之類的屬性資料)
        self.radius = 20
        #pygame.draw.circle(self.image, RED, self.rect.center, self.radius)   #畫出圓形碰撞的範圍
        """self.rect.x = 200       # 移動到遊戲視窗內的(200,200)的位置  => 最左上角的點為(200,200)
        #self.rect.y = 200
        self.rect.center = (WIDTH/2, HEIGHT/2)    #使物件在遊戲視窗正中央的位置"""
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 8
        self.speedy = 8
        self.health = 100
        self.lives = 3
        self.hidden = False
        self.hide_time = 0
        self.gun = 1
        self.gun_time = 0
    
    def update(self):
        now = pygame.time.get_ticks()
        if self.gun > 1 and now - self.gun_time > 5000:
            self.gun -= 1
            self.gun_time = now

        if self.hidden and now - self.hide_time > 1000:
            self.hidden = False
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 10

        key_pressed = pygame.key.get_pressed() # => 會回傳True / False
        if key_pressed[pygame.K_RIGHT]:   #Keyboard_RIGHT => K_RIGHT   所以如果是要ABCD鍵的話=> pygame.K_a   space=>K_SPACE
            self.rect.x += self.speedx
        elif key_pressed[pygame.K_LEFT]:
            self.rect.x -= self.speedx
        elif key_pressed[pygame.K_DOWN]:
            self.rect.y += self.speedy 
        elif key_pressed[pygame.K_UP]:
            self.rect.y -= self.speedy
        
        if self.rect.right > WIDTH:       #卡在邊邊避免跑出screen範圍
            self.rect.right = WIDTH
        elif self.rect.left < 0:
            self.rect.left = 0

        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
        """
        if self.rect.top < 0:
            self.rect.top = 0 """
        
        """self.rect.x += 2    #當每次while迴圈執行update時  rect的座標往右(x+2)持續移動
        if self.rect.left > WIDTH:
            self.rect.right = 0   # 從再次左邊出現"""


    def shoot(self):     #射擊子彈
        if not(self.hidden):
            if self.gun == 1:
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
                shoot_sound.play()      #播放射擊音效
            elif self. gun >= 2:            #當子彈數大於2時
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.right, self.rect.centery)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                bullets.add(bullet1)
                bullets.add(bullet2)
                shoot_sound.play()    #播放射擊音效 

    def hide(self):
        self.hidden = True
        self.hide_time = pygame.time.get_ticks()
        self.rect.center = (WIDTH/2, -1000)

    def gunup(self):
        self.gun += 1
        self.gun_time = pygame.time.get_ticks()




class ROCK(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_origin = random.choice(rock_imgs)   #無失真圖片   #隨機挑列表中的一個圖片出來使用
        self.image_origin.set_colorkey(BLACK)
        self.image = self.image_origin.copy()
        #self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * 0.85 / 2)     #讓分數變成整數 而避免過多小數點
        #pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.x = random.randrange(0, WIDTH-self.rect.width)
        self.rect.y = random.randrange(-180,-100)
        self.speedx = random.randrange(-3,3)
        self.speedy = random.randrange(2,10)
        self.total_degree = 0
        self.rot_degree = random.randrange(-3,3)
    
    def rotate(self):
        self.total_degree += self.rot_degree
        self.total_degree = self.total_degree % 360     #讓圖片不會轉動超過360度
        self.image = pygame.transform.rotate(self.image_origin, self.total_degree)    #讓圖片轉動  但直接丟的話重複疊加會失真, 故創建一個原始圖片，每次轉動都針對原始圖片進行一次轉動 ex:第一次轉3度 第二次轉6度 第三次轉9度......
        center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = center  #持續重新定位中心點


    def update(self):
        self.rotate()
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT or self.rect.left > WIDTH or self.rect.right < 0:  #超出底部 左邊或右邊時重製位置
            self.rect.x = random.randrange(0, WIDTH-self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedx = random.randrange(-3,3)
            self.speedy = random.randrange(2,10)



class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.image.set_colorkey(BLACK)
        #self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = -10
    
    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:  #當超出上方螢幕時
            self.kill()   #從sprite群組內移除



class Explosion(pygame.sprite.Sprite):                  #爆炸動畫
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_anime[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50                #播放速度

    
    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1         #進到下一針(下一張圖片)
            if self.frame == len(explosion_anime[self.size]):     #若撥放到最後一張時
                self.kill()
            else:                                                 #若 尚未撥放到最後一張時
                self.image = explosion_anime[self.size][self.frame]
                center = self.rect.center
                self.rect = self.image.get_rect()
                self.rect.center = center  



class Power(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['shield', 'gun'])
        self.image = power_imgs[self.type]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 3
    
    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT:  #當掉出畫面時
            self.kill()             #從sprite群組內移除



all_sprites = pygame.sprite.Group()  #創建sprite群組
rocks = pygame.sprite.Group()
bullets = pygame.sprite.Group()
powers = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

for i in range(8):      #石頭數量
    addnew_rock()

score = 0
pygame.mixer.music.play(-1)  #重複播放次數 => -1 => 無限撥放
        



#遊戲迴圈
show_init = True
running = True
while running:
    if show_init:
        close = draw_init()     #設定  以避免直接在起使畫面直接關閉視窗時會出現錯誤
        if close:
            break
        show_init = False
        all_sprites = pygame.sprite.Group()  #創建sprite群組
        rocks = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        powers = pygame.sprite.Group()
        player = Player()
        all_sprites.add(player)
        for i in range(8):      #石頭數量
            addnew_rock()
        score = 0
    clock.tick(FPS)  #一秒中多最執行執行10次while迴圈 => 不同規格遊戲不會有不同的遊戲體驗


    #取得輸入
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False  #點叉叉後 => running變False => while迴圈結束 => 遊戲關閉
        elif event.type == pygame.KEYDOWN:   #若按下 任一按鍵時
            if event.key == pygame.K_SPACE:  #當按下空白鍵時
                player.shoot()               #執行class player內的shoot函式


    #更新遊戲
    all_sprites.update()
    hits = pygame.sprite.groupcollide(rocks, bullets, True, True)  #判斷石頭&子彈有無碰撞 => 若這兩個群組碰撞時  True => 刪除群組一or二 可填兩個boolean
    for hit in hits:                                        #當射擊到石頭時  補一顆石頭回去all_sprite和rocks群組內
        random.choice(explode_sounds).play()
        score += hit.radius                                 #根據石頭的半徑大小來增加分數
        expl = Explosion(hit.rect.center, 'lg')             #石頭&子彈爆炸動畫
        all_sprites.add(expl)
        if random.random() > 0.9:                           #掉落寶物機率10%
            pow = Power(hit.rect.center)
            all_sprites.add(pow)
            powers.add(pow)
        addnew_rock()                                       #把石頭加回來


    hits = pygame.sprite.spritecollide(player, rocks, True, pygame.sprite.collide_circle)  #預設碰撞範圍是矩形的 可另外改成圓形
    for hit in hits:                                        #撞到飛船的所有石頭
        addnew_rock()                                       #把撞到的石頭加回來
        player.health -= hit.radius
        expl = Explosion(hit.rect.center, 'sm')             #飛船&石頭爆炸動畫
        all_sprites.add(expl)
        if player.health <= 0:
            death_explosion = Explosion(player.rect.center, 'player')
            all_sprites.add(death_explosion)
            die_sound.play()
            player.lives -= 1           #死亡時生命值-1
            player.health = 100         #然後把生命值回滿
            player.hide()

    if player.lives == 0 and not(death_explosion.alive()):      #alive=> 判斷特定函式是否存在 存在=>True 不存在=> False 
        # running = False
        show_init = True

    
    hits = pygame.sprite.spritecollide(player, powers, True)  #判斷寶物與飛船是否有相撞
    for hit in hits:
        if hit.type == 'shield':
            shield_sound.play()
            player.health += 20
            if player.health > 100:
                player.health = 100
        elif hit.type == 'gun':
            player.gunup()
            gun_sound.play()


    #畫面顯示
    screen.fill(BLACK)  #填顏色 (R,G,B) 0~255
    screen.blit(background_img, (0,0))  #畫入...圖片在screen的 (x,y)位置
    all_sprites.draw(screen)   #將all_sprites群組內的東西畫入screen內
    draw_text(screen, str(score), 18, WIDTH/2, 10)    #載入分數介面
    draw_health(screen, player.health, 5, 15)
    draw_lives(screen, player.lives, player_mini_img, WIDTH-100, 15)
    pygame.display.update()

pygame.quit()

