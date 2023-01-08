## 20181227 HojinKim ##
## Pacman Dodge ##
# Project 4: Interactive Drawing & Animation

## -- Library ------------------------------------ ##
import pygame
import os
import numpy as np
import colorsys

## -- Const Variable ----------------------------- ##
# Color Related
BLACK = (0, 0, 0)
GREY = (127, 127, 127)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
MAGENTA = (255, 0, 255)
CYAN = (0, 255, 255)

## - Class ---------------------------------------- ##
class Pacman():
    def __init__(self,):
        self.pos = [WINDOW_WIDTH/2, WINDOW_HEIGHT/2]
        self.direction = 0
        self.speed = 5.0
        self.radius = 25
        stayInSafezone(self, SAFEZONE_PACMAN)
        self.collider = Collider_circle(self.pos, self.radius)
        self.isPowerUp = False
        self.imgArrIndex = 1
        self.imgArrIndexVel = 1
        self.imgArr = []
        for i in range(7):
            tempImg = pygame.image.load(os.path.join(assets_path, 'pacman_'+ str(i) +'.png'))
            self.imgArr.append(tempImg)

    def rotate(self, _mousePos):
        tempAngle = angleOf2Dot(self.pos, _mousePos)
        if tempAngle != -1:
            self.direction = tempAngle
    
    def move(self, _mousePos):
        rad = np.deg2rad(self.direction)
        distance = distanceOf2Dot(self.pos, _mousePos)
        moveAmount = self.speed
        if distance < self.speed:
            moveAmount = distance
        amountX = moveAmount * np.cos(rad)
        amountY = - moveAmount * np.sin(rad)
        self.pos = [self.pos[0]+amountX, self.pos[1]+amountY]
        stayInSafezone(self, SAFEZONE_PACMAN)
        self.collider.pos = self.pos

    def animator_move(self,): # Waka waka animation
        if self.imgArrIndex >= 6 or self.imgArrIndex <= 0:
            self.imgArrIndexVel *= -1 # Animate in reverse order
        self.imgArrIndex += self.imgArrIndexVel
    
    def update(self, _mousePos, _isPowerUp):
        self.isPowerUp = _isPowerUp
        self.rotate(_mousePos)
        self.move(_mousePos)

    def draw(self, _screen):
        self.animator_move()
        img_r = pygame.transform.rotate(self.imgArr[self.imgArrIndex], self.direction)
        if isPowerUp: # Strong state
            img = img_r.copy()
            tempHueVal = frameTime/60
            tempHueVal = tempHueVal - int(tempHueVal)
            tempColor = hsv2rgba(tempHueVal)
            reColor(img, (244,246,0,255), tempColor)
            _screen.blit(img, img.get_rect(center= self.pos))
        else: # Normal state
            img = img_r
        _screen.blit(img, img.get_rect(center= self.pos))
        #self.collider.draw(_screen)

class Ghost():
    def __init__(self,):
        self.pos = [np.random.randint(WINDOW_WIDTH), np.random.randint(WINDOW_HEIGHT)]
        self.respawnPos = self.pos
        self.isRespawn = False
        self.direction = 0
        self.speed_norm = 3.0
        self.speed_weak = 1.0
        self.speed_respawn = 10.0
        self.radius = 30
        stayOutSafezone(self, SAFEZONE_GHOST)
        stayInWindow(self)
        self.collider = Collider_circle(self.pos, self.radius)
        self.frameTime_move = 0
        self.isNew_move = True
        self.behavior = 0
        self.isPowerUp = False
        self.isPowerUp_nearEnd = False
        self.imgArrIndex = 1
        self.imgArr = []
        for i in range(5):
            tempImg = pygame.image.load(os.path.join(assets_path, 'ghost_'+ str(i) +'.png'))
            self.imgArr.append(tempImg)
        tempColor = hsv2rgba(np.random.random())
        self.reColor_init((255,0,0,255), tempColor) # Recolor ghost body with random color
        
    def reColor_init(self, _fromColor, _toColor): # Recolor of ghost body   
        for img in self.imgArr:
            for x in range(img.get_width()):
                for y in range(img.get_height()):
                    if img.get_at((x, y)) == _fromColor: # Change all red into other color
                        img.set_at((x, y), _toColor)
    
    def rotate(self, _pacmanPos):
        tempAngle = angleOf2Dot(self.pos, _pacmanPos)
        if not self.isPowerUp: # Normal state
            if tempAngle != -1:
                self.direction = tempAngle
        else: # Weak state
            if tempAngle != -1:
                self.direction = (tempAngle+180)%360
    
    def move(self, _pacmanPos, _frameTime):
        if _frameTime - self.frameTime_move > 60: # Shift behavior every 1 second
            self.isNew_move = True
        if self.isNew_move: # Select new behavior
            self.frameTime_move = _frameTime
            self.moveBehaviorSelect() # 0-front, 1-left, 2-back, 3- right
            self.isNew_move = False
        self.direction += self.behavior*90
        rad = np.deg2rad(self.direction)
        distance = distanceOf2Dot(self.pos, _pacmanPos)
        speed = self.speed_norm if not self.isPowerUp else self.speed_weak
        if distance < speed:
            moveAmount = distance
        else:
            moveAmount = speed
        amountX = moveAmount * np.cos(rad)
        amountY = - moveAmount * np.sin(rad)
        self.pos = [self.pos[0]+amountX, self.pos[1]+amountY]
        stayInWindow(self)
        self.collider.pos = self.pos

    def animator_look(self,): # Image selection according to moving direction
        if self.direction>45 and self.direction<315:
            self.imgArrIndex = int((self.direction+45)//90 + 1)
        else:
            self.imgArrIndex = 1
    
    def moveBehaviorSelect(self,):
        # Behavior ratio
        FRONT = 0.50
        LEFT = 0.20
        BACK = 0.10
        #RIGHT = 0.20
        if not self.isPowerUp: # Normal state
            tempBehavior = np.random.random()
            if tempBehavior < FRONT: # front
                self.behavior = 0
            elif tempBehavior < FRONT+LEFT: # left
                self.behavior = 1
            elif tempBehavior < FRONT+LEFT+BACK: # back
                self.behavior = 2
            else: # right
                self.behavior = 3
        else: # Weak state
            self.behavior = 0 # only go front
    
    def respawn(self,): # Move to the spawn point
        if frameTime_gameTime % int(sound_runaway.get_length()*60) == 0:
            sound_runaway.play()
        if self.pos[1] != self.respawnPos[1]: # Move on Y axis direction
            distanceY = distanceOf2Dot(self.pos, (self.pos[0],self.respawnPos[1]))
            moveAmount = self.speed_respawn
            if distanceY < self.speed_respawn:
                moveAmount = distanceY
            moveAmount = moveAmount if self.respawnPos[1]>self.pos[1] else - moveAmount
            self.pos = [self.pos[0], self.pos[1]+moveAmount]
            self.collider.pos = self.pos
        elif self.pos[0] != self.respawnPos[0]: # Move on X axis direction
            distanceX = distanceOf2Dot(self.pos, self.respawnPos)
            moveAmount = self.speed_respawn
            if distanceX < self.speed_respawn:
                moveAmount = distanceX
            moveAmount = moveAmount if self.respawnPos[0]>self.pos[0] else - moveAmount
            self.pos = [self.pos[0]+moveAmount, self.pos[1]]
            self.collider.pos = self.pos
        else: # End of respawn when reaching respawn point
            self.isRespawn = False
    
    def update(self, _pacmanPos, _frameTime, _isPowerUp):
        if not self.isRespawn: # Normal
            if _frameTime - frameTime_powerUp >= COOL_POWERUP-COOL_POWERUP_ALERT:
                self.isPowerUp_nearEnd = True
            else:
                self.isPowerUp_nearEnd = False
            self.isPowerUp = _isPowerUp
            self.rotate(_pacmanPos)
            self.move(_pacmanPos, _frameTime)
        else: # Respawn
            self.respawn()

    def draw(self, _screen):
        if not self.isRespawn: # Normal
            if not self.isPowerUp: # When powerup
                self.animator_look()
            else:
                self.imgArrIndex = 0
            img = self.imgArr[self.imgArrIndex].copy()
            if self.isPowerUp_nearEnd: # When powerup is about to end
                if (frameTime//4)%2: # Blinking effect
                    reColor(img, (53, 41, 247, 255), (255,255,255,255))
        else: # Respawn
            img = self.imgArr[0].copy()
            reColor(img, (53, 41, 247, 255), (255,255,255,0))
        _screen.blit(img, img.get_rect(center= self.pos))
        #self.collider.draw(_screen)

class Dot():
    def __init__(self,):
        self.pos = [np.random.randint(WINDOW_WIDTH), np.random.randint(WINDOW_HEIGHT)]
        self.radius = 5
        stayInSafezone(self, SAFEZONE_DOT)
        self.collider = Collider_circle(self.pos, self.radius)
        self.img = pygame.image.load(os.path.join(assets_path, 'dot.png'))
    
    def relocate(self):
        self.pos = [np.random.randint(WINDOW_WIDTH), np.random.randint(WINDOW_HEIGHT)]
        stayInSafezone(self, SAFEZONE_DOT)
        self.collider.pos = self.pos

    def draw(self, _screen):
        _screen.blit(self.img, self.img.get_rect(center= self.pos))
        #self.collider.draw(_screen)

class Power():
    def __init__(self,):
        self.pos = [-100, -100]
        self.radius = 20
        self.collider = Collider_circle(self.pos, self.radius)
        self.img = pygame.image.load(os.path.join(assets_path, 'power.png'))
    
    def relocate(self): # Let power displayed inside the screen
        self.pos = [np.random.randint(WINDOW_WIDTH), np.random.randint(WINDOW_HEIGHT)]
        stayInSafezone(self, SAFEZONE_DOT)
        self.collider.pos = self.pos
    
    def exclude(self): # Let power displayed out of screen
        self.pos = [-100, -100]
        self.collider.pos = self.pos

    def draw(self, _screen):
        img = self.img.copy()
        tempHueVal = frameTime/60
        tempHueVal = tempHueVal - int(tempHueVal)
        tempColor = hsv2rgba(tempHueVal)
        reColor(img, (255,0,0,255), tempColor)
        _screen.blit(img, img.get_rect(center= self.pos))
        #self.collider.draw(_screen)

class Collider_circle:
    def __init__(self, _pos, _radius):
        self.pos = _pos
        self.radius = _radius

    def draw(self, _screen): # for debug
        pygame.draw.circle(_screen, RED, self.pos, self.radius, 1)

class Button:
    def __init__(self, _displayVal, _x, _y, _width, _height):
        self.displayVal = _displayVal
        self.left = _x - _width/2
        self.top = _y - _height/2
        self.centerX = _x
        self.centerY = _y
        self.width = _width
        self.height = _height

    def isPressed(self, _mousePos):
        if _mousePos[0] > self.left and _mousePos[0] < self.left+self.width and _mousePos[1] > self.top and _mousePos[1] < self.top+self.height:
            # Pressed
            return self.displayVal
        else:
            # Not Pressed
            return 0
    
    def draw(self, _screen):
        pygame.draw.rect(_screen, (255,255,255), (self.left, self.top, self.width, self.height), 8)
        text_displayVal = font_norm.render(str(self.displayVal), True, (255,255,255))
        _screen.blit(text_displayVal, text_displayVal.get_rect(center=(self.centerX, self.centerY)))

## - Function -------------------------------------- ##
def drawUI(_screen,): # UI of ingame
    sliderVal = np.clip(collectedDot/requiredDot*SLIDER_MAX, 0,SLIDER_MAX)
    sliderColor = (127, 127, 127)
    if sliderVal == SLIDER_MAX:
        sliderColor = (255, 255, 255)
    pygame.draw.rect(_screen, (53, 41, 247), pygame.Rect(10,UI_TOP, SLIDER_MAX+20,50), 0, 10)
    pygame.draw.rect(_screen, sliderColor, pygame.Rect(20,UI_TOP+10, sliderVal,30), 0, 5)
    text_score = "Score: " + str(score)
    _screen.blit(font_norm.render(text_score, True, (255,255,255)), (10, UI_TOP+60))
    text_time = "Time: " + str(int(frameTime_gameTime/60)).zfill(4)
    _screen.blit(font_norm.render(text_time, True, (255,255,255)), (WINDOW_WIDTH-255, UI_TOP+60))
    
def drawResult(_screen,): # Result of endgame
    text_gameover = font_larger.render("Gameover", True, (255,255,255))
    _screen.blit(text_gameover, text_gameover.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2-250)))
    text_score = font_large.render("Score: "+str(score), True, (255,255,255))
    _screen.blit(text_score, text_score.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2-100)))
    text_time = font_large.render("Time: " + str(int(frameTime_gameTime/60)).zfill(4), True, (255,255,255))
    _screen.blit(text_time, text_time.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2)))
    text_playAgain = font_large.render("Play Again?", True, (255,255,255))
    _screen.blit(text_playAgain, text_playAgain.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2+150)))

def drawBackground(_screen): # Blue frame
    pygame.draw.rect(_screen, (53, 41, 247), pygame.Rect(SAFEZONE_PACMAN-10, SAFEZONE_PACMAN-10
    , WINDOW_WIDTH-2*SAFEZONE_PACMAN+20, WINDOW_HEIGHT-2*SAFEZONE_PACMAN+20), 10, 30)
    pygame.draw.rect(_screen, (53, 41, 247), pygame.Rect(SAFEZONE_PACMAN-30, SAFEZONE_PACMAN-30
    , WINDOW_WIDTH-2*SAFEZONE_PACMAN+60, WINDOW_HEIGHT-2*SAFEZONE_PACMAN+60), 10, 45)

def angleOf2Dot(_start, _end): # Angle between two dots in degree
    differenceX = _end[0] - _start[0]
    differenceY = _end[1] - _start[1]
    if differenceX != 0:
        if differenceX > 0 and differenceY <= 0: # 0~90
            angle = -np.rad2deg(np.arctan(differenceY/differenceX))
        elif differenceX < 0 and differenceY < 0: # 90~180
            angle = 180 - np.rad2deg(np.arctan(differenceY/differenceX))
        elif differenceX < 0 and differenceY >= 0: # 180~270
            angle = 180 - np.rad2deg(np.arctan(differenceY/differenceX))
        elif differenceX > 0 and differenceY > 0: # 270~360
            angle = 360 - np.rad2deg(np.arctan(differenceY/differenceX))
    else:
        if differenceY > 0:
            angle = 270.0
        elif differenceY < 0:
            angle = 90.0
        else: # When _end point is same as _start point
            angle = -1
    return angle

def distanceOf2Dot(_start, _end): # Distance between two dots
    differenceX = _end[0] - _start[0]
    differenceY = _end[1] - _start[1]
    return np.power(np.power(differenceX,2) + np.power(differenceY,2), 0.5)

def is2ObjCollide(_obj1, _obj2): # Is two circle collider collides
    obj1_pos = _obj1.collider.pos
    obj1_radius = _obj1.collider.radius
    obj2_pos = _obj2.collider.pos
    obj2_radius = _obj2.collider.radius
    obj_distance = distanceOf2Dot(obj1_pos, obj2_pos)
    if obj_distance < obj1_radius +obj2_radius:
        return True
    else:
        return False

def stayInSafezone(_obj, _safeZone): # Change position to inside of safe zone
    obj_pos = _obj.pos
    obj_radius = _obj.radius
    if obj_pos[0] < _safeZone+obj_radius:
        _obj.pos[0] = _safeZone+obj_radius
    elif obj_pos[0] > WINDOW_WIDTH-_safeZone-obj_radius:
        _obj.pos[0] = WINDOW_WIDTH-_safeZone-obj_radius
    if obj_pos[1] < _safeZone+obj_radius:
        _obj.pos[1] = _safeZone+obj_radius
    elif obj_pos[1] > WINDOW_HEIGHT-_safeZone-obj_radius:
        _obj.pos[1] = WINDOW_HEIGHT-_safeZone-obj_radius

def stayOutSafezone(_obj, _safeZone): # Change position to outside of safe zone
    obj_pos = _obj.pos
    obj_radius = _obj.radius
    if obj_pos[0] < WINDOW_WIDTH/2:
        if obj_pos[0] > _safeZone-obj_radius:
            _obj.pos[0] = _safeZone-obj_radius
    else:
        if obj_pos[0] < WINDOW_WIDTH-_safeZone+obj_radius:
            _obj.pos[0] = WINDOW_WIDTH-_safeZone+obj_radius
    if obj_pos[1] < WINDOW_HEIGHT/2:
        if obj_pos[1] > _safeZone-obj_radius:
            _obj.pos[1] = _safeZone-obj_radius
    else:
        if obj_pos[1] < WINDOW_HEIGHT-_safeZone+obj_radius:
            _obj.pos[1] = WINDOW_HEIGHT-_safeZone+obj_radius

def stayInWindow(_obj,): # Change position to inside of window screen
    obj_pos = _obj.pos
    obj_radius = _obj.radius
    if obj_pos[0] < obj_radius:
        _obj.pos[0] = obj_radius
    elif obj_pos[0] > WINDOW_WIDTH-obj_radius:
        _obj.pos[0] = WINDOW_WIDTH-obj_radius
    if obj_pos[1] < obj_radius:
        _obj.pos[1] = obj_radius
    elif obj_pos[1] > WINDOW_HEIGHT-obj_radius:
        _obj.pos[1] = WINDOW_HEIGHT-obj_radius

def hsv2rgba(h): # RGBA color with hue value
    tempRgba = []
    for i in colorsys.hsv_to_rgb(h,1,1):
        tempRgba.append(round(i * 255))
    tempRgba.append(255)
    return tuple(tempRgba)

def reColor(_img, _fromColor, _toColor): # Swap certain pixel into other color
    for x in range(_img.get_width()):
        for y in range(_img.get_height()):
            #print(_img.get_at((x, y)))
            if _img.get_at((x, y)) == _fromColor:
                _img.set_at((x, y), _toColor)

## -- Setup -------------------------------------- ##
# Pygame init
pygame.init()
pygame.display.set_caption("Project4_2018227_HojinKim")
#WINDOW_WIDTH, WINDOW_HEIGHT = 1920, 1080
#screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WINDOW_WIDTH, WINDOW_HEIGHT = pygame.display.get_surface().get_size()

SAFEZONE_GHOST = 150
SAFEZONE_PACMAN = 250
SAFEZONE_DOT = 300
clock = pygame.time.Clock()

# Asset path
assets_path = os.path.join(os.path.dirname(__file__), '_assets')

# Game value init
score = 0
frameTime_gameTime = 0
isNewGameStart = True
frameTime_powerUp = 0
COOL_POWERUP = 8*60
COOL_POWERUP_ALERT = 2*60
isPowerUp = False
isPowerSpawned = False

dotNum = 1
ghostNum = 3
collectedDot = 0
requiredDot = 3

UI_TOP = 60
SLIDER_MAX = 400

# Image init
cursorImg = pygame.image.load(os.path.join(assets_path, 'cursor.png'))

# Class init
pacman = Pacman()
power = Power()
dotArr = []
for _ in range(dotNum):
    tempDot = Dot()
    dotArr.append(tempDot)
ghostArr = []
for _ in range(ghostNum):
    tempGhost = Ghost()
    ghostArr.append(tempGhost)

button_easy = Button("Easy", WINDOW_WIDTH/2,WINDOW_HEIGHT/2+50, 400,60)
button_normal = Button("Normal", WINDOW_WIDTH/2,WINDOW_HEIGHT/2+150, 400,60)
button_hard = Button("Hard", WINDOW_WIDTH/2,WINDOW_HEIGHT/2+250, 400,60)
button_yes = Button("Yes", WINDOW_WIDTH/2-125,WINDOW_HEIGHT/2+250, 200,60)
button_no = Button("No", WINDOW_WIDTH/2+125,WINDOW_HEIGHT/2+250, 200,60)

# Font init
font_small = pygame.font.Font('_assets/Joystix.TTF', 20)
font_norm = pygame.font.Font('_assets/Joystix.TTF', 40)
font_large = pygame.font.Font('_assets/Joystix.TTF', 80)
font_larger = pygame.font.Font('_assets/Joystix.TTF', 120)
font_title = pygame.font.Font('_assets/Joystix.TTF', 160)

# Sound init
volume_low = 0.1
volume_lower = 0.07
sound_start = pygame.mixer.Sound(os.path.join(assets_path, 'sound_start.wav'))
sound_start.set_volume(volume_low)
sound_start_isPlay = True
sound_end = pygame.mixer.Sound(os.path.join(assets_path, 'sound_end.wav'))
sound_end.set_volume(volume_low)
sound_end_isPlay = True
sound_dot = pygame.mixer.Sound(os.path.join(assets_path, 'sound_dot.wav'))
sound_dot.set_volume(volume_lower)
sound_waka1 = pygame.mixer.Sound(os.path.join(assets_path, 'sound_waka1.wav'))
sound_waka1.set_volume(volume_lower)
sound_waka2 = pygame.mixer.Sound(os.path.join(assets_path, 'sound_waka2.wav'))
sound_waka2.set_volume(volume_lower)
sound_siren1 = pygame.mixer.Sound(os.path.join(assets_path, 'sound_siren1.wav'))
sound_siren1.set_volume(volume_lower)
sound_siren2 = pygame.mixer.Sound(os.path.join(assets_path, 'sound_siren2.wav'))
sound_siren2.set_volume(volume_lower)
sound_eat = pygame.mixer.Sound(os.path.join(assets_path, 'sound_eat.wav'))
sound_eat.set_volume(volume_low)
sound_runaway = pygame.mixer.Sound(os.path.join(assets_path, 'sound_runaway.wav'))
sound_runaway.set_volume(volume_lower)
sound_runaway_isPlay = False

# Stage selector init
# stage = ('pregame', 'ingame', 'endgame')
currentStage = 'pregame'

## -- Update -------------------------------------- ##
done = False
frameTime = 0
while not done:
    # Mouse location
    mousePos = pygame.mouse.get_pos()
    pygame.mouse.set_cursor((8,8),(0,0),(0,0,0,0,0,0,0,0),(0,0,0,0,0,0,0,0)) #invisible cursor

    # Event
    isClick = False
    input = 0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                done = True
            if event.key == pygame.K_SPACE:
                input = 1
        if event.type == pygame.MOUSEBUTTONUP:    
            isClick = True
            if currentStage == 'pregame':
                if button_easy.isPressed(mousePos):
                    input = button_easy.displayVal
                if button_normal.isPressed(mousePos):
                    input = button_normal.displayVal
                if button_hard.isPressed(mousePos):
                    input = button_hard.displayVal
            elif currentStage == 'endgame':
                if button_yes.isPressed(mousePos):
                    input = button_yes.displayVal
                if button_no.isPressed(mousePos):
                    input = button_no.displayVal

    ## Stage Selector ##
    #---------------------------------------------------#
    if currentStage == 'pregame': # Difficulty selection
        ##################
        screen.fill((0,0,0))
        drawBackground(screen)

        if input != 0:
            # Game value init
            if input == "Easy":
                ghostNum = 2
                requiredDot = 2
            elif input == "Normal":
                ghostNum = 3
                requiredDot = 3
            elif input == "Hard":
                ghostNum = 4
                requiredDot = 4

            # Reset game value
            score = 0
            frameTime_gameTime = 0
            isNewGameStart = True
            frameTime_powerUp = 0
            isPowerUp = False
            isPowerSpawned = False

            dotNum = 1
            collectedDot = 0

            # Class init
            pacman = Pacman()
            power = Power()
            dotArr = []
            for _ in range(dotNum):
                tempDot = Dot()
                dotArr.append(tempDot)
            ghostArr = []
            for _ in range(ghostNum):
                tempGhost = Ghost()
                ghostArr.append(tempGhost)
            currentStage = 'ingame' # Next Stage

        # Update
        pacman.update(mousePos, False) # Background pacman

        # Draw
        pacman.draw(screen)
        text_title = font_title.render("Pacman Dodge", True, (255,255,255))
        screen.blit(text_title, text_title.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2-150)))
        button_easy.draw(screen)
        button_normal.draw(screen)
        button_hard.draw(screen)
        screen.blit(cursorImg, cursorImg.get_rect(center= mousePos)) 

        # Sound
        if sound_start_isPlay:
            sound_start.play()
            sound_end_isPlay = True
            sound_start_isPlay = False

    #---------------------------------------------------#
    elif currentStage == 'ingame': # Gameplay until player dies
        ##################
        screen.fill((0,0,0))
        drawBackground(screen)

        # End powerup
        if frameTime - frameTime_powerUp >= COOL_POWERUP: 
            if isPowerUp:
                dotNum += 1
                ghostNum += 1
                isPowerSpawned = False
            isPowerUp = False

        # Spawn object
        if len(dotArr) < dotNum:
            tempDot = Dot()
            dotArr.append(tempDot)
        if len(ghostArr) < ghostNum:
            tempGhost = Ghost()
            ghostArr.append(tempGhost)
        if collectedDot >= requiredDot:
            if not isPowerSpawned:
                power.relocate()
                isPowerSpawned = True

        # Power collision check
        if is2ObjCollide(pacman, power):
            if not isPowerUp:
                frameTime_powerUp = frameTime
                requiredDot += dotNum
                collectedDot = 0
                power.exclude()
                isPowerUp = True

        # Update
        pacman.update(mousePos, isPowerUp)
        for ghost in ghostArr:
            ghost.update(pacman.pos, frameTime, isPowerUp)

        # Collision check
        for dot in dotArr:
            if is2ObjCollide(pacman, dot):
                dot.relocate()
                collectedDot += 1
                sound_dot.play()
                score += 1
        for ghost in ghostArr:
            if is2ObjCollide(pacman, ghost):
                if not isPowerUp and not ghost.isRespawn:
                    currentStage = 'endgame'
                else:
                    if not ghost.isRespawn:
                        sound_eat.play()
                        score += 3
                    ghost.isRespawn = True

        # Draw
        pacman.draw(screen)
        for ghost in ghostArr:
            ghost.draw(screen)
        for dot in dotArr:
            dot.draw(screen)
        power.draw(screen)
        drawUI(screen)
        screen.blit(cursorImg, cursorImg.get_rect(center= mousePos)) 

        # Sound Play
        if not isPowerUp: # Not in powerup
            if frameTime_gameTime % int(sound_waka1.get_length()*60) == 0:
                sound_waka1.play()
            if frameTime_gameTime % int(sound_siren1.get_length()*60) == 0:
                sound_siren1.play()
        else: # In powerup
            if frameTime_gameTime % int(sound_waka2.get_length()*60) == 0:
                sound_waka2.play()
            if frameTime_gameTime % int(sound_siren2.get_length()*60) == 0:
                sound_siren2.play()
            
        # Time Lasts
        frameTime_gameTime += 1

    #---------------------------------------------------#
    elif currentStage == 'endgame': # Display game result, Ask to play again
        ##################
        screen.fill((0,0,0))
        drawBackground(screen)

        if input != 0:
            if input == "Yes":
                currentStage = 'pregame' # First stage
            if input == "No":
                done = True # End game

        # Draw
        drawResult(screen)
        button_yes.draw(screen)
        button_no.draw(screen)
        screen.blit(cursorImg, cursorImg.get_rect(center= mousePos))

        # Sound
        if sound_end_isPlay:
            sound_end.play()
            sound_start_isPlay = True
            sound_end_isPlay = False 

    # Performance Debug
    #screen.blit(font_small.render(str(round(frameTime/60, 2)), True, (255,255,255)), (10, WINDOW_HEIGHT-20))

    # Display Update
    pygame.display.flip()
    clock.tick(60)
    frameTime += 1
    
pygame.quit()