import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Player properties
PLAYER_RADIUS = 10
PLAYER_SPEED = 5
PLAYER_HEALTH = 100

# Bullet properties
BULLET_SPEED = 10
BULLET_RADIUS = 3

# Zone properties
INITIAL_ZONE_RADIUS = 300
ZONE_SHRINK_SPEED = 0.1  # pixels per frame

# Item properties
ITEM_RADIUS = 5
WEAPON_DAMAGE = 20

# AI properties
NUM_AI = 5
AI_SPEED = 3

# Game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Simple Battle Royale")

# Fonts
font = pygame.font.Font(None, 36)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.health = PLAYER_HEALTH
        self.has_weapon = False
        self.angle = 0  # Facing angle for shooting

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        # Keep within screen bounds (simple boundary)
        self.x = max(PLAYER_RADIUS, min(SCREEN_WIDTH - PLAYER_RADIUS, self.x))
        self.y = max(PLAYER_RADIUS, min(SCREEN_HEIGHT - PLAYER_RADIUS, self.y))

    def draw(self):
        pygame.draw.circle(screen, GREEN, (int(self.x), int(self.y)), PLAYER_RADIUS)
        # Draw health bar
        pygame.draw.rect(screen, RED, (self.x - PLAYER_RADIUS, self.y - PLAYER_RADIUS - 10, PLAYER_RADIUS * 2 * (self.health / PLAYER_HEALTH), 5))

    def shoot(self, bullets):
        if self.has_weapon:
            bullet = Bullet(self.x, self.y, self.angle)
            bullets.append(bullet)

class AI:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.health = PLAYER_HEALTH
        self.has_weapon = random.choice([True, False])

    def move_towards(self, target_x, target_y):
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.hypot(dx, dy)
        if dist > 0:
            dx /= dist
            dy /= dist
            self.x += dx * AI_SPEED
            self.y += dy * AI_SPEED

    def draw(self):
        pygame.draw.circle(screen, BLUE, (int(self.x), int(self.y)), PLAYER_RADIUS)
        # Draw health bar
        pygame.draw.rect(screen, RED, (self.x - PLAYER_RADIUS, self.y - PLAYER_RADIUS - 10, PLAYER_RADIUS * 2 * (self.health / PLAYER_HEALTH), 5))

class Bullet:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle
        self.dx = math.cos(angle) * BULLET_SPEED
        self.dy = math.sin(angle) * BULLET_SPEED

    def update(self):
        self.x += self.dx
        self.y += self.dy

    def draw(self):
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), BULLET_RADIUS)

class Item:
    def __init__(self, x, y, item_type):
        self.x = x
        self.y = y
        self.item_type = item_type  # 'weapon' or 'health'

    def draw(self):
        color = RED if self.item_type == 'weapon' else GREEN
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), ITEM_RADIUS)

class Zone:
    def __init__(self, center_x, center_y, radius):
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius

    def shrink(self):
        self.radius -= ZONE_SHRINK_SPEED
        if self.radius < 10:
            self.radius = 10

    def draw(self):
        pygame.draw.circle(screen, RED, (int(self.center_x), int(self.center_y)), int(self.radius), 2)

    def is_inside(self, x, y):
        return math.hypot(x - self.center_x, y - self.center_y) <= self.radius

def check_collision(obj1_x, obj1_y, obj1_r, obj2_x, obj2_y, obj2_r):
    return math.hypot(obj1_x - obj2_x, obj1_y - obj2_y) < obj1_r + obj2_r

def main():
    clock = pygame.time.Clock()
    running = True

    # Initialize player in center
    player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

    # Initialize AI opponents
    ais = [AI(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT)) for _ in range(NUM_AI)]

    # Initialize items
    items = [Item(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT), random.choice(['weapon', 'health'])) for _ in range(10)]

    # Initialize bullets
    bullets = []

    # Initialize zone
    zone = Zone(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, INITIAL_ZONE_RADIUS)

    # Game loop
    while running:
        screen.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click to shoot
                    player.shoot(bullets)

        # Get mouse position for aiming
        mouse_x, mouse_y = pygame.mouse.get_pos()
        player.angle = math.atan2(mouse_y - player.y, mouse_x - player.x)

        # Player movement
        keys = pygame.key.get_pressed()
        dx = 0
        dy = 0
        if keys[pygame.K_w]:
            dy -= PLAYER_SPEED
        if keys[pygame.K_s]:
            dy += PLAYER_SPEED
        if keys[pygame.K_a]:
            dx -= PLAYER_SPEED
        if keys[pygame.K_d]:
            dx += PLAYER_SPEED
        if dx != 0 and dy != 0:
            dx /= math.sqrt(2)
            dy /= math.sqrt(2)
        player.move(dx, dy)

        # AI movement: move towards player
        for ai in ais[:]:
            if ai.health <= 0:
                ais.remove(ai)
                continue
            ai.move_towards(player.x, player.y)

            # AI shooting (simple: shoot if has weapon and close)
            if ai.has_weapon and random.random() < 0.01:  # Random chance to shoot
                ai_angle = math.atan2(player.y - ai.y, player.x - ai.x)
                bullets.append(Bullet(ai.x, ai.y, ai_angle))

        # Update bullets
        for bullet in bullets[:]:
            bullet.update()
            if bullet.x < 0 or bullet.x > SCREEN_WIDTH or bullet.y < 0 or bullet.y > SCREEN_HEIGHT:
                bullets.remove(bullet)
                continue

            # Check bullet hit player
            if check_collision(bullet.x, bullet.y, BULLET_RADIUS, player.x, player.y, PLAYER_RADIUS):
                player.health -= WEAPON_DAMAGE
                bullets.remove(bullet)
                if player.health <= 0:
                    running = False  # Game over

            # Check bullet hit AI
            for ai in ais[:]:
                if check_collision(bullet.x, bullet.y, BULLET_RADIUS, ai.x, ai.y, PLAYER_RADIUS):
                    ai.health -= WEAPON_DAMAGE
                    bullets.remove(bullet)
                    if ai.health <= 0:
                        ais.remove(ai)

        # Check player pickup items
        for item in items[:]:
            if check_collision(player.x, player.y, PLAYER_RADIUS, item.x, item.y, ITEM_RADIUS):
                if item.item_type == 'weapon':
                    player.has_weapon = True
                elif item.item_type == 'health':
                    player.health = min(PLAYER_HEALTH, player.health + 50)
                items.remove(item)

        # Shrink zone and apply damage outside
        zone.shrink()
        if not zone.is_inside(player.x, player.y):
            player.health -= 1  # Damage over time outside zone
            if player.health <= 0:
                running = False

        for ai in ais[:]:
            if not zone.is_inside(ai.x, ai.y):
                ai.health -= 1
                if ai.health <= 0:
                    ais.remove(ai)

        # Draw everything
        zone.draw()
        player.draw()
        for ai in ais:
            ai.draw()
        for item in items:
            item.draw()
        for bullet in bullets:
            bullet.draw()

        # Draw health text
        health_text = font.render(f"Health: {player.health}", True, WHITE)
        screen.blit(health_text, (10, 10))

        # Check win condition
        if not ais:
            win_text = font.render("You Win!", True, GREEN)
            screen.blit(win_text, (SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2))
            running = False  # End game on win

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()

# For bullet collisions, add a flag to track if bullet should be removed:
for bullet in bullets[:]:
    bullet.update()
    if bullet.x < 0 or bullet.x > SCREEN_WIDTH or bullet.y < 0 or bullet.y > SCREEN_HEIGHT:
        bullets.remove(bullet)
        continue

    bullet_hit = False
    
    # Check bullet hit player
    if check_collision(bullet.x, bullet.y, BULLET_RADIUS, player.x, player.y, PLAYER_RADIUS):
        player.health -= WEAPON_DAMAGE
        bullet_hit = True
        if player.health <= 0:
            running = False

    # Check bullet hit AI
    if not bullet_hit:  # Only check if bullet didn't already hit player
        for ai in ais[:]:
            if check_collision(bullet.x, bullet.y, BULLET_RADIUS, ai.x, ai.y, PLAYER_RADIUS):
                ai.health -= WEAPON_DAMAGE
                bullet_hit = True
                break
    
    if bullet_hit and bullet in bullets:
        bullets.remove(bullet)
        
