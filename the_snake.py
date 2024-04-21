from random import randint
import pygame


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

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

BAD_FOOD_COLOR = (88, 57, 39)  # Цвет плохой еды

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 5

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


# Тут опишите все классы игры.
class GameObject:
    """Базовый класс для всех игровых объектов на поле."""

    body_color: tuple[int, int, int] = (0, 0, 0)

    def __init__(self):
        """Инициализирует позицию объекта в центре игрового поля."""
        self.position = ((GRID_WIDTH - 1 // 2) * GRID_SIZE,
                         (GRID_HEIGHT - 1 // 2) * GRID_SIZE)

    def draw(self):
        """Заготовка для child-классов."""
        pass


class Apple(GameObject):
    """Класс яблока, которое может быть съедено змейкой."""

    body_color = APPLE_COLOR

    def __init__(self):
        super().__init__()
        self.randomize_position()

    def randomize_position(self):
        """Устанавливает случайное положение яблока на игровом поле."""
        self.position = (randint(1, GRID_WIDTH - 1) * GRID_SIZE,
                         randint(1, GRID_HEIGHT - 1) * GRID_SIZE)

    def draw(self):
        """Отрисовывает яблоко на игровом поле."""
        rect = pygame.Rect(self.position, (GRID_SIZE - 1, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class BadFood(Apple):
    """Класс плохой пищи, уменьшающей размер змейки при съедении."""

    body_color = BAD_FOOD_COLOR

    def __init__(self):
        """Инициализирует плохую пищу и устанавливает
        её случайное положение на поле.
        """
        super().__init__()


class Snake(GameObject):
    """Класс змейки, управляемой игроком."""

    body_color = SNAKE_COLOR

    def __init__(self):
        """Инициализирует змейку в центре поля
        с начальной длиной в один сегмент.
        """
        super().__init__()
        self.lenght = 1
        self.positions = [self.position]
        self.direction = RIGHT
        self.next_direction = None
        self.previous_tail_pos = None

    def get_head_position(self):
        """Возвращает координаты головы змейки."""
        return (self.positions[0])

    def move(self):
        """Двигает змейку по координатам в текущем направлении."""
        coord_delta = [delta * 20 for delta in self.direction]

        new_head_position = tuple(dir_coord + head_coord
                                  for dir_coord, head_coord
                                  in zip(coord_delta,
                                         self.get_head_position()))

        new_head_position = self.fix_out_of_boundries(new_head_position)
        self.positions.insert(0, new_head_position)

        self.previous_tail_pos = self.positions[- 1]
        self.positions.pop()

        self.collision_check()

    def grow(self):
        """Увеличивает длину змейки на 1."""
        self.positions.append(self.previous_tail_pos)
        self.lenght += 1

    def shrink(self):
        """Уменьшает длину змейки, удаляя последний сегмент."""
        self.positions.pop()
        self.lenght -= 1
        if self.lenght == 0:
            self.reset()

    def reset(self):
        """Сбрасывает змейку к начальному состоянию."""
        self.positions = [self.position]
        self.direction = RIGHT
        self.next_direction = None
        self.lenght = 1
        self.previous_tail_pos = None

    def collision_check(self):
        """Проверяет столкновения змейки с самой собой."""
        coord_set = set()
        if any(coord in coord_set or coord_set.add(coord)
               for coord in self.positions):
            self.reset()

    @staticmethod
    def fix_out_of_boundries(new_head_position):
        """Корректирует позицию головы змейки при выходе за границы поля."""
        col, row = new_head_position

        max_col_coord = SCREEN_WIDTH - GRID_SIZE
        max_row_coord = SCREEN_HEIGHT - GRID_SIZE

        if new_head_position[0] > max_col_coord:
            col = 0

        if new_head_position[1] > max_row_coord:
            row = 0

        if new_head_position[0] < 0:
            col = max_col_coord

        if new_head_position[1] < 0:
            row = max_row_coord

        return (col, row)

    def update_direction(self):
        """Обновляет направления после нажатия на кнопку."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def draw(self):
        """Отрисовывает змейку на игровом поле."""
        for position in self.positions:
            rect = (pygame.Rect(position, (GRID_SIZE, GRID_SIZE)))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

        # Отрисовка головы змейки
        head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        # Затирание последнего сегмента
        if self.previous_tail_pos:
            last_rect = pygame.Rect(self.previous_tail_pos, (GRID_SIZE,
                                                             GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)


def check_snake_ate_apple(snake: Snake, apple: Apple):
    """Проверяет, съела ли змейка яблоко."""
    if snake.get_head_position() == apple.position:
        snake.grow()
        return (True)

    else:
        return (False)


def check_snake_ate_bad_food(snake: Snake, bad_food: BadFood):
    """Проверяет, съела ли змейка плохую пищу."""
    if snake.get_head_position() == bad_food.position:
        snake.shrink()
        return (True)

    else:
        return (False)


def handle_keys(game_object):
    """Обрабатывает пользовательские вводы с клавиатуры
    для управления направлением игрового объекта.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main():
    """Основная функция, инициализирующая и запускающая игровой цикл."""
    # Инициализация PyGame:
    pygame.init()
    # Тут нужно создать экземпляры классов.
    snake = Snake()
    apple = Apple()
    bad_food = BadFood()

    while True:
        clock.tick(SPEED)
        screen.fill(BOARD_BACKGROUND_COLOR)  # Заливка экрана перед отрисовкой

        handle_keys(snake)
        snake.update_direction()
        snake.move()

        if check_snake_ate_apple(snake, apple):
            apple.randomize_position()
        if check_snake_ate_bad_food(snake, bad_food):
            bad_food.randomize_position()

        apple.draw()
        snake.draw()
        bad_food.draw()
        pygame.display.update()


if __name__ == '__main__':
    main()
