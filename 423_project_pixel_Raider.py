from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math

# Screen dimensions
WIDTH, HEIGHT = 800, 600

# Player attributes
player_pos = [50, 50]
player_speed = 5

# Maze attributes
maze_walls = []
cell_size = 40
rows, cols = HEIGHT // cell_size, WIDTH // cell_size

# Treasure attributes
treasures = []
num_treasures = 5

# Enemy attributes
enemies = []
num_enemies = 3
enemy_speed = 2

# Game state
score = 0
game_over = False

def draw_point(x, y):
    glBegin(GL_POINTS)
    glVertex2f(x, y)
    glEnd()

def mid_point_line(x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    d = 2 * dy - dx
    y = y1
    for x in range(x1, x2 + 1):
        draw_point(x, y)
        if d > 0:
            y += 1
            d -= 2 * dx
        d += 2 * dy

def mid_point_circle(cx, cy, r):
    x, y = 0, r
    d = 1 - r
    draw_circle_points(cx, cy, x, y)
    while x < y:
        if d < 0:
            d += 2 * x + 3
        else:
            d += 2 * (x - y) + 5
            y -= 1
        x += 1
        draw_circle_points(cx, cy, x, y)

def draw_circle_points(cx, cy, x, y):
    draw_point(cx + x, cy + y)
    draw_point(cx - x, cy + y)
    draw_point(cx + x, cy - y)
    draw_point(cx - x, cy - y)
    draw_point(cx + y, cy + x)
    draw_point(cx - y, cy + x)
    draw_point(cx + y, cy - x)
    draw_point(cx - y, cy - x)

def generate_maze():
    global maze_walls
    for row in range(rows):
        for col in range(cols):
            if random.random() < 0.3:
                x1, y1 = col * cell_size, row * cell_size
                x2, y2 = x1 + cell_size, y1 + cell_size
                maze_walls.append(((x1, y1), (x2, y2)))

def place_treasures():
    global treasures
    treasures = [(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(num_treasures)]

def place_enemies():
    global enemies
    enemies = [(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(num_enemies)]

def is_collision(pos1, pos2, radius=10):
    return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2) < radius

def move_enemies():
    global enemies
    for i, (ex, ey) in enumerate(enemies):
        direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
        enemies[i] = (ex + direction[0] * enemy_speed, ey + direction[1] * enemy_speed)

def draw_text(x, y, text, color=(1, 1, 1)):
    glColor3f(*color)
    glRasterPos2f(x, y)
    for char in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))

def draw_button(x, y, width, height, label):
    glColor3f(0.5, 0.5, 0.5)
    glBegin(GL_QUADS)
    glVertex2f(x, y)
    glVertex2f(x + width, y)
    glVertex2f(x + width, y + height)
    glVertex2f(x, y + height)
    glEnd()

    draw_text(x + 10, y + 10, label, color=(0, 0, 0))

def display():
    global score, game_over

    glClear(GL_COLOR_BUFFER_BIT)

    if game_over:
        draw_text(WIDTH // 2 - 50, HEIGHT // 2, "Game Over", color=(1, 0, 0))
        glutSwapBuffers()
        return

    # Draw maze walls
    glColor3f(1, 1, 1)
    for (start, end) in maze_walls:
        mid_point_line(start[0], start[1], end[0], end[1])

    # Draw treasures
    glColor3f(0, 1, 0)
    for tx, ty in treasures:
        mid_point_circle(tx, ty, 5)

    # Draw enemies
    glColor3f(1, 0, 0)
    for ex, ey in enemies:
        mid_point_circle(ex, ey, 5)

    # Draw player
    glColor3f(0, 0, 1)
    mid_point_circle(player_pos[0], player_pos[1], 5)

    # Draw scoreboard
    draw_text(10, HEIGHT - 20, f"Score: {score}")

    # Draw end button
    draw_button(WIDTH - 100, HEIGHT - 40, 80, 30, "End")

    glutSwapBuffers()

def keyboard(key, x, y):
    global player_pos, score, game_over, treasures

    if game_over:
        return

    if key == b'w':
        player_pos[1] += player_speed
    elif key == b's':
        player_pos[1] -= player_speed
    elif key == b'a':
        player_pos[0] -= player_speed
    elif key == b'd':
        player_pos[0] += player_speed

    # Check collisions
    new_treasures = []
    for t in treasures:
        if is_collision(player_pos, t):
            score += 10
        else:
            new_treasures.append(t)
    treasures = new_treasures

    if not treasures:
        place_treasures()

    for (start, end) in maze_walls:
        if (start[0] <= player_pos[0] <= end[0] or end[0] <= player_pos[0] <= start[0]) and \
           (start[1] <= player_pos[1] <= end[1] or end[1] <= player_pos[1] <= start[1]):
            game_over = True

    for ex, ey in enemies:
        if is_collision(player_pos, (ex, ey)):
            game_over = True

    glutPostRedisplay()

def mouse(button, state, x, y):
    global game_over

    if game_over:
        return

    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        if WIDTH - 100 <= x <= WIDTH - 20 and HEIGHT - 40 <= HEIGHT - y <= HEIGHT - 10:
            print("Game Ended by User!")
            game_over = True

    glutPostRedisplay()

def timer(value):
    if not game_over:
        move_enemies()
    glutPostRedisplay()
    glutTimerFunc(100, timer, 0)

def main():
    global maze_walls, treasures, enemies

    # OpenGL initialization
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(WIDTH, HEIGHT)
    glutCreateWindow(b"Pixel Raider - A Treasure Hunt Adventure")
    glClearColor(0, 0, 0, 1)
    gluOrtho2D(0, WIDTH, 0, HEIGHT)

    generate_maze()
    place_treasures()
    place_enemies()

    glutDisplayFunc(display)
    glutKeyboardFunc(keyboard)
    glutMouseFunc(mouse)
    glutTimerFunc(100, timer, 0)

    glutMainLoop()

if __name__ == "__main__":
    main()
