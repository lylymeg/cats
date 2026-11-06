import pygame
import random
import math
import sys

pygame.init()

# Dimensions de la fenêtre
WIDTH, HEIGHT = 950, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Virtual Desktop Cats Simulator (VS Code Pets style)")
clock = pygame.time.Clock()

# Couleurs (Thème Bureau Dark Mode)
DARK_BG = (18, 22, 33)
FLOOR_COLOR = (28, 34, 48)
TEXT_COLOR = (240, 245, 255)
GRAY = (120, 130, 150)
ACCENT_PINK = (255, 105, 180)

# Liste de prénoms mignons pour les chats
CAT_NAMES = ["Mochi", "Simba", "Luna", "Oliver", "Nala", "Kitty", "Felix", "Neko", "Milky", "Ziggy", "Panther"]

# Polices
font_medium = pygame.font.SysFont("Arial", 20, bold=True)
font_small = pygame.font.SysFont("Arial", 13, bold=True)
font_tiny = pygame.font.SysFont("Arial", 11)

class Cat:
    def __init__(self, x, y, name=None):
        self.x = x
        self.y = y
        self.name = name if name else random.choice(CAT_NAMES)
        self.color = random.choice([
            (240, 150, 60),   # Roux (Ginger)
            (220, 220, 220),  # Blanc
            (60, 60, 60),     # Noir
            (180, 110, 50),   # Tigré brun
            (140, 140, 160)   # Gris bleuté
        ])
        self.target_x = x
        self.target_y = y
        self.state = "idle"  # "idle", "walking", "sleeping", "chasing"
        self.state_timer = random.randint(60, 180)
        self.speed = 1.8
        self.facing_right = random.choice([True, False])

    def update(self, toy_pos):
        # Si une baballe / laser est actif, les chats courent après !
        if toy_pos:
            self.state = "chasing"
            self.target_x, self.target_y = toy_pos
        else:
            # Gestion des états aléatoires (marche, sieste, immobile)
            self.state_timer -= 1
            if self.state_timer <= 0:
                self.state_timer = random.randint(90, 250)
                choice = random.choices(["idle", "walking", "sleeping"], weights=[40, 45, 15])[0]
                self.state = choice
                if self.state == "walking":
                    # Choisir une nouvelle position aléatoire sur le bureau
                    self.target_x = random.uniform(100, WIDTH - 100)
                    self.target_y = random.uniform(120, HEIGHT - 80)

        # Mouvement vers la cible
        if self.state in ["walking", "chasing"]:
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            dist = math.hypot(dx, dy)

            if dist > 4:
                self.facing_right = dx > 0
                current_speed = self.speed * 1.8 if self.state == "chasing" else self.speed
                self.x += (dx / dist) * current_speed
                self.y += (dy / dist) * current_speed
            else:
                if self.state == "chasing":
                    self.state = "idle"

        # Limites de l'écran
        self.x = max(40, min(WIDTH - 40, self.x))
        self.y = max(100, min(HEIGHT - 40, self.y))

    def draw(self, surface):
        # Corps du chat (stylisé mignon / pixel-art vectoriel)
        cx, cy = int(self.x), int(self.y)
        
        # Oreilles
        ear_offset = 8 if self.facing_right else -8
        pygame.draw.polygon(surface, self.color, [(cx - 12, cy - 10), (cx - 6, cy - 22), (cx - 2, cy - 12)])
        pygame.draw.polygon(surface, self.color, [(cx + 2, cy - 12), (cx + 6, cy - 22), (cx + 12, cy - 10)])

        # Corps (ovale)
        pygame.draw.ellipse(surface, self.color, (cx - 16, cy - 10, 32, 22))

        # Tête
        head_x = cx + (6 if self.facing_right else -6)
        pygame.draw.circle(surface, self.color, (head_x, cy - 8), 11)

        # Yeux / Sommeil
        if self.state == "sleeping":
            pygame.draw.line(surface, (40, 40, 40), (head_x - 4, cy - 9), (head_x - 1, cy - 7), 2)
            pygame.draw.line(surface, (40, 40, 40), (head_x + 1, cy - 7), (head_x + 4, cy - 9), 2)
            # Effet Zzz
            zzz_txt = font_tiny.render("z Z z", True, (180, 190, 210))
            surface.blit(zzz_txt, (cx + 12, cy - 28))
        else:
            eye_dir = 2 if self.facing_right else -2
            pygame.draw.circle(surface, (30, 30, 30), (head_x + eye_dir - 2, cy - 9), 2)
            pygame.draw.circle(surface, (30, 30, 30), (head_x + eye_dir + 3, cy - 9), 2)

        # Queue
        tail_start_x = cx - 12 if self.facing_right else cx + 12
        tail_end_x = tail_start_x + (14 if self.facing_right else -14)
        pygame.draw.line(surface, self.color, (tail_start_x, cy), (tail_end_x, cy - 10), 3)

        # Étiquette du nom au-dessus du chat
        name_surf = font_small.render(self.name, True, TEXT_COLOR)
        name_rect = name_surf.get_rect(center=(cx, cy - 28))
        
        # Petit fond semi-transparent pour le nom
        bg_rect = name_rect.inflate(8, 4)
        pygame.draw.rect(surface, (30, 38, 55), bg_rect, border_radius=6)
        pygame.draw.rect(surface, (70, 90, 120), bg_rect, 1, border_radius=6)
        surface.blit(name_surf, name_rect.topleft)

# Initialisation de la colonie de chats de compagnie
cats = [
    Cat(WIDTH // 2 - 80, HEIGHT // 2, "Mochi"),
    Cat(WIDTH // 2 + 80, HEIGHT // 2, "Simba")
]

toy_position = None  # Position du pointeur / jouet cliqué

running = True
while running:
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and mouse_pos[1] > 90:  # Clic gauche sur le bureau
                toy_position = mouse_pos

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:
                # Appuyer sur 'C' pour adopter un nouveau chat !
                spawn_x = random.randint(100, WIDTH - 100)
                spawn_y = random.randint(120, HEIGHT - 80)
                cats.append(Cat(spawn_x, spawn_y))
            elif event.key == pygame.K_r:
                # Réinitialiser / vider le bureau
                cats = [Cat(WIDTH // 2, HEIGHT // 2, "Mochi")]
                toy_position = None

    # Mettre à jour tous les chats
    for cat in cats:
        cat.update(toy_position)

    # --- RENDU GRAPHIQUE ---
    screen.fill(DARK_BG)

    # Dessiner un faux "bureau / tapis de souris géant" au centre
    desk_rect = pygame.Rect(40, 90, WIDTH - 80, HEIGHT - 130)
    pygame.draw.rect(screen, FLOOR_COLOR, desk_rect, border_radius=16)
    pygame.draw.rect(screen, (45, 55, 75), desk_rect, 2, border_radius=16)

    # Dessiner le jouet / laser si actif
    if toy_position:
        pygame.draw.circle(screen, ACCENT_PINK, toy_position, 6)
        pygame.draw.circle(screen, TEXT_COLOR, toy_position, 10, 2)
        # Le jouet disparaît une fois que les chats s'en approchent
        if all(math.hypot(c.x - toy_position[0], c.y - toy_position[1]) < 30 for c in cats):
            toy_position = None

    # Dessiner tous les chats
    for cat in cats:
        cat.draw(screen)

    # --- HUD ET INSTRUCTIONS ---
    title_txt = font_medium.render("VIRTUAL DESKTOP PETS — COMPAGNONS DE CODE", True, TEXT_COLOR)
    screen.blit(title_txt, (WIDTH // 2 - title_txt.get_width() // 2, 12))

    stats_txt = font_small.render(f"Chats adoptés : {len(cats)}", True, ACCENT_PINK)
    screen.blit(stats_txt, (60, 45))

    inst_txt = font_small.render("CLIC GAUCHE : Lancer un jouet | C : Adopter un chat | R : Reset", True, GRAY)
    screen.blit(inst_txt, (WIDTH - inst_txt.get_width() - 60, 45))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()