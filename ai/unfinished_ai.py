#!/usr/bin/env python

# Copyright 2017 Pablo Quilez

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from termcolor import colored
from itertools import chain, combinations
import random
import copy

# This class contains the board information
class grid:

	def __init__(self, width, height, mines):
		self.width = width
		self.height = height
		self.mines  = set(random.sample(range(width*height), mines)) # Mine positions saved as a set
		self.marked = set() 										 # Already marked squares

	# ---------------------------------------------------
	# Private functions
	# ---------------------------------------------------

	# Returns if the position is inside the limits
	def inside(self,x,y):
		return (y>=0) and (y<self.width) and (x>=0) and (x<self.height)

	# Returns if the position is a mine
	def is_mine(self,x,y):
		return self.index(x,y) in self.mines

	# Returns 
	def mines_surrounding_i(self,index):
		x = index / self.width
		y = index % self.width
		return self.mines_surrounding(x,y)

	def mines_surrounding(self,x,y):
		assert(self.index(x,y) in self.marked)
		found = 0
		for i in [x-1,x,x+1]:
			for j in [y-1,y,y+1]:
				if self.inside(i,j) and self.index(i,j) in self.mines:
					found += 1
		return found

	# return the number of discovered tiles
	def discovered(self):
		#return self.grid.count(1)
		return len(self.mines)

	def index(self,x,y):
		assert self.inside(x,y)
		return x * self.width + y

	# 0 means correctly marked
	# 1 means marked a mine -> finish game loose
	# 2 means game won
	def mark_i(self,index):
		x = index / self.width
		y = index % self.width
		return self.mark(x,y)
	def mark(self,x,y):
		if self.is_mine(x,y):
			return 1
		else:
			# Mark the square
			# self.grid(index(x,y)) = 1
			self.marked.add(self.index(x,y))

			if len(self.marked) + len(self.mines) == self.width * self.height:
				return 2
			else:
				return 0

	def printgrid_mines(self):
		for x in range(self.height):
			for y in range(self.width):
				if not self.index(x,y) in self.mines:
					print colored("O","green"),
				else:
					print colored("X","red"),
			print ""
		print "-----------------------"

	def printgrid(self):
		for x in range(self.height):
			for y in range(self.width):
				if self.index(x,y) in self.marked:
					print colored(self.mines_surrounding(x,y),"green"),
				else:
					print colored("X","white"),
			print ""
		print "-----------------------"

# -------------------------------------------------------------------------------------
# Algorithmical solution of the game
# UNFINISHED
# -------------------------------------------------------------------------------------

class unfinished_ai:

	def __init__(self, grid):
		self.grid = grid
		self.possible_mines = range(grid.width * grid.height) # at the beginning all is a possible mine
		self.discovered = set()

	# returns true if a mine was marked
	# false if no mines were discovered
	def mark_possible_mines(self):

		#s=set(self.grid.marked)
		#subs = [set(j) for i in range(len(s)) for j in combinations(s, i+1)]



		progress = False

		c = copy.deepcopy(self.grid.marked)

		for x in c:
			if self.mark_surrounding_i(x):
				progress = True
		return progress

	def mark_surrounding_i(self,index):
		x = index / self.grid.width
		y = index % self.grid.width
		return self.mark_surrounding(x,y)
	def mark_surrounding(self,x,y):
		progress = False
		assert (self.grid.index(x,y) in self.grid.marked)
		menaces = self.grid.mines_surrounding(x,y)
		discovered = self.surrounding_discovered(x,y)
		possibilites = self.surrounding_possibilities_to_mark(x,y)
		print menaces,discovered, possibilites
		if menaces + len(possibilities) == len(discovered):
			for p in possibilites:
				if p not in discovered:
					self.grid.mark_i(p)
					progress = True
		return progress


	def surrounding_discovered(self,x,y):
		l = []
		for i in [x-1,x, x+1]:
			for j in [y-1,y,y+1]:
				if (i != x or j != y) and self.grid.inside(i,j):
					if (self.grid.index(i,j) in self.discovered):
						l.append(self.grid.index(i,j))
		return l

	def surrounding_possibilities_to_mark(self,x,y):
		l = []
		for i in [x-1,x, x+1]:
			for j in [y-1,y,y+1]:
				if (i != x or j != y) and self.grid.inside(i,j):
					if not (self.grid.index(i,j) in self.grid.marked):
						l.append(self.grid.index(i,j))
		return l

	# This function marks as discovered some squares
	def assume(self, some_marked_squares):
		self.dicovered = set() # clear the set
		for x in some_marked_squares:
			self.assume_surrounding_i(x)
	def assume_surrounding_i(self,index):
		x = index / self.grid.width
		y = index % self.grid.width
		self.assume_surrounding(x,y)
	def assume_surrounding(self,x,y):
		assert (self.grid.index(x,y) in self.grid.marked)
		for i in [x-1,x, x+1]:
			for j in [y-1,y,y+1]:
				if (i != x or j != y) and self.grid.inside(i,j):
					self.discovered.add(self.grid.index(i,j))



	#def get_best_to_marked(return values.index(min(values)))

def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))

def subsets(s):
    return map(set, powerset(s))

# returns those > 0 marked squares
def frontiers(grid):
	s = set()
	for x in grid.marked:
		if (grid.mines_surrounding_i(x) > 0):
			s.add(x)
	return s

def play(grid, ai):
	if (grid.mark(0,0) != 0): return
	grid.printgrid()

	end = False
	while(not end):
		end = True
		for s in subsets(frontiers(grid)):
			ai.assume(s)
			print ai.discovered
			progress = True
			while(progress):
				progress = ai.mark_possible_mines()
				if (progress): end = False
				#grid.printgrid()


# --------------------------------------------------------------------------------------------------------

# --------------------------------------------------------------------------------------------------------


def human_game(grid):
	grid.printgrid()
	end = 0
	while (end == 0):
		i,j = raw_input("Please enter square as x y: ").split()
		end = grid.mark(int(i),int(j))
		grid.printgrid()
	if end == 1:
		print "you loose!"
	else:
		print "you won!"


if __name__ == '__main__':

	w = 3
	h = 3
	m = int(0.1 * w * h)
	m = 2

	grid = grid(w,h,m)
	human_game(grid)

	#grid = grid(w,h,m)
	#grid.printgrid_mines()

	#ai = ai(grid)
	#play(grid, ai)

	#grid.printgrid()

	#print "finish"