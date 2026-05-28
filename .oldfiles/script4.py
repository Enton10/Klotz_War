import random


import pygame


pygame.init()
screen = pygame.display.set_mode((2300, 1300))
Gamemode_2normal = False
font = pygame.font.SysFont("arial", 32)
Text_Hallo = font.render("Hallo", True, (255, 255, 255))

Text_n2 = font.render("2 Sieler Normal", True, (255, 255, 255))
maus_pos = pygame.mouse.get_pos()
rect_2normal = pygame.Rect(1150, 300, 220, 50)
run = True
def Start(run):
    pygame.draw.rect(screen, (0, 200, 200), rect_2normal)
    screen.blit(Text_Hallo, (1150, 200))
    screen.blit(Text_n2, (1150, 300))

    while run == True:
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            print("hi")
            if event.type == pygame.MOUSEBUTTONDOWN:
                print("h0")
                # War der Klick auf dem Text-Rechteck?
                if rect_2normal.collidepoint(event.pos):
                    print(maus_pos)


def Gamemode_2n():

    run = True
    clock = pygame.time.Clock()
    rect = pygame.Rect(2280, 1280, 20, 20)
    rect1 = pygame.Rect(0, 0, 20, 20)
    f_rect = pygame.Rect(0, 0, 1, 1)
    Waechsler = pygame.Rect(-100, -100, 10, 10)
    speed = 5
    speed1 = 5
    range_ = 10
    range_1 = 10
    faenger = rect
    spur_punkte_ = []
    spur_punkte_1 = []
    count_for_end = 0
    count_Waechsler = 0
    normal_color_rect = (0, 0, 255)
    normal_color_rect1 = (0, 255, 0)
    color_rect = (0, 0, 0)
    color_rect1 = (0, 0, 0)

    def Berwaegen_rect(rect):
        if keys[pygame.K_LEFT]:
            rect.x -= speed
        if keys[pygame.K_RIGHT]:
            rect.x += speed
        if keys[pygame.K_DOWN]:
            rect.y += speed
        if keys[pygame.K_UP]:
            rect.y -= speed

    def Berwaegen_rect1(rect1):
        if keys[pygame.K_a]:
            rect1.x -= speed1
        if keys[pygame.K_d]:
            rect1.x += speed1
        if keys[pygame.K_s]:
            rect1.y += speed1
        if keys[pygame.K_w]:
            rect1.y -= speed1

    def Border_rect(rect):
        if rect.x < 0:
            rect.x = 0
        if rect.x > 2280:
            rect.x = 2280
        if rect.y < 0:
            rect.y = 0
        if rect.y > 1280:
            rect.y = 1280

    def Border_rect1(rect1):
        if rect1.x < 0:
            rect1.x = 0
        if rect1.x > 2280:
            rect1.x = 2280
        if rect1.y < 0:
            rect1.y = 0
        if rect1.y > 1280:
            rect1.y = 1280

    def Abstand_rect(rect, rect1, range_, count_for_end):
        if (abs(rect.x - rect1.x)) <= range_ and (abs(rect.y - rect1.y)) <= range_:
            while True:
                count_for_end += 1

                screen.fill((0, 0, 0))
                if count_for_end == 5000:
                    pygame.quit()

    def Abstand_rect1(rect, rect1, range_1, count_for_end):
        if (abs(rect1.x - rect.x)) <= range_1 and (abs(rect1.y - rect.y)) <= range_1:
            while True:
                count_for_end += 1

                screen.fill((0, 0, 0))
                if count_for_end == 5000:
                    pygame.quit()

    def Wechseln_(count_Waechsler, Waechsler, speed1, faenger, rect1):

        if count_Waechsler == 200:
            Waechsler.x = random.randint(0, 2290)
            Waechsler.y = random.randint(0, 1290)
            pygame.draw.rect(screen, (0, 200, 200), Waechsler)
            print("hallo")
        if (abs(rect1.x - Waechsler.x)) <= range_1 and (abs(rect1.y - Waechsler.y)) <= range_1:
            Bonus = random.randint(1, 2)
            pygame.draw.rect(screen, (0, 200, 0), Waechsler)
            Waechsler.x = -100
            Waechsler.y = -100
            if Bonus == 1:
                speed1 += 1
            if Bonus == 2:
                faenger = rect1

            count_Waechsler = 0
            print(count_Waechsler, Waechsler)
        return count_Waechsler, speed1, faenger, Waechsler

    def Wechseln_1(count_Waechsler, Waechsler, speed, faenger, rect):

        if (abs(rect.x - Waechsler.x)) <= range_ and (abs(rect.y - Waechsler.y)) <= range_:
            Bonus = random.randint(1, 2)
            pygame.draw.rect(screen, (0, 0, 200), Waechsler)
            Waechsler.x = -100
            Waechsler.y = -100
            if Bonus == 1:
                speed += 1
            if Bonus == 2:
                faenger = rect

            count_Waechsler = 0
            print(count_Waechsler, Waechsler)
        return count_Waechsler, speed, faenger, Waechsler

    # ef Faeerwechsel(rect, rect1, faenger, color_rect, color_rect1):

    while run:

        pygame.event.get()
        if pygame.event.get(pygame.QUIT):
            run = False
        keys = pygame.key.get_pressed()

        spur_punkte_.append(rect.copy())

        spur_punkte_1.append(rect1.copy())

        count_Waechsler += 1

        if len(spur_punkte_) > 15:
            spur_punkte_.pop(0)
        if len(spur_punkte_1) > 15:
            spur_punkte_1.pop(0)

        Berwaegen_rect(rect)
        Berwaegen_rect1(rect1)
        Border_rect(rect)
        Border_rect1(rect1)
        count_Waechsler, speed1, faenger, Waechsler = Wechseln_(count_Waechsler, Waechsler, speed1, faenger, rect1)
        count_Waechsler, speed, faenger, Waechsler = Wechseln_1(count_Waechsler, Waechsler, speed, faenger, rect)
        if faenger == rect:
            Abstand_rect(rect, rect1, range_, count_for_end)
        if faenger == rect1:
            Abstand_rect1(rect, rect1, range_1, count_for_end)
        if faenger == rect1:
            color_rect1 = (255, 0, 0)
            color_rect = normal_color_rect
        if faenger == rect:
            color_rect1 = normal_color_rect1
            color_rect = (255, 0, 0)
        if keys[pygame.K_1]:
            faenger = rect1
        if keys[pygame.K_0]:
            faenger = rect

        for p in spur_punkte_:
            pygame.draw.rect(screen, (0, 0, 200), p)
        for p1 in spur_punkte_1:
            pygame.draw.rect(screen, (0, 200, 0), p1)

        pygame.draw.rect(screen, color_rect, rect)
        pygame.draw.rect(screen, color_rect1, rect1)
        pygame.display.flip()
        clock.tick()
    pygame.quit()



if Gamemode_2normal == False:
    Gamemode_2normal = Start(run)
if Gamemode_2normal:
    Gamemode_2n()
    print("hi")







