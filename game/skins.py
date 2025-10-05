from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List

import pygame


@dataclass(frozen=True)
class Skin:
    """Represents a playable skin with a factory that returns a fresh surface."""

    name: str
    factory: Callable[[], pygame.Surface]

    def create_surface(self) -> pygame.Surface:
        return self.factory()


def _base_canvas() -> pygame.Surface:
    return pygame.Surface((56, 64), pygame.SRCALPHA)


def _draw_face(surface: pygame.Surface, center: tuple[int, int], radius: int, color: tuple[int, int, int]):
    pygame.draw.circle(surface, color, center, radius)
    pygame.draw.circle(surface, (30, 30, 30), (center[0] - 6, center[1] - 4), 2)
    pygame.draw.circle(surface, (30, 30, 30), (center[0] + 6, center[1] - 4), 2)
    pygame.draw.arc(surface, (40, 40, 40), pygame.Rect(center[0] - 8, center[1] - 2, 16, 12), 0.3, 2.8, 2)


def _make_yuki() -> pygame.Surface:
    surface = _base_canvas()
    uniform = (210, 230, 255)
    trim = (110, 200, 255)
    hair = (200, 215, 255)
    pygame.draw.rect(surface, uniform, pygame.Rect(18, 22, 20, 30), border_radius=8)
    pygame.draw.rect(surface, trim, pygame.Rect(18, 38, 20, 10), border_radius=4)
    pygame.draw.polygon(surface, hair, [(18, 18), (12, 6), (16, 24)])
    pygame.draw.polygon(surface, hair, [(38, 18), (44, 6), (40, 24)])
    _draw_face(surface, (28, 24), 12, (255, 240, 240))
    pygame.draw.rect(surface, trim, pygame.Rect(14, 48, 28, 10), border_radius=6)
    pygame.draw.circle(surface, trim, (18, 26), 3)
    pygame.draw.circle(surface, trim, (38, 26), 3)
    pygame.draw.rect(surface, trim, pygame.Rect(6, 20, 8, 6), border_radius=3)
    pygame.draw.rect(surface, trim, pygame.Rect(42, 20, 8, 6), border_radius=3)
    return surface


def _make_kairo() -> pygame.Surface:
    surface = _base_canvas()
    ninja = (60, 20, 90)
    glow = (80, 255, 190)
    pygame.draw.rect(surface, ninja, pygame.Rect(16, 16, 24, 36), border_radius=6)
    pygame.draw.rect(surface, ninja, pygame.Rect(12, 44, 32, 12), border_radius=6)
    pygame.draw.rect(surface, glow, pygame.Rect(16, 24, 24, 4))
    pygame.draw.rect(surface, glow, pygame.Rect(16, 32, 24, 4))
    pygame.draw.circle(surface, glow, (28, 20), 10, 2)
    pygame.draw.line(surface, glow, (12, 52), (44, 52), 3)
    pygame.draw.polygon(surface, glow, [(10, 26), (18, 30), (10, 34)])
    pygame.draw.polygon(surface, glow, [(46, 26), (38, 30), (46, 34)])
    return surface


def _make_nova() -> pygame.Surface:
    surface = _base_canvas()
    dress = (245, 210, 245)
    aura = (200, 150, 255)
    pygame.draw.ellipse(surface, dress, pygame.Rect(16, 28, 24, 24))
    pygame.draw.circle(surface, dress, (28, 24), 12)
    pygame.draw.circle(surface, aura, (20, 12), 6)
    pygame.draw.circle(surface, aura, (36, 12), 6)
    pygame.draw.circle(surface, (255, 255, 255), (20, 12), 3)
    pygame.draw.circle(surface, (255, 255, 255), (36, 12), 3)
    pygame.draw.circle(surface, (255, 255, 255), (28, 12), 4)
    pygame.draw.circle(surface, (255, 180, 240), (28, 24), 10, 2)
    pygame.draw.circle(surface, (230, 200, 255), (28, 44), 10, 2)
    return surface


def _make_orion() -> pygame.Surface:
    surface = _base_canvas()
    armor = (150, 30, 30)
    neon = (40, 190, 255)
    pygame.draw.rect(surface, armor, pygame.Rect(16, 18, 24, 32), border_radius=6)
    pygame.draw.rect(surface, armor, pygame.Rect(14, 40, 28, 14), border_radius=6)
    pygame.draw.rect(surface, neon, pygame.Rect(18, 24, 20, 6))
    pygame.draw.rect(surface, neon, pygame.Rect(18, 34, 20, 6))
    pygame.draw.polygon(surface, neon, [(28, 14), (22, 4), (34, 4)])
    pygame.draw.rect(surface, (80, 80, 80), pygame.Rect(24, 8, 8, 16))
    pygame.draw.rect(surface, neon, pygame.Rect(8, 30, 8, 4))
    pygame.draw.rect(surface, neon, pygame.Rect(40, 30, 8, 4))
    pygame.draw.rect(surface, neon, pygame.Rect(26, 48, 4, 14))
    return surface


def _make_astra() -> pygame.Surface:
    surface = _base_canvas()
    cloak = (30, 30, 80)
    stars = (120, 180, 255)
    pygame.draw.polygon(surface, cloak, [(10, 54), (28, 10), (46, 54)])
    pygame.draw.circle(surface, (180, 150, 255), (28, 22), 12)
    for i in range(6):
        pygame.draw.circle(surface, stars, (14 + i * 7, 40 - (i % 2) * 6), 2)
    pygame.draw.rect(surface, stars, pygame.Rect(24, 8, 8, 8))
    pygame.draw.polygon(surface, stars, [(28, 4), (22, 12), (34, 12)])
    pygame.draw.circle(surface, (255, 255, 200), (28, 32), 6)
    return surface


def _make_pixel_pup() -> pygame.Surface:
    surface = _base_canvas()
    body = (150, 255, 180)
    helmet = (180, 220, 255)
    pygame.draw.rect(surface, body, pygame.Rect(18, 26, 20, 20), border_radius=4)
    pygame.draw.rect(surface, body, pygame.Rect(14, 42, 28, 10), border_radius=4)
    pygame.draw.circle(surface, helmet, (28, 20), 14)
    pygame.draw.rect(surface, (70, 120, 90), pygame.Rect(22, 18, 12, 8))
    pygame.draw.rect(surface, (255, 255, 255), pygame.Rect(24, 16, 4, 4))
    pygame.draw.circle(surface, (255, 255, 255), (20, 20), 2)
    pygame.draw.circle(surface, (255, 255, 255), (36, 20), 2)
    pygame.draw.polygon(surface, (255, 255, 255), [(28, 32), (24, 36), (32, 36)])
    return surface


def _make_zeta() -> pygame.Surface:
    surface = _base_canvas()
    gown = (190, 140, 220)
    trim = (240, 210, 120)
    pygame.draw.ellipse(surface, gown, pygame.Rect(16, 30, 24, 26))
    pygame.draw.circle(surface, (230, 200, 255), (28, 22), 12)
    pygame.draw.rect(surface, trim, pygame.Rect(18, 34, 20, 4))
    pygame.draw.rect(surface, trim, pygame.Rect(20, 44, 16, 4))
    pygame.draw.circle(surface, trim, (28, 10), 6)
    pygame.draw.circle(surface, trim, (20, 12), 3)
    pygame.draw.circle(surface, trim, (36, 12), 3)
    pygame.draw.arc(surface, trim, pygame.Rect(14, 18, 28, 22), 0.2, 2.9, 2)
    return surface


def _make_cosmo_kun() -> pygame.Surface:
    surface = _base_canvas()
    suit = (30, 80, 180)
    jet = (255, 120, 40)
    pygame.draw.rect(surface, suit, pygame.Rect(18, 20, 20, 28), border_radius=6)
    pygame.draw.rect(surface, suit, pygame.Rect(16, 40, 24, 10), border_radius=6)
    pygame.draw.circle(surface, (200, 220, 255), (28, 18), 12)
    pygame.draw.rect(surface, jet, pygame.Rect(24, 46, 8, 16))
    pygame.draw.polygon(surface, jet, [(28, 62), (22, 54), (34, 54)])
    pygame.draw.rect(surface, (255, 200, 120), pygame.Rect(12, 32, 6, 16))
    pygame.draw.rect(surface, (255, 200, 120), pygame.Rect(38, 32, 6, 16))
    return surface


def _make_neon_oni() -> pygame.Surface:
    surface = _base_canvas()
    body = (20, 20, 20)
    glow = (255, 40, 150)
    pygame.draw.rect(surface, body, pygame.Rect(16, 18, 24, 34), border_radius=8)
    pygame.draw.rect(surface, body, pygame.Rect(14, 40, 28, 14), border_radius=6)
    pygame.draw.polygon(surface, glow, [(22, 12), (20, 2), (26, 8)])
    pygame.draw.polygon(surface, glow, [(34, 12), (36, 2), (30, 8)])
    pygame.draw.circle(surface, glow, (22, 26), 4)
    pygame.draw.circle(surface, glow, (34, 26), 4)
    pygame.draw.rect(surface, glow, pygame.Rect(24, 34, 8, 4))
    pygame.draw.rect(surface, glow, pygame.Rect(10, 34, 4, 20))
    pygame.draw.rect(surface, glow, pygame.Rect(42, 34, 4, 20))
    return surface


def _make_luma() -> pygame.Surface:
    surface = _base_canvas()
    jelly = (120, 220, 255)
    glow = (150, 255, 210)
    pygame.draw.ellipse(surface, glow, pygame.Rect(12, 10, 32, 26))
    pygame.draw.ellipse(surface, jelly, pygame.Rect(16, 14, 24, 20))
    for i in range(5):
        pygame.draw.line(surface, glow, (16 + i * 6, 34), (14 + i * 6, 54), 3)
    pygame.draw.circle(surface, (255, 255, 255), (24, 22), 3)
    pygame.draw.circle(surface, (255, 255, 255), (32, 22), 3)
    pygame.draw.rect(surface, glow, pygame.Rect(20, 28, 16, 6), border_radius=3)
    return surface


def _make_robo_tan() -> pygame.Surface:
    surface = _base_canvas()
    metal = (180, 190, 200)
    screen = (80, 200, 255)
    pygame.draw.rect(surface, metal, pygame.Rect(14, 16, 28, 32), border_radius=6)
    pygame.draw.rect(surface, metal, pygame.Rect(18, 40, 20, 14), border_radius=6)
    pygame.draw.rect(surface, screen, pygame.Rect(18, 20, 20, 14), border_radius=4)
    pygame.draw.rect(surface, (30, 30, 30), pygame.Rect(20, 24, 4, 4))
    pygame.draw.rect(surface, (30, 30, 30), pygame.Rect(30, 24, 4, 4))
    pygame.draw.rect(surface, (255, 255, 255), pygame.Rect(24, 28, 8, 4))
    pygame.draw.rect(surface, metal, pygame.Rect(10, 20, 4, 18))
    pygame.draw.rect(surface, metal, pygame.Rect(42, 20, 4, 18))
    return surface


def _make_echo() -> pygame.Surface:
    surface = _base_canvas()
    aura = (150, 130, 200)
    core = (220, 220, 255)
    pygame.draw.circle(surface, aura, (28, 26), 18)
    pygame.draw.circle(surface, core, (28, 26), 12)
    pygame.draw.circle(surface, (120, 90, 200), (28, 26), 6)
    for angle in range(0, 360, 45):
        pygame.draw.circle(surface, aura, (28 + int(16 * pygame.math.Vector2(1, 0).rotate(angle).x), 26 + int(16 * pygame.math.Vector2(1, 0).rotate(angle).y)), 2)
    pygame.draw.rect(surface, aura, pygame.Rect(22, 40, 12, 12), border_radius=6)
    return surface


def _make_astropug() -> pygame.Surface:
    surface = _base_canvas()
    suit = (180, 210, 255)
    fur = (240, 220, 200)
    pygame.draw.rect(surface, suit, pygame.Rect(16, 30, 24, 24), border_radius=8)
    pygame.draw.circle(surface, suit, (28, 22), 16)
    pygame.draw.circle(surface, fur, (22, 24), 6)
    pygame.draw.circle(surface, fur, (34, 24), 6)
    pygame.draw.circle(surface, (60, 40, 40), (22, 24), 3)
    pygame.draw.circle(surface, (60, 40, 40), (34, 24), 3)
    pygame.draw.arc(surface, (60, 40, 40), pygame.Rect(24, 26, 8, 6), 0.2, 2.8, 2)
    pygame.draw.polygon(surface, suit, [(18, 46), (12, 58), (20, 56)])
    pygame.draw.polygon(surface, suit, [(38, 46), (44, 58), (36, 56)])
    return surface


def _make_sakura_san() -> pygame.Surface:
    surface = _base_canvas()
    petals = (255, 200, 220)
    trim = (240, 240, 255)
    pygame.draw.rect(surface, petals, pygame.Rect(18, 22, 20, 28), border_radius=8)
    pygame.draw.rect(surface, petals, pygame.Rect(16, 44, 24, 12), border_radius=6)
    pygame.draw.circle(surface, trim, (28, 18), 12)
    for dx in (-12, -6, 0, 6, 12):
        pygame.draw.circle(surface, petals, (28 + dx, 8 + abs(dx) // 3), 3)
    pygame.draw.circle(surface, (255, 240, 245), (28, 34), 8)
    pygame.draw.polygon(surface, (255, 170, 200), [(24, 26), (28, 32), (32, 26)])
    return surface


def _make_tako() -> pygame.Surface:
    surface = _base_canvas()
    body = (150, 80, 220)
    glow = (200, 150, 255)
    pygame.draw.circle(surface, body, (28, 26), 18)
    for i in range(6):
        pygame.draw.ellipse(surface, glow, pygame.Rect(10 + i * 6, 32, 12, 18))
    pygame.draw.circle(surface, (255, 255, 255), (22, 24), 3)
    pygame.draw.circle(surface, (255, 255, 255), (34, 24), 3)
    pygame.draw.rect(surface, glow, pygame.Rect(22, 30, 12, 4), border_radius=2)
    return surface


def _make_zero() -> pygame.Surface:
    surface = _base_canvas()
    ice = (180, 220, 255)
    glow = (120, 200, 255)
    pygame.draw.rect(surface, ice, pygame.Rect(18, 20, 20, 30), border_radius=8)
    pygame.draw.rect(surface, ice, pygame.Rect(16, 42, 24, 12), border_radius=6)
    pygame.draw.circle(surface, glow, (28, 18), 12)
    pygame.draw.rect(surface, (220, 240, 255), pygame.Rect(20, 26, 16, 8))
    pygame.draw.line(surface, (255, 255, 255), (20, 48), (36, 48), 2)
    pygame.draw.line(surface, (255, 255, 255), (20, 52), (36, 52), 2)
    return surface


def _make_giga_neko() -> pygame.Surface:
    surface = _base_canvas()
    metal = (200, 200, 210)
    accent = (250, 230, 80)
    pygame.draw.rect(surface, metal, pygame.Rect(16, 26, 24, 22), border_radius=8)
    pygame.draw.rect(surface, metal, pygame.Rect(12, 44, 32, 10), border_radius=6)
    pygame.draw.circle(surface, metal, (22, 18), 8)
    pygame.draw.circle(surface, metal, (34, 18), 8)
    pygame.draw.circle(surface, (20, 20, 20), (22, 18), 3)
    pygame.draw.circle(surface, (20, 20, 20), (34, 18), 3)
    pygame.draw.polygon(surface, accent, [(28, 40), (22, 46), (34, 46)])
    pygame.draw.polygon(surface, accent, [(12, 34), (8, 30), (8, 38)])
    pygame.draw.polygon(surface, accent, [(44, 34), (48, 30), (48, 38)])
    return surface


def _make_vega() -> pygame.Surface:
    surface = _base_canvas()
    coat = (150, 20, 60)
    gold = (255, 210, 90)
    pygame.draw.rect(surface, coat, pygame.Rect(16, 18, 24, 34), border_radius=8)
    pygame.draw.rect(surface, coat, pygame.Rect(14, 42, 28, 12), border_radius=6)
    pygame.draw.circle(surface, (200, 150, 120), (28, 18), 12)
    pygame.draw.circle(surface, gold, (34, 20), 5)
    pygame.draw.circle(surface, gold, (20, 24), 3)
    pygame.draw.rect(surface, gold, pygame.Rect(18, 30, 20, 6))
    pygame.draw.line(surface, gold, (12, 20), (12, 52), 3)
    return surface


def _make_kira() -> pygame.Surface:
    surface = _base_canvas()
    body = (200, 160, 255)
    rainbow = [(255, 100, 180), (255, 180, 80), (120, 220, 255), (160, 255, 160)]
    pygame.draw.rect(surface, body, pygame.Rect(18, 24, 20, 24), border_radius=8)
    pygame.draw.circle(surface, body, (22, 16), 8)
    pygame.draw.circle(surface, body, (34, 16), 8)
    pygame.draw.polygon(surface, body, [(18, 48), (8, 56), (20, 54)])
    pygame.draw.polygon(surface, body, [(38, 48), (48, 56), (36, 54)])
    for i, color in enumerate(rainbow):
        pygame.draw.line(surface, color, (12, 56 + i), (44, 48 + i), 3)
    pygame.draw.circle(surface, (255, 255, 255), (24, 22), 2)
    pygame.draw.circle(surface, (255, 255, 255), (32, 22), 2)
    return surface


def _make_bubble_bot() -> pygame.Surface:
    surface = _base_canvas()
    bubble = (200, 230, 255)
    bot = (160, 200, 255)
    pygame.draw.circle(surface, bubble, (28, 24), 20, 2)
    pygame.draw.circle(surface, bot, (28, 24), 12)
    pygame.draw.rect(surface, bot, pygame.Rect(20, 34, 16, 18), border_radius=8)
    pygame.draw.circle(surface, (255, 255, 255), (24, 20), 3)
    pygame.draw.circle(surface, (255, 255, 255), (32, 20), 3)
    pygame.draw.rect(surface, (255, 255, 255), pygame.Rect(22, 40, 12, 4))
    pygame.draw.circle(surface, bubble, (18, 10), 4)
    pygame.draw.circle(surface, bubble, (38, 12), 3)
    return surface


SKINS: List[Skin] = [
    Skin("Yuki", _make_yuki),
    Skin("Kairo", _make_kairo),
    Skin("Nova", _make_nova),
    Skin("Orion", _make_orion),
    Skin("Astra", _make_astra),
    Skin("Pixel-Pup", _make_pixel_pup),
    Skin("Zeta", _make_zeta),
    Skin("Cosmo-Kun", _make_cosmo_kun),
    Skin("Neon Oni", _make_neon_oni),
    Skin("Luma", _make_luma),
    Skin("Robo-Tan", _make_robo_tan),
    Skin("Echo", _make_echo),
    Skin("AstroPug", _make_astropug),
    Skin("Sakura-San", _make_sakura_san),
    Skin("Tako", _make_tako),
    Skin("Zero", _make_zero),
    Skin("Giga-Neko", _make_giga_neko),
    Skin("Vega", _make_vega),
    Skin("Kira", _make_kira),
    Skin("Bubble-Bot", _make_bubble_bot),
]

