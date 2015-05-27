#!/usr/bin/env python2
import tkSimpleDialog
import argparse
import ast

import pkg_resources

from rgsimulatorUI import SimulatorUI
from rgkit.game import Player
from rgkit.gamestate import GameState
from rgkit.settings import settings
import getrgmatch

class Simulator:
    def __init__(self, player1_path, player2_path):
        self.match_id = None

        self.player = Player(player1_path) if player1_path else None
        if self.player:
            self.player1_path = player1_path
            self.player.set_player_id(1)

        self.player2 = Player(player2_path) if player2_path else None
        if self.player2:
            self.player2_path = player2_path
            self.player2.set_player_id(0)

        self.turn_repeat = False

        self.UI = SimulatorUI(settings)
        self.UI.setTitle("Robot Game Simulator")

        self.state = GameState(settings, turn=1)
        self.cached_actions = None
        self.human_actions = {}

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
        self.UI.bind("n", self.onNextAction)
        self.UI.bind("g", self.onSpawnRobots)

        self.UI.run()

    def onReloadPlayer(self, event):
        self.UI.fadeActions()
        self.cached_actions = None
        self.human_actions = {}
        if self.player:
            self.player = Player(self.player1_path)
            self.player.set_player_id(1)
        if self.player2:
            self.player2 = Player(self.player2_path)
            self.player2.set_player_id(0)

    def onSwapPlayer(self, event):
        self.UI.clearActions()
        self.UI.clearBots()
        self.onReloadPlayer(None)
        for loc, robot in self.state.robots.iteritems():
            self.state.robots[loc]["player_id"] = 1 - self.state.robots[loc]["player_id"]
            self.UI.renderBot(loc, robot.hp, robot.player_id)

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
            self.human_actions = {}
            self.state = GameState()
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
            self.human_actions = {}
            self.UI.setTurn(new_turn)
            self.state.turn = new_turn

    def onRemove(self, event):
        self._removeRobot(self.UI.selection)

    def _removeRobot(self, loc):
        if self.state.is_robot(loc):
            self.UI.fadeActions()
            self.cached_actions = None
            if loc in self.human_actions:
                del self.human_actions[loc]
            self.state.remove_robot(loc)
            self.UI.renderEmpty(loc)

    def onAddTeammate(self, event):
        self._addRobot(1, self.UI.selection)

    def onAddEnemy(self, event):
        self._addRobot(0, self.UI.selection)

    def _addRobot(self, player_id, loc):
        self.UI.fadeActions()
        self.cached_actions = None
        if self.state.is_robot(loc):
            self.state.remove_robot(loc)
            if loc in self.human_actions:
                del self.human_actions[loc]

        self.state.add_robot(loc, player_id)
        self.UI.renderBot(loc, 50, player_id)

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
        def getPlayerActions(player, player_id):
            if player:
                actions, _ = player.get_responses(self.state, player_id)
            else:
                actions = {}
            for loc, robot in self.state.robots.iteritems():
                if robot.player_id == player_id:
                    action = self.human_actions.get(loc)
                    if action or loc not in actions:
                        actions[loc] = action if action else ('guard',)
            return actions
        actions = getPlayerActions(self.player, 1)
        actions.update(getPlayerActions(self.player2, 0))
        return actions

    def onClear(self, event):
        self.UI.clearActions()
        self.UI.clearBots()
        self.cached_actions = None
        self.human_actions = {}
        self.state = GameState(turn=self.state.turn)

    def onShowActions(self, event):
        if self.state.turn < 100:
            #the following is needed since if the turn does not change,
            # non-stateless bots behave differently
            if self.player and self.turn_repeat:
                self.player = Player(self.player1_path)
                self.player.set_player_id(1)
            if self.player2 and self.turn_repeat:
                self.player2 = Player(self.player2_path)
                self.player2.set_player_id(0)
            self.UI.clearActions()
            actions = self.getActions()
            self.cached_actions = actions

            for loc, action in actions.iteritems():
                self.UI.renderAction(loc, action)

            self.turn_repeat = True

            try:
                rgsim_text = self.player._module.rgsim_text
                for loc,text in rgsim_text.iteritems():
                    self.UI.renderText(loc,text)

            except AttributeError:
                print "No rgsim_text dict found for player 1, skipping..."
            except:
                print ("Error in rgsim_text dict, please ensure keys are "+
                       "valid locations and values are strings")

    def onSimulate(self, event):
        if self.state.turn < 100:
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
            self.human_actions = {}
            self.UI.setTurn(self.state.turn)
            self.turn_repeat = False

    def onNextAction(self, event):
        if not self.state.is_robot(self.UI.selection):
            return
        robot = self.state.robots[self.UI.selection]
        action = self.human_actions.get(self.UI.selection)
        if action is None and self.cached_actions is not None:
            action = self.cached_actions.get(self.UI.selection)
        if action is None:
            action = ('guard',)
        x, y = self.UI.selection
        adjacent_locs = ((x, y-1), (x+1, y), (x, y+1), (x-1, y))
        move_locs = [l for l in adjacent_locs if l not in settings.obstacles]
        all_actions = [('guard',)]
        all_actions += [('move', loc) for loc in move_locs]
        all_actions += [('attack', loc) for loc in adjacent_locs]
        all_actions += [('suicide',)]
        i = (all_actions.index(action) + 1) % len(all_actions)
        action = all_actions[i]
        if self.cached_actions is not None:
            self.cached_actions[self.UI.selection] = action
        self.human_actions[self.UI.selection] = action
        self.UI.clearAction(self.UI.selection)
        self.UI.renderAction(self.UI.selection, action)

    def onSpawnRobots(self, event):
        all_locs = self.state._get_spawn_locations()
        for loc in settings.spawn_coords:
            self._removeRobot(loc)
        for i, loc in enumerate(all_locs):
            player_id = i // settings.spawn_per_player
            self._addRobot(player_id, loc)

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
    settings.init_map(map_data)

    p1_path = args.player
    p2_path = args.player2

    Simulator(p1_path, p2_path)
