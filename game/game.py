from __future__ import annotations

import random
from typing import Tuple

import pygame

from . import settings
from .bonus import Bonus
from .platform import Platform, PlatformManager
from .player import Player


class Button:
    def __init__(self, text: str, center: Tuple[int, int], font: pygame.font.Font):
        self.text = text
        self.font = font
        self.rect = pygame.Rect(0, 0, 260, 80)
        self.rect.center = center

    def draw(self, surface: pygame.Surface):
        mouse_pos = pygame.mouse.get_pos()
        is_hover = self.rect.collidepoint(mouse_pos)
        color = settings.BUTTON_HOVER_COLOR if is_hover else settings.BUTTON_COLOR
        pygame.draw.rect(surface, color, self.rect, border_radius=12)
        pygame.draw.rect(surface, settings.WHITE, self.rect, width=3, border_radius=12)
        text_surf = self.font.render(self.text, True, settings.WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        return is_hover

    def is_clicked(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False


class Game:
    """Main game state machine."""

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Sky Jumper")
        self.screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = "start"
        self.font_large = pygame.font.SysFont("arial", 48, bold=True)
        self.font_medium = pygame.font.SysFont("arial", 32)
        self.font_small = pygame.font.SysFont("arial", 24)

        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.bonuses = pygame.sprite.Group()
        self.platform_manager = PlatformManager(self.platforms)
        self.player = Player(self.platforms, self.bonuses)
        self.all_sprites.add(self.player)
        self.camera_offset = 0.0
        self.highscore = self.load_highscore()
        self.score = 0
        self.best_score = self.highscore
        self.stars = self.create_starfield()
        self.planets = self.create_planets()
        self.start_button = Button("Начать игру", (settings.WIDTH // 2, settings.HEIGHT // 2), self.font_medium)
        self.retry_button = Button("Попробовать снова", (settings.WIDTH // 2, settings.HEIGHT // 2 + 120), self.font_medium)
        self.generate_initial_platforms()

    def load_highscore(self) -> int:
        try:
            with open(settings.HIGHSCORE_FILE, "r", encoding="utf-8") as file:
                return int(file.read().strip() or 0)
        except (OSError, ValueError):
            return 0

    def save_highscore(self):
        try:
            with open(settings.HIGHSCORE_FILE, "w", encoding="utf-8") as file:
                file.write(str(self.best_score))
        except OSError:
            pass

    # -------------------- Setup helpers --------------------
    def reset(self):
        self.all_sprites.empty()
        self.platforms.empty()
        self.bonuses.empty()
        self.platform_manager = PlatformManager(self.platforms)
        self.player = Player(self.platforms, self.bonuses)
        self.all_sprites.add(self.player)
        self.camera_offset = 0.0
        self.score = 0
        self.stars = self.create_starfield()
        self.planets = self.create_planets()
        self.generate_initial_platforms()

    def generate_initial_platforms(self):
        base = Platform(settings.WIDTH // 2 - 80, settings.HEIGHT - 50, 160)
        self.platforms.add(base)
        self.platform_manager.last_platform_center = base.rect.centerx
        y = settings.HEIGHT - 150
        while y > -settings.HEIGHT:
            difficulty = self.difficulty_factor(y)
            platform = self.platform_manager.create_platform(y, difficulty)
            if random.random() < settings.BONUS_CHANCE:
                bonus = Bonus(platform.rect.centerx, platform.rect.top)
                self.bonuses.add(bonus)
            y -= random.randint(settings.PLATFORM_MIN_Y_GAP, settings.PLATFORM_MAX_Y_GAP)

    # -------------------- Game loop --------------------
    def run(self):
        while self.running:
            if self.state == "start":
                self.start_screen()
            elif self.state == "running":
                self.game_loop()
            elif self.state == "game_over":
                self.game_over_screen()
        pygame.quit()

    def start_screen(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            if self.start_button.is_clicked(event):
                self.reset()
                self.state = "running"

        self.draw_background(0)
        title_text = self.font_large.render("Sky Jumper", True, settings.WHITE)
        subtitle = self.font_small.render("Используйте A/D или ←/→ для движения, W или ↑ для прыжка", True, settings.WHITE)
        self.screen.blit(title_text, title_text.get_rect(center=(settings.WIDTH // 2, 200)))
        self.screen.blit(subtitle, subtitle.get_rect(center=(settings.WIDTH // 2, 260)))
        self.start_button.draw(self.screen)
        self.draw_highscore_text()
        pygame.display.flip()
        self.clock.tick(settings.FPS)

    def game_loop(self):
        dt = self.clock.tick(settings.FPS) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_w, pygame.K_UP):
                self.player.jump()

        self.update_sprites(dt)
        self.update_camera()
        self.check_game_over()
        self.draw()

    def game_over_screen(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            if self.retry_button.is_clicked(event):
                self.reset()
                self.state = "running"
                return

        self.draw_background(self.camera_offset)
        title = self.font_large.render("Game Over", True, settings.WHITE)
        score_text = self.font_medium.render(f"Высота: {self.score:.0f}", True, settings.WHITE)
        best_text = self.font_small.render(f"Рекорд: {self.best_score:.0f}", True, settings.WHITE)
        self.screen.blit(title, title.get_rect(center=(settings.WIDTH // 2, 200)))
        self.screen.blit(score_text, score_text.get_rect(center=(settings.WIDTH // 2, 280)))
        self.screen.blit(best_text, best_text.get_rect(center=(settings.WIDTH // 2, 330)))
        self.retry_button.draw(self.screen)
        pygame.display.flip()
        self.clock.tick(settings.FPS)

    # -------------------- Update methods --------------------
    def update_sprites(self, dt: float):
        self.all_sprites.update(dt)
        self.platforms.update()
        self.spawn_platforms()
        self.platform_manager.cleanup(self.camera_offset)

    def spawn_platforms(self):
        highest_platform_y = min((p.rect.top for p in self.platforms), default=settings.HEIGHT)
        while highest_platform_y > -settings.HEIGHT:
            gap = random.randint(settings.PLATFORM_MIN_Y_GAP, settings.PLATFORM_MAX_Y_GAP)
            spawn_y = highest_platform_y - gap
            difficulty = self.difficulty_factor(spawn_y)
            platform = self.platform_manager.create_platform(spawn_y, difficulty)
            highest_platform_y = platform.rect.top
            if random.random() < settings.BONUS_CHANCE:
                bonus = Bonus(platform.rect.centerx, platform.rect.top)
                self.bonuses.add(bonus)

        for bonus in list(self.bonuses):
            if bonus.rect.top - self.camera_offset > settings.HEIGHT + settings.PLATFORM_GAP:
                bonus.kill()

    def update_camera(self):
        # Move camera when player reaches upper third of the screen
        offset_threshold = settings.HEIGHT // 3
        if self.player.rect.top < offset_threshold:
            diff = offset_threshold - self.player.rect.top
            self.player.shift(diff)
            self.camera_offset -= diff
            self.platform_manager.shift(diff)
            for bonus in self.bonuses:
                bonus.shift(diff)
            height_climbed = max(0, -self.camera_offset)
            blocks = int(height_climbed // settings.SCORE_BLOCK_HEIGHT)
            self.score = max(self.score, blocks * settings.SCORE_PER_BLOCK)
            self.best_score = max(self.best_score, self.score, self.highscore)

    def check_game_over(self):
        if self.player.rect.top + self.camera_offset > settings.HEIGHT:
            self.state = "game_over"
            if self.score > self.highscore:
                self.best_score = self.score
                self.highscore = self.best_score
                self.save_highscore()

    # -------------------- Drawing methods --------------------
    def draw(self):
        self.draw_background(self.camera_offset)
        self.platforms.draw(self.screen)
        self.bonuses.draw(self.screen)
        self.all_sprites.draw(self.screen)
        self.draw_ui()
        pygame.display.flip()

    def draw_background(self, offset: float):
        gradient = pygame.Surface((settings.WIDTH, settings.HEIGHT))
        for y in range(settings.HEIGHT):
            t = (y + offset * 0.005) / settings.HEIGHT
            t = max(0, min(1, t))
            r = int(settings.SKY_TOP[0] * (1 - t) + settings.SKY_BOTTOM[0] * t)
            g = int(settings.SKY_TOP[1] * (1 - t) + settings.SKY_BOTTOM[1] * t)
            b = int(settings.SKY_TOP[2] * (1 - t) + settings.SKY_BOTTOM[2] * t)
            pygame.draw.line(gradient, (r, g, b), (0, y), (settings.WIDTH, y))
        self.screen.blit(gradient, (0, 0))
        self.draw_starfield(offset)
        self.draw_planets(offset)

    def draw_ui(self):
        score_text = self.font_small.render(f"Высота: {self.score:.0f}", True, settings.WHITE)
        self.screen.blit(score_text, (20, 20))
        self.draw_highscore_text()

    def draw_highscore_text(self):
        highscore_text = self.font_small.render(f"Лучший результат: {self.best_score:.0f}", True, settings.WHITE)
        rect = highscore_text.get_rect(topright=(settings.WIDTH - 20, 20))
        self.screen.blit(highscore_text, rect)

    # -------------------- Difficulty scaling --------------------
    def difficulty_factor(self, y: float) -> float:
        # Difficulty increases with height achieved
        height = max(0, -y + self.camera_offset)
        return 1.0 + height / 3000

    # -------------------- Background helpers --------------------
    def create_starfield(self):
        stars = []
        for _ in range(90):
            star = {
                "x": random.randint(0, settings.WIDTH),
                "y": random.uniform(0, settings.HEIGHT * 6),
                "size": random.randint(1, 3),
                "parallax": random.uniform(0.2, 0.6),
                "color": random.choice(settings.STAR_COLORS),
            }
            stars.append(star)
        return stars

    def create_planets(self):
        planets = []
        for _ in range(4):
            radius = random.randint(18, 42)
            planets.append(
                {
                    "x": random.randint(radius, settings.WIDTH - radius),
                    "y": random.uniform(0, settings.HEIGHT * 5),
                    "radius": radius,
                    "parallax": random.uniform(0.05, 0.25),
                    "color": random.choice(settings.PLANET_COLORS),
                    "ring": random.choice([True, False]),
                }
            )
        return planets

    def draw_starfield(self, offset: float):
        for star in self.stars:
            screen_y = star["y"] - offset * star["parallax"]
            while screen_y < -star["size"]:
                screen_y += settings.HEIGHT * 6
            while screen_y > settings.HEIGHT:
                screen_y -= settings.HEIGHT * 6
            pygame.draw.circle(
                self.screen,
                star["color"],
                (int(star["x"]), int(screen_y)),
                star["size"],
            )

    def draw_planets(self, offset: float):
        for planet in self.planets:
            screen_y = planet["y"] - offset * planet["parallax"]
            height_range = settings.HEIGHT * 5
            while screen_y < -planet["radius"] * 2:
                screen_y += height_range
            while screen_y > settings.HEIGHT + planet["radius"]:
                screen_y -= height_range
            center = (int(planet["x"]), int(screen_y))
            pygame.draw.circle(self.screen, planet["color"], center, planet["radius"])
            if planet["ring"]:
                ring_rect = pygame.Rect(0, 0, planet["radius"] * 2, planet["radius"] // 2)
                ring_rect.center = center
                pygame.draw.ellipse(self.screen, (245, 245, 245), ring_rect, width=2)

