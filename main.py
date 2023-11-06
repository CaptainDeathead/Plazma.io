import pygame as pg
import random
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
    def __init__(self, x, y, claimedColor, claimedNum, ai=False):
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
        self.claimedColor = claimedColor
        self.semiColor = (claimedColor[0] + 50, claimedColor[1] + 50, claimedColor[2] + 50)
        self.claimedNum = claimedNum
        self.trailNum = claimedNum + 0.5
        self.ai = ai
        self.lastTurn = time.time()

    def getOpporsiteDirection(self, direction):
        if direction == "up" and self.direction == "down": return True
        elif direction == "down" and self.direction == "up": return True
        elif direction == "left" and self.direction == "right": return True
        elif direction == "right" and self.direction == "left": return True
        else: return False

    def move(self):
        if self.ai and time.time() - self.lastTurn > 0.8:
            while True:
                direction = random.choice(["up", "down", "left", "right"])
                if not self.getOpporsiteDirection(direction):
                    self.direction = direction
                    break
            self.lastTurn = time.time()
            print(self.direction)

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
        self.player = Player(101, 100, (150, 150, 0), 1)
        #self.claimedColor = (150, 150, 0)
        #self.semiColor = (150, 200, 0)

        self.leftButton = pg.Rect(0, 0, 100, 100)
        self.leftButton.centerx = self.screen_rect.centerx - 130
        self.leftButton.centery = self.screen_rect.centery + 350
        self.leftButton_radius = 10
        self.rightButton = pg.Rect(0, 0, 100, 100)
        self.rightButton.centerx = self.screen_rect.centerx + 130
        self.rightButton.centery = self.screen_rect.centery + 350
        self.rightButton_radius = 10
        self.upButton = pg.Rect(0, 0, 100, 100)
        self.upButton.centerx = self.screen_rect.centerx
        self.upButton.centery = self.screen_rect.centery + 250
        self.upButton_radius = 10
        self.downButton = pg.Rect(0, 0, 100, 100)
        self.downButton.centerx = self.screen_rect.centerx
        self.downButton.centery = self.screen_rect.centery + 450
        self.downButton_radius = 10
                
        self.map = [[0 for i in range(200)] for e in range(200)]
        self.setUp3x3(self.player.playerPos[0]-1, self.player.playerPos[1], 1)

        self.bots = []
        for i in range(2, 3):
            self.bots.append(Player(105, 100, (random.randint(0, 205), random.randint(0, 205), random.randint(0, 205)), i, True))
            self.setUp3x3(self.bots[i-2].playerPos[0]-1, self.bots[i-2].playerPos[1], i)

        for y in range(200):
            self.map[y][0] = -1
            self.map[y][199] = -1
            
        for x in range(200):
            self.map[0][x] = -1
            self.map[199][x] = -1

    def setUp3x3(self, x, y, claimedNum):
        self.map[y][x] = claimedNum
        self.map[y][x + 1] = claimedNum
        self.map[y][x + 2] = claimedNum
        self.map[y + 1][x] = claimedNum
        self.map[y + 1][x + 1] = claimedNum
        self.map[y + 1][x + 2] = claimedNum
        self.map[y + 2][x] = claimedNum
        self.map[y + 2][x + 1] = claimedNum
        self.map[y + 2][x + 2] = claimedNum

    def drawBots(self):
        for bot in self.bots:
            if time.time() - bot.lastUpdate > 0.12:
                bot.move()
                bot.lastUpdate = time.time()

            if self.map[bot.playerPos[1]][bot.playerPos[0]] == -1:
                self.bots.remove(bot)
                for y in range(200):
                    for x in range(200):
                        if self.map[y][x] == bot.claimedNum or self.map[y][x] == bot.trailNum:
                            self.map[y][x] = 0
                continue
            elif type(self.map[bot.playerPos[1]][bot.playerPos[0]]) == int:
                self.map[bot.playerPos[1]][bot.playerPos[0]] = bot.trailNum
                bot.trail.append(bot.playerPos.copy())
            elif self.map[bot.playerPos[1]][bot.playerPos[0]] == 1.5:
                return True
            elif self.map[bot.playerPos[1]][bot.playerPos[0]] == bot.claimedNum and len(bot.trail) > 0:
                trailsY = {}
                smallestY = 200
                biggestY = 0
                smallestX = 200
                biggestX = 0
                for trail in bot.trail:
                    if trail[1] not in trailsY:
                        trailsY[trail[1]] = [trail[0]]
                    else:
                        trailsY[trail[1]].append(trail[0])
                    if trail[1] > biggestY:
                        biggestY = trail[1]
                    if trail[1] < smallestY:
                        smallestY = trail[1]
                    if trail[0] > biggestX:
                        biggestX = trail[0]
                    if trail[0] < smallestX:
                        smallestX = trail[0]

                    self.map[trail[1]][trail[0]] = bot.claimedNum

                for y in trailsY:
                    trailsY[y].sort()
                    for i in range(len(trailsY[y])-1):
                        for x in range(trailsY[y][i], trailsY[y][i+1]):
                            self.map[y][x] = bot.claimedNum

                fullY = {}
                for y in range(200):
                    for x in range(200):
                        if self.map[y][x] == bot.claimedNum:
                            if y not in fullY:
                                fullY[y] = [x]
                            else:
                                fullY[y].append(x)

                for y in fullY:
                    fullY[y].sort()
                    for i in range(len(fullY[y])-1):
                        for x in range(fullY[y][i], fullY[y][i+1]):
                            self.map[y][x] = bot.claimedNum

            for trail in bot.trail:
                pg.draw.rect(self.screen, bot.claimedColor, (trail[0] * 50 + bot.movementFromCenter[0], trail[1] * 50 + bot.movementFromCenter[1], 50, 50))

            pg.draw.rect(self.screen, bot.claimedColor, (bot.playerPos[0] * 50 + bot.movementFromCenter[0], bot.playerPos[1] * 50 + bot.movementFromCenter[1], 50, 50))

        return False

    def draw(self):
        #print("E")
        self.screen.fill(self.bg_color)
        if self.drawBots(): return False
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
                    pg.draw.rect(self.screen, self.player.claimedColor, (x*50-4825+self.player.movementFromCenter[0], y*50-4525+self.player.movementFromCenter[1], 50, 50))
                elif self.map[y][x] == 1.5:
                    pg.draw.rect(self.screen, self.player.semiColor, (x*50-4825+self.player.movementFromCenter[0], y*50-4525+self.player.movementFromCenter[1], 50, 50))
                elif self.map[y][x] == -1:
                    pg.draw.rect(self.screen, (0, 0, 255), (x*50-4825+self.player.movementFromCenter[0], y*50-4525+self.player.movementFromCenter[1], 50, 50))
                else:
                    for bot in self.bots:
                        if self.map[self.player.playerPos[1]][self.player.playerPos[0]] == bot.claimedNum:
                            pg.draw.rect(self.screen, bot.claimedColor, (x*50-4825+self.player.movementFromCenter[0], y*50-4525+self.player.movementFromCenter[1], 50, 50))
                            self.player.owned += 1
                            bot.owned -= 1
                        elif self.map[self.player.playerPos[1]][self.player.playerPos[0]] == bot.trailNum:
                            self.bots.remove(bot)
                            for y in range(200):
                                for x in range(200):
                                    if self.map[y][x] == bot.claimedNum or self.map[y][x] == bot.trailNum:
                                        self.map[y][x] = 0
                            self.player.owned += 1
                            self.map[self.player.playerPos[1]][self.player.playerPos[0]] = 1.5
                            pg.draw.rect(self.screen, bot.semiColor, (x*50-4825+self.player.movementFromCenter[0], y*50-4525+self.player.movementFromCenter[1], 50, 50))
                        if bot.claimedNum == self.map[y][x]:
                            pg.draw.rect(self.screen, bot.claimedColor, (x*50-4825+self.player.movementFromCenter[0], y*50-4525+self.player.movementFromCenter[1], 50, 50))
                        elif bot.trailNum == self.map[y][x]:
                            pg.draw.rect(self.screen, bot.semiColor, (x*50-4825+self.player.movementFromCenter[0], y*50-4525+self.player.movementFromCenter[1], 50, 50))
                    
        self.screen.blit(self.player.playerSprite, self.player.playerSprite_rect)
        self.player.progress.currentVal = self.player.owned

        pg.draw.rect(self.screen, (0, 0, 0), self.leftButton, border_radius=self.leftButton_radius)
        pg.draw.rect(self.screen, (0, 0, 0), self.rightButton, border_radius=self.rightButton_radius)
        pg.draw.rect(self.screen, (0, 0, 0), self.upButton, border_radius=self.upButton_radius)
        pg.draw.rect(self.screen, (0, 0, 0), self.downButton, border_radius=self.downButton_radius)

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
                elif game.leftButton.collidepoint(event.pos) and not game.player.direction == "right":
                    game.player.direction = "left"
                elif game.rightButton.collidepoint(event.pos) and not game.player.direction == "left":
                    game.player.direction = "right"
                elif game.upButton.collidepoint(event.pos) and not game.player.direction == "down":
                    game.player.direction = "up"
                elif game.downButton.collidepoint(event.pos) and not game.player.direction == "up":
                    game.player.direction = "down"
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    menu.show_menu = True
                    game = Game()
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
            dead = not game.draw()
            if dead:
                menu.show_menu = True
                game = Game()

        pg.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)

asyncio.run(main())