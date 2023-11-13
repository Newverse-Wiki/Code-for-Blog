import pygame
import math

class Particle(pygame.sprite.Sprite):
    def __init__(self, position, velocity, mass, *groups):
        super().__init__(*groups)

        self.position = pygame.Vector2(position)
        self.velocity = pygame.Vector2(velocity)
        self.acceleration = pygame.Vector2(0, 0)

        self.update_mass(mass)

    def update_mass(self, mass):
        self.mass   = mass
        self.radius = int(math.cbrt(mass / 20))
        self.scale_radius = self.radius

        # 质量越大，黄色越深
        b_value = max(0, int(255 - mass / 250))
        self.color = pygame.Color(255, 255, b_value)

        self.update_image(self.radius)

    def update_image(self, radius):
        self.image = pygame.Surface((2 * radius, 2 * radius))
        self.image.set_colorkey('black')
        pygame.draw.circle(self.image, self.color, (radius, radius), radius)

    def scale_image(self, scale):

        radius = max(1, int(self.radius * scale))

        if self.scale_radius != radius:
            self.scale_radius = radius
            self.update_image(radius)

    def update(self, dt):
        self.velocity += self.acceleration * dt
        self.position += self.velocity * dt
