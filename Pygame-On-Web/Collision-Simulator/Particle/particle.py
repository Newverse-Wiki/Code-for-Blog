import pygame

class Particle(pygame.sprite.Sprite):
    def __init__(self, position, radius, velocity):
        super().__init__()

        self.position = pygame.Vector2(position)
        self.velocity = pygame.Vector2(velocity)

        self.radius = radius
        self.color = 'blue'

        self.image = pygame.Surface((2 * radius, 2 * radius))
        self.image.fill('black')
        self.image.set_colorkey('black')
        pygame.draw.circle(self.image, self.color, (radius, radius), radius)
        self.rect = self.image.get_rect(center = self.position)

    def bounce(self):
        screen_width, screen_height = pygame.display.get_window_size()

        bound_left   = self.radius
        bound_right  = screen_width - self.radius
        bound_top    = self.radius
        bound_bottom = screen_height - self.radius

        if self.position.x < bound_left:
            self.position.x = 2.0 * bound_left - self.position.x
            if self.velocity.x < 0:
                self.velocity.x *= -1.0
        elif self.position.x > bound_right:
            self.position.x = 2.0 * bound_right - self.position.x
            if self.velocity.x > 0:
                self.velocity.x *= -1.0

        if self.position.y < bound_top:
            self.position.y = 2.0 * bound_top - self.position.y
            if self.velocity.y < 0:
                self.velocity.y *= -1.0
        elif self.position.y > bound_bottom:
            self.position.y = 2.0 * bound_bottom - self.position.y
            if self.velocity.y > 0:
                self.velocity.y *= -1.0

    def update(self, dt):
        self.position += self.velocity * dt
        self.bounce()
        self.rect.center = self.position
