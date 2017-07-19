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

# A simple minesweeper console game

from termcolor import colored
from itertools import chain, combinations
import random
import copy
import operator

# This class contains the board information
# According to the rules, no mine can be set at the beginning position
# At least there must be a possible free square

# Rules of the minesweeper:
# Max mines mus be width*height - 1

class grid:

	def __init__(self, width, height, mines):
		if mines >= width * height : mines = width * height - 1
		self.width = width
		self.height = height
		#self.mines  = set(random.sample(range(width*height), mines)) # Mine positions saved as a set
		self.marked = set() # Already marked squares
		self.max_mines = mines

	# ---------------------------------------------------
	# Public functions
	# ---------------------------------------------------

	# Mark a mine by using index or x,y (row, column)
	# 0 means correctly marked
	# 1 means marked a mine -> finish game loose
	# 2 means game won
	def mark_i(self,index):
		x = index / self.width
		y = index % self.width
		return self.mark(x,y)
	def mark(self,x,y):

		assert self.index(x,y) not in self.marked

		# We generate the board after the first click
		if not self.marked:
			# The first clicked square must be free, also the surrounding, if possible, until complete max mines
			p = range(self.width*self.height)
			p.remove(self.index(x,y)) # Remove the first square from the possibilites
			s = self.surrounding_tiles_i(self.index(x,y))

			surrounding_free_squares = self.width * self.height - 1 - self.max_mines
			if surrounding_free_squares > 9 : surrounding_free_squares = 9

			for z in range(surrounding_free_squares):
				if s:
					r = random.choice(s)
					s.remove(r)
					p.remove(r)

			self.mines = set(random.sample(p, self.max_mines)) # Mine positions saved as a set

		if self.is_mine(x,y):
			return 1
		else:
			self.marked.add(self.index(x,y))
			if len(self.marked) + len(self.mines) == self.width * self.height:
				return 2
			else:
				# Check if no mines are surrounding and mark surrounding tiles therefore
				if self.mines_surrounding(x,y) == 0:
					s = self.surrounding_tiles_i(self.index(x,y))
					for z in s:
						if z not in self.marked:
							self.mark_i(z)
				return 0

	def surrounding_tiles_i(self,index):
		x = index / self.width
		y = index % self.width
		return self.surrounding_tiles(x,y)

	def surrounding_tiles(self,x,y):
		l = []
		for i in [x-1,x, x+1]:
			for j in [y-1,y,y+1]:
				if (i != x or j != y) and self.inside(i,j):
					l.append(self.index(i,j))
		return l

	def surrounding_possibilities_to_mark_i(self,index):
		x = index / self.width
		y = index % self.width
		return self.surrounding_possibilities_to_mark(x,y)

	def surrounding_possibilities_to_mark(self,x,y):
		l = []
		for i in [x-1,x, x+1]:
			for j in [y-1,y,y+1]:
				if (i != x or j != y) and self.inside(i,j):
					if not (self.index(i,j) in self.marked):
						l.append(self.index(i,j))
		return l

	# Print the grid showing the mine positions
	def print_mine_positions(self):
		for x in range(self.height):
			for y in range(self.width):
				if not self.index(x,y) in self.mines:
					print colored("O","green"),
				else:
					print colored("X","red"),
			print ""
		print "-----------------------"

	# Print the current state of the grid
	def printgrid(self, opt = -1, mines_found = []):
		for x in range(self.height):
			for y in range(self.width):
				if self.index(x,y) in self.marked:
					print colored(self.mines_surrounding(x,y),"green"),
				elif self.index(x,y) == opt:
					print colored("O","blue"),
				elif self.index(x,y) in mines_found:
					print colored("M","red"),
				else:
					print colored("X","white"),
			print ""
		print "-----------------------"

	# Returns a set containing unmarked tiles
	def unmarked(self):
		return set([x for x in range(0, self.width * self.height) if x not in self.marked])

	# Returns the number of mines surrounding the square
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

	# ---------------------------------------------------
	# Helper functions
	# ---------------------------------------------------

	# Returns if the position is inside the limits
	def inside(self,x,y):
		return (y>=0) and (y<self.width) and (x>=0) and (x<self.height)

	# Returns if the position is a mine
	def is_mine(self,x,y):
		return self.index(x,y) in self.mines


	def index(self,x,y):
		assert self.inside(x,y)
		return x * self.width + y

# --------------------------------------------------------------------------------------------------------
# Brute force AI, working but too slow
# --------------------------------------------------------------------------------------------------------

class brute_ai():

	def __init__(self, grid):
		self.grid = grid
		self.mines_found = set()
		self.safe_to_mark = set()

	# Calculate the safe mark possibilities and find mines
	# Returns true if progress was done or False if not
	def calculate(self):
		
		pre_mines_found = copy.deepcopy(self.mines_found)
		pre_safe_to_mark = copy.deepcopy(self.safe_to_mark)

		for x in self.grid.marked:
			mines_there_are = self.grid.mines_surrounding_i(x)
			number_of_mines_found = len(self.surrounding_mines_found(x))
			mark_possibilities = len(self.safe_surrounding_possibilities_to_mark_i(x))

			if self.grid.mines_surrounding_i(x) == 0:
				# No mines surrounding, all safe
				self.safe_to_mark = self.safe_to_mark.union(self.grid.surrounding_possibilities_to_mark_i(x))
			elif mines_there_are - number_of_mines_found == mark_possibilities:
				# All surrounding are mines
				self.mines_found = self.mines_found.union(self.safe_surrounding_possibilities_to_mark_i(x))
				progress = True
			elif mines_there_are - number_of_mines_found == 0:
				# All mines surrounding were found
				self.safe_to_mark = self.safe_to_mark.union(self.safe_surrounding_possibilities_to_mark_i(x))
				progress = True
		if pre_mines_found != self.mines_found or pre_safe_to_mark != self.safe_to_mark:
			self.calculate() # Calculate again if some progress was achieved

	# TODO: Check if this function is really getting a good option
	# This function is invoked when we get a possition where we can't determine any progress any more
	# We need to guess.
	def get_less_probable_tile_with_mine(self):

		probability = {}

		safe_marks = [x for x in self.grid.unmarked() if not x in self.mines_found] 

		#for x in safe_marks:
		#	probability[x] = float(self.grid.max_mines - len(self.mines_found)) / float(len(safe_marks))

		for x in self.mines_found:
			probability[x] = 1.0 # Mines found have a probability of 1
		
		for x in self.grid.marked:
			s = self.safe_surrounding_possibilities_to_mark_i(x) # At least we know it could be no mine
			known = len(self.surrounding_mines_found(x))
			mines = self.grid.mines_surrounding_i(x)
			for y in s:
				p = float(mines - known) / float(len(s))
				if y in probability:
					if p > probability[y]:
						probability[y] = p
				else:
					probability[y] = p

		sorted_prob = sorted(probability.items(), key=operator.itemgetter(1))

		#assert sorted_prob[0][0] not in self.grid.marked

		if sorted_prob:
			return sorted_prob[0][0]
		else:
			return random.choice(list(self.grid.unmarked()))


	def surrounding_mines_found(self, index, mf = None):
		if mf:
			return [x for x in self.grid.surrounding_tiles_i(index) if x in mf]	
		else:
			return [x for x in self.grid.surrounding_tiles_i(index) if x in self.mines_found]			

	def safe_surrounding_possibilities_to_mark_i(self, index):
		neighbours = self.grid.surrounding_possibilities_to_mark_i(index)
		return [x for x in neighbours if x not in self.mines_found]

	def get_best_option_to_mark(self):
		#if not self.grid.marked:
		#	return 0, self.mines_found

		for x in self.grid.marked:
			if x in self.safe_to_mark: self.safe_to_mark.remove(x) # This is necessary because 0 mark can mark another tiles

		self.calculate()
		if self.safe_to_mark:
			return self.safe_to_mark.pop(), self.mines_found
		else:
			print "Using brute force"
			# Time to do some brute force
			self.calculate_by_brute_force()
			if self.safe_to_mark:
				return self.safe_to_mark.pop(), self.mines_found
			else:
				print "Guessing"
				return self.get_less_probable_tile_with_mine(), self.mines_found

	def get_safe_frontiers(self):
		s = set()
		for x in self.grid.marked:
			s = s.union(self.safe_surrounding_possibilities_to_mark_i(x))
		return s

	def calculate_by_brute_force(self):
		solution_mines = []
		self.get_solutions_brute_force(self.get_safe_frontiers(), self.mines_found, solution_mines)
		# Mark as safe those tiles who are not in any solution
		u = set()
		for s in solution_mines:
			u = u.union(s)
		for x in self.get_safe_frontiers():
			if x not in u:
				self.safe_to_mark.add(x)

	# We pass frontiers, mines_found and safe_to_mark
	def get_solutions_brute_force(self, f, mf, solution_mines):

		if self.it_may_be_ok(mf):
			if f:
				cf1 = copy.deepcopy(f)
				cf2 = copy.deepcopy(f)
				cmf1 = copy.deepcopy(mf)
				cmf2 = copy.deepcopy(mf)
				x = cf1.pop()
				cf2.remove(x)
				cmf2.add(x)
				self.get_solutions_brute_force(cf1, cmf1, solution_mines)
				self.get_solutions_brute_force(cf2, cmf2, solution_mines)
			else:
				# Check if all marked squares have the corrected number of surrounding mines
				for x in self.grid.marked:
					mines = self.grid.mines_surrounding_i(x)
					found = len(self.surrounding_mines_found(x, mf))
					if mines != found:
						return
				solution_mines.append(mf)
		else:
			return

	# We consider a mine assumption could be ok as long as the surrounding sume doesn't surpass the know number of mines
	def it_may_be_ok(self, mf):
		for x in self.grid.marked:
			km = self.grid.mines_surrounding_i(x)
			fm = len(self.surrounding_mines_found(x, mf))
			if fm > km:
				return False
		return True

	def play(self):
		self.grid.printgrid()
		end = 0
		while (end == 0):
			opt, mines_found = self.get_best_option_to_mark()

			if opt == -1:
				self.grid.printgrid(-1, mines_found)
				print "No idea how to continue"
				return 0

			end = self.grid.mark_i(opt)
			self.grid.printgrid(opt, mines_found)
		if end == 1:
			print "You loose!"	
			return 0
		else:
			print "You win!"
			return


# --------------------------------------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------------------------------------

def prob_ai_game(grid):
	grid.printgrid()
	end = 0
	ai = prob_ai(grid)
	#end = grid.mark(0,0)
	while (end == 0):
		opt = ai.get_best_option_to_mark()
		end = grid.mark_i(opt)
		grid.printgrid(opt)
	if end == 1:
		print "you loose!"
	else:
		print "you won!"


def human_game(grid):
	grid.printgrid()
	end = 0
	while (end == 0):
		i,j = raw_input("Please enter square as x y: ").split()
		i = int(i)
		j = int(j)
		if grid.inside(i,j):
			end = grid.mark(i,j)
		grid.printgrid()
	if end == 1:
		print "you loose!"
	else:
		print "you won!"


if __name__ == '__main__':

	w = int(raw_input("Please enter the width of the grid: "))
	h = int(raw_input("Please enter the height of the grid: "))
	m = int(raw_input("Please enter the number of mines: "))

	#victories = 0
	#for x in range(100):
	#	g = grid(w,h,m)
	#	b = brute_ai(g)
	#	if b.play() : victories += 1

	#print victories / 100.0

	#human_game(grid)


	g = grid(w,h,m)
	brute_ai(g).play()
	#human_game(g)