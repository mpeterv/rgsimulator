#!/usr/bin/python
import Tkinter
import tkSimpleDialog
import argparse
import game
import ast
import sys
import traceback
import os
import rg
import settings
from settings import AttrDict
import tkFont

def mid(l1, l2):
	return (int((l1[0]+l2[0]) / 2), int((l1[1]+l2[1]) / 2))

class SimulatorUI:
	def __init__(self, settings, map, player, player2):
		self.settings = settings
		self.map = map
		self.player = player
		self.player2 = player2

		self.center = rg.CENTER_POINT

		self.square_size = 40
		self.fill_color = "#FFF"
		self.obstacle_fill_color = "#555"
		self.enemy_fill_color = "#F00"
		self.teammate_fill_color = "#0F0"
		self.border_color = "#333"
		self.selection_border_color = "#FF0"
		self.move_arrow_color = "#00F"
		self.attack_arrow_color = "#000"

		self.map_width = settings.board_size
		self.map_height = settings.board_size
		self.width = self.square_size*self.map_width
		self.height = self.square_size*self.map_height

		self.root = Tkinter.Tk()
		self.root.resizable(0, 0)
		self.setTitle("Robot Game Simulator")

		self.turn_label = Tkinter.Label(self.root, text = "")
		self.turn_label.pack()
		self.setTurn(1)

		self.canvas = Tkinter.Canvas(self.root, width = self.width, height = self.height)
		self.canvas.pack()

		self.squares = {}
		self.labels = {}
		self.actions = []
		for x in xrange(0, self.map_width):
			for y in xrange(0, self.map_height):
				coordinates = self.getSquareCoordinates((x, y))
				x1, y1 = coordinates[0]
				x2, y2 = coordinates[1]

				self.squares[(x, y)] = self.canvas.create_rectangle(
					x1, y1, x2, y2,
					fill = self.obstacle_fill_color if self.isObstacle((x, y)) else self.fill_color,
					outline = self.border_color,
					width = 1
				)
				self.labels[(x, y)] =  self.canvas.create_text(
					x1 + self.square_size/2, y1 + self.square_size/2,
					text = (x+1)*(y+1)-1 if x*y == 0 else "", # the most clever hack I've ever did
					font = "TkFixedFont", 
					fill = "#000"
				)

		self.selection = self.center
		selection_coordinates = self.getSquareCoordinates(self.selection)
		selection_x1, selection_y1 = selection_coordinates[0]
		selection_x2, selection_y2 = selection_coordinates[1]
		self.selection_square = self.canvas.create_rectangle(
			selection_x1, selection_y1, selection_x2, selection_y2,
			fill = "",
			outline = self.selection_border_color,
			width = 5
		)

		self.robots = []
		self.field = game.Field(settings.board_size)
		self.robot_id = 0

		# self.player

		self.root.bind("w", lambda ev: self.moveSelection((0, -1)))
		self.root.bind("a", lambda ev: self.moveSelection((-1, 0)))
		self.root.bind("s", lambda ev: self.moveSelection((0, 1)))
		self.root.bind("d", lambda ev: self.moveSelection((1, 0)))
		self.root.bind("<Up>", lambda ev: self.moveSelection((0, -1)))
		self.root.bind("<Left>", lambda ev: self.moveSelection((-1, 0)))
		self.root.bind("<Down>", lambda ev: self.moveSelection((0, 1)))
		self.root.bind("<Right>", lambda ev: self.moveSelection((1, 0)))

		self.root.bind("t", self.onEditTurn)
		self.root.bind("f", self.onAddTeammate)
		self.root.bind("e", self.onAddEnemy)
		self.root.bind("r", self.onRemove)
		self.root.bind("<Delete>", self.onRemove)
		self.root.bind("<BackSpace>", self.onRemove)
		self.root.bind("h", self.onEditHP)
		self.root.bind("<space>", self.onSimulate)
		self.root.bind("<Return>", self.onSimulate)

		# I am a dirty hack, fix me
		text_font = tkFont.nametofont("TkTextFont")
		text_font.configure(weight = "bold")

		self.root.mainloop()

	def getSquareCoordinates(self, loc):
		x, y = loc
		return (
			(self.square_size*x, self.square_size*y), 
			(self.square_size*(x + 1), self.square_size*(y + 1))
		)

	def isObstacle(self, loc):
		return loc in self.map['obstacle']

	def setSelection(self, loc):
		if not self.isObstacle(loc):
			selection_coordinates = self.getSquareCoordinates(loc)
			selection_x1, selection_y1 = selection_coordinates[0]
			selection_x2, selection_y2 = selection_coordinates[1]
			self.canvas.coords(self.selection_square, selection_x1, selection_y1, selection_x2, selection_y2)
			self.selection = loc

	def moveSelection(self, dloc):
		self.setSelection((self.selection[0] + dloc[0], self.selection[1] + dloc[1]))

	def setTitle(self, title):
		self.root.title(title)

	def setTurn(self, turn):
		self.turn = turn
		self.turn_label.config(text = "Turn %s" % self.turn)

	def setFill(self, loc, color):
		self.canvas.itemconfigure(self.squares[loc], fill = color)
	
	def setText(self, loc, text):
		self.canvas.itemconfigure(self.labels[loc], text = text)

	def onEditTurn(self, event):
		self.clearActions()
		new_turn = tkSimpleDialog.askinteger(
			"Edit turn", "Enter new turn", 
			parent = self.root, 
			initialvalue = self.turn,
			minvalue = 1,
			maxvalue = 100
		)
		if new_turn is not None:
			self.setTurn(new_turn)

	def updateSquare(self, loc):
		robot = self.getRobot(loc)
		if robot is None:
			self.setFill(loc, self.fill_color)
			self.setText(loc, "")
		else:
			if robot.player_id == 1:
				self.setFill(loc, self.teammate_fill_color)
			else:
				self.setFill(loc, self.enemy_fill_color)

			self.setText(loc, robot.hp)


	def onRemove(self, event):
		self.clearActions()
		if self.getRobot(self.selection) is not None:
			self.removeRobot(self.selection)

		self.updateSquare(self.selection)

	def onAddTeammate(self, event):
		self.clearActions()
		if self.getRobot(self.selection) is not None:
			self.removeRobot(self.selection)

		self.addRobot(self.selection, 1)
		self.updateSquare(self.selection)

	def onAddEnemy(self, event):
		self.clearActions()
		if self.getRobot(self.selection) is not None:
			self.removeRobot(self.selection)

		self.addRobot(self.selection, 0)
		self.updateSquare(self.selection)


	def onEditHP(self, event):
		self.clearActions()
		robot = self.getRobot(self.selection)
		if robot is not None:
			new_hp = tkSimpleDialog.askinteger(
				"Edit hp", "Enter new hp", 
				parent = self.root, 
				initialvalue = robot.hp,
				minvalue = 1,
				maxvalue = 50
			)
			if new_hp is not None:
				robot.hp = new_hp
				self.updateSquare(self.selection)


	def getRobotID(self):
		ret = self.robot_id
		self.robot_id += 1
		return ret

	def removeRobot(self, loc):
		self.robots.remove(self.field[loc])
		self.field[loc] = None

	def getRobot(self, loc):
		return self.field[loc]

	def addRobot(self, loc, player_id):
		robot_id = self.getRobotID()
		robot = game.InternalRobot(loc, self.settings.robot_hp, player_id, robot_id, self.field)
		self.robots.append(robot)
		self.field[loc] = robot

	def buildGameInfo(self):
		return AttrDict({
			'robots': dict((
				y.location,
				AttrDict(dict(
					(x, getattr(y, x)) for x in
					(self.settings.exposed_properties + self.settings.player_only_properties)
				))
			) for y in self.robots),
			'turn': self.turn,
		})

	def getActions(self):
		self.player._robot = None
		self.player2._robot = None
		game_info = self.buildGameInfo()
		actions = {}

		for robot in self.robots:
			if robot.player_id == 1:
				robot_player = self.player
			else:
				if self.player2 is not None:
					robot_player = self.player2
				else:
					continue

			user_robot = robot_player.get_robot()
			for prop in self.settings.exposed_properties + self.settings.player_only_properties:
				setattr(user_robot, prop, getattr(robot, prop))
			try:
				next_action = user_robot.act(game_info)
				if not robot.is_valid_action(next_action):
					raise Exception('Bot %d: %s is not a valid action from %s' % (robot.player_id + 1, str(next_action), robot.location))
			except Exception:
				traceback.print_exc(file = sys.stdout)
				next_action = ['guard']
			actions[robot] = next_action

		commands = list(self.settings.valid_commands)
		commands.remove('guard')
		commands.remove('move')
		commands.insert(0, 'move')

		for cmd in commands:
			for robot, action in actions.iteritems():
				if action[0] != cmd:
					continue

				old_loc = robot.location
				try:
					robot.issue_command(action, actions)
				except Exception:
					traceback.print_exc(file=sys.stdout)
					actions[robot] = ['guard']
				if robot.location != old_loc:
					if self.field[old_loc] is robot:
						self.field[old_loc] = None
						self.updateSquare(old_loc)
					self.field[robot.location] = robot
		return actions

	def onSimulate(self, event):
		self.clearActions()
		actions = self.getActions()
		self.remove_dead()

		for robot, action in actions.items():
			self.renderAction(robot.location, action)
			self.updateSquare(robot.location)

	def remove_dead(self):
	    to_remove = [x for x in self.robots if x.hp <= 0]
	    for robot in to_remove:
	        self.robots.remove(robot)
	        if self.field[robot.location] == robot:
	            self.field[robot.location] = None

	def clearActions(self):
		for action in self.actions:
			self.canvas.delete(action)

		self.actions = []

	def putActionChar(self, loc, char):
		coordinates = self.getSquareCoordinates(loc)
		center_coordinates = mid(coordinates[0], coordinates[1])
		char_coordinates = mid(center_coordinates, coordinates[1])
		x, y = char_coordinates

		action_char = self.canvas.create_text(
			x, y, 
			text = char,
			font = "TkTextFont",
			fill = "#000"
		)

		self.actions.append(action_char)

	def putActionArrow(self, loc, loc2, color):
		# this is very ugly
		coordinates1 = self.getSquareCoordinates(loc)
		center_coordinates1 = mid(coordinates1[0], coordinates1[1])
		coordinates2 = self.getSquareCoordinates(loc2)
		center_coordinates2 = mid(coordinates2[0], coordinates2[1])
		mid_coordinates = mid(center_coordinates1, center_coordinates2)
		x1, y1 = mid(center_coordinates1, mid_coordinates)
		x2, y2 = mid(center_coordinates2, mid_coordinates)

		arrow = self.canvas.create_line(x1, y1, x2, y2, fill = color, width = 3.0, arrow = Tkinter.LAST)
		self.actions.append(arrow)

	def renderAction(self, loc, action):
		if action[0] == "guard":
			self.putActionChar(loc, "G")
		elif action[0] == "suicide":
			self.putActionChar(loc, "S")
		elif action[0] == "move":
			self.putActionChar(loc, "M")
			self.putActionArrow(loc, action[1], self.move_arrow_color)
		else:
			self.putActionChar(loc, "A")
			self.putActionArrow(loc, action[1], self.attack_arrow_color)



if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Robot game simulation script.")
	parser.add_argument(
		"usercode",
		help="File containing first robot class definition."
	)
	parser.add_argument(
		"-u", "--usercode2",
		help="File containing second robot class definition."
	)
	parser.add_argument(
		"-m", "--map", 
		help="User-specified map file.",
		default=os.path.join(os.path.dirname(__file__), 'maps/default.py'))

	args = parser.parse_args()

	map_name = os.path.join(args.map)
	map_data = ast.literal_eval(open(map_name).read())
	game.init_settings(map_data)
	player = game.Player(open(args.usercode).read())
	player2 = game.Player(open(args.usercode2).read())

	SimulatorUI(settings.settings, map_data, player, player2)
	

