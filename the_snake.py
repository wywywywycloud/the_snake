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

    body_color: tuple[int, int, int] = (0, 0, 0)

    def __init__(self):
        """Инициализирует позицию объекта в центре игрового поля."""
        self.position = (((GRID_WIDTH - 1) // 2) * GRID_SIZE,
                         ((GRID_HEIGHT - 1) // 2) * GRID_SIZE)

    def draw(self):
        """Заготовка для child-классов."""
        pass


class Apple(GameObject):
    """Класс яблока, которое может быть съедено змейкой."""

    def __init__(self, occupied_coords):
        """Инициализирует объект со случайными координатами на поле."""
        super().__init__()
        while True:
            self.randomize_position()
            if self.position not in occupied_coords:
                break
        self.body_color = APPLE_COLOR

    def randomize_position(self):
        """Устанавливает случайное положение яблока на игровом поле."""
        self.position = (randint(1, GRID_WIDTH - 1) * GRID_SIZE,
                         randint(1, GRID_HEIGHT - 1) * GRID_SIZE)

    def draw(self):
        """Отрисовывает яблоко на игровом поле."""
        rect = pg.Rect(self.position, (GRID_SIZE - 1, GRID_SIZE))
        pg.draw.rect(screen, self.body_color, rect)
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)


class BadFood(Apple):
    """Класс плохой пищи, уменьшающей размер змейки при съедении."""

    def __init__(self, occupied_coords):
        """Инициализирует объект со случайными координатами на поле."""
        super().__init__(occupied_coords)
        self.body_color = BAD_FOOD_COLOR


class Snake(GameObject):
    """Класс змейки, управляемой игроком."""

    def __init__(self):
        """Инициализирует змейку в центре поля.

        Начальная длина - один сегмент.
        """
        super().__init__()
        self.body_color = SNAKE_COLOR
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

        self.position = new_head_position

        if len(self.positions) > self.lenght:
            self.previous_tail_pos = self.positions.pop()
        else:
            self.previous_tail_pos = None

    def grow(self):
        """Увеличивает длину змейки на 1."""
        self.lenght += 1
        self.previous_tail_pos = None

        screen.fill(BOARD_BACKGROUND_COLOR)

    def shrink(self):
        """Уменьшает длину змейки, удаляя последний сегмент."""
        if self.lenght > 1:
            self.positions.pop()
            self.lenght -= 1
        else:
            self.reset()
        self.previous_tail_pos = None

        screen.fill(BOARD_BACKGROUND_COLOR)

    def reset(self):
        """Сбрасывает змейку к начальному состоянию."""
        self.position = (((GRID_WIDTH - 1) // 2) * GRID_SIZE,
                         ((GRID_HEIGHT - 1) // 2) * GRID_SIZE)
        self.positions = [self.position]
        self.direction = choice(DIRECTION_LIST)
        self.next_direction = None
        self.lenght = 1
        self.previous_tail_pos = None

        screen.fill(BOARD_BACKGROUND_COLOR)

    @staticmethod
    def fix_out_of_boundries(new_head_position):
        """Корректирует позицию головы змейки при выходе за границы поля."""
        new_head_col, new_head_row = new_head_position

        # Используем деление по модулю для коррекции позиции
        new_head_col = new_head_col % (SCREEN_WIDTH)
        new_head_row = new_head_row % (SCREEN_HEIGHT)

        return (new_head_col, new_head_row)

    def update_direction(self):
        """Обновляет направления после нажатия на кнопку."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def draw(self):
        """Отрисовывает змейку на игровом поле."""
        for position in self.positions:
            rect = (pg.Rect(position, (GRID_SIZE, GRID_SIZE)))
            pg.draw.rect(screen, self.body_color, rect)
            pg.draw.rect(screen, BORDER_COLOR, rect, 1)

        # Отрисовка головы змейки
        head_rect = pg.Rect(self.get_head_position(), (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, self.body_color, head_rect)
        pg.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        # Затирание последнего сегмента
        if self.previous_tail_pos:
            last_rect = pg.Rect(self.previous_tail_pos, (GRID_SIZE,
                                                         GRID_SIZE))
            pg.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)


def check_snake_ate_apple(snake: Snake, apple: Apple):
    """Проверяет, съела ли змейка яблоко."""
    if not snake.get_head_position() == apple.position:
        return False
    return True


def check_snake_ate_bad_food(snake: Snake, bad_food: BadFood):
    """Проверяет, съела ли змейка плохую пищу."""
    if snake.get_head_position() == bad_food.position:
        return True

    else:
        return False


def handle_keys(game_object):
    """Обрабатывает пользовательские вводы.

    Обрабатывает ввод с клавиатуры
    и управляет направлением игрового объекта.
    """
    DIRECTION_MAP = {
        (pg.K_UP, DOWN): None,
        (pg.K_DOWN, UP): None,
        (pg.K_LEFT, RIGHT): None,
        (pg.K_RIGHT, LEFT): None,
        (pg.K_UP, UP): UP,
        (pg.K_UP, LEFT): UP,
        (pg.K_UP, RIGHT): UP,
        (pg.K_DOWN, DOWN): DOWN,
        (pg.K_DOWN, LEFT): DOWN,
        (pg.K_DOWN, RIGHT): DOWN,
        (pg.K_LEFT, LEFT): LEFT,
        (pg.K_LEFT, UP): LEFT,
        (pg.K_LEFT, DOWN): LEFT,
        (pg.K_RIGHT, RIGHT): RIGHT,
        (pg.K_RIGHT, UP): RIGHT,
        (pg.K_RIGHT, DOWN): RIGHT
    }

    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit('Игра закрыта пользователем.')

        if event.type == pg.KEYDOWN:
            new_direction = DIRECTION_MAP.get(
                (event.key, game_object.direction), game_object.direction)
            if new_direction:
                game_object.next_direction = new_direction


def check_collision(snake: Snake):
    """Проверяет столкновения змейки с самой собой."""
    return snake.get_head_position() in snake.positions[1:]


def get_occupied_cells(*args: GameObject):
    """Возвращает список координат занятых ячеек на поле.

    Параметры:
        *args (GameObject): Переменное количество игровых объектов.

    Возвращает:
        list: Список кортежей с координатами занятых ячеек.
    """
    positions_list = []
    for game_object in args:
        if hasattr(game_object, 'positions'):
            positions_list.extend(game_object.positions)

        positions_list.append(game_object.position)
    return positions_list


def main():
    """Основная функция, инициализирующая и запускающая игровой цикл."""
    pg.init()

    get_occupied_cells()

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
            apple = Apple(get_occupied_cells(snake, apple, bad_food))
            bad_food = BadFood(get_occupied_cells(snake, apple, bad_food))

        if check_snake_ate_apple(snake, apple):
            apple = Apple(get_occupied_cells(snake, apple, bad_food))
            snake.grow()

        if check_snake_ate_bad_food(snake, bad_food):
            if snake.lenght == 1:
                snake.reset()
                apple = Apple(get_occupied_cells(snake, apple, bad_food))
                bad_food = BadFood(get_occupied_cells(snake, apple, bad_food))
            else:
                snake.shrink()
                bad_food = BadFood(get_occupied_cells(snake, apple, bad_food))

        apple.draw()
        snake.draw()
        bad_food.draw()
        pg.display.update()


if __name__ == '__main__':
    main()
