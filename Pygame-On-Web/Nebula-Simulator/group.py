import pygame
import math

class NebulaGroup(pygame.sprite.Group):
    def __init__(self, *sprites):
        super().__init__(*sprites)

        self.combined = []

    def attract(self):
        p_list = self.sprites()

        for p in p_list:
            p.acceleration = pygame.Vector2(0, 0)

        for i, p1 in enumerate(p_list):
            for p2 in p_list[i+1:]:
                r1 = p1.position
                r2 = p2.position
                m1 = p1.mass
                m2 = p2.mass

                r = r2 - r1
                d = r.length()
                
                if d < p1.radius + p2.radius:
                    if not ((p1 in self.combined) or (p2 in self.combined)):
                        v1 = p1.velocity
                        v2 = p2.velocity

                        mm = m1 + m2
                        #rr = (m1 * r1 + m2 * r2) / mm
                        vv = (m1 * v1 + m2 * v2) / mm

                        if m1 >= m2:
                            p1.update_mass(mm)
                            p1.velocity = vv
                            self.combined.append(p2)
                        else:
                            p2.update_mass(mm)
                            p2.velocity = vv
                            self.combined.append(p1)
                else:
                    fr = r / d ** 3
                    p1.acceleration += m2 * fr
                    p2.acceleration -= m1 * fr

    def update(self, dt):
        self.attract()

        for sprite in self.combined:
            sprite.kill()
        self.combined.clear()

        for sprite in self.sprites():
            sprite.update(dt)
