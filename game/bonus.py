from __future__ import annotations

import random
from typing import Optional, TYPE_CHECKING

import pygame

from . import settings

if TYPE_CHECKING:  # pragma: no cover - only for type hints
    from .player import Player


class Bonus(pygame.sprite.Sprite):
    """Base bonus class. Provides boost effects when collected."""

    TYPES = ("spring", "rocket")

    def __init__(self, x: int, y: int, bonus_type: Optional[str] = None):
        super().__init__()
        if bonus_type is None:
            bonus_type = random.choices(
                Bonus.TYPES, weights=[settings.SPRING_CHANCE, 1 - settings.SPRING_CHANCE]
            )[0]
        self.type = bonus_type
        size = (30, 20) if self.type == "spring" else (30, 40)
        self.image = pygame.Surface(size, pygame.SRCALPHA)
        if self.type == "spring":
            self.image.fill((0, 255, 0))
        else:
            self.image.fill((255, 120, 0))
        self.rect = self.image.get_rect(midtop=(x, y - 10))

    def apply(self, player: "Player"):
        if self.type == "spring":
            player.velocity.y = settings.SUPER_JUMP_SPEED
        else:
            player.activate_rocket()
        self.kill()

    def shift(self, dy: float):
        self.rect.y += dy
