"""
Этот модуль реализует классическую игру "Змейка" с использованием
библиотеки Pygame.
Игрок управляет змейкой, которая должна есть яблоки на игровом поле.
При съедании яблок змейка увеличивается в размере. Игра также включает
"плохую пищу", которая уменьшает размер змейки. Цель игры - съесть как
можно больше яблок, избегая столкновения змейки с самой собой.
"""
from random import randint, choice
import pygame as pg


# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
DIRECTION_LIST = [UP, DOWN, LEFT, RIGHT]

BOARD_BACKGROUND_COLOR = (0, 0, 0)  # Цвет фона - черный:

DEFAULT_OBJECT_COLOR = BOARD_BACKGROUND_COLOR  # Совпадает с цветом фона

BAD_FOOD_COLOR = (88, 57, 39)  # Цвет плохой еды

BORDER_COLOR = (93, 216, 228)  # Цвет границы ячейки

APPLE_COLOR = (255, 0, 0)  # Цвет яблока

SNAKE_COLOR = (0, 255, 0)  # Цвет змейки

SPEED = 7  # Скорость движения змейки:

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pg.display.set_caption('Змейка')

# Настройка времени:
clock = pg.time.Clock()


class GameObject:
    """Базовый класс для всех игровых объектов на поле."""

    body_color: tuple[int, int, int] = DEFAULT_OBJECT_COLOR

    def __init__(self):
        """Инициализирует позицию объекта в центре игрового поля."""
        self.position = (((GRID_WIDTH - 1) // 2) * GRID_SIZE,
                         ((GRID_HEIGHT - 1) // 2) * GRID_SIZE)

    def draw(self):
        """Заготовка для child-классов."""


class Apple(GameObject):
    """Класс яблока, которое может быть съедено змейкой."""

    def __init__(self, occupied_coords=[], color=APPLE_COLOR):
        """Инициализирует объект со случайными координатами на поле."""
        super().__init__()
        self.randomize_position(occupied_coords)
        self.body_color = color

    def randomize_position(self, occupied_coords):
        """Устанавливает случайное положение яблока на игровом поле."""
        while True:
            self.position = (randint(1, GRID_WIDTH - 1) * GRID_SIZE,
                             randint(1, GRID_HEIGHT - 1) * GRID_SIZE)

            if self.position not in occupied_coords:
                break

    def draw(self):
        """Отрисовывает яблоко на игровом поле."""
        rect = pg.Rect(self.position, (GRID_SIZE - 1, GRID_SIZE))
        pg.draw.rect(screen, self.body_color, rect)
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)


class BadFood(Apple):
    """Класс плохой пищи, уменьшающей размер змейки при съедении."""

    def __init__(self, occupied_coords, color=BAD_FOOD_COLOR):
        """Инициализирует объект со случайными координатами на поле."""
        super().__init__(occupied_coords)
        self.body_color = color


class Snake(GameObject):
    """Класс змейки, управляемой игроком."""

    def __init__(self, color=SNAKE_COLOR):
        """Инициализирует змейку в центре поля.

        Начальная длина - один сегмент.
        """
        super().__init__()
        self.body_color = color
        self.reset()

    def get_head_position(self):
        """Возвращает координаты головы змейки."""
        return (self.positions[0])

    def move(self):
        """Двигает змейку по координатам в текущем направлении."""
        coord_delta = [delta * GRID_SIZE for delta in self.direction]

        new_head_position = tuple(dir_coord + head_coord
                                  for dir_coord, head_coord
                                  in zip(coord_delta,
                                         self.get_head_position()))

        new_head_position = self.fix_out_of_boundries(new_head_position)
        self.positions.insert(0, new_head_position)
        self.last = self.positions[-1]
        self.position = new_head_position

        if len(self.positions) > self.lenght:
            self.last = self.positions.pop()
        else:
            self.last = None

    def grow(self):
        """Увеличивает длину змейки на 1."""
        self.lenght += 1

    def shrink(self):
        """Уменьшает длину змейки, удаляя последний сегмент."""
        if self.lenght > 1:
            self.positions.pop()
            self.lenght -= 1
        else:
            self.reset()
        self.last = None

    def reset(self):
        """Сбрасывает змейку к начальному состоянию."""
        self.position = (((GRID_WIDTH - 1) // 2) * GRID_SIZE,
                         ((GRID_HEIGHT - 1) // 2) * GRID_SIZE)
        self.positions = [self.position]
        self.direction = choice(DIRECTION_LIST)
        self.next_direction = None
        self.lenght = 1
        self.last = None

    @staticmethod
    def fix_out_of_boundries(new_head_position):
        """Корректирует позицию головы змейки при выходе за границы поля."""
        new_head_col, new_head_row = new_head_position

        # Используем деление по модулю для коррекции позиции
        new_head_col = new_head_col % (SCREEN_WIDTH)
        new_head_row = new_head_row % (SCREEN_HEIGHT)

        return new_head_col, new_head_row

    def update_direction(self):
        """Обновляет направления после нажатия на кнопку."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def draw(self):
        """Отрисовывает змейку на игровом поле."""
        # Отрисовка головы змейки
        head_rect = pg.Rect(self.get_head_position(), (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, self.body_color, head_rect)
        pg.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        # Затирание последнего сегмента, если он есть
        if self.last:
            last_rect = pg.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pg.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)


def check_snake_ate_apple(snake: Snake, apple: Apple):
    """Проверяет, съела ли змейка яблоко."""
    return bool(snake.get_head_position() == apple.position)


def check_snake_ate_bad_food(snake: Snake, bad_food: BadFood):
    """Проверяет, съела ли змейка плохую пищу."""
    return bool(snake.get_head_position() == bad_food.position)


def handle_keys(game_object):
    """Обрабатывает пользовательские вводы.

    Обрабатывает ввод с клавиатуры и управляет направлением игрового объекта.
    """
    DIRECTION_MAP = {
        pg.K_UP: UP,
        pg.K_DOWN: DOWN,
        pg.K_LEFT: LEFT,
        pg.K_RIGHT: RIGHT
    }

    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit('Игра закрыта пользователем.')

        if event.type == pg.KEYDOWN:
            if event.key in DIRECTION_MAP:
                new_direction = DIRECTION_MAP[event.key]
                if (new_direction[0] + game_object.direction[0] != 0
                        or new_direction[1] + game_object.direction[1] != 0):
                    game_object.next_direction = new_direction


def check_collision(snake: Snake):
    """Проверяет столкновения змейки с самой собой."""
    return snake.get_head_position() in snake.positions[1:]


def get_occupied_cells(*args: GameObject):
    """Возвращает множество координат занятых ячеек на поле.

    Параметры:
        *args (GameObject): Переменное количество игровых объектов.

    Возвращает:
        set: Множество кортежей с координатами занятых ячеек.
    """
    positions_set = set()
    for game_object in args:
        if hasattr(game_object, 'positions'):
            positions_set.update(game_object.positions)

        positions_set.add(game_object.position)
    return positions_set


def main():
    """Основная функция, инициализирующая и запускающая игровой цикл."""
    pg.init()

    snake = Snake()
    apple = Apple(get_occupied_cells(snake))
    bad_food = BadFood(get_occupied_cells(snake, apple))

    screen.fill(BOARD_BACKGROUND_COLOR)

    while True:
        clock.tick(SPEED)

        handle_keys(snake)
        snake.update_direction()
        snake.move()

        if check_collision(snake):
            snake.reset()
            screen.fill(BOARD_BACKGROUND_COLOR)
            apple.randomize_position(get_occupied_cells
                                     (snake, apple, bad_food))
            bad_food.randomize_position(get_occupied_cells
                                        (snake, apple, bad_food))

        if check_snake_ate_apple(snake, apple):
            apple.randomize_position(get_occupied_cells
                                     (snake, apple, bad_food))
            snake.grow()

        if check_snake_ate_bad_food(snake, bad_food):
            snake.shrink()
            screen.fill(BOARD_BACKGROUND_COLOR)
            bad_food.randomize_position(get_occupied_cells
                                        (snake, apple, bad_food))

        apple.draw()
        snake.draw()
        bad_food.draw()
        pg.display.update()


if __name__ == '__main__':
    main()
