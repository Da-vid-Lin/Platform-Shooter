#Importing all the libaries needed
import sys
import pygame
from pygame.locals import QUIT
import time

#Initialising pygame
pygame.init()

#Initialising the mixer for sounds
pygame.mixer.init

#Data constants that will be used  a lot
Font = pygame.font.SysFont(None,30)
Red = (255,0,0)
Blue = (0,0,255)
Black = (0,0,0)
White = (255,255,255)
Grey = (128,128,128)

#Data constants specific for game
GAME_NAME = "Ginklu Karas"
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
Fps = 60
Gravity = 0.75

#Music constants
track0 = "Music/menu.mp3"
track1 = "Music/map1.mp3"
track2 = "Music/map2.mp3"
track3 = "Music/map3.mp3"

#Soundeffect constants
playerhit = pygame.mixer.Sound("Sound/playerhit.mp3")
deathsound = pygame.mixer.Sound("Sound/deathsound.mp3")
menuclick = pygame.mixer.Sound("Sound/menuclick.mp3")
shoot = pygame.mixer.Sound("Sound/shoot.mp3")

sounds = [playerhit, deathsound, menuclick, shoot]

#Backgrounds constants
menubg = pygame.transform.scale(pygame.image.load("Background/menubg.jpg"), (1280,720))
optionsbg = pygame.transform.scale(pygame.image.load("Background/optionsbg.webp"), (1280,720))
controlsbg = pygame.transform.scale(pygame.image.load("Background/controlsbg.png"), (1280,720))
gunbg = pygame.transform.scale(pygame.image.load("Background/gunbg.jpg"), (1280,720))
mapsbg = pygame.transform.scale(pygame.image.load("Background/mapsbg.png"), (1280,720))
map1bg = pygame.transform.scale(pygame.image.load("Background/map1bg.webp"), (1280,720))
map2bg = pygame.transform.scale(pygame.image.load("Background/map2bg.png"), (1280,720))
map3bg = pygame.transform.scale(pygame.image.load("Background/map3bg.webp"), (1280,720))
overbg = pygame.transform.scale(pygame.image.load("Background/overbg.jpg"), (1280,720))


pygame.mixer.music.load(track0)
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.6)

def SwitchLeft(index):
    if index == 0:
        return 2
    else:
        return (index-1)
    
def SwitchRight(index):
    if index == 2:
        return 0
    else:
        return (index+1)


#Button class
def text_size(text, font):
    textobj = font.render(text, 1, (255,255,255))
    textrect = textobj.get_rect()
    return textrect.width, textrect.height
def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)
    return textrect.width, textrect.height
class Button:
    def __init__(self, screen, font, text, position, colour, boxcolour, wantbox):
        self.screen = screen
        self.font = font
        self.text = text
        self.vertical = position[0]
        self.horizontal = position[1]
        self.colour = colour
        self.boxcolour = boxcolour
        self.wantbox = wantbox
                
        self.size = text_size(self.text, self.font)
        self.pos = ((SCREEN_WIDTH - self.size[0])/2)+self.horizontal
        self.box = pygame.Rect(self.pos-5, self.vertical, self.size[0]+10, 50)
    
    def draw(self):
        if self.wantbox:
            pygame.draw.rect(self.screen, self.boxcolour, self.box)
        draw_text(self.text, self.font, self.colour, self.screen, self.pos, self.vertical+15)
                
    def collision(self):
        MouseX,MouseY = pygame.mouse.get_pos()
        if self.box.collidepoint((MouseX,MouseY)):
            menuclick.play()
            return True

    def hovered(self):
        MouseX,MouseY = pygame.mouse.get_pos()
        if self.box.collidepoint((MouseX,MouseY)):
            self.boxcolour = Red
        else:
            self.boxcolour = Blue

#Sprite/Bullet/Player class
class sprite(pygame.sprite.Sprite):
    def __init__(self, screen, x, y, scale, speed, playerstats):
        pygame.sprite.Sprite.__init__(self)
        self.screen = screen
        self.speed = speed
        self.stats = playerstats
        self.bullets = pygame.sprite.Group()
        self.direction = 1
        self.jump = False
        self.down = False
        self.vel_y = 0
        img = playerstats.image
        self.image = pygame.transform.scale(img, (140 * scale, 140 * scale))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.on_platform = False
        self.alive = True

    def move(self, moving_left, moving_right, platforms):
        if moving_left:
            self.rect.x -= self.speed
            self.direction = -1
        if moving_right:
            self.rect.x += self.speed
            self.direction = 1

        self.vel_y += Gravity
        self.rect.y += self.vel_y

        on_platform = False

        #player doesnt fall through platform
        for platform_rect in platforms:
            if self.rect.colliderect(platform_rect):
                if self.vel_y > 0:  
                    self.rect.y = platform_rect.y - self.rect.height
                    self.vel_y = 0
                    on_platform = True
                    break

        #player doesnt fall off map yet
        if self.rect.y > SCREEN_HEIGHT - self.rect.height:
            deathsound.play()
            #self.rect.y = SCREEN_HEIGHT- self.rect.height #Allows the player to fall off map now
            self.vel_y = 0
            on_platform = False
            self.alive = False

        #jump
        if self.jump and on_platform:
            self.vel_y = -15
            self.jump = False  

        if self.down and on_platform:
            self.rect.y += 100
            self.down = False

        self.jump = False
        self.down = False
        self.on_platform = on_platform
        
    #draw sprite
    def draw(self):
        if self.direction == 1:
            self.screen.blit(self.image, self.rect)
        else:
            flipped_image = pygame.transform.flip(self.image, True, False)
            self.screen.blit(flipped_image, self.rect)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, screen, x, y, direction, speed):
        pygame.sprite.Sprite.__init__(self)
        self.screen = screen
        self.speed = speed
        bullet_img = pygame.image.load("Images/bulletimage.png")
        self.image = pygame.transform.scale(bullet_img, (20,20))
        self.image = pygame.transform.rotate(self.image, 90)
        self.direction = 1
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction
  
    #drawing bullet
    def draw(self):
        if self.direction == -1:
            self.screen.blit(self.image, self.rect)
        else:
            flipped_image = pygame.transform.flip(self.image, True, False)
            self.screen.blit(flipped_image, self.rect)

    #move bullet
    def update(self):
        self.rect.x += self.speed * self.direction
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()
            
class Player:
   def __init__(self, image, gun, max_bullets, strength, reload_time, speed):
        self.message = ""
        self.image = image
        self.gun = gun
        self.max_bullets = max_bullets
        self.reload_time = reload_time
        self.strength = strength
        self.speed = speed
        self.bullets_left = max_bullets
        self.reload_count = 0
        self.reloading = False
        self.moving_left = False
        self.moving_right = False

#Main game class
class MainGame:
    def __init__(self):
        pygame.display.set_caption(GAME_NAME)
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.state = "Menu"
        self.click = False
        self.player = ""
        self.enemy = ""
        self.playerchoice = 0
        self.enemychoice = 0
        self.display = "Game"
        self.cooldown = 150
        self.platforms = ""
        self.backgroundimage = ""
        self.sound = 3
        self.music = 3
        self.countdown = ""

    def events(self):
        #All the keyboard/mouse inputs etc here
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                pygame.display.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.click = True

            if event.type == pygame.KEYDOWN and self.state == "Game" and self.countdown <= time.time():
                #Player 1 movement
                if event.key == pygame.K_a:
                    self.player.stats.moving_left = True
                if event.key == pygame.K_d:
                    self.player.stats.moving_right = True
                if event.key == pygame.K_w:
                    self.player.jump = True
                if event.key == pygame.K_s:
                    self.player.down = True
                
                #Player 2 movement
                if event.key == pygame.K_LEFT:
                    self.enemy.stats.moving_left = True
                if event.key == pygame.K_RIGHT:
                    self.enemy.stats.moving_right = True
                if event.key == pygame.K_UP:
                    self.enemy.jump = True
                if event.key == pygame.K_DOWN:
                    self.enemy.down = True

                #Shooting bullets
                if event.key == pygame.K_SPACE and len(self.player.bullets) < self.player.stats.max_bullets:
                    if self.player.stats.bullets_left > 0:
                        new_bullet = Bullet(self.screen, self.player.rect.centerx, self.player.rect.centery, self.player.direction, self.player.stats.speed)
                        self.player.bullets.add(new_bullet)
                        self.player.stats.bullets_left -= 1
                        shoot.play()

                if event.key == pygame.K_r and self.player.stats.bullets_left < self.player.stats.max_bullets:
                    self.player.stats.reloading = True

                if event.key == pygame.K_o and len(self.enemy.bullets) < self.enemy.stats.max_bullets:
                    if self.enemy.stats.bullets_left > 0:
                        new_bullet = Bullet(self.screen, self.enemy.rect.centerx, self.enemy.rect.centery, self.enemy.direction, self.enemy.stats.speed)
                        self.enemy.bullets.add(new_bullet)
                        self.enemy.stats.bullets_left -= 1
                        shoot.play()

                if event.key == pygame.K_p and self.enemy.stats.bullets_left < self.enemy.stats.max_bullets:
                    self.enemy.stats.reloading = True
                    
            #Stopping player movement
            if event.type == pygame.KEYUP and self.state == "Game":
                if event.key == pygame.K_a:
                    self.player.stats.moving_left = False
                if event.key == pygame.K_d:
                    self.player.stats.moving_right = False

                if event.key == pygame.K_LEFT:
                    self.enemy.stats.moving_left = False
                if event.key == pygame.K_RIGHT:   
                    self.enemy.stats.moving_right = False

    def menu(self):
        #All code for menu here
        self.screen.blit(menubg, (0, 0))
        GameDisplay = Button(self.screen, Font, f"Main Menu", [100,0], White, Blue, False)
        GameDisplay.draw()
        
        Start = Button(self.screen, Font, f"Start", [180,0], White, Blue, True)
        Start.hovered()
        Start.draw()

        Options = Button(self.screen, Font, f"Options", [240,0], White, Blue, True)
        Options.hovered()
        Options.draw()
        
        Controls = Button(self.screen, Font, f"Controls", [300,0], White, Blue, True)
        Controls.hovered()
        Controls.draw()

        Exit = Button(self.screen, Font, f"Exit", [360,0], White, Blue, True)
        Exit.hovered()
        Exit.draw()
        
        if self.click:
            if Start.collision():
                self.state = "Guns"
            if Options.collision():
                self.state = "Options"
            if Controls.collision():
                self.state = "Controls"
            if Exit.collision():
                run = False
                pygame.quit()
                pygame.display.quit()
                sys.exit()
            self.click = False
        
    def options(self):
        #All code for options page here
        self.screen.blit(optionsbg, (0, 0))
        GameDisplay = Button(self.screen, Font, f"Options", [100,0], White, Blue, False)
        GameDisplay.draw()

        Sound = Button(self.screen, Font, f"Sound", [220,-100], White, Blue, False)
        Sound.draw()

        Sound1 = Button(self.screen, Font, f"1", [220,-50], White, Blue, True)
        Sound1.draw()

        Sound2 = Button(self.screen, Font, f"2", [220,0], White, Blue, True)
        Sound2.draw()

        Sound3 = Button(self.screen, Font, f"3", [220,50], White, Blue, True)
        Sound3.draw()

        Music = Button(self.screen, Font, f"Music", [280,-100], White, Blue, False)
        Music.draw()

        Music1 = Button(self.screen, Font, f"1", [280,-50], White, Blue, True)
        Music1.draw()

        Music2 = Button(self.screen, Font, f"2", [280,0], White, Blue, True)
        Music2.draw()

        Music3 = Button(self.screen, Font, f"3", [280,50], White, Blue, True)
        Music3.draw()

        Back = Button(self.screen, Font, f"Back", [660,0], White, Blue, True)
        Back.hovered()
        Back.draw()

        if self.sound == 3:
            Sound3.boxcolour = (0,255,255)
            Sound3.draw()
        elif self.sound == 2:
            Sound2.boxcolour = (0,255,255)
            Sound2.draw()
        elif self.sound == 1:
            Sound1.boxcolour = (0,255,255)
            Sound1.draw()

        if self.music == 3:
            Music3.boxcolour = (0,255,255)
            Music3.draw()
        elif self.music == 2:
            Music2.boxcolour = (0,255,255)
            Music2.draw()
        elif self.music == 1:
            Music1.boxcolour = (0,255,255)
            Music1.draw()
        
        if self.click:
            if Back.collision():
                self.state = "Menu"
            if Sound1.collision():
                self.sound = 1
                for sound in sounds:
                    sound.set_volume(0)
            if Sound2.collision():
                self.sound = 2
                for sound in sounds:
                    sound.set_volume(0.5)
            if Sound3.collision():
                self.sound = 3
                for sound in sounds:
                    sound.set_volume(1)
            if Music1.collision():
                self.music = 1
                pygame.mixer.music.set_volume(0)
            if Music2.collision():
                self.music = 2
                pygame.mixer.music.set_volume(0.3)
            if Music3.collision():
                self.music = 3
                pygame.mixer.music.set_volume(0.6)
            self.click = False

    def controls(self):
        #All code for viewing controls here
        self.screen.blit(controlsbg, (0, 0))
        GameDisplay = Button(self.screen, Font, f"Controls", [100,0], White, Blue, False)
        GameDisplay.draw()
        
        Back = Button(self.screen, Font, f"Back", [660,0], White, Blue, True)
        Back.hovered()
        Back.draw()
        
        if self.click:
            if Back.collision():
                self.state = "Menu"
            self.click = False
            
    def guns(self):
        #All code for choosing guns here
        self.screen.blit(gunbg, (0, 0))
        GameDisplay = Button(self.screen, Font, f"Gun Choices", [100,0], White, Blue, False)
        GameDisplay.draw()

        Start = Button(self.screen, Font, f"Next", [640,0], White, Blue, True)
        Start.hovered()
        Start.draw()

        #images - gun name - total bullets - bullet strength - reload time - bullet speed

        O = [["Images/pistolman.png","Pistol",6,30,90,12],
             ["Images/assaultrifleman.png","Assault",20,20,100,8],
             ["Images/sniperman.png","Sniper",1,80,150,50]]

        PlayerImage = pygame.image.load(O[self.playerchoice][0])
        PlayerImage = pygame.transform.scale(PlayerImage, (80,80))

        EnemyImage = pygame.image.load(O[self.enemychoice][0])
        EnemyImage = pygame.transform.scale(EnemyImage, (80,80))

        self.screen.blit((PlayerImage),((SCREEN_WIDTH/2)-100-56,180))
        self.screen.blit((EnemyImage),((SCREEN_WIDTH/2)+100,180))

        Player1 = Button(self.screen, Font, f"Gun: {O[self.playerchoice][1]}", [260,-140], White, Blue, False).draw()
        Player1 = Button(self.screen, Font, f"Bullets: {O[self.playerchoice][2]}", [300,-140], White, Blue, False).draw()
        Player1 = Button(self.screen, Font, f"Strength: {O[self.playerchoice][3]}", [340,-140], White, Blue, False).draw()
        Player1 = Button(self.screen, Font, f"Reload Speed: {O[self.playerchoice][4]}", [380,-140], White, Blue, False).draw()
        Player1 = Button(self.screen, Font, f"Bullet Speed: {O[self.playerchoice][5]}", [420,-140], White, Blue, False).draw()

        Player1 = Button(self.screen, Font, f"Player", [470,-140], White, Blue, True).draw()
        PlayerLeft = Button(self.screen, Font, f"<", [470,-200], White, Blue, True)
        PlayerLeft.hovered()
        PlayerLeft.draw()
        PlayerRight = Button(self.screen, Font, f">", [470,-80], White, Blue, True)
        PlayerRight.hovered()
        PlayerRight.draw()

        Enemy1 = Button(self.screen, Font, f"Gun: {O[self.enemychoice][1]}", [260,140], White, Blue, False).draw()
        Enemy1 = Button(self.screen, Font, f"Bullets: {O[self.enemychoice][2]}", [300,140], White, Blue, False).draw()
        Enemy1 = Button(self.screen, Font, f"Strength: {O[self.enemychoice][3]}", [340,140], White, Blue, False).draw()
        Enemy1 = Button(self.screen, Font, f"Reload: {O[self.enemychoice][4]}", [380,140], White, Blue, False).draw()
        Enemy1 = Button(self.screen, Font, f"Bullet Speed: {O[self.enemychoice][5]}", [420,140], White, Blue, False).draw()

        Enemy1 = Button(self.screen, Font, f"Enemy", [470,140], White, Blue, True).draw()
        EnemyLeft = Button(self.screen, Font, f">", [470,200], White, Blue, True)
        EnemyLeft.hovered()
        EnemyLeft.draw()
        EnemyRight = Button(self.screen, Font, f"<", [470,80], White, Blue, True)
        EnemyRight.hovered()
        EnemyRight.draw()

        if self.click:
            if Start.collision():
                P1 = self.playerchoice
                P2 = self.enemychoice

                playerimage =  pygame.image.load(O[P1][0])
                enemyimage = pygame.image.load(O[P2][0])

                playeroptions = Player(playerimage,O[P1][1],O[P1][2],O[P1][3],O[P1][4],O[P1][5])
                enemyoptions = Player(enemyimage,O[P2][1],O[P2][2],O[P2][3],O[P2][4],O[P2][5])

                self.player = sprite(self.screen, 600, 200, 0.4, 5, playeroptions)
                self.enemy = sprite(self.screen, 680, 200, 0.4, 5, enemyoptions)

                self.state = "Maps"

            if PlayerLeft.collision():
                self.playerchoice = SwitchLeft(self.playerchoice)
            if PlayerRight.collision():
                self.playerchoice = SwitchRight(self.playerchoice)
            if EnemyRight.collision():
                self.enemychoice = SwitchLeft(self.enemychoice)
            if EnemyLeft.collision():
                self.enemychoice = SwitchRight(self.enemychoice)

            self.click = False

    def maps(self):
        #All code for choosing maps here
        self.screen.blit(mapsbg, (0, 0))
        GameDisplay = Button(self.screen, Font, f"Map Choices", [100,0], White, Blue, False)
        GameDisplay.draw()

        Map1 = Button(self.screen, Font, f"Map 1", [480,-400], White, Blue, True)
        Map1.hovered()
        Map1.draw()

        Map2 = Button(self.screen, Font, f"Map 2", [480,0], White, Blue, True)
        Map2.hovered()
        Map2.draw()

        Map3 = Button(self.screen, Font, f"Map 3", [480,400], White, Blue, True)
        Map3.hovered()
        Map3.draw()
        
        MapImage1 = pygame.image.load("Images/map1.png")
        MapImage1 = pygame.transform.scale(MapImage1, (320,180))
        self.screen.blit(MapImage1,(480-400,180))

        MapImage2 = pygame.image.load("Images/map2.png")
        MapImage2 = pygame.transform.scale(MapImage2, (320,180))
        self.screen.blit(MapImage2,(480,180))

        MapImage3 = pygame.image.load("Images/map3.png")
        MapImage3 = pygame.transform.scale(MapImage3, (320,180))
        self.screen.blit(MapImage3,(480+400,180))

        #pygame.Rect(left->right, top->bottom, width/thickness, height)
        if self.click:
            if Map1.collision():
                self.countdown = time.time() + 5
                pygame.mixer.music.load(track1)
                pygame.mixer.music.play()
                self.backgroundimage = map1bg
                line1 = pygame.Rect(SCREEN_WIDTH/10, 12*(SCREEN_HEIGHT/20), SCREEN_WIDTH-(2*SCREEN_WIDTH/10), 5)
                line2 = pygame.Rect((SCREEN_WIDTH/2)-100, (SCREEN_HEIGHT/2)-60, (SCREEN_HEIGHT/4)+10, 5)
                line3 = pygame.Rect((SCREEN_WIDTH/2)-85, (SCREEN_HEIGHT/2)+210, (SCREEN_HEIGHT/6)+10, 5)
                line4 = pygame.Rect((SCREEN_WIDTH/2)+200, (SCREEN_HEIGHT/2)+210, (SCREEN_HEIGHT/6), 5)
                line5 = pygame.Rect((SCREEN_WIDTH/2)-400, (SCREEN_HEIGHT/2)+210, (SCREEN_HEIGHT/6), 5)
                self.platforms = [line1,line2,line3,line4,line5]
                self.state = "Game"
            if Map2.collision():
                self.countdown = time.time() + 5
                pygame.mixer.music.load(track2)
                pygame.mixer.music.play()
                self.backgroundimage = map2bg
                line1 = pygame.Rect(SCREEN_WIDTH/2-SCREEN_WIDTH/10, 16*(SCREEN_HEIGHT/20), SCREEN_WIDTH/2, 5)
                line2 = pygame.Rect(SCREEN_WIDTH/10, 12*(SCREEN_HEIGHT/20), SCREEN_WIDTH/2, 5)
                line3 = pygame.Rect(SCREEN_WIDTH/2-SCREEN_WIDTH/10, 8*(SCREEN_HEIGHT/20), SCREEN_WIDTH/2, 5)
                self.platforms = [line1,line2,line3]
                self.state = "Game"
            if Map3.collision():
                self.countdown = time.time() + 5
                pygame.mixer.music.load(track3)
                pygame.mixer.music.play()
                self.backgroundimage = map3bg
                line1 = pygame.Rect(SCREEN_WIDTH/4-SCREEN_WIDTH/8, 8*(SCREEN_HEIGHT/20), SCREEN_WIDTH/4, 5)
                line2 = pygame.Rect(3*SCREEN_WIDTH/4-SCREEN_WIDTH/8, 8*(SCREEN_HEIGHT/20), SCREEN_WIDTH/4, 5)
                line3 = pygame.Rect(SCREEN_WIDTH/4, 12*(SCREEN_HEIGHT/20), SCREEN_WIDTH/2, 5)
                line4 = pygame.Rect(SCREEN_WIDTH/4-SCREEN_WIDTH/8, 16*(SCREEN_HEIGHT/20), SCREEN_WIDTH/4, 5)
                line5 = pygame.Rect(3*SCREEN_WIDTH/4-SCREEN_WIDTH/8, 16*(SCREEN_HEIGHT/20), SCREEN_WIDTH/4, 5)
                self.platforms = [line1,line2,line3,line4,line5]
                self.state = "Game"
            self.click = False

    def game(self):
        #All code for actual game
        self.screen.blit(self.backgroundimage, (0, 0))
        
        listofplatforms = self.platforms
        for platform in listofplatforms:
            pygame.draw.rect(self.screen, Blue, platform)

        self.player.draw()
        self.enemy.draw()
        
        if (self.countdown) >= (time.time()):
            GameDisplay1 = Button(self.screen, Font, f"Starting in {int(self.countdown-time.time())+1}", [100,0], White, Blue, False)
            GameDisplay1.draw()
        else:
            GameDisplay = Button(self.screen, Font, f"{self.display}", [100,0], White, Blue, False)
            GameDisplay.draw()
        
            for bullet in self.player.bullets:
                bullet.draw()
                bullet.update()     
        
                if bullet.rect.colliderect(self.enemy.rect):
                    self.enemy.rect.x = self.enemy.rect.x + (bullet.direction*5*self.player.stats.strength)
                    bullet.kill()
                    playerhit.play()
               
            for bullet in self.enemy.bullets:
                bullet.draw()
                bullet.update()

                if bullet.rect.colliderect(self.player.rect):
                   self.player.rect.x = self.player.rect.x + (bullet.direction*5*self.enemy.stats.strength)
                   bullet.kill()
                   playerhit.play()

            draw_text(f"Player", Font, Black, self.screen, self.player.rect.x+10, self.player.rect.y-15)
            draw_text(f"{self.player.stats.bullets_left}", Font, White, self.screen, self.player.rect.x, self.player.rect.y+15)
            draw_text(f"{self.player.stats.message}", Font, White, self.screen, self.player.rect.x+10, self.player.rect.y-33)

            draw_text(f"Enemy", Font, Black, self.screen, self.enemy.rect.x+10, self.enemy.rect.y-15)
            draw_text(f"{self.enemy.stats.bullets_left}", Font, White, self.screen, self.enemy.rect.x, self.enemy.rect.y+15)
            draw_text(f"{self.enemy.stats.message}", Font, White, self.screen, self.enemy.rect.x, self.enemy.rect.y-33)

            if self.player.stats.reloading:
                self.player.stats.reload_count += 1
                self.player.stats.message = f"Reloading {self.player.stats.reload_count}/{self.player.stats.reload_time}"
                if self.player.stats.reload_count >= self.player.stats.reload_time:
                    self.player.stats.message = ""
                    self.player.stats.reload_count = 0
                    self.player.stats.bullets_left = self.player.stats.max_bullets
                    self.player.stats.reloading = False

            if self.enemy.stats.reloading:
                self.enemy.stats.reload_count += 1
                self.enemy.stats.message = f"Reloading {self.enemy.stats.reload_count}/{self.enemy.stats.reload_time}"
                if self.enemy.stats.reload_count >= self.enemy.stats.reload_time:
                    self.enemy.stats.message = ""
                    self.enemy.stats.reload_count = 0
                    self.enemy.stats.bullets_left = self.enemy.stats.max_bullets
                    self.enemy.stats.reloading = False

            self.player.move(self.player.stats.moving_left, self.player.stats.moving_right, listofplatforms)
            self.enemy.move(self.enemy.stats.moving_left, self.enemy.stats.moving_right, listofplatforms)

            if self.player.alive == False or self.enemy.alive == False:
                if self.player.alive == False and self.cooldown >= 100:
                    self.display = "Enemy Wins"
                elif self.enemy.alive == False and self.cooldown >= 100:
                    self.display = "Player Wins"

                self.cooldown = self.cooldown - 1
                if self.cooldown <= 0:
                    self.cooldown = 100
                    self.display = "Game"
                    self.state = "Over"

    def over(self):
        #All code for win/game over screen
        self.screen.blit(overbg, (0, 0))
        GameDisplay = Button(self.screen, Font, f"{self.display} Over", [100,0], Black, Blue, False)
        GameDisplay.draw() 

        Again = Button(self.screen, Font, f"Play Again", [260,0], White, Blue, True)
        Again.hovered()
        Again.draw()

        Menu = Button(self.screen, Font, f"Return to Menu", [340,0], White, Blue, True)
        Menu.hovered()
        Menu.draw()

        if self.click:
            if Menu.collision():
                pygame.mixer.music.load(track0)
                pygame.mixer.music.play()
                self.platforms = ""
                self.state = "Menu"
            if Again.collision():
                
                #Resetting player location and bullets
                self.player.alive = True
                self.player.rect.x = 600-28
                self.player.rect.y = 200
                self.player.stats.bullets_left = self.player.stats.max_bullets

                self.enemy.alive = True
                self.enemy.rect.x = 680-28
                self.enemy.rect.y = 200
                self.enemy.stats.bullets_left = self.enemy.stats.max_bullets
                
                #Resetting countdown timer
                self.countdown = time.time() + 5

                self.state = "Game"

            self.click = False
        

#main game loop
def GameMenu():
    run = True
    clock = pygame.time.Clock()

    Game = MainGame()
    while run:
        #Checking for all the different key/mouse inputs
        Game.events()
        
        Game.screen.fill((Grey))
        
        #All the different game states
        if Game.state == "Menu":
            Game.menu()

        elif Game.state == "Options":
            Game.options()
            
        elif Game.state == "Controls":
            Game.controls()

        elif Game.state == "Guns":
            Game.guns()

        elif Game.state == "Maps":
            Game.maps()
          
        elif Game.state == "Game":
            Game.game()

        elif Game.state == "Over":
            Game.over()
        
        clock.tick(Fps)
        pygame.display.update()

#Only actual line being ran
GameMenu()

