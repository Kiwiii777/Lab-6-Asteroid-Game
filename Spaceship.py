import pygame
import math

THRUST = 0.15
DRAG = 0.99
MAX_SPEED = 7

ROTATION_SPEED = 3

WIDTH, HEIGHT = 800, 600
SHIP_SPEED = 4

screen = pygame.display.set_mode((WIDTH, HEIGHT))


class Spaceship:
    def __init__(self,x,y):
        self.position = pygame.Vector2(x,y)
        self.velocity = pygame.Vector2(0,0)
        self.acceleration = pygame.Vector2(0,0)
        self.angle = 90
        self.radius = 18
        self.is_thrusting = False

    def get_forward_vector(self):
        rad = math.radians(self.angle)
        forward = pygame.Vector2(math.cos(rad),-math.sin(rad))
        return forward

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.angle += ROTATION_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                    self.angle -= ROTATION_SPEED
        forward = self.get_forward_vector()
        self.acceleration = pygame.Vector2(0, 0)
        self.is_thrusting = False
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.acceleration = forward * THRUST
            self.is_thrusting = True
        self.velocity += self.acceleration
        self.velocity *= DRAG
        if self.velocity.length() > MAX_SPEED:
            self.velocity.scale_to_length(MAX_SPEED)
        self.position += self.velocity

        if self.position.x > WIDTH:
            self.position.x = 0

        if self.position.x < 0:
            self.position.x = WIDTH

        if self.position.y > HEIGHT:
            self.position.y = 0

        if self.position.y < 0:
            self.position.y = HEIGHT

    def draw(self, screen):
        forward = self.get_forward_vector()
        left = forward.rotate(140)
        right = forward.rotate(-140)
        front = self.position+forward*22
        back_left = self.position+left*17
        back_right = self.position+right*17

        pygame.draw.polygon(screen, "white", [front, back_left, back_right], 2)
        pygame.draw.circle(screen, (255,0,0), (int(self.position.x), int(self.position.y)), 3)

    def get_forward(self, forward):
         return forward