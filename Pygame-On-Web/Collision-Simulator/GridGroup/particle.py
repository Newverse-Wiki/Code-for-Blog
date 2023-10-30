import pygame

class Particle(pygame.sprite.Sprite):
    def __init__(self, position, velocity, radius, density, groups):
        super().__init__(groups)

        self.position = pygame.Vector2(position)
        self.velocity = pygame.Vector2(velocity)

        self.radius  = radius
        self.density = density
        self.mass    = density * radius ** 2
        
        self.elasticity = 0.95

        # 密度越大，蓝色越深
        rg_value = 200 - density * 10
        self.color = pygame.Color(rg_value, rg_value, 255)

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

    def collide(self, p2):
        p1 = self

        separation  = p1.position - p2.position
        overlap = p1.radius + p2.radius - separation.length()

        if overlap > 0:
            m1 = p1.mass
            m2 = p2.mass
            r1 = p1.position
            r2 = p2.position
            v1 = p1.velocity
            v2 = p2.velocity

            v1n = v1 - 2 * m2 / (m1 + m2) * (v1 - v2).dot(r1 - r2) / (r1 - r2).length_squared() * (r1 - r2)
            v2n = v2 - 2 * m1 / (m1 + m2) * (v2 - v1).dot(r2 - r1) / (r2 - r1).length_squared() * (r2 - r1)

            p1.velocity = v1n * self.elasticity
            p2.velocity = v2n * self.elasticity

            separation.scale_to_length(overlap)
            p1.position += 0.5 * separation
            p2.position -= 0.5 * separation

    def update(self, dt):
        self.position += self.velocity * dt
        self.bounce()
        self.rect.center = self.position
