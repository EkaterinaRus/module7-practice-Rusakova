from random import randint


# класс точек на поле. Каждая точка описывается параметрами:
# Координата по оси x.
# Координата по оси y.
class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    # проверка точек на равенство
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"Dot{(self.x, self.y)}"


# общий класс исключений
class BoardException(Exception):
    pass


# класс исключений, когда игрок пытается выстрелить в клетку за пределами поля
class BoardOutException(BoardException):
    def __str__(self):
        return 'Вы стреляете за пределы поля'


# класс исключений, когда игрок пытается выстрелить в клетку, в которую уже стрелял
class BoardUsedException(BoardException):
    def __str__(self):
        return 'Вы уже стреляли в эту клетку'


#  исключение для размещения кораблей
class BoardWrongShipException(BoardException):
    pass


class Ship:
    def __init__(self, dot_bow_ship, length_ship, direction_ship):
        self.dot_bow_ship = dot_bow_ship  # точка, где размещён нос корабля
        self.length_ship = length_ship  # длина корабля
        self.direction_ship = direction_ship  # ориентация корабля
        self.count_lives = length_ship  # количество жизней (сколько точек корабля еще не подбито)

    # возвращает список всех точек корабля
    @property
    def dots(self):
        all_dots_ship = []
        for i in range(self.length_ship):
            coord_x = self.dot_bow_ship.x
            coord_y = self.dot_bow_ship.y

            if self.direction_ship == 0:
                coord_x += i

            elif self.direction_ship == 1:
                coord_y += i

            all_dots_ship.append(Dot(coord_x, coord_y))

        return all_dots_ship


class Board:
    def __init__(self, hid=False, size=6):
        self.size = size
        self.hid = hid  # True - скрывать корабли на доске (для вывода доски врага), False - нет (для своей доски)

        self.count = 0  # количество пораженных кораблей

        self.field = [["O"] * size for _ in range(size)]  # сетка

        self.busy = []  # список занятых точек, либо кораблем(в том числе и соседние с ним), либо уже куда стреляли
        self.ships = []  # список кораблей доски

    # ставит корабли на доску. Если не получается, выбрасывает исключение
    def add_ship(self, ship):

        for dot in ship.dots:
            if self.out(dot) or dot in self.busy:
                raise BoardWrongShipException()

            self.field[dot.x][dot.y] = "■"
            self.busy.append(dot)

        self.ships.append(ship)
        self.contour(ship)

    # обводит корабль по контуру
    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for dot in ship.dots:
            for x, y in near:
                coord = Dot(dot.x + x, dot.y + y)
                if not (self.out(coord)) and coord not in self.busy:
                    if verb:
                        self.field[coord.x][coord.y] = "."
                    self.busy.append(coord)

    def __str__(self):
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hid:
            res = res.replace("■", "O")
        return res

    # который для точки (объекта класса Dot) возвращает True,
    # если точка выходит за пределы поля, и False, если не выходит
    def out(self, dot):
        return not ((0 <= dot.x < self.size) and (0 <= dot.y < self.size))

    # который делает выстрел по доске (если есть попытка выстрелить
    # за пределы и в использованную точку, нужно выбрасывать исключения).
    def shot(self, dot):
        if self.out(dot):
            raise BoardOutException()

        if dot in self.busy:
            raise BoardUsedException()

        self.busy.append(dot)

        for ship in self.ships:
            if dot in ship.dots:
                ship.count_lives -= 1
                self.field[dot.x][dot.y] = "X"
                if ship.count_lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True

        self.field[dot.x][dot.y] = "."
        print("Мимо!")
        return False

    def begin(self):
        self.busy = []


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    # метод, который «спрашивает» игрока, в какую клетку он делает выстрел
    def ask(self):
        raise NotImplementedError

    # метод, который делает ход в игре
    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BaseException as e:
                print(e)


class AI(Player):
    # переопределяем метод ask. Для компьютера это будет выбор случайной точки
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {d.x+1} {d.y+1}")
        return d


class User(Player):
    # переопределяем метод ask. Для пользователя этот метод спрашивает координаты точки из консоли
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print(" Введите 2 координаты! ")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


class Game:
    def __init__(self, size=6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    @staticmethod
    def greet():
        print("-------------------")
        print("  Приветствуем вас  ")
        print("      в игре       ")
        print("    морской бой    ")
        print("-------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")

    def loop(self):
        num = 0
        while True:
            print("-" * 20)
            print("Доска пользователя:")
            print(self.us.board)
            print("-" * 20)
            print("Доска компьютера:")
            print(self.ai.board)
            if num % 2 == 0:
                print("-" * 20)
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("-" * 20)
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.count == 7:
                print("-" * 20)
                print("Пользователь выиграл!")
                break

            if self.us.board.count == 7:
                print("-" * 20)
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()

b = Game()
b.start()
