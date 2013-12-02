#!/usr/bin/env python2
from rgsimulatorUI import SimulatorUI
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


class Simulator:
	def __init__(self, settings, player, player2):
		self.settings = settings
		self.player = player
		self.player2 = player2
		self.UI = SimulatorUI(settings)
		self.UI.setTitle("Robot Game Simulator")

		self.robots = []
		self.cached_actions = None
		self.field = game.Field(settings.board_size)
		self.robot_id = 0

		self.turn = 1
		self.UI.setTurn(self.turn)

		self.UI.bind("w", lambda ev: self.UI.moveSelection((0, -1)))
		self.UI.bind("a", lambda ev: self.UI.moveSelection((-1, 0)))
		self.UI.bind("s", lambda ev: self.UI.moveSelection((0, 1)))
		self.UI.bind("d", lambda ev: self.UI.moveSelection((1, 0)))
		self.UI.bind("<Up>", lambda ev: self.UI.moveSelection((0, -1)))
		self.UI.bind("<Left>", lambda ev: self.UI.moveSelection((-1, 0)))
		self.UI.bind("<Down>", lambda ev: self.UI.moveSelection((0, 1)))
		self.UI.bind("<Right>", lambda ev: self.UI.moveSelection((1, 0)))

		self.UI.bind("t", self.onEditTurn)
		self.UI.bind("f", self.onAddTeammate)
		self.UI.bind("e", self.onAddEnemy)
		self.UI.bind("r", self.onRemove)
		self.UI.bind("c", self.onClear)
		self.UI.bind("<Delete>", self.onRemove)
		self.UI.bind("<BackSpace>", self.onRemove)
		self.UI.bind("h", self.onEditHP)
		self.UI.bind("<space>", self.onShowActions)
		self.UI.bind("<Return>", self.onSimulate)

		self.UI.run()

	def onEditTurn(self, event):
		self.UI.fadeActions()
		new_turn = tkSimpleDialog.askinteger(
			"Edit turn", "Enter new turn", 
			parent = self.UI.root, 
			initialvalue = self.turn,
			minvalue = 1,
			maxvalue = 100
		)
		if new_turn is not None:
			self.UI.setTurn(new_turn)
			self.turn = new_turn

	def onRemove(self, event):
		self.UI.fadeActions()
		if self.getRobot(self.UI.selection) is not None:
			self.removeRobot(self.UI.selection)
			self.UI.renderEmpty(self.UI.selection)

	def onAddTeammate(self, event):
		self.UI.fadeActions()
		if self.getRobot(self.UI.selection) is not None:
			self.removeRobot(self.UI.selection)

		self.addRobot(self.UI.selection, 1)
		self.UI.renderBot(self.UI.selection, 50, 1)

	def onAddEnemy(self, event):
		self.UI.fadeActions()
		if self.getRobot(self.UI.selection) is not None:
			self.removeRobot(self.UI.selection)

		self.addRobot(self.UI.selection, 0)
		self.UI.renderBot(self.UI.selection, 50, 0)

	def onEditHP(self, event):
		self.UI.fadeActions()
		robot = self.getRobot(self.UI.selection)
		if robot is not None:
			new_hp = tkSimpleDialog.askinteger(
				"Edit hp", "Enter new hp", 
				parent = self.UI.root, 
				initialvalue = robot.hp,
				minvalue = 1,
				maxvalue = 50
			)
			if new_hp is not None:
				robot.hp = new_hp
				self.UI.renderBot(self.UI.selection, new_hp, robot.player_id)

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
		if self.player2 is not None:
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
					# Don't act
					actions[robot] = ['guard']
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

		return actions

	def remove_dead(self):
	    to_remove = [x for x in self.robots if x.hp <= 0]
	    for robot in to_remove:
	        self.robots.remove(robot)
	        if self.field[robot.location] == robot:
	            self.field[robot.location] = None
	            self.UI.renderEmpty(robot.location)

	def onClear(self, event):
		self.UI.clearActions()
		locations = [robot.location for robot in self.robots]
		self.robots = []
		for loc in locations:
			self.field[loc] = None
			self.UI.renderEmpty(loc)

	def onShowActions(self, event):
		#self.onSimulate(event)
		self.UI.clearActions()
		actions = self.getActions()
		self.cached_actions = actions

		for robot, action in actions.items():
			self.UI.renderAction(robot.location, action)

	def applyActions(self, actions):
		for robot, action in actions.iteritems():

			old_loc = robot.location
			try:
				robot.issue_command(action, actions)
			except Exception:
				traceback.print_exc(file=sys.stdout)
				actions[robot] = ['guard']
			if robot.location != old_loc:
				if self.field[old_loc] is robot:
					self.field[old_loc] = None
					self.UI.renderEmpty(old_loc)
				self.field[robot.location] = robot

	def onSimulate(self, event):
		self.UI.clearActions()
		if self.cached_actions is None:
			actions = self.getActions()
		else:
			actions = self.cached_actions

		self.applyActions(actions)

		for robot, action in actions.items():
			self.UI.renderAction(robot.location, action)
			self.UI.renderBot(robot.location, robot.hp, robot.player_id)

		self.remove_dead()
		self.cached_actions = None
		self.turn += 1
		self.UI.setTurn(self.turn)

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Robot game simulation script.")
	parser.add_argument(
		"usercode",
		help="File containing first robot class definition."
	)
	parser.add_argument(
		"usercode2", nargs="?", default=None,
		help="File containing second robot class definition (optional)."
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
	if args.usercode2 is None:
		player2 = None
	else:
		player2 = game.Player(open(args.usercode2).read())

	Simulator(game.settings, player, player2)
