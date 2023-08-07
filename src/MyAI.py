# ==============================CS-199==================================
# FILE:			MyAI.py
#
# AUTHOR: 		Justin Chung
#
# DESCRIPTION:	This file contains the MyAI class. You will implement your
#				agent in this file. You will write the 'getAction' function,
#				the constructor, and any additional helper functions.
#
# NOTES: 		- MyAI inherits from the abstract AI class in AI.py.
#
#				- DO NOT MAKE CHANGES TO THIS FILE.
# ==============================CS-199==================================

from AI import AI
from Action import Action
import queue
import random


class MyAI( AI ):

	def __init__(self, rowDimension, colDimension, totalMines, startX, startY):

		self.dimensions = rowDimension
		self.coldimensions = colDimension
		# how many mines in total
		self.mines = totalMines
		self.blocks = (colDimension * rowDimension) - 1
		# a (rowDimension * colDimension) game board
		self.map = [["*" for i in range(rowDimension)] for j in range(colDimension)]
		# how many uncovered block currently need to be flag
		self.flag = []
		#how many mines we already flagged
		self.flagged = 0
		#list of covered block that is yet unchecked but guaranteed to be safe
		self.safe_covered = []
		#a pair that stores the current block location
		self.current = (startX, startY)
		self.double_check = []
		self.finished_double_check = []
		#bool value indicates we got all mines and need to finish up
		self.finished = False


	def find_covered_neighbor(self, row, col) -> list:
		neighbors = []
        # valid left neighbor
		if (row-1 >= 0):
			if (self.map[row-1][col] == "*"):
				neighbors.append((row-1, col))
        # valid top left neighbor
		if ( (row-1 >= 0 and col+1 <= self.dimensions-1)):
			if (self.map[row-1][col+1] == "*"):
				neighbors.append((row-1, col+1))
        # valid top neighbor
		if (col+1 <= self.dimensions-1):
			if (self.map[row][col+1] == "*"):
				neighbors.append((row, col+1))
        # valid right neighbor
		if (row+1 <= self.coldimensions-1):
			if (self.map[row+1][col] == "*"):
 				neighbors.append((row+1, col))
        # valid top right neighbor
		if ( (row+1 <= self.coldimensions-1) and (col+1 <= self.dimensions-1) ):
			if (self.map[row+1][col+1] == "*"):
				neighbors.append((row+1, col+1))
        # valid bottom neighbor
		if (col-1 >= 0):
			if (self.map[row][col-1] == "*"):
				neighbors.append((row, col-1))
        # valid bottom right neighbor
		if (col-1 >= 0 and row+1 <= self.coldimensions-1):
			if (self.map[row+1][col-1] == "*"):
				neighbors.append((row+1, col-1))
        # valid bottom left neighbor
		if (col-1 >= 0 and row-1 >= 0):
			if (self.map[row-1][col-1] == "*"):
				neighbors.append((row-1, col-1))

		return neighbors

	def find_next_covered(self) -> (int, int):
		found = -1
		for i in range(len(self.safe_covered)):
			x, y = self.safe_covered[i]
			if (self.map[x][y] == "*"):
				found = i
				break
		
		if (found == -1):
			#if we fail to find one unchecked
			self.safe_covered = []
			return (-1, -1)
		else:
			row,col = self.safe_covered[found]
			self.safe_covered = self.safe_covered[(found+1):]
			return (row, col)

	def find_next_double_check(self) -> (int, int, int):
		found = -1
		for i in range(len(self.double_check)):
			x, y, n = self.double_check[i]
			nb = self.find_covered_neighbor(x, y)

			if (len(nb) > 0):
				found = i
				self.double_check = self.double_check[(found+1):]
				return (x, y, n)
	
		self.double_check = []
		return (-1, -1, -1)

	#-1 is err(try again), 0 is UNCOVER, 1 is FLAG
	def advanced_check(self, x, y, n) -> int:
		nb = self.find_covered_neighbor(x, y)
		#find all flagged mine for neighbour
		discovered_mine = self.find_mine(x, y)
		
		# if neighbors are safe or mine, take action
		if (len(discovered_mine) == n):
			self.safe_covered += nb
			return 0
		elif (len(nb) + len(discovered_mine) == n):
			self.flag += nb
			for v1, v2 in nb:
				self.map[v1][v2] = -1
				self.flagged += 1	
			return 1
		else:
			return -1

	def getAction(self, number: int) -> "Action Object":
		#print("start----------------------------")
		#update our map each turn
		row, col = self.current
		self.map[row][col] = number
		#print("checking for end----------------------------")

		if (self.finished):
			#print("entered finishing")
			if (self.safe_covered):
				x, y = self.safe_covered[0]
				self.safe_covered = self.safe_covered[1:]
				self.current = (x, y)
				return Action(AI.Action.UNCOVER, x, y)
			else:
				return Action(AI.Action.LEAVE)
		
		if (self.blocks == self.mines):
			#print("leave when blocks are uncovered")
			return Action(AI.Action.LEAVE)
		
		elif (self.mines == self.flagged):
			#print("mine == flagged")
			self.safe_covered = []
			self.finished = True
			for i in range(self.coldimensions):
				for j in range(self.dimensions):
					if (self.map[i][j] == "*"):
						self.safe_covered.append((i,j))
			#print("passed")
			return self.getAction(number)
		
		
		
		

		#Rule of thumb algorithms 
		else:
			#print("rule of thumb----------------------------")	
			x, y = self.current
			neignbour = self.find_covered_neighbor(row, col)
			found_mine = self.find_mine(x, y)
			if (neignbour):
				if (number == 0):
					self.safe_covered = neignbour + self.safe_covered
				elif ((number - len(found_mine)) == len(neignbour)):
					for v1, v2 in neignbour:
						self.map[v1][v2] = -1
					self.flag = self.flag + neignbour
					self.flagged += len(neignbour)
				elif (number > 0):
					x, y = self.current
					num = number
					self.double_check.append((x, y, num))

			if (self.safe_covered):
				#print("#start uncover----------------------------")
				x, y = self.find_next_covered()
				if (x != -1):
					self.current = (x, y)
					self.blocks -= 1
					return Action(AI.Action.UNCOVER, x, y)
			
			if (self.double_check):
				#print("double check----------------------------")	
				#result = self.check_double()
				guess = False 
				while (True):
					result = self.check_double()
					self.double_check = self.finished_double_check
					#things could be revised
					if (self.mines == self.flagged):
						return self.getAction(number)
					if (result == -1):
						guess = True
						break
					elif (result == 0):
						break
				
				if(guess):
					#print("GUESSING________________________")
					# key: (x,y), value: sum of probabilities
					prob = dict()
					for v1, v2, v3 in self.double_check:
						nb = self.find_covered_neighbor(v1, v2)
						mines = self.find_mine(v1, v2)
						result = (v3 - len(mines)) / len(nb)
						for value in nb:
							if value not in prob:
								prob[value] = result
							else:
								prob[value] += result
					#tiles w/ lowest probability are safe
					
					#something we can change here: the program would leave when a block is surrounded by mines
					if (prob):
						mins = min(prob.values())
						min_nb = [vs for vs in prob if prob[vs] == mins]
						random.shuffle(min_nb)
						self.safe_covered.append(min_nb[0])
					else:
						#print("surround by mine!")
						self.finished = True
						return self.getAction(number)

					

				if (self.safe_covered):
					#print("uncovering after guess!")
					x, y = self.find_next_covered()
					if (x != -1):
						self.current = (x, y)
						self.blocks -= 1
						return Action(AI.Action.UNCOVER, x, y)
				
				
					
					
				
			return Action(AI.Action.LEAVE)



	def check_double(self) -> int:
		self.finished_double_check = []
		prev_double_check = self.double_check
		x, y, num = (0, 0, 0)
		flagged_something = 0
		while (x != -1):
			
			x, y, num = self.find_next_double_check()
			if (x != -1):
				ints = self.advanced_check(x, y, num)
				if (ints == -1):
					self.finished_double_check.append((x, y, num))
				elif (ints == 1):
					flagged_something = 1
		if (len(self.finished_double_check) == len(prev_double_check) and self.finished_double_check):
			return -1
		elif (self.safe_covered):
			return 0
		elif (flagged_something == 1):
			return 1
		else:
			return -1


	def find_mine(self, x, y) -> list:
		discovered_mine = []
		for i in range(-1, 2):
			for j in range(-1, 2):
				nb_x, nb_y = x + i, y + j
				if (0 <= nb_x <= self.coldimensions-1) and (0 <= nb_y <= self.dimensions-1):
					if self.map[nb_x][nb_y] == -1:
						discovered_mine.append((nb_x, nb_y))

		return discovered_mine