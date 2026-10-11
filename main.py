import pygame
import sys
import random  # Required to generate random positions
import asyncio
import math
from Spaceship import *
# Initialize Pygame

async def main():
    pygame.init()

    # Window Setup
    WIDTH, HEIGHT = 800, 600
    SHIP_SPEED = 4

    MISSILE_SPEED = 7
    NUM_ASTEROIDS = 12
    ASTEROID_COLOR = (255,255,255)
    MISSILE_RADIUS = 4

    FIRE_DELAY = 200
    ASTEROID_SPEED_SCALE = .5

    DETECTION_RANGE = 300

    FOV_THRESHOLD = 0.7


    font = pygame.font.SysFont(None, 24)

    THRUST = 0.15
    DRAG = 0.99
    MAX_SPEED = 7

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Game")
    clock = pygame.time.Clock()

    player_sprite_surface = pygame.image.load("player.png").convert_alpha()
    player_sprite_surface = pygame.transform.smoothscale(player_sprite_surface, (64, 64))

    # Convert Raw Base64 string back into a Pygame Surface
    player_sprite_surface = pygame.image.load("player.png").convert_alpha()
    player_sprite_surface = pygame.transform.smoothscale(player_sprite_surface, (64,64))
    player_sprite_surface = pygame.transform.rotate(player_sprite_surface, 270)

    player = Spaceship(50,50)

    

    class Missile:
        def __init__(self, position, direction):
            self.position = pygame.Vector2(position)
            self.velocity = direction * MISSILE_SPEED

        def update(self):
            self.position += self.velocity

        def draw(self, surface):
            pygame.draw.circle(surface, (255, 0, 0), (int(self.position.x), int(self.position.y)), MISSILE_RADIUS)

    missiles = []

    class Asteroid(object):
        def __init__(self, x, y, vx, vy, mass):
            self.x = x
            self.y = y
            self.vx = vx
            self.vy = vy
            self.mass = mass
            self.radius = int(8+mass*4)

        def update(self):
            self.x += self.vx
            self.y += self.vy

            if self.x - self.radius < 0:
                self.x = self.radius
                self.vx *= -1
            elif self.x + self.radius > WIDTH:
                self.x = WIDTH - self.radius
                self.vx *= -1
            if self.y - self.radius < 0:
                self.y = self.radius
                self.vy *= -1
            elif self.y + self.radius > HEIGHT:
                self.y = HEIGHT - self.radius
                self.vy *= -1
        def draw(self, surface):
            pygame.draw.circle(surface, ASTEROID_COLOR, (int(self.x), int(self.y)), self.radius, 2)

    def distance(a,b):
        return math.hypot(a.x-b.x,a.y-b.y)
    def resolve_collision(a,b):
        dx = b.x-a.x
        dy = b.y-a.y
        dist = math.hypot(dx,dy)

        if dist == 0:
            dx,dy=1.0,0.0
            dist=1.0
        
        normal_x, normal_y = dx/dist,dy/dist
        tx, ty = -normal_y,normal_x

        overlap = (a.radius + b.radius) - dist
        if (overlap>0):
            a.x -= normal_x*overlap/2
            a.y -= normal_y*overlap/2
            b.x += normal_x*overlap/2
            b.y += normal_y*overlap/2

        v1n = a.vx*normal_x+a.vy*normal_y
        v1t = a.vx*tx+a.vy*ty
        v2n = b.vx*normal_x+b.vy*normal_y
        v2t = b.vx*tx+b.vy*ty

        if (v1n-v2n<0):
            return

        m1, m2 = a.mass,b.mass
        v1n_final = ((m1-m2)*v1n + 2 * m2 *v2n)/(m1+m2)
        v2n_final = ((m2-m1)*v2n + 2 * m1 *v1n)/(m1+m2)

        a.vx = v1n_final * normal_x + v1t * tx
        a.vy = v1n_final * normal_y + v1t * ty
        b.vx = v2n_final * normal_x + v2t * tx
        b.vy = v2n_final * normal_y + v2t * ty

        

    def make_asteroids(n):
        asteroids = []

        speeds = random.sample(range(2,2+n*2),n)
        attempts = 0
        while len(asteroids) < n and attempts < 1000:
            attempts += 1
            mass = random.uniform(1,5)
            radius = int(8+mass*4)
            x = random.uniform(radius, WIDTH - radius)
            y = random.uniform(radius, HEIGHT - radius)

            angle = random.uniform(0, 2 * math.pi)
            speed = speeds[len(asteroids)] * ASTEROID_SPEED_SCALE
            vx = speed * math.cos(angle)
            vy = speed * math.sin(angle)

            asteroids.append(Asteroid(x, y, vx, vy, mass))

        return asteroids

    def draw_enemy(surface, pos, forward, color):
        right = pygame.Vector2(-forward.y, forward.x)
        points = [
            pos + forward * 20,
            pos - forward * 14 + right * 12,
            pos - forward * 14 - right * 12,
        ]
        pygame.draw.polygon(surface, color, points)

    enemy_position = pygame.Vector2(
        WIDTH / 4,
        HEIGHT / 2
    )

    enemy_angle = 0

    radians = math.radians(enemy_angle)

    

    


    asteroids = make_asteroids(NUM_ASTEROIDS)
    last_shot = 0
    running = True
    # Main Game Loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        keys = pygame.key.get_pressed()
        now = pygame.time.get_ticks()
        if keys[pygame.K_SPACE] and now - last_shot >= FIRE_DELAY:
            forward = player.get_forward_vector()
            muzzle = player.position + forward * 22
            missiles.append(Missile(muzzle, forward))
            last_shot = now
        for missile in missiles:
            missile.update()

        missiles = [m for m in missiles if 0 <= m.position.x <= WIDTH and 0 <= m.position.y <= HEIGHT]
        
        player.update()

        screen.fill((0,0,0))

        for a in asteroids:
            a.update()
    
        for i in range(len(asteroids)):
            for j in range(i+1, len(asteroids)):
                a,b = asteroids[i],asteroids[j]
                if distance(a,b) < a.radius+b.radius:
                    resolve_collision(a,b)
    
        for a in asteroids:
            a.draw(screen)
    
        for missile in missiles:
            missile.draw(screen)

        enemy_forward = pygame.Vector2(
            math.cos(radians),
            -math.sin(radians)
        )

        to_player = (
            player.position - enemy_position
        )

        if to_player.length() > 0:
            to_player = to_player.normalize()

        distance_to_player = enemy_position.distance_to(
            player.position
        )

        dot = enemy_forward.dot(
            to_player
        )

        if (distance_to_player < DETECTION_RANGE and dot > FOV_THRESHOLD):
            detected = True
            print(detected)

        else:
            detected = False
            print(detected)

        asteroids = [n for n in asteroids if not any(m.position.distance_to(pygame.Vector2(n.x,n.y)) < MISSILE_RADIUS + n.radius for m in missiles)]
        player.draw(screen)
        draw_enemy(screen, enemy_position, enemy_forward, (255,0,0))
        angle_text = font.render(f"Angle: {player.angle:.0f}",True,(255,255,255))
        vector_text = font.render(f"Forward: ({player.get_forward_vector().x:.2f}, {player.get_forward_vector().y:.2f})",True,(255,255,255))
        position_text = font.render(f"Position: ({player.position.x:.2f}, {player.position.y:.2f})",True,(255,255,255))
        
        screen.blit(angle_text, (20, 20))
        screen.blit(vector_text, (20, 50))
        screen.blit(position_text, (20, 80))

        pygame.draw.circle(
            screen,
            (211,211,211),
            enemy_position,
            DETECTION_RANGE,
            1
        )

        pygame.draw.line(
            screen,
            (255,0,0),
            enemy_position,
            enemy_position + enemy_forward * 100,
            3
        )




        # Refresh Screen
        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)

    pygame.quit()




if __name__ == "__main__":
    asyncio.run(main())