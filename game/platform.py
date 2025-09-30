from __future__ import annotations

import random
from typing import Tuple

import pygame

from . import settings


class Platform(pygame.sprite.Sprite):
    """Static or horizontal moving platform that the player can jump on."""

    def __init__(self, x: int, y: int, width: int, moving: bool = False, speed: float = 0.0):
        super().__init__()
        self.image = pygame.Surface((width, settings.PLATFORM_HEIGHT))
        self.image.fill(settings.LIGHT_GREY if not moving else (180, 220, 255))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.moving = moving
        self.speed = speed
        self.direction = 1

    def update(self):
        if not self.moving:
            return

        self.rect.x += self.speed * self.direction
        if self.rect.right > settings.WIDTH or self.rect.left < 0:
            self.direction *= -1
            self.rect.x += self.speed * self.direction

    @property
    def position(self) -> Tuple[int, int]:
        return self.rect.topleft


class PlatformManager:
    """Keeps track of platforms and generates new ones as the player ascends."""

    def __init__(self, group: pygame.sprite.Group):
        self.group = group

    def create_platform(self, y: int, difficulty: float) -> Platform:
        width = random.randint(*settings.PLATFORM_WIDTH_RANGE)
        x = random.randint(0, settings.WIDTH - width)
        moving = random.random() < settings.MOVING_PLATFORM_CHANCE * difficulty
        speed = random.uniform(1.5, 3.5) * difficulty if moving else 0
        platform = Platform(x, y, width, moving=moving, speed=speed)
        self.group.add(platform)
        return platform

    def cleanup(self, camera_offset: float):
        """Remove platforms that are far below the visible area."""
        for platform in list(self.group):
            if platform.rect.top - camera_offset > settings.HEIGHT + settings.PLATFORM_GAP:
                platform.kill()

    def shift(self, dy: float):
        for platform in self.group:
            platform.rect.y += dy

