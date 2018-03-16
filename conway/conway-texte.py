#!/usr/bin/env python3
# -*- coding: utf8 -*-
#
# Jeu de la vie, en mode texte
#
# 01/2018 PG (pguillaumaud@april.org)
# (inspire du livre 'Analyse-scientifique-avec-python')
#
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA
#
import random

# --------------------------------------------------------------------------------
class Life(object):
    # representation textuelle des cellules
    cells = { False: ".", True: "#" }

    def __init__(self, h, w, periodic=False):
        self.h = int(h)
        self.w = int(w)
        assert self.h > 0 and self.w > 0

        # initialisation de la grille
        # 'h' lignes de 'w' colonnes
        self.world = [[random.choice([True, False]) for j in range(self.w)] for i in range(self.h)]

        self.periodic = periodic

    # Retourne l'etat de la cellule i,j
    def get(self, i, j):
        if self.periodic:
            return self.world[i % self.h][j % self.w]
        else:
            if(0 <= i < self.h) and (0 <= j < self.w):
                # dans la grille
                return self.world[i][j]
            else:
                return False

    # Converti la grille en chaine de caracteres
    # pour l'affichage par print
    def __str__(self):
        return '\n'.join([''.join([self.cells[val] for val in row]) for row in self.world])

    # Evolution de la cellule i,j
    def evolve_cell(self, i, j):
        # Etat actuel de la cellule
        alive = self.get(i, j)

        # On compte les voisins vivants
        count = sum(self.get(i + ii, j + jj) for ii in [-1, 0, 1] for jj in [-1, 0, 1] if (ii, jj) != (0, 0))

        if count == 3:
            # 3 voisins vivants, la cellule reste vivante ou le devient
            future = True
        elif count < 2 or count > 3:
            # Trop ou pas assez de voisin vivants, mort de la cellule
            future = False
        else:
            # 2 ou 3 voisins, reste dans le meme etat
            future = alive

        return future


    # Met a jour la grille
    def evolve(self):
        self.world = [[self.evolve_cell(i, j) for j in range(self.w)] for i in range(self.h)]

# --------------------------------------------------------------------------------
if __name__ == "__main__":
    import argparse
    import time

    # Valeurs par defaut
    h, w = (20, 60)
    periodic = False

    # Les arguments eventuels
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-H', required=False, type=int, default=h, action='store', help='Nombre de lignes de la grille')
    parser.add_argument('-W', required=False, type=int, default=w, action='store', help='Nombre de colonnes de la grille')
    parser.add_argument('-P', required=False, default=periodic, action='store_true', help='Grille périodique')
    args = parser.parse_args()

    if args.H is not None:
        h = args.H
    if args.W is not None:
        w = args.W
    if args.P is not None:
        periodic = args.P

    life = Life(h, w, periodic=False)

    # Ctrl+C pour terminer
    try:
        while True:
            print(life)
            print("\n")
            # pause
            time.sleep(0.5)
            # evolution
            life.evolve()
    except KeyboardInterrupt:
        print("Fin du programme")

# eof
