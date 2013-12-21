#!/usr/bin/env python2
from rgsimulatorUI import SimulatorUI
import Tkinter
import tkSimpleDialog
import argparse
from rgkit import rg, game
from rgkit.gamestate import GameState
from rgkit.settings import AttrDict
import ast
import sys
import traceback
import os

class Simulator:
	def __init__(self, settings, player, player2):
		self.settings = settings
		self.player = player
		self.player2 = player2
		self.UI = SimulatorUI(settings)
		self.UI.setTitle("Robot Game Simulator")

		self.state = GameState(settings, turn=1)
		self.cached_actions = None

		self.UI.setTurn(self.state.turn)

		self.UI.bind("w", lambda ev: self.UI.moveSelection((0, -1)))
		self.UI.bind("a", lambda ev: self.UI.moveSelection((-1, 0)))
		self.UI.bind("s", lambda ev: self.UI.moveSelection((0, 1)))
		self.UI.bind("d", lambda ev: self.UI.moveSelection((1, 0)))
		self.UI.bind("<Up>", lambda ev: self.UI.moveSelection((0, -1)))
		self.UI.bind("<Left>", lambda ev: self.UI.moveSelection((-1, 0)))
		self.UI.bind("<Down>", lambda ev: self.UI.moveSelection((0, 1)))
		self.UI.bind("<Right>", lambda ev: self.UI.moveSelection((1, 0)))
		self.UI.bind("<ButtonPress-1>", lambda ev: self.UI.onMouseClick(ev))

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
		new_turn = tkSimpleDialog.askinteger(
			"Edit turn", "Enter new turn", 
			parent = self.UI.root, 
			initialvalue = self.state.turn,
			minvalue = 1,
			maxvalue = 100
		)
		if new_turn is not None:
			self.UI.fadeActions()
			self.cached_actions = None
			self.UI.setTurn(new_turn)
			self.state.turn = new_turn

	def onRemove(self, event):
		if self.state.is_robot(self.UI.selection):
			self.UI.fadeActions()
			self.cached_actions = None
			self.state.remove_robot(self.UI.selection)
			self.UI.renderEmpty(self.UI.selection)

	def onAddTeammate(self, event):
		self.UI.fadeActions()
		self.cached_actions = None
		if self.state.is_robot(self.UI.selection):
			self.state.remove_robot(self.UI.selection)

		self.state.add_robot(self.UI.selection, 1)
		self.UI.renderBot(self.UI.selection, 50, 1)

	def onAddEnemy(self, event):
		self.UI.fadeActions()
		self.cached_actions = None
		if self.state.is_robot(self.UI.selection):
			self.state.remove_robot(self.UI.selection)

		self.state.add_robot(self.UI.selection, 0)
		self.UI.renderBot(self.UI.selection, 50, 0)

	def onEditHP(self, event):
		if self.state.is_robot(self.UI.selection):
			robot = self.state[self.UI.selection]
			self.UI.fadeActions()
			self.cached_actions = None
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

	def buildGameInfo(self):
		return AttrDict({
			'robots': dict((
				loc,
				AttrDict(dict(
					(x, getattr(robot, x)) for x in
					(self.settings.exposed_properties + self.settings.player_only_properties)
				))
			) for loc, robot in self.state.robots.iteritems()),
			'turn': self.state.turn,
		})

	def getActions(self):
		self.player._robot = None
		if self.player2 is not None:
			self.player2._robot = None
		game_info = self.buildGameInfo()
		actions = {}

		for loc, robot in self.state.robots.iteritems():
			if robot.player_id == 1:
				robot_player = self.player
			else:
				if self.player2 is not None:
					robot_player = self.player2
				else:
					# Don't act
					actions[loc] = ['guard']
					continue

			user_robot = robot_player.get_robot()
			for prop in self.settings.exposed_properties + self.settings.player_only_properties:
				setattr(user_robot, prop, getattr(robot, prop))
			try:
				next_action = user_robot.act(game_info)
				if not self.state.is_valid_action(loc, next_action):
					raise Exception('Bot %d: %s is not a valid action from %s' % (robot.player_id + 1, str(next_action), robot.location))
			except Exception:
				traceback.print_exc(file = sys.stdout)
				next_action = ['guard']
			actions[loc] = next_action

		return actions

	def onClear(self, event):
		self.UI.clearActions()
		self.UI.clearBots()
		self.cached_actions = None
		self.state = GameState(self.settings)

	def onShowActions(self, event):
		self.UI.clearActions()
		actions = self.getActions()
		self.cached_actions = actions

		for loc, action in actions.iteritems():
			self.UI.renderAction(loc, action)

	def onSimulate(self, event):
		self.UI.clearActions()
		self.UI.clearBots()
		if self.cached_actions is None:
			actions = self.getActions()
		else:
			actions = self.cached_actions

		self.state = self.state.apply_actions(actions, spawn=False)

		for loc, robot in self.state.robots.iteritems():
			self.UI.renderBot(loc, robot.hp, robot.player_id)

		self.cached_actions = None
		self.UI.setTurn(self.state.turn)

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
		default=os.path.join(os.path.dirname(rg.__file__), 'maps/default.py'))

	args = parser.parse_args()

	map_name = os.path.join(args.map)
	map_data = ast.literal_eval(open(map_name).read())
	settings = game.init_settings(map_data)
	player = game.Player(open(args.usercode).read())
	if args.usercode2 is None:
		player2 = None
	else:
		player2 = game.Player(open(args.usercode2).read())

	Simulator(settings, player, player2)
