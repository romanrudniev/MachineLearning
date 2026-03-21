from collections import defaultdict
import pygame as pg
import random
import numpy as np

width, height = 700, 450
FPS = 60

pg.init()
screen = pg.display.set_mode([width, height])
timer = pg.time.Clock()

images_dict = {
    'bg': pg.image.load('img/Background.png'),
    'player': {
        'rear': pg.image.load('img/cab_rear.png'),
        'left': pg.image.load('img/cab_left.png'),
        'front': pg.image.load('img/cab_front.png'),
        'right': pg.image.load('img/cab_right.png'),
    },
    'hotel': pg.transform.scale(pg.image.load('img/hotel.png'), (40, 40)),
    'passenger': pg.image.load('img/passenger.png'),
    'parking': pg.transform.scale(pg.image.load('img/parking.png'), (80, 45)),
}

def is_crash():
    for x in range(player_rect.x, player_rect.topright[0], 1):
        for y in range(player_rect.y, player_rect.bottomleft[1], 1):
            try:
                if screen.get_at((x, y)) == (220, 215, 177) or screen.get_at((x, y)) == (155, 144, 122, 255) or screen.get_at((x, y)) == (216, 211, 175, 255) or screen.get_at((x, y)) == (166, 164, 139, 255) or screen.get_at((x, y)) == (149, 147, 135, 255) or screen.get_at((x, y)) == (65, 113, 26, 255) or screen.get_at((x, y)) == (104, 132, 69, 255):
                    return True
            except IndexError:
                print("Назад в діапазон!!")
                return True

def draw_message(text, color):
    font = pg.font.SysFont(None, 36)
    message = font.render(text, True, color)
    screen.blit(message, (250, 150))
    pg.display.flip()
    pg.time.delay(1500)

player_view = 'rear'
player_rect = images_dict['player'][player_view].get_rect()
player_rect.x, player_rect.y = 300, 300

hotel_img = images_dict['hotel']
hotel_rect = hotel_img.get_rect()

hotel_positions = [
    (60, 50),
    (555, 50),
    (60, 300),
    (445, 300)
]

# готель
hotel_rect.x, hotel_rect.y = random.choice(hotel_positions)

# парковка
parking_img = images_dict['parking']
parking_rect = parking_img.get_rect()
parking_rect.x = hotel_rect.x
parking_rect.y = hotel_rect.y + hotel_rect.height

# пасажир
passenger_img = images_dict['passenger']
passenger_rect = passenger_img.get_rect()

available_positions = [pos for pos in hotel_positions if pos != (hotel_rect.x, hotel_rect.y)]
passenger_rect.x, passenger_rect.y = random.choice(available_positions)
passenger_rect.y += hotel_rect.height

has_passenger = False

def apply_action(action):
    global player_view
    x_dir, y_dir = 0, 0

    if action == 0:
        x_dir, player_view = 1, 'right'
    elif action == 1:
        x_dir, player_view = -1, 'left'
    elif action == 2:
        y_dir, player_view = -1, 'rear'
    elif action == 3:
        y_dir, player_view = 1, 'front'

    new_x = player_rect.x + player_rect.width * x_dir
    new_y = player_rect.y + player_rect.height * y_dir

    if 0 < new_x < width - player_rect.width:
        player_rect.x = new_x
    if 0 < new_y < height - player_rect.height:
        player_rect.y = new_y

def draw_elements():
    screen.blit(images_dict['bg'], (0, 0))
    screen.blit(hotel_img, hotel_rect)
    screen.blit(parking_img, parking_rect)

    if not has_passenger:
        screen.blit(passenger_img, passenger_rect)

    screen.blit(images_dict['player'][player_view], player_rect)
    pg.display.flip()

actions = [0, 1, 2, 3]
Q_table = defaultdict(lambda: [0, 0, 0, 0])

learning_rate = 0.9
discount_factor = 0.9
epsilon = 0.3

def choose_action(state):
    if random.random() < epsilon:
        return random.choice(actions)
    return np.argmax(Q_table[state])

def update_q(state, action, reward, next_state):
    best_next = max(Q_table[next_state])
    Q_table[state][action] += learning_rate * (
        reward + discount_factor * best_next - Q_table[state][action]
    )

def get_distance(target):
    dx = player_rect.centerx - target.centerx
    dy = player_rect.centery - target.centery
    return (dx**2 + dy**2) ** 0.5

def make_step():
    global has_passenger

    current_state = (player_rect.x, player_rect.y, has_passenger)
    action = choose_action(current_state)

    target = passenger_rect if not has_passenger else parking_rect
    old_distance = get_distance(target)

    reward = -0.1
    episode_end = False
    success = False

    apply_action(action)
    draw_elements()

    if is_crash():
        reward = -50
        episode_end = True

    elif not has_passenger and player_rect.colliderect(passenger_rect):
        has_passenger = True
        reward = 20

    elif has_passenger and parking_rect.contains(player_rect):
        reward = 50
        episode_end = True
        success = True

    else:
        target = passenger_rect if not has_passenger else parking_rect
        new_distance = get_distance(target)

        if new_distance < old_distance:
            reward += 1
        else:
            reward -= 0.5

    next_state = (player_rect.x, player_rect.y, has_passenger)
    update_q(current_state, action, reward, next_state)

    return episode_end, success

# НАВЧАННЯ
for episode in range(300):
    player_rect.x, player_rect.y = 280, 300
    has_passenger = False

    for _ in range(50):
        end, success = make_step()
        if end:
            break

draw_message("Навчання завершено", pg.Color('blue'))

# ТЕСТ
player_rect.x, player_rect.y = 280, 300
player_view = 'rear'
has_passenger = False
epsilon = -1

FPS = 20
run = True

while run:
    timer.tick(FPS)

    state = (player_rect.x, player_rect.y, has_passenger)
    action = choose_action(state)
    apply_action(action)

    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False

    if is_crash():
        draw_message("IS CRASH", pg.Color('red'))
        break

    if not has_passenger and player_rect.colliderect(passenger_rect):
        has_passenger = True

    if has_passenger and parking_rect.contains(player_rect):
        draw_message("Перемога!", pg.Color('green'))
        break

    draw_elements()

pg.quit()