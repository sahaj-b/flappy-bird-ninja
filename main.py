import random
import sys
import pygame
from pygame.locals import QUIT, KEYDOWN, K_SPACE, K_UP, K_ESCAPE, K_s
pygame.init()

FPS = 50
swidth = 500
sheight = 750
screen = pygame.display.set_mode((swidth, sheight))
basey = sheight * 0.8
sprites = {}
sounds = {}

def textScreen(text, color, x, y):
    screen_text = pygame.font.SysFont(None, 60).render(text, True, color)
    screen.blit(screen_text, (x, y))

def didCollide(playerx, playery, upperPipes, lowerPipes, badBirds):
    if playery > basey - 60 or playery < 0:
        return True

    for pipe in upperPipes:
        pipeHeight = sprites['pipe'][0].get_height()
        if (playery < pipeHeight + pipe['y'] - 10 and abs(playerx - pipe['x']) < sprites['pipe'][0].get_width() - 3):
            return True

    for pipe in lowerPipes:
        if (playery + sprites['player'].get_height() > pipe['y'] - 10) and abs(playerx - pipe['x']) < sprites['pipe'][0].get_width() - 3:
            return True

    for bird in badBirds:
        if sprites['badbird'].get_rect(topleft=(bird['x'], bird['y'])).scale_by(0.9, 0.8).colliderect(sprites['player'].get_rect(topleft=(playerx, playery))):
            return True
    return False

def getRandomPipe():
    offset = sheight/8 - 80
    y2 = random.randrange(int(sheight/2) - 100, int(basey - 100))
    pipex = swidth+random.randrange(90, 200)
    y1 = y2 - sheight + offset
    pipe = [
        {'x': pipex, 'y': y1},
        {'x': pipex, 'y': y2}
    ]
    return pipe

def getRandomBird():
    badbirdx = random.randrange(swidth + 300, swidth + 550)
    badbirdy = random.randrange(100, int(basey) - 100)
    badbirds = {'x': badbirdx, 'y': badbirdy}
    return badbirds

def printScore(score, x, y):
    width = 0
    myDigits = [int(x) for x in list(str(score))]
    for digit in myDigits:
        width += sprites['numbers'][digit].get_width()
    for digit in myDigits:
        screen.blit(sprites['numbers'][digit], (x, y))
        x += sprites['numbers'][digit].get_width()

def welcomeScreen():
    messagex = 0
    messagey = 0
    basex = 0
    playerx = int(swidth/2 - sprites['player'].get_width()/2)
    playery = int(sheight/3 + 90)
    animateNinja = True
    ninjaAngle = 20
    ninjaScale = 5
    ninjaWidth = sprites['ninja'].get_width()
    ninjaHeight = sprites['ninja'].get_height()
    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                return

        screen.blit(sprites['bg'], (0, 0))
        screen.blit(sprites['shuriken'], (playerx, playery - 20))
        screen.blit(sprites['player'], (playerx, playery))
        screen.blit(sprites['base'], (basex, basey))
        screen.blit(sprites['menu'], (messagex, messagey))
        screen.blit(pygame.transform.scale_by(pygame.transform.rotate(sprites['ninja'], ninjaAngle), ninjaScale), (150 - (ninjaScale-1)*ninjaWidth, 120 - (ninjaScale-1)*ninjaHeight))
        if animateNinja:
            ninjaAngle += 20
            ninjaScale -= 0.1
            if ninjaScale <= 1.5:
                animateNinja = False
        pygame.display.update()
        FPSCLOCK.tick(FPS)

def badBirdGotHit(badBirds, shurikenx, shurikeny):
    hitCtr = 0
    if shurikenx < swidth + 50:
        for bird in badBirds:
            if sprites['shuriken'].get_rect(topleft=(shurikenx, shurikeny)).colliderect(sprites['badbird'].get_rect(topleft=(bird['x'], bird['y']))):
                bird['x'] = shurikenx + 40
                bird['y'] = shurikeny + 7
                hitCtr += 1
    return hitCtr

def gameOverScreen(score):
    sounds['ded'].play()
    try:
        with open('hs.txt') as f:
            highScore = int(f.read())
    except FileNotFoundError:
        with open('hs.txt', 'w') as f:
            f.write('0')
        highScore = score
    if score > highScore:
        print(f'New Highscore: {score}')
        highScore = int(score)
        with open('hs.txt', 'w') as high:
            high.write(str(highScore))
    screen.blit(sprites['gameover'], (0, 0))
    textScreen('Score:', (48, 39, 9), swidth/5 - 20, basey + 50)
    textScreen('Highscore:', (48, 39, 9), swidth/5 - 20, basey + 100)
    printScore(score, 2*swidth/3, basey + 50)
    printScore(highScore, 2*swidth/3, basey + 100)

def mainGame():
    score = 0
    playerx = int(swidth/5)
    playery = int(sheight/3)
    basex = 0

    newPipe1 = getRandomPipe()

    upperPipes = [
        {'x': swidth+200, 'y': newPipe1[0]['y']},
    ]
    lowerPipes = [
        {'x': swidth+200, 'y': newPipe1[1]['y']},
    ]
    badBird1 = getRandomBird()
    badBird2 = getRandomBird()
    badBirds = [{'x': badBird1['x'], 'y': badBird1['y']},
                {'x': badBird2['x']+200, 'y': badBird2['y']}]
    pipeVelX = -4
    badBirdVelx = -5
    playerVelY = 0
    gravity = 0.6
    angle = 0
    shuriken_angle = 0
    shurikenx = playerx
    shurikeny = playery-10
    shurikenVelx = 0
    shurikenVely = 0
    playerFlapped = False
    shoot = False
    playHitSound = True
    playHitSound2 = True
    baseResetScroll = 35
    pipeFreq = 1500
    lastPipe = pygame.time.get_ticks() + 1000
    birdFreq = 1500
    lastBird = pygame.time.get_ticks() + 1000
    paused = False
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if playery > 0:
                    playerVelY = -9
                    angle = 45
                    playerFlapped = True
                    sounds['wing'].play()
            elif event.type == KEYDOWN and (event.key == K_s):
                if not shoot:
                    shoot = True
                    sounds['throw'].play()
            elif event.type == KEYDOWN and (event.key == K_ESCAPE):
                paused = True

        gameover = didCollide(playerx, playery, upperPipes, lowerPipes, badBirds)

        if gameover:
            gameOverScreen(score)
            pygame.display.update()
            while True:
                for event in pygame.event.get():
                    if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                        pygame.quit()
                        sys.exit()
                    elif event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                        return

        if paused:
            textScreen('Paused', (255, 225, 125), swidth/2 - 80, sheight/2 - 30)
            pygame.display.update()
            while paused:
                for event in pygame.event.get():
                    if event.type == QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP or event.key == K_ESCAPE):
                        paused = False

        playerMidPos = playerx + sprites['player'].get_width()/2
        for pipe in upperPipes:
            pipeMidPos = pipe['x'] + sprites['pipe'][0].get_width()/2
            if pipeMidPos <= playerMidPos < pipeMidPos + 4:
                score += 1

        if not playerFlapped:
            playerVelY += gravity
            angle -= gravity*3
        if playerFlapped:
            playerFlapped = False
        playery += playerVelY

        for upperPipe, lowerPipe in zip(upperPipes, lowerPipes):
            upperPipe['x'] += pipeVelX
            lowerPipe['x'] += pipeVelX

        for bird in badBirds:
            bird['x'] += badBirdVelx

        currTime = pygame.time.get_ticks()
        if currTime - lastPipe > pipeFreq:
            newpipe = getRandomPipe()
            upperPipes.append(newpipe[0])
            lowerPipes.append(newpipe[1])
            lastPipe = currTime
            pipeFreq = random.randrange(1000, 2000)

        if currTime - lastBird > birdFreq:
            badBirds.append(getRandomBird())
            lastBird = currTime
            birdFreq = random.randrange(900, 2200)

        if shoot:
            if shurikenx > swidth + 400 or shurikeny >= basey:
                shoot = False
                playHitSound = True
                playHitSound2 = True
            hitCtr = badBirdGotHit(badBirds, shurikenx, shurikeny)
            if hitCtr:
                if playHitSound and shoot:
                    sounds['hit'].play()
                    score += 1
                    playHitSound = False
                if hitCtr == 2 and playHitSound2 and shoot:
                    sounds['hit'].play()
                    score += 1
                    playHitSound2 = False

                shurikenVelx = 10
                shurikenVely += gravity
            else:
                shurikenVelx = 15
                shuriken_angle += 20
        else:
            shurikenVely = 0
            shurikenVelx = 0
            shurikenx = playerx
            shurikeny = playery - 10
        shurikenx += shurikenVelx
        shurikeny += shurikenVely

        try:
            if upperPipes[0]['x'] < -sprites['pipe'][0].get_width():
                upperPipes.pop(0)
                lowerPipes.pop(0)
        except IndexError:
            pass

        try:
            if badBirds[0]['x'] < -40:
                badBirds.pop(0)
        except IndexError:
            pass

        screen.blit(sprites['bg'], (0, 0))
        for upperPipe, lowerPipe in zip(upperPipes, lowerPipes):
            screen.blit(sprites['pipe'][0], (upperPipe['x'], upperPipe['y']))
            screen.blit(sprites['pipe'][1], (lowerPipe['x'], lowerPipe['y']))
        for bird in badBirds:
            screen.blit(sprites['badbird'], (bird['x'], bird['y']))
            if bird['y'] > basey - 100:
                badBirds.remove(bird)
        basex += pipeVelX
        if basex < -baseResetScroll:
            basex = 0
        screen.blit(pygame.transform.rotate(
            sprites['shuriken'], shuriken_angle), (shurikenx, shurikeny))
        screen.blit(pygame.transform.rotate(
            sprites['player'], angle), (playerx, playery))
        screen.blit(sprites['base'], (basex, basey))

        printScore(score, (swidth)/2, 10)
        pygame.display.update()
        FPSCLOCK.tick(FPS)

if __name__ == '__main__':
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    pygame.display.set_caption('Flappy Bird NINJA')
    sprites['numbers'] = (
        pygame.image.load('sprites/0.png').convert_alpha(),
        pygame.image.load('sprites/1.png').convert_alpha(),
        pygame.image.load('sprites/2.png').convert_alpha(),
        pygame.image.load('sprites/3.png').convert_alpha(),
        pygame.image.load('sprites/4.png').convert_alpha(),
        pygame.image.load('sprites/5.png').convert_alpha(),
        pygame.image.load('sprites/6.png').convert_alpha(),
        pygame.image.load('sprites/7.png').convert_alpha(),
        pygame.image.load('sprites/8.png').convert_alpha(),
        pygame.image.load('sprites/9.png').convert_alpha()
    )

    sprites['menu'] = pygame.transform.scale(pygame.image.load('sprites/menu.png').convert_alpha(), (swidth, sheight))
    sprites['gameover'] = pygame.transform.scale(pygame.image.load('sprites/gameover.png').convert_alpha(), (swidth - 5, sheight / 5))
    pipeImg = pygame.transform.scale(pygame.image.load('sprites/pipe.png').convert_alpha(), (swidth / 8, sheight / 1.5))
    sprites['pipe'] = (
        pygame.transform.rotate(pipeImg, 180),
        pipeImg
    )
    sprites['bg'] = pygame.transform.scale(pygame.image.load('sprites/background.png').convert_alpha(), (swidth, sheight))
    sprites['player'] = pygame.transform.scale(pygame.image.load('sprites/flappy.png'), (swidth / 10, swidth / 12))
    sprites['badbird'] = pygame.transform.flip(pygame.transform.scale(
        pygame.image.load('sprites/badbird.png'), (swidth / 10, swidth / 12)), True, False)
    sprites['base'] = pygame.transform.scale(pygame.image.load('sprites/base.png').convert_alpha(), (swidth + 30, sheight / 4))
    sprites['shuriken'] = pygame.transform.scale(pygame.image.load('sprites/shuriken.png'), (swidth / 15, swidth / 15))
    sprites['ninja'] = pygame.image.load('sprites/ninja.png')
    sounds['throw'] = pygame.mixer.Sound('audio/throw.mp3')
    sounds['ded'] = pygame.mixer.Sound('audio/ded.wav')
    sounds['wing'] = pygame.mixer.Sound('audio/wing.wav')
    sounds['hit'] = pygame.mixer.Sound('audio/hit.wav')
    sounds['throw'].set_volume(0.4)
    sounds['ded'].set_volume(0.4)
    sounds['wing'].set_volume(0.1)
    sounds['hit'].set_volume(0.4)

    while True:
        welcomeScreen()
        mainGame()
