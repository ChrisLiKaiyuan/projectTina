import tkinter as tk
import PIL
from tkinter import messagebox
from PIL import Image, ImageTk


class Entity:
    """ """

    def __init__(self):
        """
        Something the player can interact with
        """
        self._collidable = True

    def get_id(self):
        """ """
        return self._id

    def set_collide(self, collidable):
        """ """
        self._collidable = collidable

    def can_collide(self):
        """ """
        return self._collidable

    def __str__(self):
        return f"{self.__class__.__name__}({self._id!r})"

    def __repr__(self):
        return str(self)


class Wall(Entity):
    """ """

    _id = "#"

    def __init__(self):
        """ """
        super().__init__()
        self.set_collide(False)


class Item(Entity):
    """ """

    def on_hit(self, game):
        """ """
        raise NotImplementedError


class Key(Item):
    """ """

    _id = "K"

    def on_hit(self, game):
        """ """
        player = game.get_player()
        player.add_item(self)
        game.get_game_information().pop(player.get_position())


class MoveIncrease(Item):
    """ """

    _id = "M"

    def __init__(self, moves=5):
        """ """
        super().__init__()
        self._moves = moves

    def on_hit(self, game):
        """ """
        player = game.get_player()
        player.change_move_count(self._moves)
        game.get_game_information().pop(player.get_position())


class Door(Entity):
    """ """
    _id = "D"

    def on_hit(self, game):
        """ """
        player = game.get_player()
        for item in player.get_inventory():
            if item.get_id() == "K":
                game.set_win(True)
                return

        print("You don't have the key!")


class Player(Entity):
    """ """
    _id = "O"

    def __init__(self, move_count):
        """ """
        super().__init__()
        self._move_count = move_count
        self._inventory = []
        self._position = None

    def set_position(self, position):
        """ """
        self._position = position

    def get_position(self):
        """ """
        return self._position

    def change_move_count(self, number):
        """
        Parameters:
            number (int): number to be added to move count
        """
        self._move_count += number

    def moves_remaining(self):
        """ """
        return self._move_count

    def add_item(self, item):
        """Adds item (Item) to inventory
        """
        self._inventory.append(item)

    def get_inventory(self):
        """ """
        return self._inventory


class GameLogic:
    """ """

    def load_game(self, filename):
        dungeon_layout = []

        with open(filename, 'r') as file:
            for line in file:
                line = line.strip()
                dungeon_layout.append(list(line))

        return dungeon_layout

    def __init__(self, dungeon_name="game2.txt"):
        """ """
        self._dungeon = self.load_game(dungeon_name)
        self._dungeon_size = len(self._dungeon)
        # dungeon layout: max moves allowed
        GAME_LEVELS = {"game1.txt": 7, "game2.txt": 12, "game3.txt": 19, }
        self._player = Player(GAME_LEVELS[dungeon_name])
        self._game_information = self.init_game_information()
        self._win = False
        self._DIRECTIONS = {"W": (-1, 0),
                            "S": (1, 0),
                            "D": (0, 1),
                            "A": (0, -1)}

    def get_positions(self, entity):
        """ """
        positions = []
        for row, line in enumerate(self._dungeon):
            for col, char in enumerate(line):
                if char == entity:
                    positions.append((row, col))

        return positions

    def init_game_information(self):
        """ """
        player_pos = self.get_positions("O")[0]
        key_position = self.get_positions("K")[0]
        door_position = self.get_positions("D")[0]
        wall_positions = self.get_positions("#")
        move_increase_positions = self.get_positions("M")

        self._player.set_position(player_pos)

        information = {
            key_position: Key(),
            door_position: Door(),
        }

        for wall in wall_positions:
            information[wall] = Wall()

        for move_increase in move_increase_positions:
            information[move_increase] = MoveIncrease()

        return information

    def get_player(self):
        """ """
        return self._player

    def get_entity(self, position):
        """ """
        return self._game_information.get(position)

    def get_entity_in_direction(self, direction):
        """ """
        new_position = self.new_position(direction)
        return self.get_entity(new_position)

    def get_game_information(self):
        """ """
        return self._game_information

    def get_dungeon_size(self):
        """ """
        return self._dungeon_size

    def move_player(self, direction):
        """ """
        new_pos = self.new_position(direction)
        self.get_player().set_position(new_pos)

    def collision_check(self, direction):
        """
        Check to see if a player can travel in a given direction
        Parameters:
            direction (str): a direction for the player to travel in.

        Returns:
            (bool): False if the player can travel in that direction without colliding otherwise True.
        """
        new_pos = self.new_position(direction)
        entity = self.get_entity(new_pos)
        if entity is not None and not entity.can_collide():
            return True

        return not (0 <= new_pos[0] < self._dungeon_size and 0 <= new_pos[1] < self._dungeon_size)

    def new_position(self, direction):
        """ """
        x, y = self.get_player().get_position()
        dx, dy = self._DIRECTIONS[direction]
        return x + dx, y + dy

    def check_game_over(self):
        """ """
        return self.get_player().moves_remaining() <= 0

    def set_win(self, win):
        """ """
        self._win = win

    def won(self):
        """ """
        return self._win


class AbstractGrid(tk.Canvas):
    def __init__(self, master, rows, cols, width, height, **kwargs):
        super().__init__(master, width=width, height=height, **kwargs)
        self._unitx = width / cols
        self._unity = height / rows

    def get_bbox(self, position, **kwargs):
        coord = (self._unitx * (position[1]), self._unity * (position[0])), \
                (self._unitx * (position[1] + 1), self._unity * (position[0] + 1))
        self.create_rectangle(coord, **kwargs)

    def pixel_to_position(self, pixel):
        x = pixel[0] // self._unitx
        y = pixel[1] // self._unity
        return (x, y)

    def get_position_center(self, position):
        center = (self._unitx * (position[0] + 0.5), self._unity * (position[1] + 0.5))
        return center

    def annotate_position(self, position, text):
        if len(position) == 2:
            x, y = self.get_position_center((position[1], position[0]))
            self.create_text(x, y, text=text)
        else:
            x = (position[0] + position[2]) / 2
            y = (position[1] + position[3]) / 2
            self.create_text(x, y, text=text)


class DungeonMap(AbstractGrid):
    def __init__(self, master, size, width, **kwargs):
        super().__init__(master, size, size, width, width, **kwargs)

    def draw_grid(self, dungeon, player_position, **kwargs):
        for position in dungeon:
            if dungeon[position].get_id() == '#':
                self.get_bbox(position, fill='#68686b')

            elif dungeon[position].get_id() == 'K':
                self.get_bbox(position, fill='yellow')
                self.annotate_position(position, 'Trash')

            elif dungeon[position].get_id() == 'D':
                self.get_bbox(position, fill='red')
                self.annotate_position(position, 'Nest')

            elif dungeon[position].get_id() == 'M':
                self.get_bbox(position, fill='#ed6a37')
                self.annotate_position(position, 'Banana')

        self.get_bbox(player_position, fill='green')
        self.annotate_position(player_position, 'ibis')

    def re_draw_grid(self, dungeon, player_position, **kwargs):
        self.delete(tk.ALL)
        self.draw_grid(dungeon, player_position, **kwargs)


class AdvancedDungeonMap(DungeonMap):
    def __init__(self, master, size, width, **kwargs):
        super().__init__(master, size, width, **kwargs)

    def draw_grid(self, dungeon, player_position):
        index = 0
        wall = [None] * len(dungeon)
        for position in dungeon:
            pixel = self.get_position_center((position[1], position[0]))
            if dungeon[position].get_id() == '#':
                wall[index] = tk.PhotoImage(file='wall.png')
                self.create_image(pixel[0], pixel[1], image=wall[index])

            elif dungeon[position].get_id() == 'K':
                self.get_bbox(position, fill='yellow')
                self.annotate_position(position, 'Trash')

            elif dungeon[position].get_id() == 'D':
                self.get_bbox(position, fill='red')
                self.annotate_position(position, 'Nest')

            elif dungeon[position].get_id() == 'M':
                self.get_bbox(position, fill='#ed6a37')
                self.annotate_position(position, 'Banana')
            index += 1

        self.get_bbox(player_position, fill='green')
        self.annotate_position(player_position, 'ibis')
        self.mainloop()


class KeyPad(AbstractGrid):
    def __init__(self, master, width=200, height=100, **kwargs):
        super().__init__(master, 2, 3, width, height)
        self._texts = ('W', 'S', 'N', 'E')
        n = 0
        while n < len(self._texts):
            text = self._texts[n]
            self._positions = [(0, 1), (1, 1), (1, 0), (1, 2)]
            self.get_bbox(self._positions[n], fill='grey')
            self.annotate_position(self._positions[n], text)
            n += 1


class Message_box():
    def __init__(self, task):
        self._task = task

    def show_info(self, result, new_game, score):
        if self._task == 1:
            if result == 1:
                # win in task 1
                messagebox.showinfo(title="You won!", message="You have finished the level!")
            else:
                # lose in task 1
                messagebox.showinfo(title="Sorry you lost!", message="You have lost in this level")
        elif self._task == 2:
            if result == 1:
                # win in task 2
                if messagebox.askyesno(title="You won!",
                                       message=
                                       "You have finished  the level with a score of {} \n Would you like to play again?".format(
                                           score)):
                    # icon='question'
                    # print("you win restart")
                    new_game()
                else:
                    exit()

            else:
                # lose in task 2
                if messagebox.askyesno(
                        title="You lost!",
                        message="You have lost the level. \n Would you like to play again?"):
                    new_game()
                else:
                    exit()


class StatusBar(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        button_frame = tk.Frame(master, bg='green')
        button_frame.pack(side=tk.LEFT)
        self._button_new = tk.Button(button_frame, text="New game")
        self._button_new.pack(side=tk.TOP)
        self._button_quit = tk.Button(button_frame, text="Quit")
        self._button_quit.pack(side=tk.TOP, fill=tk.X)
        self._timer = tk.Label(master, text="Time elapsed\n{}m {}s ".format(0, 0))
        self._timer.pack(side=tk.LEFT)
        self._second = 0
        self._min = 0
        self._move_left = tk.Label(master)
        self._move_left.pack(side=tk.LEFT)

    def time_change(self):
        self._second += 1
        if self._second % 60 == 0:
            self._min += 1
            self._second = 0
        self._timer.config(text="Time elapsed\n{}m {}s ".format \
            (self._min, self._second))
        self._timer.after(1000, self.time_change)


class GameApp():
    """ """

    def __init__(self, master, task, dungeon_name):
        super().__init__()
        # initialise game information
        self._game = GameLogic()
        self._master = master
        # self._display = None
        self._player = self._game.get_player()
        self._task = task
        self._dungeon_name = dungeon_name
        self._game_frame = tk.Frame(master)
        self._game_frame.pack()
        if task == 1:
            """ """
            # initialise GUI
            self._dungeonmap = DungeonMap(self._game_frame, self._game.get_dungeon_size(),
                                          width=600, bg='grey')
            self._dungeonmap.pack(side=tk.LEFT)
            self._keypad = KeyPad(self._game_frame)
            self._keypad.pack(side=tk.LEFT)
        elif task == 2:
            """ """
            self._dungeonmap = AdvancedDungeonMap(self._game_frame, self._game.get_dungeon_size(),
                                                  width=600)
            self._dungeonmap.pack(side=tk.LEFT)
            self._keypad = KeyPad(self._game_frame)
            self._keypad.pack(side=tk.LEFT)
            # initialise Status Bar
            self._status_bar = StatusBar(master)
            self._status_bar.pack()
            self._status_bar.time_change()
            self._status_bar._move_left.config(text="Moves left\n {} moves remaining".format
            (self._player.moves_remaining()))

        self._keypad.bind("<Button-1>", self.mouse_control)
        self._master.bind("<Key>", self.key_control)

        # initialise Message_box
        self._message_box = Message_box(self._task)

    def key_control(self, e):
        direction = e.char.upper()
        self.move_player(direction)

    def mouse_control(self, e):
        position = self._keypad.pixel_to_position((e.x, e.y))
        n = self._keypad._positions.index((position[1], position[0]))
        directions = ("W", "S", "A", "D")
        direction = directions[n]
        self.move_player(direction)

    def move_player(self, direction):
        if not self._game.collision_check(direction):
            self._game.move_player(direction)
            entity = self._game.get_entity(self._player.get_position())
            # process on_hit and check win state
            if entity is not None:
                entity.on_hit(self._game)
                if self._game.won():
                    if self._task == 1:
                        self._message_box.show_info(1, self.new_game, score=None)
                    else:
                        score = "{}m {}s".format(self._status_bar._min, self._status_bar._second)
                        self._message_box.show_info(1, self.new_game, score)

        self._player.change_move_count(-1)
        if self._task == 2:
            self._status_bar._move_left.configure(text="Moves left\n {} moves remaining".format
            (self._player.moves_remaining()))
        if self._game.check_game_over():
            if self._game.check_game_over():
                self._message_box.show_info(2, self.new_game, score=None)

        self._dungeonmap.delete(tk.ALL)
        self._dungeonmap.re_draw_grid(self._game.get_game_information(),
                                      self._player.get_position())

    def display(self):
        self._dungeonmap.draw_grid(self._game.get_game_information(),
                                   self._player.get_position())

    def new_game(self):
        self._game_frame.destroy()
        self._status_bar.destroy()
        print("bar under")
        self.__init__(self._master, self._task, self._dungeon_name)


class Model():
    def __init__(self):
        entity = Entity()
        wall = Wall()
        player = Player()
        item = Item()
        key = Key()
        gamelogic = GameLogic()


def main():
    root = tk.Tk()
    root.title('Key Cave Advanture Game')
    title = tk.Label(root, text='Key Cave Advanture Game')
    title.pack(side=tk.TOP)
    app = GameApp(root, 2, "game2.txt")
    app.display()


if __name__ == "__main__":
    main()
