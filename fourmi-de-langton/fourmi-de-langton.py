#!/usr/bin/env python3
# -*- coding: utf8 -*-
#
# La fourmi de langton
#
# 01/2018 PG (pguillaumaud@april.org)
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
import sys, os
import pickle
import random
import tkinter as TK
import tkinter.messagebox as TKM
import tkinter.filedialog as TKF

# --------------------------------------------------------------------------------
# Valeurs par defaut du canvas
h, w = (600, 800)
periodic = False
# Taille des cellules
c_sz = 10
# Tempo entre 2 générations (ms)
tempo = 10
# Flag pour l'animation de la grille
flag = False
# nb de générations
nbgen = 0
# le label pour affichage
label_gen = 'génération: {0:6d}'

# couleur et etat des cases
NOIR   = 0
BLANC  = 1
FOURMI = 2

# vide = noir
color_NOIR   = "#000000"
# blanc
color_BLANC  = "#ffffff"
# fourmi rouge
color_FOURMI = "#ff0000"

# le nom du programme (sans l'extension)
name_app = os.path.splitext(os.path.basename(sys.argv[0]))[0]

# --------------------------------------------------------------------------------
# Fin du programme
def OnExit():
    # on supprime le fichier temporaire
    try:
        filename = '/tmp/'+name_app+'-gen0.bin'
        os.remove(filename)
    except:
        pass
    fen.destroy()

# --------------------------------------------------------------------------------
# Met a jour le label d'affichage des générations
def UpdateLabel():
    ng.set(label_gen.format(nbgen))
    fen.update_idletasks()

# --------------------------------------------------------------------------------
# Enregistre la génération 0 (pour le rewind)
def WriteGen0():
    filename = '/tmp/'+name_app+'-gen0.bin'
    try:
        fh = open(filename, 'wb')
        pickle.dump(life.world, fh)
        fh.close()
    except:
        pass

# --------------------------------------------------------------------------------
# Réinitialise avec la génération 0 sauvegardée
def Rewind():
    global life, nbgen
    filename = '/tmp/'+name_app+'-gen0.bin'
    try:
        fh = open(filename, 'rb')
        life.world = pickle.load(fh)
        fh.close()
        nbgen = 0
        UpdateLabel()
        life.DrawWorld()
    except:
        pass

# --------------------------------------------------------------------------------
# Ouvre un fichier
def OpenFile():
    global life, nbgen
    filename = TKF.askopenfilename(title="Ouvrir",filetypes=[('bin files','.bin'),('all files','.*')])
    if len(filename) > 0:
        try:
            fh = open(filename, 'rb')
            life.world = pickle.load(fh)
            fh.close()
            nbgen = 0
            UpdateLabel()
            life.DrawWorld()
        except e:
            TKM.showinfo("alerte", "Exception:" + e)

# --------------------------------------------------------------------------------
# Enregistrer
def WriteFile():
    filename = TKF.asksaveasfilename(title="Enregistrer",filetypes=[('bin files','.bin'),('all files','.*')])
    if len(filename) > 0:
        try:
            fh = open(filename, 'wb')
            pickle.dump(life.world, fh)
            fh.close()
        except e:
            TKM.showinfo("alerte", "Exception:" + e)

# --------------------------------------------------------------------------------
# dessine la grille
def DrawGrille():
    # les lignes verticales
    c_x = 0
    while c_x != w:
        canvas.create_line(c_x,0,c_x,h,width=1,fill='black')
        c_x += c_sz
    # les lignes horizontales
    c_y = 0
    while c_y != h:
        canvas.create_line(0,c_y,w,c_y,width=1,fill='black')
        c_y += c_sz

# --------------------------------------------------------------------------------
# démarre l'animation
def Go():
    global flag
    flag = True
    Play()

# --------------------------------------------------------------------------------
# arrète l'animation
def Stop():
    global flag
    flag = False

# --------------------------------------------------------------------------------
# Modifie la tempo
def ModifTempo(event):
    global tempo
    tempo = int(eval(stempo.get()))

# --------------------------------------------------------------------------------
# Animation
def Play():
    global flag, tempo, nbgen
    # On sauve la génération 0
    if nbgen == 0:
        WriteGen0()
    # evolution
    life.evolve()
    # met a jour le label
    nbgen += 1
    UpdateLabel()
    # affichage
    life.DrawWorld()
    if flag:
        fen.after(tempo,Play)

# --------------------------------------------------------------------------------
# Avance d'une génération
def PlayOne():
    global nbgen
    # On sauve la génération 0
    if nbgen == 0:
        WriteGen0()
    # evolution
    life.evolve()
    # met a jour le label
    nbgen += 1
    UpdateLabel()
    # affichage
    life.DrawWorld()

# --------------------------------------------------------------------------------
# Met la cellule sélectionnée dans l'état donné
def setCell(event, etat):
    x = event.x - (event.x%c_sz)
    y = event.y - (event.y%c_sz)
    # i = int(x/c_sz)
    # j = int(y/c_sz)
    i = int(y/c_sz)
    j = int(x/c_sz)
    life.set(i,j,etat)
    life.DrawWorld()

# --------------------------------------------------------------------------------
# Vide la cellule sur le clic gauche ...
def CellVide(event):
    setCell(event, NOIR)

# --------------------------------------------------------------------------------
# Remplis la cellule sur clic droit
def CellPlein(event):
    setCell(event, BLANC)

# --------------------------------------------------------------------------------
# Boutton RaZ de la grille
def RaZWorld():
    global nbgen
    life.init_world_raz()
    nbgen = 0
    UpdateLabel()
    life.DrawWorld()

# --------------------------------------------------------------------------------
# Boutton RnD de la grille
def RnDWorld():
    global nbgen
    life.init_world_rnd()
    nbgen = 0
    UpdateLabel()
    life.DrawWorld()

# --------------------------------------------------------------------------------
# La fourmi
class Ant(object):
    def __init__(self, i, j, dir, rows, columns):
        self.rows = rows
        self.columns = columns
        self.i = i
        self.j = j
        # direction: 0=Nord, 1=Est, 2=Sud, 3=West
        self.dir = dir

    def Move(self, currentCell):
        # on met a jour la direction (case blanche = 90° droite, case noire = 90° gauche)
        if currentCell == BLANC:
            self.dir = (self.dir + 1) % 4
        else:
            self.dir = self.dir -1
            if self.dir == -1:
                self.dir = 3

        # on avance d'une case
        if (self.dir == 0):
            # nord: en haut
            self.i = (self.i - 1) % self.rows
        elif (self.dir == 1):
            # est: a droite
            self.j = (self.j + 1) % self.columns
        elif (self.dir == 2):
            # sud: en bas
            self.i = (self.i + 1) % self.rows
        else:
            # ouest: a gauche
            self.j = (self.j - 1) % self.columns

# --------------------------------------------------------------------------------
# La grille
class Life(object):
    # representation des cellules
    cells = { NOIR: color_NOIR, BLANC: color_BLANC }

    def __init__(self, h, w, periodic=False):
        self.li = int(h/c_sz)
        self.co = int(w/c_sz)
        assert self.li > 0 and self.co > 0
        self.periodic = periodic

        # une fourmi
        self.ant = Ant(int(random.random()*self.li), int(random.random()*self.co), 0, self.li, self.co)

    # initialise la grille avec des cellules vides
    def init_world_raz(self):
        self.world = [[NOIR for j in range(self.co)] for i in range(self.li)]

    # initialise la grille avec des cellules aléatoires
    def init_world_rnd(self):
        self.world = [[random.choice([NOIR, BLANC]) for j in range(self.co)] for i in range(self.li)]

    # Retourne l'etat de la cellule i,j
    def get(self, i, j):
        if self.periodic:
            return self.world[i % self.li][j % self.co]
        else:
            if(0 <= i < self.li) and (0 <= j < self.co):
                # dans la grille
                return self.world[i][j]
            else:
                return False

    # Initialise l'etat de la cellule i,j
    def set(self, i, j, state):
        if(0 <= i < self.li) and (0 <= j < self.co):
            # dans la grille
            self.world[i][j] = state

    # Affichage de la fourmi
    def DrawAnt(self):
        y = self.ant.i*c_sz
        x = self.ant.j*c_sz
        canvas.create_rectangle(x, y, x+c_sz, y+c_sz, fill=color_FOURMI)

    # Affichage
    def DrawWorld(self):
        canvas.delete(TK.ALL)
        DrawGrille()
        for i in range(self.li):
            for j in range(self.co):
                # x = i*c_sz
                # y = j*c_sz
                y = i*c_sz
                x = j*c_sz
                canvas.create_rectangle(x, y, x+c_sz, y+c_sz, fill=self.cells[self.world[i][j]])
        self.DrawAnt()

    # Evolution de l'automate
    def evolve(self):
        # on inverse la couleur  sur la fourmi
        coul = self.get(self.ant.i, self.ant.j)
        if coul == NOIR:
            coul = BLANC
        else:
            coul = NOIR
        self.set(self.ant.i, self.ant.j, coul)
        # La fourmi se déplace
        self.ant.Move(coul)

# --------------------------------------------------------------------------------
if __name__ == "__main__":
    import argparse

    # Les arguments eventuels
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-H', required=False, type=int, default=h, action='store', help='Hauteur du canvas (px)')
    parser.add_argument('-W', required=False, type=int, default=w, action='store', help='Largeur du canvas (px)')
    parser.add_argument('-P', required=False, default=periodic, action='store_true', help='Grille périodique')
    args = parser.parse_args()

    if args.H is not None:
        h = args.H
    if args.W is not None:
        w = args.W
    if args.P is not None:
        periodic = args.P

    life = Life(h, w, periodic=False)

    # la fenêtre et le reste
    fen = TK.Tk()
    fen.title("La fourmi de Langton")
    fen.protocol("WM_DELETE_WINDOW",OnExit)
    fen.resizable(False, False)

    # pour le label d'affichage des générations
    ng = TK.StringVar()

    # le menu
    menubar = TK.Menu(fen)

    menu1 = TK.Menu(menubar, tearoff=0)
    menu1.add_command(label = "Enregistrer", command = WriteFile)
    menu1.add_command(label = "Ouvrir", command = OpenFile)
    menu1.add_separator()
    menu1.add_command(label = "Quitter", command = OnExit)

    menubar.add_cascade(label = "Fichier", menu = menu1)
    fen.config(menu = menubar)

    canvas = TK.Canvas(fen, width = w, height = h, bg ='white')
    # les clic souris sur la grille
    canvas.bind("<Button-1>", CellVide)
    canvas.bind("<Button-3>", CellPlein)
    canvas.grid(row = 0, column = 1, rowspan = 8, columnspan = 2, pady = 5)

    # initialisation de l'automate
    RnDWorld()

    # les bouttons
    # avec icones
    wb = 90
    img_start = TK.PhotoImage(file = 'icons/media-playback-start.png')
    b1 = TK.Button(fen, text ='Play', image = img_start, compound="left", width = wb, command = Go)
    img_stop = TK.PhotoImage(file = 'icons/media-playback-stop.png')
    b2 = TK.Button(fen, text ='Stop', image = img_stop, compound="left", width = wb, command = Stop)
    img_raz = TK.PhotoImage(file = 'icons/draw-eraser.png')
    b3 = TK.Button(fen, text ='RaZ', image = img_raz, compound="left", width = wb, command = RaZWorld)
    img_rnd = TK.PhotoImage(file = 'icons/transform-rotate.png')
    b4 = TK.Button(fen, text ='RnD', image = img_rnd, compound="left", width = wb, command = RnDWorld)
    img_rew = TK.PhotoImage(file = 'icons/media-seek-backward.png')
    b5 = TK.Button(fen, text ='Rewind', image = img_rew, compound="left", width = wb, command = Rewind)
    img_run = TK.PhotoImage(file = 'icons/system-run.png')
    b6 = TK.Button(fen, text ='Gén+1', image = img_run, compound="left", width = wb, command = PlayOne)
    b1.grid(row = 0, column = 0)
    b2.grid(row = 1, column = 0)
    b3.grid(row = 2, column = 0)
    b4.grid(row = 3, column = 0)
    b5.grid(row = 4, column = 0)
    b6.grid(row = 5, column = 0)
    img_quit = TK.PhotoImage(file = 'icons/system-log-out.png')
    bQ = TK.Button(fen, text ='Quitter', image = img_quit, compound="left", width = wb, command = OnExit)
    bQ.grid(row = 7, column = 0)

    # la zone de status en bas
    status = TK.Frame(fen)

    # la tempo
    chaine = TK.Label(status)
    chaine.configure(text = "Tempo (ms) :")
    chaine.grid(row = 0, column = 0, sticky = "W")
    stempo = TK.Entry(status, width = 5)
    stempo.insert(TK.END, tempo)
    stempo.bind("<Return>", ModifTempo)
    stempo.grid(row = 0, column = 1, sticky = "W")

    status.grid(row = 8, column = 0)

    # Affichage des dimensions
    sdim = TK.Label(fen)
    sdim.configure(text = "{0}x{1} ({2}x{3})".format(w, h, life.co, life.li))
    sdim.grid(row = 8, column = 1, sticky = "E")

    # le label pour l'affichage des générations
    ng.set(label_gen.format(nbgen))
    affgen = TK.Label(fen, textvariable = ng, width = 20, anchor = TK.E, fg = "blue", justify = TK.RIGHT)
    affgen.grid(row = 8, column = 2, sticky = "E")

    fen.mainloop()
# eof
