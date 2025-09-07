# Complete your game here
from random import randint, choice
import pygame

class Shape:
    """Root of graphics objects"""
    def __init__(self, display, image):
        self._display = display
        self._image = image
        self.__x = 0
        self.__y = 0

    @property
    def rect(self):
        """Bounds of shape"""
        return pygame.Rect(self.x, self.y, self._image.get_width(), self._image.get_height())

    @property
    def x(self):
        return self.__x

    @x.setter
    def x(self, x_):
        self.__x = x_

    @property
    def y(self):
        return self.__y

    @y.setter
    def y(self, y_):
        self.__y = y_

    @property
    def surface(self):
        return self._image

    @property
    def place(self):
        return self.x, self.y


class Entity(Shape):
    """A Shape what it can be draw into a display"""
    def __init__(self, display, image):
        super().__init__(display, image)

    def draw(self):
        self._display.blit(self.surface, self.place)


class Booster(Entity):
    """An Entity what use door.png image. Boost to Monster and scare to player show and hide it"""
    def __init__(self, display, top_left: bool, image=pygame.image.load("door.png")):
        super().__init__(display, image)
        self.__set_place(top_left)

    def __set_place(self, top_left):
        self.y = 0  # Y-init position at top of screen
        if top_left:
            self.x = 0  # X-init At left position into screen
        else:
            self.x = self._display.get_width() - self._image.get_width()  # X-init At right position into screen


class Monster(Entity):
    """The Game's Monster. Bounces and rebounces into the screen,
       when it collides with a booster learns to improve its speed
       and if it collides with Robot steals its points"""
    AGE = 20
    def __init__(self, velocity, display, image=pygame.image.load("monster.png")):
        super().__init__(display, image)
        self.__age = Monster.AGE
        self.__x_velocity = choice([-velocity, velocity])
        self.__y_velocity = choice([-velocity, velocity])
        self.__set_place()

    def __set_place(self):
        self.x = (self._display.get_width() - self._image.get_width()) // 2  # X-init position into screen
        ## self.y = self._display.get_height() - self._image.get_height()  # Y-init position at bottom of screen
        self.y = self._image.get_height()  # Y-init position at top of screen
        self._display.blit(self.surface, self.place)

    def move(self):

        self.x += self.__x_velocity
        self.y += self.__y_velocity

        if self.__x_velocity > 0 and self.x + self._image.get_width() >= self._display.get_width():  # To right - ok
            self.__x_velocity = -self.__x_velocity
        if self.__y_velocity > 0 and self.y + self._image.get_height() >= self._display.get_height():  # To down - ok 
            self.__y_velocity = -self.__y_velocity
        if self.__x_velocity < 0 and self.x <= 0:  # To Left - ok
            self.__x_velocity = -self.__x_velocity
        if self.__y_velocity < 0 and self.y <= 0:  # To up - ok
            self.__y_velocity = -self.__y_velocity

        self.draw()

    def has_collided(self, entity: Entity):
        result = self.rect.colliderect(entity.rect)
        if result and isinstance(entity, Robot):  # The Monster interacts with the Robot
            self.__y_velocity = -self.__y_velocity

        if result and isinstance(entity, Booster):  # The Monster interacts with the Boosters
            self.__age -= 1
            if self.__age == 0:
                self.__age = Monster.AGE
                self.__x_velocity += 1
                self.__y_velocity += 1
                self.__y_velocity = -self.__y_velocity

        return result


class Coin(Entity):
    """The Game's Reward. Each coin colleted by the robot adds one point to score"""
    COIN_GAP = 20

    def __init__(self, y_velocity, display, image=pygame.image.load("coin.png")):
        super().__init__(display, image)
        self.__y_velocity = y_velocity
        self.random_place()

    def random_place(self):
        self.x = randint(self._image.get_width(), self._display.get_width() - self._image.get_width())  # X-init position into screen
        self.y = -randint(self._image.get_height(), Coin.COIN_GAP * self._image.get_height())  # Y-init position above of screen
        self._display.blit(self.surface, self.place)

    def move_down(self):
        self.y += self.__y_velocity
        self._display.blit(self.surface, self.place)

    def out_of_screen(self):
        return self.y > self._display.get_height()


class Robot(Entity):
    """The Game's Hero. Collets coins to sum points to score"""
    def __init__(self, x_velocity, display, image=pygame.image.load("robot.png")):
        super().__init__(display, image)
        self.__set_place()
        self.__x_velocity = x_velocity
        self.moving_left = False
        self.moving_right = False

    def __set_place(self):
        self.x = (self._display.get_width() - self._image.get_width()) // 2  # X-init position into screen
        self.y = self._display.get_height() - self._image.get_height()  # Y-init position at bottom of screen
        self._display.blit(self.surface, self.place)

    def move_side(self):
        if self.moving_left:
            if self.x > 0:
                self.x -= self.__x_velocity
        if self.moving_right:
            if self.x + self._image.get_width() <= self._display.get_width():
                self.x += self.__x_velocity
        self._display.blit(self.surface, self.place)

    def has_collided(self, coins):
        result = False
        index = self.rect.collidelist(list(map(lambda r: r.rect, coins.coins)))
        if index != -1:
            coins.coins.pop(index)
            result = True
        return result

class Coins():
    """Collection of coins"""
    NUM_COINS = 10

    def __init__(self, y_velocity, display, image=pygame.image.load("coin.png")):
        self.__coins = []
        self.__display = display
        self.__y_velocity = y_velocity
        self.__image = image
        self.__assing_coins()

    def __assing_coins(self):
        for coin in range(Coins.NUM_COINS):
            coin = Coin(self.__y_velocity, self.__display, self.__image)
            coin.random_place()
            self.__coins.append(coin)

    def __iter__(self):
        return iter(self.__coins)

    @property
    def coins(self):
        return self.__coins

    def move_down(self):
        for coin in self.__coins:
            coin.move_down()

    def __all_out(self):
        return len(self.__coins) == 0 or all(map(lambda r: r.out_of_screen(), self.__coins))

    def check(self):
        if self.__all_out():
            self.__coins = []
            self.__assing_coins()


class Game:
    """The Game"""
    # Colors
    SCARE = (100, 100, 100)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)

    # Window config
    WIDTH, HEIGHT = 640, 480
    CENTER = (WIDTH // 2, HEIGHT // 2)
    DASHBOARD = (40, 0)

    # Game config
    PLAYER_EASY = 5

    def __init__(self, tick=60, accelerator=1, difficulty=1):
        pygame.init()
        self.background_color = Game.BLACK
        self.window = pygame.display.set_mode((Game.WIDTH, Game.HEIGHT))
        self.game_font = pygame.font.SysFont("Arial", 24)
        self.clock = pygame.time.Clock()
        self.tick = tick
        self.accelerator = accelerator
        self.difficulty = difficulty
        self.new_game()
        self.dashboard = None
        pygame.display.set_caption("Robot's Odissey")
        self.main_loop()

    def new_game(self):
        self.points = 0
        self.door_left = Booster(self.window, True)
        self.door_right = Booster(self.window, False)
        self.enemy = Monster(self.difficulty, self.window)
        self.robot = Robot(Game.PLAYER_EASY * self.difficulty, self.window)
        self.coins = Coins(self.difficulty, self.window)

    def update_dashboard(self):
        self.dashboard = self.game_font.render(f"{"F2 = new game":<30}{"Esc = exit game":<40}Points: {self.points:02}", True, Game.RED)
        self.window.blit(self.dashboard, Game.DASHBOARD)

    def main_loop(self):
        while True:
            self.check_events()
            self.draw_window()

    def check_events(self):

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.robot.moving_left = True
                if event.key == pygame.K_RIGHT:
                    self.robot.moving_right = True
                if event.key == pygame.K_F2:
                    self.new_game()
                if event.key == pygame.K_ESCAPE:
                    exit()                        
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    self.robot.moving_left = False
                if event.key == pygame.K_RIGHT:
                    self.robot.moving_right = False
            if event.type == pygame.QUIT:
                exit()

    def draw_window(self):
        self.window.fill(self.background_color)

        # Draw the objects into window
        self.door_left.draw()
        self.door_right.draw()
        self.enemy.move()
        self.robot.move_side()

        # Check the collides between objects
        if self.robot.has_collided(self.coins):
            self.points += 1

        if self.enemy.has_collided(self.robot):
            self.points -= 1

        if self.enemy.has_collided(self.door_left):
            self.swap_background_color()

        if self.enemy.has_collided(self.door_right):
            self.swap_background_color()

        # Move coins down and check if they remain into screen
        self.coins.move_down()
        self.coins.check()

        # Upgrade score
        self.update_dashboard()

        # Upgrade window and game's timer
        pygame.display.flip()
        self.clock.tick(self.tick * self.accelerator)

    def swap_background_color(self):
        self.background_color = Game.BLACK if self.background_color == Game.SCARE else Game.SCARE


if __name__ == "__main__":
    game = Game(accelerator=1)
    game.main_loop()
