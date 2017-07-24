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

# A simple minesweeper console game with solver

import itertools, operator, random, copy, time, sys	

debug = 0 # 0 for no extra info, 1 for some info, 2 for much more info

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

		to_mark = set()
		to_mark.add((x,y))

		while to_mark:

			current = to_mark.pop()
			x = current[0]
			y = current[1]

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
								#self.mark_i(z)
								to_mark.add((z / self.width, z % self.width))

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
		print "Still " + str(self.max_mines - len(mines_found)) + " mines to be found from " + str(self.max_mines)
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
# Algorithmical solver
# TODO: improve guessing based on probabilities
# TODO: use mines rest information for calculations, specially at the end
# --------------------------------------------------------------------------------------------------------

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
			possibilities_to_mark = grid.surrounding_possibilities_to_mark_i(tile) # Unmarked surrounding
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
		def intersection(self, group):
			return self.tiles.intersection(group)
		def difference(self, group):
			return self.tiles.difference(group)
		# Overwrite print operators
		def __str__(self):
			return str(self.tiles) + "--> " + str(self.mines)
		def __repr__(self):
			return self.__str__()
		def __hash__(self):
			return hash((frozenset(self.tiles), self.mines))
		def __eq__(self, other):
			return (self.tiles, self.mines) == (other.tiles, other.mines)

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
	# Duplicates are deleted to speed up calculations
	def get_islands(self, groups):
		islands = []
		for x in groups:
			island = set()
			island.add(x)
			for y in groups:
				if x.touchs(y):
					island.add(y)
			islands.append(frozenset(island))
		#print len(set(islands)), len(islands)
		#raw_input("Await")
		return islands

    # ---------------------------------------------------------------
	# Class entry point
	# ---------------------------------------------------------------
	def __init__(self, grid, debug = False):
		self.grid = grid
		self.mines_found = set()
		self.safe_to_mark = set()
		self.debug = debug
	# ---------------------------------------------------------------
	# Logic
	# ---------------------------------------------------------------
	def calculate(self):
		progress = -1
		origin = len(self.safe_to_mark) + len(self.mines_found)
		while (origin != progress):
			origin = len(self.safe_to_mark) + len(self.mines_found)
			# Calculate easy determined mines in groups
			# This is covered in calculate_collisions, but calculating
			# simple cmbinations first speed up the algorithm
			self.calculate_simple_case()
			self.calculate_safe_squares()
			# Calculate complex combinations
			# Basically we get all possible sorted combinations for each islands
			# and then we check if the combination determines mines
			self.calculate_collisions()
			self.calculate_safe_squares()
			progress = len(self.safe_to_mark) + len(self.mines_found)
		# Speed up, only as last resource:
		if not self.safe_to_mark:
			self.calculate_brute_force()
			self.calculate_safe_squares()
		
	def calculate_simple_case(self):
		#progress = False
		groups = self.get_groups()
		for group in groups:
			if group.is_determined(): # If there are the same number of mines and tiles in the group
				self.mines_found = self.mines_found.union(group.tiles)
				#progress = True
			if group.mines == 0:
		   		self.safe_to_mark = self.safe_to_mark.union(group.tiles)
		#if progress : self.calculate_simple_case()

	def calculate_collisions(self):
		groups = self.get_groups()
		islands = self.get_islands(groups)

		progress = len(self.safe_to_mark) + len(self.mines_found)
		for island in islands:

			if self.debug : print "Calculating all combinations and sortering... ",

			all_combinations = []
			for i in range(1,len(island)+1):
		   		all_combinations.extend(list(itertools.combinations(island,i)))

		   	all_sorted_combinations = []
		   	for i in all_combinations:
		   		li = list(i)
		   		li.sort(lambda x,y: cmp(len(x.tiles), len(y.tiles)))
		   		all_sorted_combinations.append(li)

			if self.debug : print str(len(all_sorted_combinations)) + " found"

			# TODO: this is the part of the code which have the biggest impact in performance:

		   	for combination in all_sorted_combinations:
		   		#assert(len(combination) > 0)

		   		combination = list(combination)
		   		current = combination.pop()
		   		if not combination:
		   			if current.is_determined():
		   				self.mines_found = self.mines_found.union(current.tiles)
		   			if current.mines == 0:
		   				self.safe_to_mark = self.safe_to_mark.union(current.tiles)
		   		else:
		   			while(combination):
		   				element = combination.pop()

		   				#if current.intersection(element)
		   				#if len(element.difference(current)) <= element.mines:

		   				if element.issubset(current):
		   					current.remove_from_group(element)
		   					if current.is_determined():
		   						self.mines_found = self.mines_found.union(current.tiles)
		   					if current.mines == 0:
		   						self.safe_to_mark = self.safe_to_mark.union(current.tiles)


		   	if progress != len(self.safe_to_mark) + len(self.mines_found) : return

	def calculate_brute_force(self):
		groups = self.get_groups()
		frontiers = set() # Frontiers are those unmarked squares touching a marked square and not found as mines
		for g in groups:
			for t in g.tiles:
				frontiers.add(t)
		combinations = []
		self.subsets(frontiers, set(), combinations) # Returns all valid combinations
		if combinations:
			lengths = [len(x) for x in combinations]
			max_mines = max(lengths) + len(self.mines_found)
			min_mines = min(lengths) + len(self.mines_found)
			assert self.grid.max_mines >= min_mines
			assert self.grid.max_mines >= max_mines
			if self.grid.max_mines - min_mines == 0:
				# We know unmarked not frontiers are safe
				for x in [y for y in self.grid.unmarked() if (y not in frontiers) and (y not in self.mines_found)]:
					self.safe_to_mark.add(x)
			# Those mines who appears in all possible combinations are sure mines:
			inter = combinations[0]
			for c in combinations:
				inter = inter.intersection(c)
			self.mines_found = self.mines_found.union(inter) 
			# Safe positions will be calculated later


	# Returns true if a given combination of mines is valid
	def is_valid(self, combination):
		if len(combination) + len(self.mines_found) > self.grid.max_mines: return False
		for x in self.grid.marked:
			mark_possibilities = set(self.grid.surrounding_possibilities_to_mark_i(x))
			mines_surrounding = mark_possibilities.intersection(self.mines_found.union(combination))
			if len(mines_surrounding) != self.grid.mines_surrounding_i(x): return False
		return True

	def it_may_be_ok(self, combination):
		if len(combination) + len(self.mines_found) > self.grid.max_mines: return False
		for x in self.grid.marked:
			mark_possibilities = set(self.grid.surrounding_possibilities_to_mark_i(x))
			mines_surrounding = mark_possibilities.intersection(self.mines_found.union(combination))
			if len(mines_surrounding) > self.grid.mines_surrounding_i(x): return False
		return True

	def subsets(self, rest, combination, combinations):
		if self.it_may_be_ok(combination):
			if not rest:
				if self.is_valid(combination):
					combinations.append(copy.deepcopy(combination))
			else:
				#crest1 = copy.deepcopy(rest)
				#crest2 = copy.deepcopy(rest)
				#cc1 = copy.deepcopy(combination)
				#cc2 = copy.deepcopy(combination)
				
				
				x = rest.pop()
				combination.add(x)
				self.subsets(rest, combination, combinations)
				combination.remove(x)
				self.subsets(rest, combination, combinations)
				rest.add(x)



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

		# First turm, random choice
		if not self.grid.marked:
			return random.choice(list(self.grid.unmarked())), self.mines_found

		if self.safe_to_mark:
			return self.safe_to_mark.pop(), self.mines_found
		else:
			keep_on = True
			while keep_on:
				progress = len(self.safe_to_mark) + len(self.mines_found)
				self.calculate()
				keep_on = len(self.safe_to_mark) + len(self.mines_found) != progress
		if self.safe_to_mark:
			return self.safe_to_mark.pop(), self.mines_found
		else:
			return self.calculate_based_on_probabilities(), self.mines_found

# --------------------------------------------------------------------------------------------------------
# Human game
# --------------------------------------------------------------------------------------------------------

class human_game:

	def __init__(self, grid):
		self.grid = grid

	def play(self):
		self.grid.printgrid()
		end = 0
		while (end == 0):
			error = True
			i = j = 0
			while error:
				error = False
				try:
					i,j = raw_input("Please enter square as x y: ").split()
				except:
					print "Wrong selection."
					error = True
			i = int(i)
			j = int(j)
			if self.grid.inside(i,j):
				end = self.grid.mark(i,j)
			self.grid.printgrid()
		if end == 1:
			print "you loose!"
		else:
			print "you win!"

# --------------------------------------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------------------------------------

# Helper for allowing running on Pypy
try:
	from termcolor import colored
except:
	def colored(x,y):
		return x


if __name__ == '__main__':

	#try:
	w = int(raw_input("Please enter the width of the grid: "))
	h = int(raw_input("Please enter the height of the grid: "))
	m = int(raw_input("Please enter the number of mines: "))

	print "Type H for human game"
	print "Type M for computer game"
	print "Type B for benchmark based on 100 games"
	who_plays = raw_input("Your selection: ").upper()

	if who_plays == "H":
		g = grid(w,h,m)
		h = human_game(g)
		h.play()
	elif who_plays == "M" or who_plays == "B":
		victories = 0
		how_many = 1
		if who_plays == "B" : how_many = 100
		for x in range(how_many):
			g = grid(w,h,m)
			b = brute_ai(g)
			if b.play() : victories += 1
			print "Victory rate: " + str(victories / float(x + 1)) + " by " + str(x + 1) + " games"
			if (debug): time.sleep(1)
	#except Exception as e:
	#	print "Something went wrong! Bye!"
	#	if (debug): print e