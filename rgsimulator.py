#!/usr/bin/env python2
from rgsimulatorUI import SimulatorUI
import Tkinter
import pkg_resources
import tkSimpleDialog
import argparse
from rgkit import rg, game
from rgkit.game import Player
from rgkit.gamestate import GameState
from rgkit.settings import AttrDict
import ast
import sys
import traceback
import os
import getrgmatch

class Simulator:
    def __init__(self, settings, p1_path, p2_path):
        self.settings = settings
        self.match_id = None
        self.p1_path = p1_path
        self.p2_path = p2_path
        self.code = open(p1_path).read()
        if p2_path is None:
            self.p2_path = map_data = open(pkg_resources.resource_filename('rgkit', 'bots/guardbot.py')).read()
        self.code2 = open(p2_path).read()

        self.player = Player(self.code)
        self.player.set_player_id(1)
        self.player2 = Player(self.code2)
        self.player2.set_player_id(0)
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

        self.UI.bind("l", self.onLoadMatch)
        self.UI.bind("k", self.onLoadTurn)
        self.UI.bind("o", self.onReloadPlayer)
        self.UI.bind("p", self.onSwapPlayer)
        
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

    def onReloadPlayer(self, event):
        self.UI.fadeActions()
        self.cached_actions = None
        self.code = open(self.p1_path).read()
        self.code2 = open(self.p2_path).read()
        self.player = Player(self.code)
        self.player.set_player_id(1)
        self.player2 = Player(self.code2)
        self.player2.set_player_id(0)

    def onSwapPlayer(self, event):
        self.p1_path, self.p2_path = self.p2_path, self.p1_path
        
    def onLoadMatch(self, event):
        self.match_id = tkSimpleDialog.askinteger(
            "Load match", "Enter match number", 
            parent = self.UI.root, 
            initialvalue = 2588548,
            minvalue = 1,
            maxvalue = 99999999
        )
        if self.match_id is not None:
            self.moves = getrgmatch.get_match_result(self.match_id)
            self.loadBotsfromTurn(1)
 
    def onLoadTurn(self, event):
        if self.match_id is not None:
            new_turn = tkSimpleDialog.askinteger(
                "Edit turn", "Enter new turn", 
                parent = self.UI.root, 
                initialvalue = self.state.turn,
                minvalue = 1,
                maxvalue = 100
            )
            if new_turn is not None:
                self.loadBotsfromTurn(new_turn)
 
    def loadBotsfromTurn (self, new_turn):
        if self.match_id is not None:
            self.UI.clearActions()
            self.UI.clearBots()
            self.cached_actions = None
            self.state = GameState(self.settings)
            for bot in self.moves[new_turn]:
                loc = tuple(bot['location'])
                # print bot
                self.state.add_robot(loc, bot['player_id'])
                self.state.robots[loc].hp = bot['hp']
                self.UI.renderBot(loc, bot['hp'], bot['player_id'])
                
            self.UI.setTurn(new_turn)
            self.state.turn = new_turn
       
        
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
            robot = self.state.robots[self.UI.selection]
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

    def getActions(self):
        actions = self.player.get_actions(self.state, 0)
        actions2 = self.player2.get_actions(self.state, 0)
        actions.update(actions2)

        return actions

    def onClear(self, event):
        self.UI.clearActions()
        self.UI.clearBots()
        self.cached_actions = None
        self.state = GameState(self.settings)

    def onShowActions(self, event):
        self.player.reload()
        self.player2.reload()
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
        "player",
        help="File containing first robot class definition."
    )
    parser.add_argument(
        "player2", nargs="?", default=None,
        help="File containing second robot class definition (optional)."
    )
    parser.add_argument(
        "-m", "--map", 
        help="User-specified map file.",
        type=argparse.FileType('r'),
        default=pkg_resources.resource_filename('rgkit',
                                                'maps/default.py')
    )

    args = parser.parse_args()

    map_data = ast.literal_eval(args.map.read())
    settings = game.init_settings(map_data)

    Simulator(settings, args.player, args.player2)
