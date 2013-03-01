# coding=utf-8

#import os, pygame, time, random, uuid
import pygame
import os
import uuid


class Timer(object):
	def __init__(self):
		self.timers = []

	def add(self, interval, f, repeat = -1):
		options = {
			"interval"	: interval,
			"callback"	: f,
			"repeat"		: repeat,
			"times"			: 0,
			"time"			: 0,
			"uuid"			: uuid.uuid4()
		}
		self.timers.append(options)

		return options["uuid"]

	def destroy(self, uuid_nr):
		for timer in self.timers:
			if timer["uuid"] == uuid_nr:
				self.timers.remove(timer)
				return

	def update(self, time_passed):
		for timer in self.timers:
			timer["time"] += time_passed
			if timer["time"] > timer["interval"]:
				timer["time"] -= timer["interval"]
				timer["times"] += 1
				if timer["repeat"] > -1 and timer["times"] == timer["repeat"]:
					self.timers.remove(timer)
				else:
					timer["callback"]()

	def inc_interval(self,uuid,interval):
		for timer in self.timers:
			if timer["uuid"] == uuid:
				timer["interval"] += interval


class Map():
	(TILE_EMPTY, TILE_BRICK, TILE_STEEL, TILE_WATER, TILE_GRASS, TILE_FROZE) = range(6)
	TILE_SIZE = 16

	def __init__(self, castle, level_nr = None):
		global sprites

		tile_images = [
			pygame.Surface((8*2, 8*2)),
			sprites.subsurface(48*2, 64*2, 8*2, 8*2),
			sprites.subsurface(48*2, 72*2, 8*2, 8*2),
			sprites.subsurface(56*2, 72*2, 8*2, 8*2),
			sprites.subsurface(64*2, 64*2, 8*2, 8*2),
			sprites.subsurface(72*2, 64*2, 8*2, 8*2),
			sprites.subsurface(64*2, 72*2, 8*2, 8*2)
		]
		self.tile_empty = tile_images[0]
		self.tile_brick = tile_images[1]
		self.tile_steel = tile_images[2]
		self.tile_grass = tile_images[3]
		self.tile_water = tile_images[4]
		self.tile_water1= tile_images[4]
		self.tile_water2= tile_images[5]
		self.tile_froze = tile_images[6]

		self.mapr = []

		level_nr = 0 if level_nr == None else level_nr%35
		'''
		if level_nr == 0:
			level_nr = 35
		'''

		self.castle = castle

		self.loadLevel(level_nr)
		self.updateObstacleRects()

		gtimer.add(400, lambda :self.toggleWaves())

	def hitTile(self, pos, power = 1, sound = False):
		"""
			Hit the tile
			@param pos Tile's x, y in px
			@return True if bullet was stopped, False otherwise
		"""

		#global play_sounds, sounds

		for tile in self.mapr:
			if tile[1].topleft == pos:
				if tile[0] == self.TILE_BRICK:
					'''
					if play_sounds and sound:
						sounds["brick"].play()
					'''
					self.mapr.remove(tile)
					self.updateObstacleRects()
					return True
				elif tile[0] == self.TILE_STEEL:
					'''
					if play_sounds and sound:
						sounds["steel"].play()
					'''
					if power == 2:
						self.mapr.remove(tile)
						self.updateObstacleRects()
					return True
				else:
					return False

	def loadLevel(self, level_nr = 1):
		filename = "levels/"+str(level_nr)
		if (not os.path.isfile(filename)):
			return False
		level = []
		f = open(filename, "r")
		data = f.read().split("\n")
		self.mapr = []
		x, y = 0, 0
		for row in data:
			for ch in row:
				if ch == "#":
					self.mapr.append((self.TILE_BRICK, pygame.Rect(x, y, self.TILE_SIZE, self.TILE_SIZE)))
				elif ch == "@":
					self.mapr.append((self.TILE_STEEL, pygame.Rect(x, y, self.TILE_SIZE, self.TILE_SIZE)))
				elif ch == "~":
					self.mapr.append((self.TILE_WATER, pygame.Rect(x, y, self.TILE_SIZE, self.TILE_SIZE)))
				elif ch == "%":
					self.mapr.append((self.TILE_GRASS, pygame.Rect(x, y, self.TILE_SIZE, self.TILE_SIZE)))
				elif ch == "-":
					self.mapr.append((self.TILE_FROZE, pygame.Rect(x, y, self.TILE_SIZE, self.TILE_SIZE)))
				x += self.TILE_SIZE
			x = 0
			y += self.TILE_SIZE
		return True

	def toggleWaves(self):
		""" Toggle water image """
		if self.tile_water == self.tile_water1:
			self.tile_water = self.tile_water2
		else:
			self.tile_water = self.tile_water1

	def draw(self, tiles = None):
		""" Draw specified map on top of existing surface """

		global screen

		if tiles == None:
			tiles = [self.TILE_BRICK, self.TILE_STEEL, self.TILE_WATER, self.TILE_GRASS, self.TILE_FROZE]

		for tile in self.mapr:
			if tile[0] in tiles:
				if tile[0] == self.TILE_BRICK:
					screen.blit(self.tile_brick, tile[1].topleft)
				elif tile[0] == self.TILE_STEEL:
					screen.blit(self.tile_steel, tile[1].topleft)
				elif tile[0] == self.TILE_WATER:
					screen.blit(self.tile_water, tile[1].topleft)
				elif tile[0] == self.TILE_FROZE:
					screen.blit(self.tile_froze, tile[1].topleft)
				elif tile[0] == self.TILE_GRASS:
					screen.blit(self.tile_grass, tile[1].topleft)

	def updateObstacleRects(self):
		""" Set self.obstacle_rects to all tiles' rects that players can destroy
		with bullets """

		#global castle

		self.obstacle_rects = [self.castle.rect]

		for tile in self.mapr:
			if tile[0] in (self.TILE_BRICK, self.TILE_STEEL, self.TILE_WATER):
				self.obstacle_rects.append(tile[1])

	def buildFortress(self, tile):
		""" Build walls around castle made from tile """

		positions = [
			(11*self.TILE_SIZE, 23*self.TILE_SIZE),
			(11*self.TILE_SIZE, 24*self.TILE_SIZE),
			(11*self.TILE_SIZE, 25*self.TILE_SIZE),
			(14*self.TILE_SIZE, 23*self.TILE_SIZE),
			(14*self.TILE_SIZE, 24*self.TILE_SIZE),
			(14*self.TILE_SIZE, 25*self.TILE_SIZE),
			(12*self.TILE_SIZE, 23*self.TILE_SIZE),
			(13*self.TILE_SIZE, 23*self.TILE_SIZE)
		]

		obsolete = []

		for i, rect in enumerate(self.mapr):
			if rect[1].topleft in positions:
				obsolete.append(rect)
		for rect in obsolete:
			self.mapr.remove(rect)

		for pos in positions:
			self.mapr.append((tile, pygame.Rect(pos, [self.TILE_SIZE, self.TILE_SIZE])))

		self.updateObstacleRects()


class Bullet():
	(DIR_UP, DIR_LEFT, DIR_DOWN, DIR_RIGHT) = range(4)

	(STATE_REMOVED, STATE_ACTIVE, STATE_EXPLODING) = range(3)

	def __init__(self,position, direction,map):
		global sprites

		self.image = sprites.subsurface(75*2, 74*2, 3*2, 4*2)
		self.direction = direction

		if direction == self.DIR_UP:
			self.rect = pygame.Rect(position[0] + 11, position[1] - 8, 6, 8)
		elif direction == self.DIR_RIGHT:
			self.image = pygame.transform.rotate(self.image, 270)
			self.rect = pygame.Rect(position[0] + 26, position[1] + 11, 8, 6)
		elif direction == self.DIR_DOWN:
			self.image = pygame.transform.rotate(self.image, 180)
			self.rect = pygame.Rect(position[0] + 11, position[1] + 26, 6, 8)
		elif direction == self.DIR_LEFT:
			self.image = pygame.transform.rotate(self.image, 90)
			self.rect = pygame.Rect(position[0] - 8 , position[1] + 11, 8, 6)

		self.state = self.STATE_ACTIVE
		self.map = map

	
	def draw(self):
		""" draw bullet """
		global screen
		if self.state == self.STATE_REMOVED:
			return
		screen.blit(self.image, self.rect.topleft)

	def move(self):
		if self.state == self.STATE_REMOVED:
			return
		if self.direction == self.DIR_LEFT:
			self.rect.left -= 8
			if self.rect.left < 0:
				self.destroy()
		elif self.direction == self.DIR_RIGHT:
			self.rect.left += 8
			if self.rect.left+13 > 480:
				self.destroy()
		elif self.direction == self.DIR_UP:
			self.rect.top -= 8
			if self.rect.top < 0:
				self.destroy()
		elif self.direction == self.DIR_DOWN:
			self.rect.top += 8
			if self.rect.top+15 > 416:
				self.destroy()

		castle = self.map.castle
		if self.rect.colliderect(castle.rect):
			castle.destroy()
			self.destroy()
			return

		rects = self.map.obstacle_rects
		collisions = self.rect.collidelistall(rects)
		if collisions != []:
			for i in collisions:
				if self.map.hitTile(rects[i].topleft):
					self.destroy()

	def destroy(self):
		self.state = self.STATE_REMOVED

class Tank():
	(DIR_UP,DIR_LEFT , DIR_DOWN, DIR_RIGHT) = range(4)
	def __init__(self,map):
		global sprites
		self.image_up = sprites.subsurface(0,0,13*2,15*2) 
		self.image = self.image_up
		self.image_left = pygame.transform.rotate(self.image, 90*1)
		self.image_down = pygame.transform.rotate(self.image, 90*2)
		self.image_right = pygame.transform.rotate(self.image, 90*3)
		self.images = [self.image_up,self.image_left,self.image_down,self.image_right]

		self.direction = self.DIR_UP

		#self.rect = self.image.get_rect()
		self.rect = pygame.Rect(16*8, 16*24, 26,26)
		self.x_s = 0
		self.y_s = 0

		self.map = map
		self.speed = 2 

	def fire(self):
		bullet = Bullet( self.rect.topleft, self.direction, self.map)
		return bullet

	def rotate(self, direction):
		self.image = self.images[direction]
		self.direction = direction

	def move(self, direction):
		if (self.direction!= direction):
			self.rotate(direction)

		if direction == self.DIR_UP:
			new_position = [self.rect.left, self.rect.top - self.speed]
			if new_position[1] < 0:
				return
		elif direction == self.DIR_RIGHT:
			new_position = [self.rect.left + self.speed, self.rect.top]
			if new_position[0] > (416 - 26):
				return
		elif direction == self.DIR_DOWN:
			new_position = [self.rect.left, self.rect.top + self.speed]
			if new_position[1] > (416 - 26):
				return
		elif direction == self.DIR_LEFT:
			new_position = [self.rect.left - self.speed, self.rect.top]
			if new_position[0] < 0:
				return

		player_rect = pygame.Rect(new_position, [26, 26])

		if player_rect.collidelist(self.map.obstacle_rects) != -1:
			return

		self.rect.topleft = new_position



	def draw(self):
		global screen

		screen.blit(self.image,self.rect.topleft)

class Castle():
	""" Player's castle/fortress """

	(STATE_STANDING, STATE_DESTROYED, STATE_EXPLODING) = range(3)

	def __init__(self):

		global sprites

		# images
		self.img_undamaged = sprites.subsurface(0, 15*2, 16*2, 16*2)
		self.img_destroyed = sprites.subsurface(16*2, 15*2, 16*2, 16*2)
		self.image = self.img_undamaged

		# init position
		self.rect = pygame.Rect(12*16, 24*16, 32, 32)
		self.active = True

		# start w/ undamaged and shiny castle
		#self.rebuild()

	def draw(self):
		""" Draw castle """
		global screen

		screen.blit(self.image, self.rect.topleft)

		'''
		if self.state == self.STATE_EXPLODING:
			if not self.explosion.active:
				self.state = self.STATE_DESTROYED
				del self.explosion
			else:
				self.explosion.draw()
		'''

	def destroy(self):
		""" Destroy castle """
		#self.state = self.STATE_EXPLODING
		#self.explosion = Explosion(self.rect.topleft)
		self.image = self.img_destroyed
		self.active = False

	
class Game():
	(DIR_UP,DIR_LEFT , DIR_DOWN, DIR_RIGHT) = range(4)
	def __init__(self):
		global screen
		pygame.init()
		pygame.display.set_caption("Battle City")

		size = width, height = 480, 416
		screen = pygame.display.set_mode(size)
		self.clock = pygame.time.Clock()
		self.black = [0,0,0]

		self.pressed = [False]*4

		self.bullet = None
		self.castle = Castle()
		self.map = Map(self.castle)
		self.tank = Tank(self.map)

	def draw(self):
		screen.fill(self.black)

		self.map.draw()
		done = self.controller()
		self.tank.draw()
		self.castle.draw()
		if self.bullet:
			self.bullet.draw()

		pygame.display.flip()

		return done

	def controller(self):
		time_passed = self.clock.tick(40)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				return False
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_LEFT:
					self.pressed[self.DIR_LEFT] = True
				elif event.key == pygame.K_RIGHT:
					self.pressed[self.DIR_RIGHT] = True
				elif event.key == pygame.K_UP:
					self.pressed[self.DIR_UP] = True
				elif event.key == pygame.K_DOWN:
					self.pressed[self.DIR_DOWN] = True
				elif event.key == pygame.K_SPACE:
					self.bullet = self.tank.fire()
				elif event.key == pygame.K_q:
					return False

			elif event.type == pygame.KEYUP:
				if event.key == pygame.K_LEFT:
					self.pressed[self.DIR_LEFT] = False
				elif event.key == pygame.K_RIGHT:
					self.pressed[self.DIR_RIGHT] = False
				elif event.key == pygame.K_UP:
					self.pressed[self.DIR_UP] = False
				elif event.key == pygame.K_DOWN:
					self.pressed[self.DIR_DOWN] = False
		if self.pressed[self.DIR_UP]:
			self.tank.move(self.DIR_UP)
		elif self.pressed[self.DIR_LEFT]:
			self.tank.move(self.DIR_LEFT)
		elif self.pressed[self.DIR_DOWN]:
			self.tank.move(self.DIR_DOWN)
		elif self.pressed[self.DIR_RIGHT]:
			self.tank.move(self.DIR_RIGHT)

		if self.bullet:
			self.bullet.move()

		gtimer.update(time_passed)

		return True

	def run(self):
		pass


if __name__ == "__main__":
	gtimer = Timer()
	screen = None
	sprites = pygame.transform.scale(pygame.image.load("images/sprites.gif"), [192, 256])
	g=Game()
	flag = True
	while flag:
		flag = g.draw()
