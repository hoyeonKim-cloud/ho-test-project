import pygame
import random

# Pygame 초기화
pygame.init()

# 화면 크기 설정
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("우주선 슈팅 게임")

# 색상 정의
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# 우주선 클래스
class Spaceship:
    def __init__(self):
        self.image = pygame.image.load("spaceship.png")
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT - 50))
        self.health = 100  # 체력
        self.bullet_cooldown = 0  # 총알 쿨다운

    def move(self, dx):
        self.rect.x += dx
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        # 체력바 그리기
        pygame.draw.rect(surface, RED, (self.rect.centerx - 50, self.rect.top - 10, 100, 5))
        pygame.draw.rect(surface, GREEN, (self.rect.centerx - 50, self.rect.top - 10, self.health, 5))

# 총알 클래스
class Bullet:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 5, 10)

    def move(self):
        self.rect.y -= 10

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, self.rect)

# 적 클래스
class Enemy:
    def __init__(self):
        self.image = pygame.transform.scale(pygame.image.load("enemy.png"), (40, 40))  # 이미지 크기 조정
        self.rect = self.image.get_rect(center=(random.randint(0, WIDTH - 40), 0))  # 위에서 생성
        self.health = 5  # 체력
        self.cooldown = random.randint(20, 50)  # 랜덤한 쿨다운 시간
        self.counter = 0
        self.shooting_y = random.randint(100, 300)  # 총알을 쏘기 시작할 Y 좌표
        self.is_shooting = False  # 총알 발사 상태

    def shoot(self):
        if self.is_shooting and self.counter >= self.cooldown:
            self.counter = 0
            return Bullet(self.rect.centerx, self.rect.bottom)
        self.counter += 1
        return None

    def move(self):
        if self.rect.y < self.shooting_y:
            self.rect.y += 2  # 아래로 이동
        else:
            self.is_shooting = True  # 특정 Y 좌표에 도달하면 멈춤

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        # 체력바 그리기
        pygame.draw.rect(surface, RED, (self.rect.centerx - 25, self.rect.top - 10, 50, 5))
        pygame.draw.rect(surface, GREEN, (self.rect.centerx - 25, self.rect.top - 10, (self.health / 5) * 50, 5))

# 돌진하는 적 클래스
class ChargeEnemy:
    def __init__(self):
        self.image = pygame.transform.scale(pygame.image.load("meteo.png"), (40, 40))  # 이미지 크기 조정
        self.rect = self.image.get_rect(center=(random.randint(0, WIDTH - 40), 0))  # 위에서 생성
        self.health = 3  # 체력

    def move(self):
        self.rect.y += 5  # 아래로 이동

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        # 체력바 그리기
        pygame.draw.rect(surface, RED, (self.rect.centerx - 25, self.rect.top - 10, 50, 5))
        pygame.draw.rect(surface, GREEN, (self.rect.centerx - 25, self.rect.top - 10, (self.health / 3) * 50, 5))

# 게임 루프
def main():
    clock = pygame.time.Clock()
    spaceship = Spaceship()
    bullets = []
    enemies = []
    charge_enemies = []
    enemy_bullets = []
    score = 0

    # 적 추가 함수
    def add_enemy():
        if random.random() < 0.5:
            enemies.append(Enemy())
        else:
            charge_enemies.append(ChargeEnemy())

    running = True
    while running:
        screen.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            spaceship.move(-5)
        if keys[pygame.K_RIGHT]:
            spaceship.move(5)

        # 마우스 클릭으로 총알 발사
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0]:  # 왼쪽 클릭
            if spaceship.bullet_cooldown == 0:
                bullets.append(Bullet(spaceship.rect.centerx, spaceship.rect.top))
                spaceship.bullet_cooldown = 10  # 쿨다운 시간

        # 쿨다운 감소
        if spaceship.bullet_cooldown > 0:
            spaceship.bullet_cooldown -= 1

        # 총알 이동 및 충돌 처리
        for bullet in bullets[:]:
            bullet.move()
            if bullet.rect.bottom < 0:
                bullets.remove(bullet)
            else:
                for enemy in enemies[:]:
                    if bullet.rect.colliderect(enemy.rect):
                        enemy.health -= 1
                        bullets.remove(bullet)
                        if enemy.health <= 0:
                            enemies.remove(enemy)
                            score += 1
                        break
                for charge_enemy in charge_enemies[:]:
                    if bullet.rect.colliderect(charge_enemy.rect):
                        charge_enemy.health -= 1
                        bullets.remove(bullet)
                        if charge_enemy.health <= 0:
                            charge_enemies.remove(charge_enemy)
                            score += 1
                        break
            bullet.draw(screen)

        # 적 총알 발사 및 이동
        for enemy in enemies[:]:
            enemy_bullet = enemy.shoot()
            if enemy_bullet:
                enemy_bullets.append(enemy_bullet)
            enemy.move()  # 적 이동
            enemy.draw(screen)

        # 돌진하는 적 이동
        for charge_enemy in charge_enemies[:]:
            charge_enemy.move()
            if charge_enemy.rect.top > HEIGHT:
                charge_enemies.remove(charge_enemy)
            if charge_enemy.rect.colliderect(spaceship.rect):
                spaceship.health -= 1
                charge_enemies.remove(charge_enemy)
            charge_enemy.draw(screen)

        # 적 총알 이동 및 충돌 처리
        for enemy_bullet in enemy_bullets[:]:
            enemy_bullet.rect.y += 5
            if enemy_bullet.rect.top > HEIGHT:
                enemy_bullets.remove(enemy_bullet)
            elif enemy_bullet.rect.colliderect(spaceship.rect):
                spaceship.health -= 1
                enemy_bullets.remove(enemy_bullet)

        # 적 총알 그리기
        for enemy_bullet in enemy_bullets:
            pygame.draw.rect(screen, WHITE, enemy_bullet.rect)

        # 우주선 그리기
        spaceship.draw(screen)

        # 게임 종료 조건
        if spaceship.health <= 0:
            font = pygame.font.SysFont(None, 74)
            game_over_text = font.render("Game Over", True, WHITE)
            text_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(game_over_text, text_rect)  # 중앙에 "Game Over" 표시
            pygame.display.flip()
            pygame.time.delay(2000)  # 2초 후 종료
            running = False

        # 점수 표시
        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"점수: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        # 일정 시간마다 적 추가
        if random.random() < 0.02:
            add_enemy()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
