import pygame, math, sys, time
from pygame.locals import *

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768

def level1():
    print("Initializing game...")
    print(f"Screen dimensions: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")

    # Set up the screen
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Race Game - Level 1")

    # Game clock
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 75)
    win_font = pygame.font.Font(None, 50)

    # Win/loss conditions
    win_condition = None
    win_text = font.render('Game Over - You Won!', True, (0, 255, 0))
    loss_text = font.render('Game Over - You Crashed!', True, (255, 0, 0))
    restart_text = win_font.render(' Restart', True, (255, 255, 255))

    # Timer
    t0 = time.time()

    # Load assets with error handling
    try:
        car_image = pygame.image.load('images/car.png')
        pad_image = pygame.image.load('images/race_pads.png')
        collision_image = pygame.image.load('images/collision.png')
        trophy_image = pygame.image.load('images/trophy.png')
    except FileNotFoundError as e:
        print(f"Error: {e}. Please ensure all asset files are in the 'images' folder.")
        sys.exit(1)

    class CarSprite(pygame.sprite.Sprite):
        MAX_FORWARD_SPEED = 2
        MAX_REVERSE_SPEED = 5
        ACCELERATION = 1
        TURN_SPEED = 5

        def __init__(self, image, position):
            pygame.sprite.Sprite.__init__(self)
            self.src_image = image
            self.position = position
            self.speed = self.direction = 0
            self.k_left = self.k_right = self.k_down = self.k_up = 0

        def update(self, deltat):
            self.speed += (self.k_up + self.k_down)
            if self.speed > self.MAX_FORWARD_SPEED:
                self.speed = self.MAX_FORWARD_SPEED
            if self.speed < -self.MAX_REVERSE_SPEED:
                self.speed = -self.MAX_REVERSE_SPEED
            self.direction += (self.k_right + self.k_left)
            x, y = self.position
            rad = self.direction * math.pi / 180
            x += -self.speed * math.sin(rad)
            y += -self.speed * math.cos(rad)
            self.position = (x, y)
            self.image = pygame.transform.rotate(self.src_image, self.direction)
            self.rect = self.image.get_rect()
            self.rect.center = self.position

    class PadSprite(pygame.sprite.Sprite):
        def __init__(self, image, hit_image, position):
            super(PadSprite, self).__init__()
            self.normal = image
            self.hit = hit_image
            self.image = self.normal
            self.rect = self.image.get_rect()
            self.rect.center = position

        def update(self, hit_list):
            if self in hit_list:
                self.image = self.hit
            else:
                self.image = self.normal

    # Create pads
    pads = [
        PadSprite(pad_image, collision_image, (0, 10)),
        PadSprite(pad_image, collision_image, (600, 10)),
        PadSprite(pad_image, collision_image, (1100, 10)),
        PadSprite(pad_image, collision_image, (100, 150)),
        PadSprite(pad_image, collision_image, (600, 150)),
        PadSprite(pad_image, collision_image, (100, 300)),
        PadSprite(pad_image, collision_image, (800, 300)),
        PadSprite(pad_image, collision_image, (400, 450)),
        PadSprite(pad_image, collision_image, (700, 450)),
        PadSprite(pad_image, collision_image, (200, 600)),
        PadSprite(pad_image, collision_image, (900, 600)),
        PadSprite(pad_image, collision_image, (400, 750)),
        PadSprite(pad_image, collision_image, (800, 750)),
    ]
    pad_group = pygame.sprite.RenderPlain(*pads)

    class Trophy(pygame.sprite.Sprite):
        def __init__(self, image, position):
            pygame.sprite.Sprite.__init__(self)
            self.image = image
            self.rect = self.image.get_rect()
            self.rect.x, self.rect.y = position

    # Create trophies
    trophies = [Trophy(trophy_image, (285, 0))]
    trophy_group = pygame.sprite.RenderPlain(*trophies)

    # Create a car
    car = CarSprite(car_image, (10, 730))
    car_group = pygame.sprite.RenderPlain(car)

    # Main game loop
    while True:
        print("Game loop running...")
        # Handle events
        t1 = time.time()
        dt = t1 - t0

        deltat = clock.tick(30)
        for event in pygame.event.get():
            if not hasattr(event, 'key'):
                continue
            down = event.type == KEYDOWN
            if win_condition is None:
                if event.key == K_RIGHT:
                    car.k_right = down * -2.5
                elif event.key == K_LEFT:
                    car.k_left = down * 2.5
                elif event.key == K_UP:
                    car.k_up = down * 1
                elif event.key == K_DOWN:
                    car.k_down = down * -1
                elif event.key == K_ESCAPE:
                    sys.exit(0)
            elif win_condition is not None and event.key == K_SPACE:
                # Restart the game
                level1()
                return
            elif event.key == K_ESCAPE:
                sys.exit(0)

        # Countdown timer
        seconds = round((60 - dt), 2)  # Increased time limit to 60 seconds
        if win_condition is None:
            # Convert seconds to minutes and seconds
            minutes = int(seconds // 60)
            remaining_seconds = int(seconds % 60)
            timer_text = font.render(f"{minutes:02}:{remaining_seconds:02}", True, (255, 255, 0))
            if seconds <= 0:
                win_condition = False
                timer_text = font.render("Time!", True, (255, 0, 0))

        # Rendering
        screen.fill((0, 0, 0))
        car_group.update(deltat)
        collisions = pygame.sprite.groupcollide(car_group, pad_group, False, False)
        if collisions:
            win_condition = False
            timer_text = font.render("Crash!", True, (255, 0, 0))
            car.image = collision_image
            seconds = 0
            car.MAX_FORWARD_SPEED = 0
            car.MAX_REVERSE_SPEED = 0
            car.k_right = 0
            car.k_left = 0

        trophy_collision = pygame.sprite.groupcollide(car_group, trophy_group, False, True)
        if trophy_collision:
            timer_text = font.render("Finished!", True, (0, 255, 0))
            win_condition = True
            car.MAX_FORWARD_SPEED = 0
            car.MAX_REVERSE_SPEED = 0

        pad_group.update(collisions)
        pad_group.draw(screen)
        car_group.draw(screen)
        trophy_group.draw(screen)

        # Render timer and win/loss text
        screen.blit(timer_text, (20, 60))
        if win_condition is not None:
            # Calculate positions for centered text
            win_text_rect = win_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            loss_text_rect = loss_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            restart_text_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))

            if win_condition:
                screen.blit(win_text, win_text_rect)
            else:
                screen.blit(loss_text, loss_text_rect)
            screen.blit(restart_text, restart_text_rect)

        pygame.display.flip()

# Start the game
if __name__ == "__main__":
    level1()