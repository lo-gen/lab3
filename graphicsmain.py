from gamemodel import *
from graphics import *


class GameGraphics:
    def __init__(self, game):
        self.game = game

        # open the window
        self.win = GraphWin("Cannon game" , 640, 480, autoflush=False)
        self.win.setCoords(-110, -10, 110, 155)
        
        # draw the terrain
        aLine = Line(Point(-110,0), Point(110,0))
        aLine.draw(self.win)

        self._explotion_list = [None, None]
        self._new_round = None
        self.draw_text = [None, None]
        self.draw_cannons = [self.drawCanon(0), self.drawCanon(1)]
        self.draw_scores  = [self.drawScore(0), self.drawScore(1)]
        self.draw_projs   = [None, None]

    def drawCanon(self,playerNr):
        _cannon_size = self.game.getCannonSize()
        _getX = self.game.getPlayers()[playerNr].getX()
        cannon = Rectangle(Point(_getX - _cannon_size / 2, 0), Point(_getX + _cannon_size / 2, _cannon_size))
        cannon.setFill(self.game.getPlayers()[playerNr].getColor())
        cannon.draw(self.win)
        return cannon
    
    def drawScore(self,playerNr): 
        _getX = self.game.getPlayers()[playerNr].getX()
        _score = self.game.getPlayers()[playerNr].getScore()
        _text_ = "Score: " + str(_score)
        _text = Text(Point(_getX, -5), _text_)
        _text.draw(self.win)
        self.draw_text[playerNr] = _text
        return self.draw_text[playerNr]

    def fire(self, angle, vel):
        player = self.game.getCurrentPlayer()
        proj = player.fire(angle, vel)

        circle_X = proj.getX()
        circle_Y = proj.getY()
        
        if self._new_round != None:
            self._new_round.undraw()
            self._new_round = None

        if self.draw_projs[self.game.getCurrentPlayerNumber()] != None:
            self.draw_projs[self.game.getCurrentPlayerNumber()].undraw()

        circle = Circle(Point(circle_X, circle_Y), self.game.getBallSize())
        circle.setFill(self.game.getPlayers()[self.game.getCurrentPlayerNumber()].getColor())

        circle.draw(self.win)

        while proj.isMoving():
            proj.update(1/50)

            # move is a function in graphics. It moves an object dx units in x direction and dy units in y direction
            circle.move(proj.getX() - circle_X, proj.getY() - circle_Y)

            circle_X = proj.getX()
            circle_Y = proj.getY()

            update(50)
        self.draw_projs[self.game.getCurrentPlayerNumber()] = circle
        return proj

    def updateScore(self,playerNr):
        for n in range(len(self.draw_projs)):
            if self.draw_projs[n] != None:
                self.draw_projs[n].undraw()
                self.draw_projs[n] = None
        self.draw_text[playerNr].undraw()
        self.drawScore(playerNr)

    def explode(self):
        Other_x = self.game.getOtherPlayer().getX()
        Other_y = self.game.getCannonSize() / 2
        r = self.game.getBallSize()
        while r <= 2 * self.game.getCannonSize():
            
            if r == r//2 * 2:
                self._explotion_list[1] = Circle(Point(Other_x,Other_y),r)
                self._explotion_list[1].setFill(self.game.getPlayers()[self.game.getCurrentPlayerNumber()].getColor())
                self._explotion_list[1].draw(self.win)
                if self._explotion_list[0] != None:
                    self._explotion_list[0].undraw()
            else:
                self._explotion_list[0] = Circle(Point(Other_x,Other_y),r)
                self._explotion_list[0].setFill(self.game.getPlayers()[self.game.getCurrentPlayerNumber()].getColor())
                self._explotion_list[0].draw(self.win)
                if self._explotion_list[1] != None:
                    self._explotion_list[1].undraw()
            r += 1
            update(50)
        self._explotion_list[1].undraw()
        self._explotion_list[0].undraw()

    def play(self):
        while True:
            player = self.game.getCurrentPlayer()
            oldAngle,oldVel = player.getAim()
            wind = self.game.getCurrentWind()

            # InputDialog(self, angle, vel, wind) is a class in gamegraphics
            inp = InputDialog(oldAngle,oldVel,wind)
            # interact(self) is a function inside InputDialog. It runs a loop until the user presses either the quit or fire button
            if inp.interact() == "Fire!": 
                angle, vel = inp.getValues()
                inp.close()
            elif inp.interact() == "Quit":
                exit()
            
            player = self.game.getCurrentPlayer()
            other = self.game.getOtherPlayer()
            proj = self.fire(angle, vel)
            distance = other.projectileDistance(proj)

            if distance == 0.0:
                player.increaseScore()
                self.explode()
                self.updateScore(self.game.getCurrentPlayerNumber())
                self.game.newRound()
            
            _text = "New Round! New wind is " + str(round(self.game.getCurrentWind(), 2))
            _textbox = Text(Point(0, 100), (_text))
            _textbox.setSize(25)
            _textbox.draw(self.win)
            self._new_round = _textbox

            self.game.nextPlayer()


class InputDialog:
    def __init__ (self, angle, vel, wind):
        self.win = win = GraphWin("Fire", 200, 300)
        win.setCoords(0,4.5,4,.5)
        Text(Point(1,1), "Angle").draw(win)
        self.angle = Entry(Point(3,1), 5).draw(win)
        self.angle.setText(str(angle))
        
        Text(Point(1,2), "Velocity").draw(win)
        self.vel = Entry(Point(3,2), 5).draw(win)
        self.vel.setText(str(vel))
        
        Text(Point(1,3), "Wind").draw(win)
        self.height = Text(Point(3,3), 5).draw(win)
        self.height.setText("{0:.2f}".format(wind))
        
        self.fire = Button(win, Point(1,4), 1.25, .5, "Fire!")
        self.fire.activate()
        self.quit = Button(win, Point(3,4), 1.25, .5, "Quit")
        self.quit.activate()

    def interact(self):
        while True:
            pt = self.win.getMouse()
            if self.quit.clicked(pt):
                return "Quit"
            if self.fire.clicked(pt):
                return "Fire!"

    def getValues(self):
        a = float(self.angle.getText())
        v = float(self.vel.getText())
        return a,v

    def close(self):
        self.win.close()


class Button:

    def __init__(self, win, center, width, height, label):

        w,h = width/2.0, height/2.0
        x,y = center.getX(), center.getY()
        self.xmax, self.xmin = x+w, x-w
        self.ymax, self.ymin = y+h, y-h
        p1 = Point(self.xmin, self.ymin)
        p2 = Point(self.xmax, self.ymax)
        self.rect = Rectangle(p1,p2)
        self.rect.setFill('lightgray')
        self.rect.draw(win)
        self.label = Text(center, label)
        self.label.draw(win)
        self.deactivate()

    def clicked(self, p):
        return self.active and \
               self.xmin <= p.getX() <= self.xmax and \
               self.ymin <= p.getY() <= self.ymax

    def getLabel(self):
        return self.label.getText()

    def activate(self):
        self.label.setFill('black')
        self.rect.setWidth(2)
        self.active = 1

    def deactivate(self):
        self.label.setFill('darkgrey')
        self.rect.setWidth(1)
        self.active = 0


GameGraphics(Game(11,3)).play()
