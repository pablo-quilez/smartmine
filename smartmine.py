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

# This class contains the board information
class grid:

	def __init__(self, width, height, mines):
		self.width = width
		self.height = height
		self.mines  = set(random.sample(range(width*height), mines)) # Mine positions saved as a set
		self.marked = set() 										 # Already marked squares

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
		if self.is_mine(x,y):
			return 1
		else:
			self.marked.add(self.index(x,y))
			if len(self.marked) + len(self.mines) == self.width * self.height:
				return 2
			else:
				return 0

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
	def printgrid(self):
		for x in range(self.height):
			for y in range(self.width):
				if self.index(x,y) in self.marked:
					print colored(self.mines_surrounding(x,y),"green"),
				else:
					print colored("X","white"),
			print ""
		print "-----------------------"

	# ---------------------------------------------------
	# Private / Helper functions
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

	def index(self,x,y):
		assert self.inside(x,y)
		return x * self.width + y

# --------------------------------------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------------------------------------

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

	grid = grid(w,h,m)
	human_game(grid)