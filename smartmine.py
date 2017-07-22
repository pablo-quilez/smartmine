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
import itertools
import random
import copy
import operator
import sys

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
		sys.setrecursionlimit(width * height * 2) # If all are 0 the mark algorithm generates a lot of recursions

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
		print "Still " + str(self.max_mines - len(mines_found)) + " mines to found from " + str(self.max_mines)
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



"""
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

		# This is necessary because when we mark a 0, then automatically surrounding tiles are marked
		# and the algorithm is not informed
		for x in self.grid.marked:
			if x in self.safe_to_mark: self.safe_to_mark.remove(x)

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

	# Returns those squares which can be marked and at least we didn't find a mine there
	def get_safe_frontiers(self):
		s = set()
		for x in self.grid.marked:
			s = s.union(self.safe_surrounding_possibilities_to_mark_i(x))
		return s


	# Returns groups of squares to be marked and the number of mines expected on each group
	# according to the format [[group as set(), number of mines],...]
	def get_groups(self):
		groups = []
		surrounding_marked = []
		safe_frontiers = self.get_safe_frontiers()
		for x in safe_frontiers:
			surrounding_marked.extend(self.surrounding_marked_squares(x))
		for x in surrounding_marked:
			pos = self.safe_surrounding_possibilities_to_mark_i(x)
			mines_in_pos = self.grid.mines_surrounding_i(x) - len(self.surrounding_mines_found(x))
			poscopy = copy.deepcopy(pos)
			for y in poscopy:
				if self.belongs_to_a_group(groups, y):
					pos.remove(y)
			if pos: # Don't add empty groups
				groups.append([pos,mines_in_pos])
		return groups

	def get_marked_borders(self):
		border = set()
		safe_frontiers = self.get_safe_frontiers()
		for x in safe_frontiers:
			b = [y for y in self.grid.surrounding_tiles_i(x) if y in self.grid.marked]
			border = border.union(set(b))
		return border

	# Returns if a square belong to a group or not (using format from get_groups)
	def belongs_to_a_group(self, groups, tile):
		for g in groups:
			if tile in g[0]: return True
		return False

	# Returns from a given unmarked square the surrounding marked squares
	def surrounding_marked_squares(self, tile):
		# If is surrounding a frontier, we assume that the surrounding tiles are all not 0
		return [x for x in self.grid.surrounding_tiles_i(tile) if x in self.grid.marked]

	def calculate_by_brute_force(self):

		borders = self.get_marked_borders()

		possible_solutions = []
		for g in self.get_groups():
			possible_solutions.append(self.get_possible_solutions_of_group(g))

		global lalala
		lalala =0

		configurations = self.get_mine_configurations(possible_solutions, borders)

		print len(configurations)
		raw_input("Waiting for Enter...")

		correct_configurations = []
		# We need to filter those who are not correct
		for c in configurations:
			ignore = False
			#for x in self.grid.marked:
			for x in borders:
				mines = self.grid.mines_surrounding_i(x)
				found = len(self.surrounding_mines_found(x, list(c) + list(self.mines_found)))
				if mines != found:
					ignore = True
					break
			if not ignore: correct_configurations.append(c)

		#print correct_configurations
		#raw_input("Press Enter to continue...")

		all_mines = set()
		for x in correct_configurations:
			all_mines = all_mines.union(set(x))

		# Those safe frontiers who are in no mine configuration are safe
		for x in self.get_safe_frontiers():
			if x not in all_mines:
				self.safe_to_mark.add(x)

		# Those who are in all are always mines
		if correct_configurations:
			inter = set(correct_configurations[0])
			for x in correct_configurations:
				inter = inter.intersection(x)
			self.mines_found = self.mines_found.union(inter)

	# Returns all possible combinations of mines configurations for the group as list
	def get_possible_solutions_of_group(self, group):
		k = []
		for x in range(group[1] + 1):
			k = k + list(set(itertools.combinations(group[0], x)))
		return k

	# Returns a list containing all possible mines configurations
	def get_mine_configurations(self, possible_solutions, borders):
		global lalala
		lalala += 1
		if lalala % 1000 == 0: print lalala

		solutions = []
		if not possible_solutions: return []
		front = possible_solutions.pop()
		for p in front:
			possible_solutions_copy = copy.deepcopy(possible_solutions)
			rest_solutions = self.get_mine_configurations(possible_solutions_copy, borders)
			if not rest_solutions:
				solutions.append(p)
			else:
				for r in rest_solutions:
					new_set = p + r
					if self.may_be_ok(new_set, borders):
						solutions.append(new_set)
		return solutions


	def may_be_ok(self, mines, borders):
		mf = set(mines).union(self.mines_found)
		for x in borders:
			if len(self.surrounding_mines_found(x, mf)) > self.grid.mines_surrounding_i(x):
				return False
		return True








"""
"""






















	# Returns those squares which can be marked and at least we didn't find a mine there
	def get_frontiers(self):
		s = set()
		for x in self.grid.marked:
			# Speed up, take only squares with mines surrounding
			if self.grid.mines_surrounding_i(x) == 0: continue

			# Speed up, take only squares with possibilites to mark, well, this covers indeed the previous case
			if len(self.safe_surrounding_possibilities_to_mark_i(x)) == 0: continue

			s.add(x)
		return s




















	# Returns the distance between tile a and b
	def get_distance(self, a, b):
		x1 = a / self.grid.width
		y1 = a % self.grid.width
		x2 = b / self.grid.width
		y2 = b % self.grid.width
		return max([abs(x2 - x1), abs(y2 - y1)])


	# Returns -1 if it is in no island, one element must be only in one island
	def get_island_index(self, islands, x):
		index = 0
		for island in islands:
			if x in island:
				return index
			index += 1
		return -1


	def divide_problem_in_islands(self, frontiers):
		islands = []
		for x in frontiers:
			current_island = self.get_island_index(islands, x)
			if current_island == -1:
				islands.append([])
			for y in frontiers:
				if self.get_distance(x, y) <= 3:
					islands[current_island].append(y)
		return islands

	def calculate_by_brute_force(self):
		solution_mines = []
		global la 
		la = 0
		to_check = self.get_frontiers()

		print self.get_safe_frontiers()

		self.get_solutions_brute_force(self.get_safe_frontiers(), self.mines_found, solution_mines, to_check)
		# Mark as safe those tiles who are not in any solution
		u = set()
		for s in solution_mines:
			u = u.union(s)
		for x in self.get_safe_frontiers():
			if x not in u:
				self.safe_to_mark.add(x)

	# We pass frontiers, mines_found and safe_to_mark
	def get_solutions_brute_force(self, f, mf, solution_mines, to_check):
		global la
		la += 1
		if la % 1000 == 0:
			print la
		if self.it_may_be_ok(mf, to_check):
			if f:
				cf1 = copy.deepcopy(f)
				cf2 = copy.deepcopy(f)
				cmf1 = copy.deepcopy(mf)
				cmf2 = copy.deepcopy(mf)
				x = cf1.pop()
				cf2.remove(x)
				cmf2.add(x)
				self.get_solutions_brute_force(cf1, cmf1, solution_mines, to_check)
				self.get_solutions_brute_force(cf2, cmf2, solution_mines, to_check)
			else:
				# Check if all marked squares have the corrected number of surrounding mines
				
				for x in to_check:
					mines = self.grid.mines_surrounding_i(x)
					found = len(self.surrounding_mines_found(x, mf))
					if mines != found:
						return
				solution_mines.append(mf)
		else:
			return

	# We consider a mine assumption could be ok as long as the surrounding sume doesn't surpass the know number of mines
	def it_may_be_ok(self, mf, to_check):
		for x in to_check:
			km = self.grid.mines_surrounding_i(x)
			fm = len(self.surrounding_mines_found(x, mf))
			if fm > km:
				return False
		return True

"""
"""

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
			return 1
"""

class brute_ai:

	# ---------------------------------------------------------------
	# Groups
	# ---------------------------------------------------------------
	# A group is a set of tiles which surrounds a given square
	# The group also knows how many mines are exactly in the group
	# ---------------------------------------------------------------
	class group:
		# grid must be the minesweeper grid
		# mines_found is an iterable containing found mine positions
		# tile is the current marked square which generates the group of markable tiles surrounding
		def __init__(self, grid, mines_found, tile):
			assert tile in grid.marked
			possibilities_to_mark = grid.surrounding_possibilities_to_mark_i(tile)
			self.tiles = set([x for x in possibilities_to_mark if x not in mines_found])
			self.mines = grid.mines_surrounding_i(tile) - len([x for x in mines_found if x in possibilities_to_mark])
			assert self.mines <= len(self.tiles)
		# Returns if the group already exist in an iterable of groups
		def already_exists(self, groups):
			for x in groups:
				if x.tiles == self.tiles :
					assert x.mines == self.mines # Duplicated groups must contain the same number of mines
					return True
			return False
		# Returns if all of elements of the group are mines
		def is_determined(self):
			return len(self.tiles) == self.mines
		# Remove the elements from the tiles:
		def remove(self, tiles_to_remove, number_of_mines):
			self.tiles = set([x for x in self.tiles if x not in tiles_to_remove])
			self.mines = self.mines - number_of_mines
			assert self.mines >= 0
		def remove_from_group(self, group):
			self.remove(group.tiles, group.mines)
		# Check if is a subset
		def issubset(self, group):
			return self.tiles.issubset(group.tiles)
		# Returns true if the intersection between groups is not empty
		def touchs(self, group):
			if self.tiles.intersection(group.tiles):
				return True
			return False
		# Overwrite print operators
		def __str__(self):
			return str(self.tiles) + "--> " + str(self.mines)
		def __repr__(self):
			return self.__str__()

    # Returns all possible not empty groups as a list of groups
	def get_groups(self):
		groups = []
		for x in self.grid.marked:
			group = self.group(self.grid, self.mines_found, x)
			# Remove empty groups
			if not group.tiles : continue
			# Remove duplicated
			if group.already_exists(groups) : continue
			groups.append(group)
		return groups

	# Returns all groups with are touching another group
	# TODO: delete duplicates
	def get_islands(self, groups):
		islands = []
		for x in groups:
			island = set()
			island.add(x)
			for y in groups:
				if x.touchs(y):
					island.add(y)
			islands.append(island)
		return islands

    # ---------------------------------------------------------------
	# Class entry point
	# ---------------------------------------------------------------
	def __init__(self, grid):
		self.grid = grid
		self.mines_found = set()
		self.safe_to_mark = set()
	# ---------------------------------------------------------------
	# Logic
	# ---------------------------------------------------------------
	def calculate(self):
		self.calculate_simple_case() # Calculate easy determined mines in groups
		self.calculate_collisions() # Calculate complex combinations
		self.calculate_safe_squares()
		
	def calculate_simple_case(self):
		progress = False
		groups = self.get_groups()
		for group in groups:
			if group.is_determined(): # If there are the same number of mines and tiles in the group
				self.mines_found = self.mines_found.union(group.tiles)
				progress = True
		if progress : self.calculate_simple_case()

	def calculate_collisions(self):
		groups = self.get_groups()
		islands = self.get_islands(groups)

		for island in islands:

			all_permutations = []
			for i in range(1,len(island)+1):
		   		all_permutations.extend(list(itertools.combinations(island,i)))

		   	all_combinations = []
		   	for i in all_permutations:
		   		all_combinations.extend(list(itertools.permutations(i)))

		   	for combination in all_combinations:
		   		assert(len(combination) > 0)
		   		combination = set(combination)
		   		current = combination.pop()
		   		if not combination:
		   			if current.is_determined():
		   				self.mines_found = self.mines_found.union(current.tiles)
		   		else:
		   			while(combination):
		   				element = combination.pop()
		   				if element.issubset(current):
		   					current.remove_from_group(element)
		   					if current.is_determined():
		   						self.mines_found = self.mines_found.union(current.tiles)

	def calculate_safe_squares(self):
		for x in self.get_groups():
			mines_found_in_group = x.tiles.intersection(self.mines_found)
			if len(mines_found_in_group) == x.mines:
				safe_to_mark_in_group = x.tiles.difference(mines_found_in_group)
				self.safe_to_mark = self.safe_to_mark.union(safe_to_mark_in_group)

	# Not sure if this is ok:
	def calculate_based_on_probabilities(self):
		probabilities = {}
		safe_unmarked = [y for y in self.grid.unmarked() if y not in self.mines_found]
		for x in safe_unmarked:
			probabilities[x] = float(self.grid.max_mines - len(self.mines_found)) / float(len(safe_unmarked))
		for x in self.get_groups():
			for y in x.tiles:
				group_probability = float(x.mines) / float(len(x.tiles))
				if group_probability > probabilities[y]:
					probabilities[y] = group_probability
		sorted_prob = sorted(probabilities.items(), key=operator.itemgetter(1))
		
		if sorted_prob:
			return sorted_prob[0][0]
		else:
			return random.choice(list(self.grid.unmarked()))

	def play(self):
		self.grid.printgrid()
		end = 0
		self.grid.mark(4,4)
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
			return 1

	def get_best_option_to_mark(self):

		# This is necessary because when we mark a 0, then automatically surrounding tiles are marked
		# and the algorithm is not informed
		for x in self.grid.marked:
			if x in self.safe_to_mark: self.safe_to_mark.remove(x)

		if self.safe_to_mark:
			return self.safe_to_mark.pop(), self.mines_found
		else:
			progress = True
			while progress:
				mines_beginning = len(self.mines_found)
				safe_beginning = len(self.safe_to_mark)
				self.calculate()
				mines_end = len(self.mines_found)
				safe_end = len(self.safe_to_mark)
				progress = (mines_beginning != mines_end) or (safe_beginning != safe_end)
		if self.safe_to_mark:
			return self.safe_to_mark.pop(), self.mines_found
		else:
			return self.calculate_based_on_probabilities(), self.mines_found
	# ---------------------------------------------------------------
	# Helpers
	# ---------------------------------------------------------------
	#def play(self):
	#	self.grid.printgrid()
	#	self.grid.mark(4,4)
	#	self.grid.printgrid(-1, self.mines_found)
	#	self.get_groups()
	#	return 1
	



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

	island = [1,2,3]

	victories = 0
	how_many = 100
	for x in range(100):
		g = grid(w,h,m)
		b = brute_ai(g)
		if b.play() : victories += 1

	print victories / float(how_many)

	#human_game(grid)


	#g = grid(w,h,m)
	#brute_ai(g).play()
	#human_game(g)

	