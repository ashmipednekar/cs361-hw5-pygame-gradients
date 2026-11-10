#!/usr/bin/env python
""" pygame.examples.gradients

Shows pygame.draw.gradient_rect() filling rects and whole surfaces with
linear, radial and conic gradients, redrawn every frame.

Panels:

* Linear: a vertical sky with three color stops
* Linear: a gradient whose direction rotates
* Radial: a glow that follows the mouse
* Conic: a spinning color wheel
* Hard stops: stops at the same position make sharp stripes
* Alpha: a fade from transparent to opaque, blitted over a checkerboard

Keyboard Controls:

* Space - pause or resume the animation
* S     - save a screenshot (gradients.png)
* Esc   - quit

Run with ``--screenshot FILE`` to draw a single frame, save it and exit.
"""
import argparse
import math
import time

import pygame as pg
from pygame import Vector2

WINDOW_SIZE = (960, 620)
HEADER_HEIGHT = 40
PANEL_SIZE = (300, 270)
GAP = 15

BACKGROUND = pg.Color(24, 24, 32)
TEXT = pg.Color(235, 235, 245)

RAINBOW = ["red", "yellow", "green", "cyan", "blue", "magenta", "red"]


def panel_rects():
    """Returns the six panel rects, in a 3 x 2 grid below the header."""
    w, h = PANEL_SIZE
    rects = []
    for row in range(2):
        for col in range(3):
            x = GAP + col * (w + GAP)
            y = HEADER_HEIGHT + GAP + row * (h + GAP)
            rects.append(pg.Rect(x, y, w, h))
    return rects


def make_checkerboard(size, cell=15):
    """A gray checkerboard, to show where a surface is transparent."""
    board = pg.Surface(size)
    board.fill((200, 200, 200))
    for y in range(0, size[1], cell):
        for x in range(0, size[0], cell):
            if (x // cell + y // cell) % 2:
                board.fill((140, 140, 140), (x, y, cell, cell))
    return board


def draw_label(screen, font, rect, text):
    """Draws a caption in the top left of a panel, on a dark backing."""
    image = font.render(text, True, TEXT)
    backing = pg.Surface((image.get_width() + 12, image.get_height() + 6),
                         pg.SRCALPHA)
    backing.fill((0, 0, 0, 150))
    screen.blit(backing, (rect.x + 8, rect.y + 8))
    screen.blit(image, (rect.x + 14, rect.y + 11))


def draw_panels(screen, panels, t, mouse, alpha_layer, checkerboard):
    """Draws all six gradients for animation time t (seconds)."""
    sky, rotating, glow, wheel, stripes, fade = panels

    # 1. Linear, default direction: top row to bottom row of the rect.
    pg.draw.gradient_rect(screen, ["#0b1d51", "#3d6cb9", "#f6c28b"], sky)

    # 2. Linear, any angle: start and end points rotate around the center.
    direction = Vector2(1, 0).rotate_rad(t * 0.8) * (rotating.width / 2)
    center = Vector2(rotating.center)
    pg.draw.gradient_rect(screen, ["#ff5f6d", "#ffc371", "#47cf73"], rotating,
                          start_pos=center - direction,
                          end_pos=center + direction)

    # 3. Radial: centered on the mouse, or orbiting when the mouse is away.
    if glow.collidepoint(mouse):
        focus = Vector2(mouse)
    else:
        focus = Vector2(glow.center) + Vector2(70, 0).rotate_rad(t * 1.5)
    pg.draw.gradient_rect(
        screen,
        [(0.0, "white"), (0.15, "#fff3a0"), (0.45, "#ff8c42"),
         (1.0, "#2b0b3f")],
        glow, start_pos=focus, end_pos=focus + Vector2(130, 0),
        kind="radial")

    # 4. Conic: the direction where the wheel starts turns over time.
    spin = Vector2(1, 0).rotate_rad(t * 0.6)
    wheel_center = Vector2(wheel.center)
    pg.draw.gradient_rect(screen, RAINBOW, wheel, start_pos=wheel_center,
                          end_pos=wheel_center + spin, kind="conic")

    # 5. Hard stops: two stops at the same position give a sharp edge.
    pg.draw.gradient_rect(
        screen,
        [(0.0, "#0055a4"), (1 / 3, "#0055a4"), (1 / 3, "white"),
         (2 / 3, "white"), (2 / 3, "#ef4135"), (1.0, "#ef4135")],
        stripes, start_pos=stripes.topleft,
        end_pos=(stripes.right - 1, stripes.top))

    # 6. Alpha: fill a whole SRCALPHA surface (rect=None), then blit it.
    pg.draw.gradient_rect(
        alpha_layer, [(30, 144, 255, 0), (30, 144, 255, 255)],
        start_pos=(0, 0), end_pos=(alpha_layer.get_width() - 1, 0))
    screen.blit(checkerboard, fade)
    screen.blit(alpha_layer, fade)


def main(screenshot=None):
    pg.init()
    screen = pg.display.set_mode(WINDOW_SIZE)
    pg.display.set_caption("pygame.draw.gradient_rect demo")
    font = pg.font.Font(None, 22)
    title_font = pg.font.Font(None, 28)
    clock = pg.time.Clock()

    panels = panel_rects()
    labels = ["Linear: three stops", "Linear: rotating", "Radial: follow mouse",
              "Conic: color wheel", "Hard stops", "Alpha over checkerboard"]
    alpha_layer = pg.Surface(PANEL_SIZE, pg.SRCALPHA)
    checkerboard = make_checkerboard(PANEL_SIZE)

    t = 1.0
    paused = False
    gradient_ms = 0.0
    running = True

    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    running = False
                elif event.key == pg.K_SPACE:
                    paused = not paused
                elif event.key == pg.K_s:
                    pg.image.save(screen, "gradients.png")
                    print("Saved gradients.png")

        screen.fill(BACKGROUND)

        start = time.perf_counter()
        mouse = pg.mouse.get_pos() if screenshot is None else (-1, -1)
        draw_panels(screen, panels, t, mouse, alpha_layer, checkerboard)
        # Smooth the timing so the number is readable.
        elapsed = (time.perf_counter() - start) * 1000
        gradient_ms = elapsed if gradient_ms == 0 else (
            gradient_ms * 0.9 + elapsed * 0.1)

        for rect, label in zip(panels, labels):
            draw_label(screen, font, rect, label)

        fps = clock.get_fps()
        fps_text = f"{fps:5.1f} fps   " if fps else ""
        title = title_font.render(
            f"pygame.draw.gradient_rect   {fps_text}"
            f"6 gradients: {gradient_ms:.2f} ms/frame", True, TEXT)
        screen.blit(title, (GAP, (HEADER_HEIGHT - title.get_height()) // 2 + 4))
        hint = font.render("Space: pause   S: screenshot   Esc: quit", True,
                           (150, 150, 165))
        screen.blit(hint, (WINDOW_SIZE[0] - hint.get_width() - GAP,
                           (HEADER_HEIGHT - hint.get_height()) // 2 + 4))

        if screenshot is not None:
            pg.image.save(screen, screenshot)
            print(f"Saved {screenshot}")
            break

        pg.display.flip()
        dt = clock.tick(60) / 1000
        if not paused:
            t += dt

    pg.quit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--screenshot", metavar="FILE",
                        help="draw one frame, save it to FILE and exit")
    main(parser.parse_args().screenshot)
