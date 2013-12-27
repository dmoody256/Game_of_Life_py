#! /usr/bin/python

import sys, math, time, re

from PyQt4 import QtCore, QtGui

class MainWindow(QtGui.QMainWindow):

    def __init__(self):

        super(MainWindow, self).__init__()
        
        
        #self.showFullScreen()      
        
        self.MainWidget = MainWidget(50, [])
        self.setGeometry(100, 100, 1000, 800)
        self.setCentralWidget(self.MainWidget)
        
        self.structures = []
        self.structurelist = []
        self.populateStructures()
        
        self.ControlToolBar = ControlToolbar(self)
        
        self.show()
        
        
    def populateStructures(self):
        
        file = open('structures.txt', 'r')
        
        currentstructure = []
        row = -1
        for line in file:
            if(line[0:1] == '!'):
                
                self.structurelist.append(line[1:-1])
                
                if(row != -1):
                    self.structures.append(currentstructure)
                    
                currentstructure = []
                row = 0
                
            else:
                for pos in range(len(line)):
                    if(line[pos:pos+1] == 'O'):
                        currentstructure.append([row, pos])
                
                row += 1
        
        self.structures.append(currentstructure)
        
        
    def Regrid(self):

        newgrid = self.GridEditText.text()
        if(newgrid != ''):
            newgrid = int(newgrid)
            if(newgrid > 1):
                self.MainWidget = MainWidget(int(newgrid), [])
                self.setCentralWidget(self.MainWidget)
                self.removeToolBar(self.ControlToolBar)
                self.ControlToolBar = ControlToolbar(self)
        
class ControlToolbar(QtGui.QToolBar):
     
    def __init__(self, parent):
        super(ControlToolbar, self).__init__()
        
        self.setWindowTitle('Main Menu')
        self.setMovable(False)
        
        self.parent = parent
        
        self.addQuitButton()
        self.addStartButton()
        self.addStopButton()
        self.addNewGridButton()
        self.addGridEditText()
        self.addStructureButton()
        self.addStructureText()
        self.addGenerationCounter()
    
        parent.addToolBar(QtCore.Qt.BottomToolBarArea, self)
        
    def addStructureButton(self):

        MyButton = QtGui.QPushButton('Build', self)
        MyButton.setMinimumSize(50, 30)
        MyButton.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed))
        MyButton.clicked.connect(self.parent.MainWidget.setBuildCursor)
        
        self.parent.StructureButton = MyButton
        self.addWidget(MyButton)    
        
        
    def addGridEditText(self):

        MyTextEdit = QtGui.QLineEdit(self)
        MyTextEdit.setMaximumSize(50, 30)
        MyTextEdit.setMaxLength(3)
        font = QtGui.QFont()
        font.setPointSize(13)
        MyTextEdit.setFont(font)
        MyTextEdit.setAlignment(QtCore.Qt.AlignHCenter)
        MyTextEdit.setValidator(QtGui.QIntValidator(2,300))
        MyTextEdit.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed))

        self.parent.GridEditText = MyTextEdit
        self.addWidget(MyTextEdit)
        
    def addStructureText(self):

        MyTextEdit = QtGui.QLineEdit(self)
        self.parent.StructureEditText = MyTextEdit
        MyTextEdit.setMaximumSize(250, 30)
        MyTextEdit.setMaxLength(25)
        font = QtGui.QFont()
        font.setPointSize(13)
        MyTextEdit.setFont(font)
       
        completer = QtGui.QCompleter(self.parent.structurelist, MyTextEdit)
        completer.setCompletionMode(QtGui.QCompleter.PopupCompletion)
        completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        
        MyTextEdit.setCompleter(completer)
        MyTextEdit.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed))
      
        self.addWidget(MyTextEdit)
        
    def addNewGridButton(self):

        MyButton = QtGui.QPushButton('New Grid', self)
        MyButton.setMinimumSize(50, 30)
        MyButton.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed))
        MyButton.clicked.connect(self.parent.Regrid)
        MyButton.clicked.connect(self.parent.MainWidget.stop)
        
        self.parent.NewGridButton = MyButton
        self.addWidget(MyButton)
        
    def addGenerationCounter(self):

        MyButton = QtGui.QLabel('Generations:0', self)
        MyButton.setMinimumSize(150, 30)
        MyButton.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed))
        MyButton.setLineWidth(2)
        MyButton.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Raised)
        MyButton.setAlignment(QtCore.Qt.AlignCenter)
        self.parent.GenCounter = MyButton
        self.addWidget(MyButton)
        
   
    def addStartButton(self):

        MyButton = QtGui.QPushButton('Start', self)
        MyButton.setMinimumSize(50, 30)
        MyButton.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed))
        MyButton.clicked.connect(self.parent.MainWidget.NextGeneration)
        
        self.parent.GenCounter = MyButton
        self.addWidget(MyButton)
        
    def addStopButton(self):

        MyButton = QtGui.QPushButton('Stop', self)
        MyButton.setMinimumSize(50, 30)
        MyButton.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed))
        MyButton.clicked.connect(self.parent.MainWidget.stop)
        
        self.parent.StopButton = MyButton
        self.addWidget(MyButton)
    
    def addQuitButton(self):

        MyButton = QtGui.QPushButton('Quit', self)
        MyButton.setMinimumSize(50, 30)
        MyButton.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed))
        MyButton.clicked.connect(self.parent.MainWidget.stop)
        MyButton.clicked.connect(QtCore.QCoreApplication.instance().quit)
        
        self.parent.QuitButton = MyButton
        self.addWidget(MyButton)
    

class MainWidget(QtGui.QWidget):
   
    
    def __init__(self, TotalCells, LivingCells):
        super(MainWidget, self).__init__()
        self.TotalCells = TotalCells
        self.LivingCells = LivingCells
        self.Building = 0
        self.Generations = 0
        
        if(len(LivingCells) == 0):
            for i in range(TotalCells):
                self.LivingCells.append([])
                for k in range(TotalCells):
                    self.LivingCells[i].append(0)
      
                    
    def setBuildCursor(self):
        
        buildtext = self.parent().StructureEditText.text()
        editor = self.parent().StructureEditText
        palette = editor.palette()
        
        if(self.Building == 0 and any(buildtext == val for val in self.parent().structurelist)):
           
            palette.setColor(QtGui.QPalette.Active, QtGui.QPalette.Base, QtGui.QColor(195, 253, 184))
            editor.setPalette(palette)
            self.Building = 1 
            QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
            
        else:
            
            palette.setColor(QtGui.QPalette.Active, QtGui.QPalette.Base, QtGui.QColor(231, 116, 113))
            editor.setPalette(palette)
            self.Building = 0
            QtGui.QApplication.restoreOverrideCursor()
        
        
    def mouseReleaseEvent(self, event):
        
        if(self.Building == 1):
            self.Building = 0
            QtGui.QApplication.restoreOverrideCursor()
            
            buildtext = self.parent().StructureEditText.text()
            structurelist = self.parent().structurelist
            structurepos = [i for i,x in enumerate(structurelist) if x == buildtext]
            
            structurepoints = self.parent().structures[structurepos[0]]
            pos = event.pos()
            
            for point in structurepoints:
                self.changeSquare(pos, point)
            
        else:
            self.changeSquare(event.pos(), [0,0])
            
            
    def changeSquare(self, pos, offset):
        
        size = self.size()

        xsize = ((size.width()-1)/self.TotalCells)
        ysize = ((size.height()-1)/self.TotalCells)
        
        xpos = math.floor(pos.x()/xsize) + offset[1]
        ypos = math.floor(pos.y()/ysize) + offset[0]

        if(self.LivingCells[ypos][xpos] == 1):
            self.LivingCells[ypos][xpos] = 0
        else:
            self.LivingCells[ypos][xpos] = 1
            
        print ('changed' + str(xpos) + 'and' + str(ypos))
        self.repaint()

    def paintEvent(self, e):

        qp = QtGui.QPainter()
        qp.begin(self)
        self.CreateGrid(qp)
        qp.end()
        
    def CreateGrid(self, qp):
        size = self.size()
        xsize = ((size.width()-1)/self.TotalCells)
        ysize = ((size.height()-1)/self.TotalCells)
        
        qp.setPen(QtCore.Qt.black)
        
        for i in range(self.TotalCells+1):
            qp.drawLine(xsize*i, 0, xsize*i, size.height()-1) 
            qp.drawLine(0, ysize*i, size.width()-1, ysize*i)
          
        
        for i in range(self.TotalCells):
            for k in range(self.TotalCells):
                if(self.LivingCells[i][k] == 1):
                    qp.fillRect(xsize*k,ysize*i,(xsize+1),(ysize+1), QtCore.Qt.black)
       
    def stop(self):
        self.stopsignal = 1
       
    def NextGeneration(self):
        
        self.stopsignal = 0
        
        while(self.stopsignal == 0):
        
            NewLivingCells = []
            
            for i in range(self.TotalCells):
                NewLivingCells.append([])
                for k in range(self.TotalCells):
                    nieghbors = self.getNieghbors(i,k)
                    if(self.LivingCells[i][k] == 1):
                        if(nieghbors < 2 or nieghbors > 3):
                            NewLivingCells[i].append(0)
                        else:
                            NewLivingCells[i].append(1)
                    else:
                        if(nieghbors == 3):
                            NewLivingCells[i].append(1)
                        else:
                            NewLivingCells[i].append(0)
            
            self.LivingCells = NewLivingCells
                            
            self.repaint()
            
            self.Generations += 1  
            
            parent = self.parent()
            
            parent.GenCounter.setText('Generations:' + str(self.Generations))
            
            QtGui.qApp.processEvents()
            
            time.sleep(.1)

    def getNieghbors(self, y, x):
        total = 0

        if(x > 0 and y > 0):
            total += self.LivingCells[y-1][x-1]
        if(y > 0):
            total += self.LivingCells[y-1][x]
        if(x < self.TotalCells-1 and y > 0):
            total += self.LivingCells[y-1][x+1]
        if(x > 0):
            total += self.LivingCells[y][x-1]
        if(x < self.TotalCells-1):
            total += self.LivingCells[y][x+1]
        if(y < self.TotalCells-1 and x > 0):
            total += self.LivingCells[y+1][x-1]
        if(y < self.TotalCells-1):
            total += self.LivingCells[y+1][x]
        if(y < self.TotalCells-1 and x < self.TotalCells-1):   
            total += self.LivingCells[y+1][x+1]
                
        return total
    
    
        
        
class GofLApp(QtGui.QApplication):

    def __init__(self, *args):
        QtGui.QApplication.__init__(self, *args)
        self.main = MainWindow()
        self.main.show()

    def byebye( self ):
        self.exit(0)

def main():
    
    app = GofLApp(sys.argv)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()