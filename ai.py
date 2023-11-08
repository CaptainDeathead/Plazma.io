import neat
import os
import pickle
import random
from mainai import Game, Player, ProgressBar, MiniMap
import pygame as pg
import time

pg.init()

screen = pg.display.set_mode((500, 1000))
pg.display.set_caption("Plazma.io AI Training")

def eval_genomes(genomes, config):
    game = Game()
    nets = []

    i = 2
    for genome_id, genome in genomes:
        genome.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        game.bots.append(Player(random.randint(5, game.mapSize-5), random.randint(5, game.mapSize-5), (random.randint(0, 205), random.randint(0, 205), random.randint(0, 205)), i, game.mapSize, False))
        game.setUp3x3(game.bots[-1].playerPos[0]-1, game.bots[-1].playerPos[1], i)
        i += 1

    startTime = time.time()

    while len(game.bots) > 0 and time.time() - startTime < 60:
        for i, bot in enumerate(game.bots):
            if bot.dead:
                nets.pop(i)
                game.bots.pop(i)
            else:
                genome.fitness = game.calculateArea(bot)
                vision = game.setVision(bot)
                output = nets[i].activate((vision[0], vision[1], vision[2], game.calculateAreaDir(bot)))
                
                if bot.direction == "up":
                    direction = 0
                elif bot.direction == "right":
                    direction = 1
                elif bot.direction == "down":
                    direction = 2
                elif bot.direction == "left":
                    direction = 3

                if output[0] > 0.5:
                    direction = (direction - 1) % 4
                elif output[1] > 0.5:
                    direction = (direction + 1) % 4

                if direction == 0:
                    bot.direction = "up"
                elif direction == 1:
                    bot.direction = "right"
                elif direction == 2:
                    bot.direction = "down"
                elif direction == 3:
                    bot.direction = "left"

                bot.move(game.map)

        screen.fill((200, 200, 200))
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()

        game.draw()
        pg.display.flip()
                
    best_genome = None
    for genome_id, genome in genomes:
        if best_genome == None or genome.fitness > best_genome.fitness:
            best_genome = genome

    with open("ai.pickle", "wb") as f:
        pickle.dump(best_genome, f)

def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path)
    
    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    # save them in checkpoints folder
    p.add_reporter(neat.Checkpointer(15, filename_prefix='checkpoints/neat-checkpoint-'))

    winner = p.run(eval_genomes, 500)

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config.txt")
    run(config_path)