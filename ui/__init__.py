#!/usr/bin/env python3
import click
import os
import string

def letter_to_num(letter):
    return string.ascii_lowercase.index(letter.lower())

def parse_coordinate(coord):
    coord = coord.lower()
    if coord[0] in string.ascii_lowercase:
        return letter_to_num(coord[0]), int(coord[1])-1
    else:
        return int(coord[1])-1, letter_to_num(coord[0])

class Tile():
    def __init__(self, row, col, ship=False):
        self.row = row
        self.col = col
        self.ship = ship
        self.hit = False

    def char(self):
        if self.ship:
            return 'X' if self.hit else '+'
        else:
            return '.' if self.hit else ' '

    def color(self):
        if self.ship:
            color = 'yellow' if self.hit else 'white'
        else:
            color = 'green' if self.hit else 'black'
        return click.style(' ', fg=color)


class Ship():
    def __init__(self, start, size, horizontal):
        self.body = []
        row, col = parse_coordinate(start)
        for i in range(size):
            if horizontal:
                tile = Tile(row, col+i, ship=True)
            else:
                tile = Tile(row+i, col, ship=True)
            self.body.append(tile)

    def check(self, row, col):
        for tile in self.body:
            if tile.row == row and tile.col == col:
                tile.hit = True
                return True
        return False

    def destroyed(self):
        for tile in self.body:
            if not tile.hit:
                return False
        return True

    def __str__(self):
        return self.__class__.__name__


class AircraftCarrier(Ship):
    def __init__(self, start, horizontal):
        super().__init__(start, 5, horizontal)


class Battleship(Ship):
    def __init__(self, start, horizontal):
        super().__init__(start, 4, horizontal)


class Cruiser(Ship):
    def __init__(self, start, horizontal):
        super().__init__(start, 3, horizontal)


class Destroyer(Ship):
    def __init__(self, start, horizontal):
        super().__init__(start, 2, horizontal)


class Submarine(Ship):
    def __init__(self, start, horizontal):
        super().__init__(start, 1, horizontal)


class Board():
    WIDTH = 10
    HEIGHT = 10
    def __init__(self, ships=[]):
        self.__rows = []
        for row in range(self.HEIGHT):
            self.__rows.append([Tile(row, col) for col in range(self.WIDTH)])
        self.__ships = ships
        for ship in ships:
            for tile in ship.body:
                self.rows[tile.row][tile.col] = tile
        self.__harbor = [
                'AircraftCarrier',
                'Battleship',
                'Cruiser',
                'Destroyer', 'Destroyer',
                'Submarine', 'Submarine'
            ]

    @property
    def harbor(self):
        return self.__harbor

    def harbor_empty(self):
        return bool(len(self.__harbor==0))

    @property
    def ships(self):
        return self.__ships

    def add_ship(self, ship):
        if str(ship) not in self.__harbor:
            raise("No {} available anymore!".format(str(ship)))
        self.__ships.append(ship)
        for tile in ship.body:
            self.rows[tile.row][tile.col] = tile
        self.__habour.remove(str(ship))

    @property
    def rows(self):
        return self.__rows

    def check(self, row, col):
        for ship in self.__ships:
            if ship.check(row, col):
                return True
        self.__rows[row][col].hit = True
        return False
    
    def show(self, color=False):
        lines = ['|'.join([' #']+ [c for c in string.ascii_lowercase[:self.WIDTH]])]
        for idx, row in enumerate(self.rows):
            lines.append('|'.join([str(idx+1) if idx+1>=10 else '0'+str(idx+1)]+[tile.color() if color else tile.char() for tile in row]))
        return '\n'.join(lines)


class Game():
    def __init__(self):
        self.own = Board()
        self.enemy = Board()

    def lost(self):
        for ship in self.own.ships:
            if not ship.destroyed():
                return False
        return True


@click.command()
@click.option('--peer', help='Graph output format')
@click.option('--color/--no-color', default=True)
@click.pass_context
def run(ctx, peer, color):
    """Run battleships client."""
    if os.geteuid() != 0:
        click.echo('client needs to run with root priviledges')
        return
    game = Game()

    # TODO: place own ships


    while not game.lost():
        click.clear()
        click.echo(game.enemy.show(color=color))
        coord = click.prompt('next move')
        row, col = parse_coordinate(coord)
        if game.enemy.check(row, col):
            click.echo('HIT')
        click.echo('MISSED')
