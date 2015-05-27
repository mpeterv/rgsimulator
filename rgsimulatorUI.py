import Tkinter
import tkFont


def mid(l1, l2):
    return (int((l1[0]+l2[0]) / 2), int((l1[1]+l2[1]) / 2))


class SimulatorUI:
    def __init__(self, settings):
        self.settings = settings

        self.square_size = 40
        self.border_width = 1
        self.padding = 0
        self.arrow_width = 3
        self.selection_border_width = 5
        self.fill_color = "#FFF"
        self.obstacle_fill_color = "#555"
        self.bot_fill_color = ["#57C", "#C75"]
        self.border_color = "#333"
        self.selection_border_color = "#FF0"
        self.move_arrow_color = "#00F"
        self.attack_arrow_color = "#000"

        self.map_width = self.settings.board_size
        self.map_height = self.settings.board_size
        self.width = self.square_size*self.map_width
        self.height = self.square_size*self.map_height

        self.root = Tkinter.Tk()
        self.root.resizable(0, 0)
        self.setTitle("Robot Game")

        self.turn_label = Tkinter.Label(self.root, text = "")
        self.turn_label.pack()
        self.setTurn(1)

        self.canvas = Tkinter.Canvas(self.root, width = self.width, height = self.height)
        self.canvas.pack()

        self.squares = {}
        self.labels = {}
        self.actions = {}

        for x in xrange(0, self.map_width):
            for y in xrange(0, self.map_height):
                coordinates = self.getSquareCoordinates((x, y))
                x1, y1 = coordinates[0]
                x2, y2 = coordinates[1]

                self.squares[(x, y)] = self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill = self.obstacle_fill_color if (x, y) in self.settings['obstacles'] else self.fill_color,
                    outline = self.border_color,
                    width = self.border_width
                )

                self.labels[(x, y)] = self.canvas.create_text(
                    x1 + self.square_size/2, y1 + self.square_size/2,
                    text = (x+1)*(y+1)-1 if x*y == 0 else "",
                    font = "TkFixedFont",
                    fill = "#000"
                )

                self.actions[(x, y)] = []

        self.center = (int(self.map_width/2), int(self.map_height/2))

        self.selection = self.center
        selection_coordinates = self.getSquareCoordinates(self.selection)
        selection_x1, selection_y1 = selection_coordinates[0]
        selection_x2, selection_y2 = selection_coordinates[1]
        self.selection_square = self.canvas.create_rectangle(
            selection_x1, selection_y1, selection_x2, selection_y2,
            fill = "",
            outline = self.selection_border_color,
            width = self.selection_border_width
        )

        # I am a dirty hack, fix me
        text_font = tkFont.nametofont("TkTextFont")
        text_font.configure(weight = "bold")

    def run(self):
        self.root.mainloop()

    def bind(self, event, hook):
        self.root.bind(event, hook)

    def onMouseClick(self, event):
        self.setSelection(self.getSquareByCoordinates(event.x, event.y))

    def getSquareCoordinates(self, loc):
        x, y = loc
        return (
            (self.square_size*x + self.padding/2, self.square_size*y + self.padding/2),
            (self.square_size*(x + 1) - self.padding/2, self.square_size*(y + 1) - self.padding/2)
        )

    def getSquareByCoordinates(self, x, y):
        return (x/self.square_size, y/self.square_size)

    def hideSelection(self):
        self.canvas.itemconfigure(self.selection_square, width = 0)

    def showSelection(self):
        self.canvas.itemconfigure(self.selection_square, width = self.selection_border_width)

    def setSelection(self, loc):
        if loc not in self.settings['obstacles']:
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
        self.turn_label.config(text = "Turn %s" % turn)

    def setFill(self, loc, color):
        self.canvas.itemconfigure(self.squares[loc], fill = color)

    def setText(self, loc, text):
        self.canvas.itemconfigure(self.labels[loc], text = text)

    def renderEmpty(self, loc):
        self.setText(loc, "")
        self.setFill(loc, self.obstacle_fill_color if loc in self.settings['obstacles'] else self.fill_color)

    def clearBots(self):
        for x in xrange(1, self.map_width):
            for y in xrange(1, self.map_height):
                self.renderEmpty((x, y))

    def renderBot(self, loc, hp, player_id):
        self.setText(loc, hp)
        self.setFill(loc, self.bot_fill_color[player_id])

    def clearAction(self, loc):
        for action in self.actions[loc]:
            self.canvas.delete(action)

        self.actions[loc] = []

    def clearActions(self):
        for loc in self.actions:
            self.clearAction(loc)

    def fadeAction(self, loc):
        for action in self.actions[loc]:
            if self.canvas.type(action) == "text":
                old_text = self.canvas.itemcget(action, "text")
                new_text = old_text.strip("()")
                new_text = "("+new_text+")"
                self.canvas.itemconfig(action, fill="#CCC", text=new_text)
            else:
                self.canvas.itemconfig(action, fill="#CCC")

    def fadeActions(self):
        for loc in self.actions:
            self.fadeAction(loc)

    def renderActionChar(self, loc, char):
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

        self.actions[loc].append(action_char)

    def renderActionArrow(self, loc, loc2, color):
        coordinates1 = self.getSquareCoordinates(loc)
        center_coordinates1 = mid(coordinates1[0], coordinates1[1])
        coordinates2 = self.getSquareCoordinates(loc2)
        center_coordinates2 = mid(coordinates2[0], coordinates2[1])
        mid_coordinates = mid(center_coordinates1, center_coordinates2)
        x1, y1 = mid(center_coordinates1, mid_coordinates)
        x2, y2 = mid(center_coordinates2, mid_coordinates)

        arrow = self.canvas.create_line(x1, y1, x2, y2, fill = color, width = self.arrow_width, arrow = Tkinter.LAST)
        self.actions[loc].append(arrow)

    def renderAction(self, loc, action):
        if action[0] == "guard":
            self.renderActionChar(loc, "G")
        elif action[0] == "suicide":
            self.renderActionChar(loc, "S")
        elif action[0] == "move":
            self.renderActionChar(loc, "M")
            self.renderActionArrow(loc, action[1], self.move_arrow_color)
        else:
            self.renderActionChar(loc, "A")
            self.renderActionArrow(loc, action[1], self.attack_arrow_color)

    def renderText(self, loc, text):
        coordinates = self.getSquareCoordinates(loc)
        center = mid(coordinates[0], coordinates[1])
        x, y = mid(center, coordinates[0])
        textobj = self.canvas.create_text(x, y, text=text)
        self.actions[loc].append(textobj)
