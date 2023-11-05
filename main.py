import pygame as pg
import time
import asyncio

pg.init()

screen = pg.display.set_mode((500, 1000))
pg.display.set_caption("Paper.io")
clock = pg.time.Clock()

class ProgressBar:
    def __init__(self, x, y, width, height, color, progressColor, maxVal, currentVal):
        self.screen = pg.display.get_surface()
        self.screen_rect = self.screen.get_rect()
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.progressColor = progressColor
        self.maxVal = maxVal
        self.currentVal = currentVal

    def draw(self):
        pg.draw.rect(self.screen, self.color, (self.x, self.y, self.width, self.height))
        pg.draw.rect(self.screen, self.progressColor, (self.x, self.y, self.width * (self.currentVal / self.maxVal), self.height))

class Menu:
    def __init__(self):
        self.screen = pg.display.get_surface()
        self.screen_rect = self.screen.get_rect()
        self.bg_color = (200, 200, 200)
        self.font = pg.font.Font(None, 100)
        self.text_color = (255, 200, 0)
        self.titleLbl = self.font.render("Paper.io", True, self.text_color)
        # move to the top
        self.titleLbl_rect = self.titleLbl.get_rect()          
        self.titleLbl_rect.centerx = self.screen_rect.centerx
        self.titleLbl_rect.top = 100

        self.playBtn = pg.Rect(0, 0, 200, 100)
        self.playBtn.centerx = self.screen_rect.centerx
        self.playBtn.top = 450
        self.playBtn_radius = 10

        self.playSprite = pg.image.load("sprites/play.png").convert_alpha()
        self.playSprite = pg.transform.scale(self.playSprite, (100, 100))

        self.show_menu = True

    def draw(self):
        self.screen.fill(self.bg_color)
        self.screen.blit(self.titleLbl, self.titleLbl_rect)
        pg.draw.rect(self.screen, self.text_color, self.playBtn, border_radius=self.playBtn_radius)
        self.screen.blit(self.playSprite,(self.playBtn.centerx - 50, self.playBtn.top))

class Player:
    def __init__(self, x, y):
        self.screen = pg.display.get_surface()
        self.screen_rect = self.screen.get_rect()
        self.playerSprite = pg.image.load("sprites/paperioSprite.png").convert_alpha()
        self.playerSprite = pg.transform.scale(self.playerSprite, (50, 50))
        self.playerSprite_rect = self.playerSprite.get_rect()
        self.playerSprite_rect.centerx = self.screen_rect.centerx
        self.playerSprite_rect.centery = self.screen_rect.centery
        self.direction = "up"
        self.speed = 50
        self.playerPos = [x, y]
        self.movementFromCenter = [0, 0]
        self.lastUpdate = time.time()
        self.trail = []
        self.progress = ProgressBar(0, 0, 500, 50, (0, 0, 0), (255, 0, 0), 40000, 0)
        self.owned = 9

    def move(self):
        d = self.direction
        if d == "up":
            self.movementFromCenter[1] += 50
            self.playerPos[1] -= 1
        elif d == "down":
            self.movementFromCenter[1] -= 50
            self.playerPos[1] += 1
        elif d == "left":
            self.movementFromCenter[0] += 50
            self.playerPos[0] -= 1
        else:
            self.movementFromCenter[0] -= 50
            self.playerPos[0] += 1

        self.lastUpdate = time.time()

class Game:
    def __init__(self):
        self.screen = pg.display.get_surface()
        self.screen_rect = self.screen.get_rect()
        self.bg_color = (200, 200, 200)
        self.font = pg.font.Font(None, 100)
        self.text_color = (255, 200, 0)
        self.player = Player(101, 100)
        self.claimedColor = (150, 150, 0)
        self.semiColor = (150, 200, 0)
        self.map = [[0 for i in range(200)] for e in range(200)]
        self.map[99][100] = 1
        self.map[100][100] = 1
        self.map[101][100] = 1
        self.map[99][101] = 1
        self.map[100][101] = 1
        self.map[101][101] = 1
        self.map[99][102] = 1
        self.map[100][102] = 1
        self.map[101][102] = 1

        for y in range(200):
            self.map[y][0] = -1
            self.map[y][199] = -1
            
        for x in range(200):
            self.map[0][x] = -1
            self.map[199][x] = -1

    async def draw(self):
        self.screen.fill(self.bg_color)
        if time.time() - self.player.lastUpdate >= 0.12:
            self.player.move()

            if self.map[self.player.playerPos[1]][self.player.playerPos[0]] == -1 or self.map[self.player.playerPos[1]][self.player.playerPos[0]] == 1.5:
                return False

            if self.map[self.player.playerPos[1]][self.player.playerPos[0]] == 0:
                self.map[self.player.playerPos[1]][self.player.playerPos[0]] = 1.5
                
                self.player.trail.append((self.player.playerPos[0], self.player.playerPos[1]))

            if self.map[self.player.playerPos[1]][self.player.playerPos[0]] == 1 and len(self.player.trail) > 0:
                trailsY = {}
                smallestY = 200
                biggestY = 0
                smallestX = 200
                biggestX = 0
                for trail in self.player.trail:
                    if trail[1] not in trailsY:
                        trailsY[trail[1]] = [trail[0]]
                    else:
                        trailsY[trail[1]].append(trail[0])

                    if trail[1] < smallestY:
                        smallestY = trail[1]
                    if trail[1] > biggestY:
                        biggestY = trail[1]
                    if trail[0] < smallestX:
                        smallestX = trail[0]
                    if trail[0] > biggestX:
                        biggestX = trail[0]

                    self.map[trail[1]][trail[0]] = 1

                for y in trailsY:
                    trailsY[y].sort()
                    for i in range(len(trailsY[y])-1):
                        for x in range(trailsY[y][i], trailsY[y][i+1]):
                            self.map[y][x] = 1

                fullY = {}
                for y in range(200):
                    for x in range(200):
                        if self.map[y][x] == 1:
                            if y not in fullY:
                                fullY[y] = [x]
                            else:
                                fullY[y].append(x)

                for y in fullY:
                    fullY[y].sort()
                    for i in range(len(fullY[y])-1):
                        for x in range(fullY[y][i], fullY[y][i+1]):
                            self.map[y][x] = 1

                self.player.trail = []

        self.player.owned = 0

        for y in range(200):
            for x in range(200):
                if self.map[y][x] == 1:
                    self.player.owned += 1
                    pg.draw.rect(self.screen, self.claimedColor, (x*50-4825+self.player.movementFromCenter[0], y*50-4525+self.player.movementFromCenter[1], 50, 50))
                elif self.map[y][x] == 1.5:
                    pg.draw.rect(self.screen, self.semiColor, (x*50-4825+self.player.movementFromCenter[0], y*50-4525+self.player.movementFromCenter[1], 50, 50))
                elif self.map[y][x] == -1:
                    pg.draw.rect(self.screen, (0, 0, 255), (x*50-4825+self.player.movementFromCenter[0], y*50-4525+self.player.movementFromCenter[1], 50, 50))
                    
        self.screen.blit(self.player.playerSprite, self.player.playerSprite_rect)
        
        self.player.progress.currentVal = self.player.owned
        #print(self.player.progress.currentValue)
        self.player.progress.draw()

        return True

async def main():
    menu = Menu()
    game = Game()
    running = True
    while running:
        screen.fill((200, 200, 200))
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.MOUSEBUTTONDOWN:
                if menu.playBtn.collidepoint(event.pos):
                    menu.show_menu = False
                    print("play button clicked")
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_UP and not game.player.direction == "down":
                    game.player.direction = "up"
                elif event.key == pg.K_DOWN and not game.player.direction == "up":
                    game.player.direction = "down"
                elif event.key == pg.K_LEFT and not game.player.direction == "right":
                    game.player.direction = "left"
                elif event.key == pg.K_RIGHT and not game.player.direction == "left":
                    game.player.direction = "right"

        if menu.show_menu:
            menu.draw()
        else:
            dead = not await game.draw()
            if dead:
                menu.show_menu = True
                game = Game()

        pg.display.update()
        clock.tick(60)

asyncio.run(main())