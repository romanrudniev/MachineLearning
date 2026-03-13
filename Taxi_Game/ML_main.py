from collections import defaultdict
import pygame as pg
import random
import numpy as np

width, height = 700, 450
FPS = 60
BLACK = (0, 0, 0)

x_direction = 0
y_direction = 0

player_speed = 2
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
    'hole': pg.image.load('img/hole.png'),
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

    if hotel_rect.colliderect(player_rect):
        return True

    return False

def draw_message(text, color):
    font = pg.font.SysFont(None, 36)
    message = font.render(text, True, color)
    screen.blit(message, (350, 150))
    pg.display.flip()
    pg.time.delay(1500)

player_view = 'rear'
player_rect = images_dict['player'][player_view].get_rect()
player_rect.x = 300
player_rect.y = 300

hotel_img = images_dict['hotel']
hotel_rect = hotel_img.get_rect()

hotel_positions = [
    (60, 50),
    (555, 50),
    (60, 300),
    (445, 300)
]

hotel_rect.x, hotel_rect.y = random.choice(hotel_positions)

parking_img = images_dict['parking']
parking_rect = parking_img.get_rect()
parking_rect.x, parking_rect.y = hotel_rect.x, hotel_rect.y + hotel_rect.height

passenger_img = images_dict['passenger']
passenger_rect = passenger_img.get_rect()
(passenger_rect.x, passenger_rect.y) = random.choice(hotel_positions)
passenger_rect.y += hotel_rect.height

def apply_action(action):
    global player_view
    x_direction = 0
    y_direction = 0
    if action is None:
        return
    if action == 0:
        x_direction = 1
        player_view = 'right'
    elif action == 1:
        x_direction = -1
        player_view = 'left'
    elif action == 2:
        y_direction = -1
        player_view = 'rear'
    elif action == 3:
        y_direction = 1
        player_view = 'front'

    new_x = player_rect.x + player_rect.width * x_direction
    new_y = player_rect.y + player_rect.height * y_direction

    if 0 < new_x < width - player_rect.width:
        player_rect.x = new_x
    if 0 < new_y < height - player_rect.height:
        player_rect.y = new_y

actions = [0, 1, 2, 3] # 0-right 1-left 2-up 3-bottom
Q_table = defaultdict(lambda: [0, 0, 0, 0])

learning_rate = 0.9
discount_factor = 0.9
# epsilon = -1
epsilon = 0.1

def choose_action(state):
    if random.random() < epsilon:
        return random.choice(actions)
    else:
        return np.argmax(Q_table[state])

def update_q(state, action, reward, next_state):
    best_next = max(Q_table[next_state])
    Q_table[state][action] += learning_rate * (reward + discount_factor * best_next - Q_table[state][action])

def make_step():
    current_state = (player_rect.x, player_rect.y)
    action = choose_action(current_state)

    reward = -1
    episode_end = False
    success = False
    apply_action(action)
    if is_crash():
        reward = -200
        episode_end = True

    if parking_rect.contains(player_rect):
        reward = 200
        episode_end = True
        success = True

    next_state = (player_rect.x, player_rect.y)
    update_q(current_state, action, reward, next_state)

    return(episode_end, success)

num_episodes = 300
max_step = 50
for episode in range(num_episodes):
    player_rect.x, player_rect.y = 300, 300
    for step in range(max_step):
        (episode_end, success) = make_step()
        if episode_end:
            print(success)
            break

print(Q_table)
draw_message("Навчання завершено", pg.Color('blue'))

run = True
while run:
    timer.tick(FPS)

    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False

    player_rect.x += player_speed * x_direction
    player_rect.y += player_speed * y_direction

    x_direction = 0
    y_direction = 0

    if is_crash():
        print("IS CRASH")
        player_view = 'rear'
        player_rect.x = 300
        player_rect.y = 300
        (passenger_rect.x, passenger_rect.y) = random.choice(hotel_positions)
        passenger_rect.y += hotel_rect.height
        continue

    if parking_rect.contains(player_rect):
        draw_message("Перемога!!!", pg.Color('green'))

        player_view = 'rear'
        player_rect.x = 300
        player_rect.y = 300

        hotel_rect.x, hotel_rect.y = random.choice(hotel_positions)
        parking_rect.x, parking_rect.y = hotel_rect.x, hotel_rect.y + hotel_rect.height

        (passenger_rect.x, passenger_rect.y) = random.choice(hotel_positions)
        passenger_rect.y += hotel_rect.height
        continue

    if player_rect.colliderect(passenger_rect):
        passenger_rect.x, passenger_rect.y = player_rect.x, player_rect.y

    screen.fill(BLACK)
    screen.blit(images_dict['bg'], (0, 0))

    screen.blit(hotel_img, hotel_rect)
    screen.blit(parking_img, parking_rect)
    screen.blit(passenger_img, passenger_rect)
    screen.blit(images_dict['player'][player_view], player_rect)

    pg.display.flip()

pg.quit()
