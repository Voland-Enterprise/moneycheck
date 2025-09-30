from __future__ import annotations

from dataclasses import dataclass

import pygame

from . import settings


@dataclass
class PlayerState:
    on_ground: bool = False
    rocket_time: int = 0


class Player(pygame.sprite.Sprite):
    """Main controllable character."""

    def __init__(self, platforms: pygame.sprite.Group, bonuses: pygame.sprite.Group):
        super().__init__()
        self.image = self.create_sprite()
        self.rect = self.image.get_rect(midbottom=(settings.WIDTH // 2, settings.HEIGHT - 150))
        self.velocity = pygame.math.Vector2(0, 0)
        self.state = PlayerState()
        self.platforms = platforms
        self.bonuses = bonuses

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.velocity.x = -settings.PLAYER_MOVE_SPEED
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.velocity.x = settings.PLAYER_MOVE_SPEED
        else:
            self.velocity.x = 0

    def jump(self):
        if self.state.on_ground and not self.state.rocket_time:
            self.velocity.y = settings.PLAYER_JUMP_SPEED
            self.state.on_ground = False

    def activate_rocket(self):
        self.state.rocket_time = settings.ROCKET_DURATION
        self.velocity.y = settings.ROCKET_BOOST_SPEED

    def update(self, dt: float):
        self.handle_input()
        self.apply_physics(dt)
        self.wrap_horizontally()
        self.check_platform_collisions()
        self.check_bonus_collisions()

    def apply_physics(self, dt: float):
        if self.state.rocket_time > 0:
            self.state.rocket_time -= 1
            self.velocity.y = min(self.velocity.y, settings.ROCKET_BOOST_SPEED)
        else:
            self.velocity.y += settings.GRAVITY

        self.rect.x += self.velocity.x
        self.rect.y += self.velocity.y

    def wrap_horizontally(self):
        if self.rect.right < 0:
            self.rect.left = settings.WIDTH
        elif self.rect.left > settings.WIDTH:
            self.rect.right = 0

    def check_platform_collisions(self):
        if self.velocity.y > 0:
            hits = pygame.sprite.spritecollide(self, self.platforms, False)
            for platform in hits:
                if self.rect.bottom - platform.rect.top < 25:
                    self.rect.bottom = platform.rect.top
                    self.velocity.y = settings.PLAYER_JUMP_SPEED
                    self.state.on_ground = True
                    return
        self.state.on_ground = False

    def check_bonus_collisions(self):
        hits = pygame.sprite.spritecollide(self, self.bonuses, False)
        for bonus in hits:
            bonus.apply(self)

    def shift(self, dy: float):
        self.rect.y += dy

    def create_sprite(self) -> pygame.Surface:
        """Create a cute astro-cat sprite using primitive shapes."""
        surface = pygame.Surface((56, 64), pygame.SRCALPHA)
        body_color = (240, 240, 255)
        suit_color = (135, 206, 250)
        visor_color = (180, 220, 255)
        cat_color = (255, 200, 160)

        # Space suit body
        pygame.draw.rect(surface, body_color, pygame.Rect(14, 20, 28, 34), border_radius=10)
        pygame.draw.rect(surface, suit_color, pygame.Rect(18, 38, 20, 14), border_radius=6)
        # Helmet
        pygame.draw.circle(surface, body_color, (28, 24), 22)
        pygame.draw.circle(surface, visor_color, (28, 24), 18)

        # Cat ears
        pygame.draw.polygon(surface, cat_color, [(18, 6), (10, 20), (20, 16)])
        pygame.draw.polygon(surface, cat_color, [(38, 6), (36, 16), (46, 20)])

        # Cat face inside helmet
        pygame.draw.circle(surface, cat_color, (28, 26), 12)
        pygame.draw.circle(surface, (80, 50, 40), (24, 24), 2)
        pygame.draw.circle(surface, (80, 50, 40), (32, 24), 2)
        pygame.draw.polygon(surface, (120, 70, 60), [(28, 28), (26, 32), (30, 32)])
        pygame.draw.arc(surface, (90, 60, 50), pygame.Rect(22, 28, 12, 10), 0.2, 2.9, 2)

        # Jetpack accent
        pygame.draw.rect(surface, suit_color, pygame.Rect(12, 34, 6, 12), border_radius=3)
        pygame.draw.rect(surface, suit_color, pygame.Rect(38, 34, 6, 12), border_radius=3)

        return surface
