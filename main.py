import pygame
from shapely.geometry import Point, Polygon
import numpy as np
import random

WIDTH = 800
HEIGHT = 500

GRID_SIZE_X = 100
GRID_SIZE_Y = 4
STEPS = 2000
LAMBDA = 3


REDRAW_EVERY = 1

running = True
pygame.init()
pygame.display.set_caption('Kohonen')
screen = pygame.display.set_mode((WIDTH, HEIGHT))


class DrawPoint:
    def update(self):
        self.cx, self.cy = pygame.mouse.get_pos()
        self.square = pygame.Rect(self.cx - 2, self.cy - 2, 5, 5)

    def get_position(self):
        return self.cx, self.cy

    def draw(self):
        pygame.draw.rect(screen, (255, 255, 255), self.square)


def draw_lines(points):
    for p in points:
        p.draw()
    for i in range(1, len(points)):
        pygame.draw.line(screen, (255, 255, 255), points[i - 1].get_position(), points[i].get_position())


def draw_end(points):
    for p in points:
        p.draw()
    for i in range(1, len(points)):
        pygame.draw.line(screen, (255, 255, 255), points[i - 1].get_position(), points[i].get_position())
    pygame.draw.line(screen, (255, 255, 255), points[0].get_position(), points[-1].get_position())


def generate_polygon(points):
    coords = []
    for p in points:
        coords.append(p.get_position())
    return Polygon(coords)


def get_points_positions(point_list):
    points = []
    for p in point_list:
        points.append(p.get_position())
    return points


def get_min_max(points):
    min_x, min_y = points[0].get_position()
    max_x, max_y = points[0].get_position()
    for p in points:
        x, y = p.get_position()
        if x < min_x:
            min_x = x
        if x > max_x:
            max_x = x
        if y < min_y:
            min_y = y
        if y > max_y:
            max_y = y

    return min_x, min_y, max_x, max_y


def generate_kohonen(min_max, x_size, y_size):
    kohonen = np.zeros((x_size, y_size), dtype='f,f')
    min_x, min_y, max_x, max_y = min_max
    for i in range(x_size):
        for j in range(y_size):
            v = (min_x + (max_x - min_x) / (x_size - 1) * i, min_y + (max_y - min_y) / (y_size - 1) * j)
            kohonen[i, j] = v
    return kohonen


def get_random_point(polygon, min_max):
    min_x, min_y, max_x, max_y = min_max
    while True:
        random_point = Point([random.uniform(min_x, max_x), random.uniform(min_y, max_y)])
        if random_point.within(polygon):
            return random_point


def draw_kohonen(kohonen, x_size, y_size):
    for k in np.nditer(kohonen):
        x, y = k[()]
        pygame.draw.rect(screen, (0, 255, 0), pygame.Rect(x - 2, y - 2, 5, 5))
    x, y = kohonen[0, 0]
    pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(x - 2, y - 2, 5, 5))

    for i in range(x_size):
        for j in range(y_size):
            if i < x_size - 1:
                pygame.draw.line(screen, (0, 255, 0), kohonen[i, j], kohonen[i + 1, j])
            if j < y_size - 1:
                pygame.draw.line(screen, (0, 255, 0), kohonen[i, j], kohonen[i, j + 1])


def get_closest_point(random_point, kohonen, x_size, y_size):
    distance = random_point.distance(Point(kohonen[0, 0]))
    closest_x = 0
    closest_y = 0
    for i in range(x_size):
        for j in range(y_size):
            d = random_point.distance(Point(kohonen[i, j]))
            if d < distance:
                distance = d
                closest_x = i
                closest_y = j
    return closest_x, closest_y


def get_rho(current_point, closest_point):
    current_x, current_y = current_point
    closest_x, closest_y = closest_point
    v = np.abs(current_x - closest_x) + np.abs(current_y - closest_y)
    return v


def point_diff(current_point, random_point):
    current_x, current_y = current_point
    random_x, random_y = random_point.x, random_point.y
    return random_x - current_x, random_y - current_y


def update_kohonen(random_point, kohonen, closest_point, x_size, y_size, alpha):
    closest_point_x, closest_point_y = closest_point
    for i in range(closest_point_x - LAMBDA, closest_point_x + LAMBDA + 1):
        if i < 0 or i >= x_size:
            continue
        for j in range(closest_point_y - LAMBDA, closest_point_y + LAMBDA + 1):
            if j < 0 or j >= y_size:
                continue
            rho = get_rho((i, j), closest_point)
            if rho > LAMBDA:
                continue
            e = np.exp(-(rho * rho) / (2 * LAMBDA * LAMBDA))
            pd = point_diff(kohonen[i, j], random_point)
            pd_x, pd_y = pd
            x, y = kohonen[i, j]
            kohonen[i, j] = x + alpha * e * pd_x, y + alpha * e * pd_y


def redraw(points, kohonen, rp):
    screen.fill((0, 0, 0))
    draw_end(points)
    pygame.draw.polygon(screen, (255, 0, 0), get_points_positions(points))
    draw_kohonen(kohonen, GRID_SIZE_X, GRID_SIZE_Y)
    pygame.draw.rect(screen, (0, 0, 255), pygame.Rect(rp.x - 2, rp.y - 2, 5, 5))
    pygame.display.flip()


points = []
draw = False
end = False

LEFT = 1
RIGHT = 3

points_inside = []

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == LEFT:
                p = DrawPoint()
                p.update()
                points.append(p)
                draw = True
            if event.button == RIGHT:
                end = True

    if draw:
        screen.fill((0, 0, 0))
        draw_lines(points)
        draw = False

    if end:
        screen.fill((0, 0, 0))
        end = False

        draw_end(points)
        pygame.draw.polygon(screen, (255, 0, 0), get_points_positions(points))

        poly = generate_polygon(points)
        kohonen = generate_kohonen(get_min_max(points), GRID_SIZE_X, GRID_SIZE_Y)
        rp = get_random_point(poly, get_min_max(points))
        redraw(points, kohonen, rp)

        for t in range(STEPS):
            rp = get_random_point(poly, get_min_max(points))
            print(t)
            if t % REDRAW_EVERY == 0:
                redraw(points, kohonen, rp)

            closest = get_closest_point(rp, kohonen, GRID_SIZE_X, GRID_SIZE_Y)
            update_kohonen(rp, kohonen, closest, GRID_SIZE_X, GRID_SIZE_Y, 1 - (t / STEPS))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

        redraw(points, kohonen, rp)

    pygame.display.flip()


pygame.quit()
quit()