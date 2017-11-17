"""
Module Documentation here
"""
#=========================================================================================
# Licence, Reference and Credits
#=========================================================================================
__copyright__ = ""
__credits__ = ""
__licence__ = ("")
__reference__ = ("")
#=========================================================================================
# Last code modification:
#=========================================================================================
__modifiedBy__ = "$modifiedBy$"
__dateModified__ = "$dateModified$"
__version__ = "$Revision$"
#=========================================================================================
# Created:
#=========================================================================================
__author__ = "$Author$"
__date__ = "$Date$"
#=========================================================================================
# Start of code
#=========================================================================================

import sys
import math, random
import ctypes

from PyQt5 import QtCore, QtGui, QtOpenGL, QtWidgets
from PyQt5.QtCore import (QPoint, QPointF, QRect, QRectF, QSize, Qt, QTime,
        QTimer)
from PyQt5.QtGui import (QBrush, QColor, QFontMetrics, QImage, QPainter,
        QRadialGradient, QSurfaceFormat)
from PyQt5.QtWidgets import QApplication, QOpenGLWidget
from ccpn.util.Logging import getLogger
import numpy as np
from pyqtgraph import functions as fn
from ccpn.core.PeakList import PeakList
from ccpn.core.Spectrum import Spectrum

try:
    from OpenGL import GL, GLU, GLUT
except ImportError:
    app = QtWidgets.QApplication(sys.argv)
    QtWidgets.QMessageBox.critical(None, "OpenGL hellogl",
            "PyOpenGL must be installed to run this example.")
    sys.exit(1)


class CcpnOpenGLWidget(QtWidgets.QOpenGLWidget):

    def __init__(self, parent=None):
      super(QtWidgets.QOpenGLWidget, self).__init__(parent)
      self.trolltechPurple = QtGui.QColor.fromCmykF(0.39, 0.39, 0.0, 0.0)

    def minimumSizeHint(self):
      return QtCore.QSize(100, 300)

    def sizeHint(self):
      return QtCore.QSize(400, 400)

    def initializeGL(self):
      # self.qglClearColor(self.trolltechPurple.dark())
      GL.glClearColor(*self.trolltechPurple.getRgb())

    def paintGL(self):
      GL.glMatrixMode(GL.GL_MODELVIEW)
      GL.glLoadIdentity()
      GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
      GL.glColor3f(1,0,0)
      GL.glRectf(-1,-1,1,0)
      GL.glColor3f(0,1,0)
      GL.glRectf(-1,0,1,1)
      GL.glBegin(GL.GL_TRIANGLES)
      GL.glVertex2f(3.0, 3.0)
      GL.glVertex2f(5.0, 3.0)
      GL.glVertex2f(5.0, 5.0)
      GL.glVertex2f(6.0, 4.0)
      GL.glVertex2f(7.0, 4.0)
      GL.glVertex2f(7.0, 7.0)
      GL.glEnd()
      GL.glFinish()

    def resizeGL(self, w, h):
      GL.glViewport(0, 0, w, h)


class Bubble(object):
  def __init__(self, position, radius, velocity):
    self.position = position
    self.vel = velocity
    self.radius = radius

    self.innerColor = self.randomColor()
    self.outerColor = self.randomColor()
    self.updateBrush()

  def updateBrush(self):
    gradient = QRadialGradient(QPointF(self.radius, self.radius),
                               self.radius, QPointF(self.radius * 0.5, self.radius * 0.5))

    gradient.setColorAt(0, QColor(255, 255, 255, 255))
    gradient.setColorAt(0.25, self.innerColor)
    gradient.setColorAt(1, self.outerColor)
    self.brush = QBrush(gradient)

  def drawBubble(self, painter):
    painter.save()
    painter.translate(self.position.x() - self.radius,
                      self.position.y() - self.radius)
    painter.setBrush(self.brush)
    painter.drawEllipse(0, 0, int(2 * self.radius), int(2 * self.radius))
    painter.restore()

  def randomColor(self):
    red = random.randrange(205, 256)
    green = random.randrange(205, 256)
    blue = random.randrange(205, 256)
    alpha = random.randrange(91, 192)

    return QColor(red, green, blue, alpha)

  def move(self, bbox):
    self.position += self.vel
    leftOverflow = self.position.x() - self.radius - bbox.left()
    rightOverflow = self.position.x() + self.radius - bbox.right()
    topOverflow = self.position.y() - self.radius - bbox.top()
    bottomOverflow = self.position.y() + self.radius - bbox.bottom()

    if leftOverflow < 0.0:
      self.position.setX(self.position.x() - 2 * leftOverflow)
      self.vel.setX(-self.vel.x())
    elif rightOverflow > 0.0:
      self.position.setX(self.position.x() - 2 * rightOverflow)
      self.vel.setX(-self.vel.x())

    if topOverflow < 0.0:
      self.position.setY(self.position.y() - 2 * topOverflow)
      self.vel.setY(-self.vel.y())
    elif bottomOverflow > 0.0:
      self.position.setY(self.position.y() - 2 * bottomOverflow)
      self.vel.setY(-self.vel.y())

  def rect(self):
    return QRectF(self.position.x() - self.radius,
                  self.position.y() - self.radius, 2 * self.radius,
                  2 * self.radius)


class CcpnGLWidget(QOpenGLWidget):
  def __init__(self, parent=None):
    super(CcpnGLWidget, self).__init__(parent)

    if not parent:        # don't initialise if nothing there
      return

    self.parent = parent

    for spectrumView in self.parent.spectrumViews:
      spectrumView._buildSignal._buildSignal.connect(self.paintGLsignal)

    midnight = QTime(0, 0, 0)
    random.seed(midnight.secsTo(QTime.currentTime()))

    self.object = 0
    self.xRot = 0
    self.yRot = 0
    self.zRot = 0
    self.image = QImage()
    self.bubbles = []
    self.lastPos = QPoint()

    self.trolltechGreen = QColor.fromCmykF(0.40, 0.0, 1.0, 0.0)
    self.trolltechPurple = QColor.fromCmykF(0.39, 0.39, 0.0, 0.0)

    self.animationTimer = QTimer()
    self.animationTimer.setSingleShot(False)
    self.animationTimer.timeout.connect(self.animate)
    self.animationTimer.start(25)

    self.setAutoFillBackground(False)
    self.setMinimumSize(200, 200)
    self.setWindowTitle("Overpainting a Scene")

    self._mouseX = 0
    self._mouseY = 0

    # self.eventFilter = self._eventFilter
    # self.installEventFilter(self)   # ejb
    self.setMouseTracking(True)                 # generate mouse events when button not pressed

    self.base = None
    self.spectrumValues = []
    self._GLPeakLists = []
    self._drawSelectionBox = False
    self._selectionMode = 0
    self._startCoordinate = None
    self._endCoordinate = None
    self._shift = False
    self._command = False
    self._key = ' '
    self._isSHIFT = ' '
    self._isCTRL = ' '

    # self.installEventFilter(self)
    self.setFocusPolicy(Qt.StrongFocus)

  def eventFilter(self, obj, event):
    self._key = '_'
    if type(event) == QtGui.QKeyEvent and event.key() == Qt.Key_A:
      self._key = 'A'
      event.accept()
      return True
    return super(CcpnGLWidget, self).eventFilter(obj, event)

  def _releaseDisplayLists(self, displayLists):
    for displayList in displayLists:
      GL.glDeleteLists(displayList, 1)
    displayLists[:] = []

  def _createDisplayLists(self, levels, displayLists):
    # could create them in one go but more likely to get fragmentation that way
    for level in levels:
      displayLists.append(GL.glGenLists(1))

  def _makeGLPeakList(self, spectrum:Spectrum, num:GL.GLint):
    # clear the list and rebuild
    GL.glDeleteLists(self._GLPeakLists[num], 1)
    self._GLPeakLists[num] = GL.glGenLists(1)

    # this is actually quite old-school for openGL but good for test
    GL.glNewList(self._GLPeakLists[num], GL.GL_COMPILE)
    GL.glBegin(GL.GL_LINES)

    GL.glColor4f(1.0, 1.0, 1.0, 1.0)

    GL.glEnd()
    GL.glEndList()

  def _connectSpectra(self):
    for spectrumView in self.parent.spectrumViews:
      spectrumView._buildSignal._buildSignal.connect(self.paintGLsignal)

  def setXRotation(self, angle):
    angle = self.normalizeAngle(angle)
    if angle != self.xRot:
      self.xRot = angle

  def setYRotation(self, angle):
    angle = self.normalizeAngle(angle)
    if angle != self.yRot:
      self.yRot = angle

  def setZRotation(self, angle):
    angle = self.normalizeAngle(angle)
    if angle != self.zRot:
      self.zRot = angle

  def initializeGL(self):
    GL = self.context().versionFunctions()
    GL.initializeOpenGLFunctions()

    self.object = self.makeObject()

  def mousePressEvent(self, event):
    self.lastPos = event.pos()

    self._startCoordinate = [event.pos().x(), self.height() - event.pos().y()]
    self._endCoordinate = [event.pos().x(), self.height() - event.pos().y()]
    self._drawSelectionBox = True

  def mouseReleaseEvent(self, event):
    self._drawSelectionBox = False

  def keyPressEvent(self, event: QtGui.QKeyEvent):
    self._key = event.key()
    keyMod = QApplication.keyboardModifiers()
    if keyMod == Qt.ShiftModifier:
      self._isSHIFT = 'S'
    if keyMod == Qt.ControlModifier:
      self._isCTRL = 'C'

    # if type(event) == QtGui.QKeyEvent and event.key() == QtCore.Qt.Key_A:
    #   self._key = 'A'
    # if type(event) == QtGui.QKeyEvent and event.key() == QtCore.Qt.Key_S:
    #   self._key = 'S'

  def keyReleaseEvent(self, event: QtGui.QKeyEvent):
    self._key = ' '
    self._isSHIFT = ' '
    self._isCTRL = ' '

  def mouseMoveEvent(self, event):
    self.setFocus()
    dx = event.x() - self.lastPos.x()
    dy = event.y() - self.lastPos.y()

    if event.buttons() & Qt.LeftButton:
      self.setXRotation(self.xRot + 8 * dy)
      self.setYRotation(self.yRot + 8 * dx)
    elif event.buttons() & Qt.RightButton:
      self.setXRotation(self.xRot + 8 * dy)
      self.setZRotation(self.zRot + 8 * dx)

    self.lastPos = event.pos()

    self._mouseX = event.pos().x()
    self._mouseY = self.height() - event.pos().y()

    if event.buttons() & Qt.LeftButton:
      # do the complicated keypresses first
      if (self._key == Qt.Key_Control and self._isSHIFT == 'S') or \
          (self._key == Qt.Key_Shift and self._isCTRL) == 'C':
        self._endCoordinate = [event.pos().x(), self.height() - event.pos().y()]
        self._selectionMode = 3

      elif self._key == Qt.Key_Shift:
        self._endCoordinate = [event.pos().x(), self.height() - event.pos().y()]
        self._selectionMode = 1

      elif self._key == Qt.Key_Control:
        self._endCoordinate = [event.pos().x(), self.height() - event.pos().y()]
        self._selectionMode = 2


        #   event.modifiers() & QtCore.Qt.ShiftModifier):
    #   position = event.scenePos()
    #   mousePoint = self.mapSceneToView(position)
    #   print(mousePoint)
    #
    #   elif (event.button() == QtCore.Qt.LeftButton) and (
    #   event.modifiers() & QtCore.Qt.ShiftModifier) and not (
    # event.modifiers() & QtCore.Qt.ControlModifier):
    # print('Add Select')
    #
    # elif event.button() == QtCore.Qt.MiddleButton and not event.modifiers():
    # event.accept()
    # print('Pick and Assign')
    #
    # elif event.button() == QtCore.Qt.RightButton and not event.modifiers():
    # event.accept()
    # print('Context Menu to be activated here')

  def paintEvent_WithPainter(self, event):
    self.makeCurrent()

    GL.glMatrixMode(GL.GL_MODELVIEW)
    GL.glPushMatrix()

    self.set3DProjection()

    self.setClearColor(self.trolltechPurple.darker())
    GL.glShadeModel(GL.GL_SMOOTH)
    GL.glEnable(GL.GL_DEPTH_TEST)
    # GL.glEnable(GL.GL_CULL_FACE)
    GL.glEnable(GL.GL_LIGHTING)
    GL.glEnable(GL.GL_LIGHT0)
    GL.glEnable(GL.GL_MULTISAMPLE)
    GL.glLightfv(GL.GL_LIGHT0, GL.GL_POSITION,
                      (0.5, 5.0, 7.0, 1.0))

    self.setupViewport(self.width(), self.height())

    GL.glClear(
      GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
    GL.glLoadIdentity()
    GL.glTranslated(0.0, 0.0, -10.0)
    GL.glRotated(self.xRot / 16.0, 1.0, 0.0, 0.0)
    GL.glRotated(self.yRot / 16.0, 0.0, 1.0, 0.0)
    GL.glRotated(self.zRot / 16.0, 0.0, 0.0, 1.0)
    GL.glCallList(self.object)

    GL.glMatrixMode(GL.GL_MODELVIEW)
    GL.glPopMatrix()

    painter = QPainter(self)
    painter.setRenderHint(QPainter.Antialiasing)

    for bubble in self.bubbles:
      if bubble.rect().intersects(QRectF(event.rect())):
        bubble.drawBubble(painter)

    self.drawInstructions(painter)
    painter.end()

  @QtCore.pyqtSlot(bool)
  def paintGLsignal(self, bool):
    # my signal to repaint the screen after the spectra have changed
    if bool:
      self.paintGL()

  def sign(self, x):
    return 1.0 if x >= 0 else -1.0

  def paintGL(self):
    self.makeCurrent()

    GL.glPushAttrib(GL.GL_ALL_ATTRIB_BITS)

    GL.glClearColor(0.05, 0.05, 0.05, 1.0)
    GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

    getGLvector = (GL.GLfloat * 2)()
    GL.glGetFloatv(GL.GL_ALIASED_LINE_WIDTH_RANGE, getGLvector);
    linewidths = [i for i in getGLvector]

    self.set2DProjection()

    self.modelViewMatrix = (GL.GLdouble * 16)()
    self.projectionMatrix = (GL.GLdouble * 16)()
    self.viewport = (GL.GLint * 4)()

    GL.glGetDoublev(GL.GL_MODELVIEW_MATRIX, self.modelViewMatrix)
    GL.glGetDoublev(GL.GL_PROJECTION_MATRIX, self.projectionMatrix)
    GL.glGetIntegerv(GL.GL_VIEWPORT, self.viewport)

    self.worldCoordinate = GLU.gluUnProject(
      self._mouseX, self._mouseY, 0,
      self.modelViewMatrix,
      self.projectionMatrix,
      self.viewport,
    )
    self.viewport = [i for i in self.viewport]
    # grab coordinates of the transformed viewport
    self._infiniteLineUL = GLU.gluUnProject(
      0.0,
      self.viewport[3]+self.viewport[1],
      0.0,
      self.modelViewMatrix,
      self.projectionMatrix,
      self.viewport,
    )
    self._infiniteLineBR = GLU.gluUnProject(
      self.viewport[2]+self.viewport[0],
      self.viewport[1],
      0.0,
      self.modelViewMatrix,
      self.projectionMatrix,
      self.viewport,
    )


    # GL.glEnable(GL.GL_LINE_SMOOTH)
    # GL.glHint(GL.GL_LINE_SMOOTH_HINT, GL.GL_NICEST)
    # GL.glEnable(GL.GL_BLEND)
    # GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
    GL.glLineWidth(1.0)
    for spectrumView in self.parent.spectrumViews:
      try:
        # could put a signal on buildContours
        if spectrumView.buildContours:
          spectrumView._buildContours(None)  # need to trigger these changes now
          spectrumView.buildContours = False  # set to false, as we have rebuilt
          # set to True and update() will rebuild the contours
          # can be done with a call to self.rebuildContours()

        self._spectrumValues = spectrumView._getValues()
        dx = self.sign(self._infiniteLineBR[0] - self._infiniteLineUL[0])
        dy = self.sign(self._infiniteLineUL[1] - self._infiniteLineBR[1])
        dxAF = (self._spectrumValues[0].maxAliasedFrequency-self._spectrumValues[0].minAliasedFrequency)
        dyAF = (self._spectrumValues[1].maxAliasedFrequency-self._spectrumValues[1].minAliasedFrequency)
        xScale = dx*dxAF/self._spectrumValues[0].totalPointCount
        yScale = dy*dyAF/self._spectrumValues[1].totalPointCount
        px = self._spectrumValues[0].maxAliasedFrequency
        py = self._spectrumValues[1].maxAliasedFrequency

        GL.glPushMatrix()
        GL.glTranslate(px, py, 0.0)
        GL.glScale(xScale, yScale, 1.0)
        spectrumView._paintContoursNoClip()
        GL.glPopMatrix()
      except:
        raise
        spectrumView._buildContours(None)
        # pass

    # this is needed if it is a paintEvent
    # painter = QPainter(self)
    # painter.setRenderHint(QPainter.Antialiasing)
    #
    # for bubble in self.bubbles:
    #   if bubble.rect().intersects(QRectF(event.rect())):
    #     bubble.drawBubble(painter)
    #
    # self.drawInstructions(painter)
    #
    # painter.end()

    # draw cursor
    # self.set2DProjectionFlat()
    #
    # GL.glColor4f(0.9, 0.9, 1.0, 150)
    # GL.glBegin(GL.GL_LINES)
    # GL.glVertex2f(self._mouseX, 0)
    # GL.glVertex2f(self._mouseX, self.height())
    # GL.glVertex2f(0, self._mouseY)
    # GL.glVertex2f(self.width(), self._mouseY)
    # GL.glEnd()

    self.set2DProjection()
    self._buildAxes(axisList=[0, 1], scaleGrid=[2, 1, 0], r=1.0, g=1.0, b=1.0, transparency=600.0)
    self.set2DProjectionRightAxis()
    self._buildAxes(axisList=[1], scaleGrid=[1, 0], r=0.2, g=1.0, b=0.3, transparency=64.0)
    self.set2DProjectionBottomAxis()
    self._buildAxes(axisList=[0], scaleGrid=[1, 0], r=0.2, g=1.0, b=0.3, transparency=64.0)

    # draw axis lines to right and bottom
    self.set2DProjectionFlat()
    h = self.height()
    w = self.width()
    GL.glColor4f(0.2, 1.0, 0.3, 1.0)
    GL.glBegin(GL.GL_LINES)
    GL.glVertex2d(0, 1)         # not sure why 0 doesn't work
    GL.glVertex2d(w, 1)
    GL.glVertex2d(w, 0)
    GL.glVertex2d(w, h)
    GL.glEnd()


    # draw all the peak GLLists here



    self.set2DProjection()      # set back to the main projection

    if self._drawSelectionBox:
      GL.glEnable(GL.GL_BLEND)
      GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

      self._dragStart = GLU.gluUnProject(
        self._startCoordinate[0], self._startCoordinate[1], 0,
        self.modelViewMatrix,
        self.projectionMatrix,
        self.viewport,
      )
      self._dragEnd = GLU.gluUnProject(
        self._endCoordinate[0], self._endCoordinate[1], 0,
        self.modelViewMatrix,
        self.projectionMatrix,
        self.viewport,
      )

      if self._selectionMode == 1:    # yellow
        GL.glColor4f(0.8, 0.9, 0.2, 0.2)
      elif self._selectionMode == 2:      # purple
        GL.glColor4f(0.8, 0.2, 0.9, 0.2)
      elif self._selectionMode == 3:      # cyan
        GL.glColor4f(0.2, 0.5, 0.9, 0.2)

      GL.glBegin(GL.GL_QUADS)
      GL.glVertex2d(self._dragStart[0], self._dragStart[1])
      GL.glVertex2d(self._dragEnd[0], self._dragStart[1])
      GL.glVertex2d(self._dragEnd[0], self._dragEnd[1])
      GL.glVertex2d(self._dragStart[0], self._dragEnd[1])
      GL.glEnd()

      if self._selectionMode == 1:    # yellow
        GL.glColor4f(0.8, 0.9, 0.2, 0.8)
      elif self._selectionMode == 2:      # purple
        GL.glColor4f(0.8, 0.2, 0.9, 0.8)
      elif self._selectionMode == 3:      # cyan
        GL.glColor4f(0.2, 0.5, 0.9, 0.8)

      GL.glBegin(GL.GL_LINE_STRIP)
      GL.glVertex2d(self._dragStart[0], self._dragStart[1])
      GL.glVertex2d(self._dragEnd[0], self._dragStart[1])
      GL.glVertex2d(self._dragEnd[0], self._dragEnd[1])
      GL.glVertex2d(self._dragStart[0], self._dragEnd[1])
      GL.glVertex2d(self._dragStart[0], self._dragStart[1])
      GL.glEnd()
      GL.glDisable(GL.GL_BLEND)

    # print ('>>>Coords', self._infiniteLineBL, self._infiniteLineTR)
    # this gets the correct mapped coordinates
    GL.glColor4f(0.8, 0.9, 1.0, 1.0)
    GL.glBegin(GL.GL_LINES)
    GL.glVertex2d(self.worldCoordinate[0], self._infiniteLineUL[1])
    GL.glVertex2d(self.worldCoordinate[0], self._infiniteLineBR[1])
    GL.glVertex2d(self._infiniteLineUL[0], self.worldCoordinate[1])
    GL.glVertex2d(self._infiniteLineBR[0], self.worldCoordinate[1])
    GL.glEnd()

    coords = " "+str(self._isSHIFT)+str(self._isCTRL)+str(self._key)+" : "\
              +str(round(self.worldCoordinate[0], 3))\
              +", "+str(round(self.worldCoordinate[1], 3))
    self.glut_print(self.worldCoordinate[0], self.worldCoordinate[1]
                    , GLUT.GLUT_BITMAP_HELVETICA_18
                    , coords
                    , 1.0, 1.0, 1.0, 1.0)

    GL.glPopAttrib()
    GLUT.glutSwapBuffers()

  def resizeGL(self, width, height):
    self.setupViewport(width, height)
    self.update()

  def showEvent(self, event):
    self.createBubbles(20 - len(self.bubbles))

  def sizeHint(self):
    return QSize(400, 400)

  def makeObject(self):
    # list = GL.glGenLists(1)
    list = GL.glGenLists(1)
    GL.glNewList(list, GL.GL_COMPILE)

    GL.glEnable(GL.GL_NORMALIZE)
    GL.glBegin(GL.GL_QUADS)

    GL.glMaterialfv(GL.GL_FRONT, GL.GL_DIFFUSE,
                   (self.trolltechGreen.red() / 255.0,
                    self.trolltechGreen.green() / 255.0,
                    self.trolltechGreen.blue() / 255.0, 1.0))

    x1 = +0.06
    y1 = -0.14
    x2 = +0.14
    y2 = -0.06
    x3 = +0.08
    y3 = +0.00
    x4 = +0.30
    y4 = +0.22

    self.quad(x1, y1, x2, y2, y2, x2, y1, x1)
    self.quad(x3, y3, x4, y4, y4, x4, y3, x3)

    self.extrude(x1, y1, x2, y2)
    self.extrude(x2, y2, y2, x2)
    self.extrude(y2, x2, y1, x1)
    self.extrude(y1, x1, x1, y1)
    self.extrude(x3, y3, x4, y4)
    self.extrude(x4, y4, y4, x4)
    self.extrude(y4, x4, y3, x3)

    NumSectors = 200

    for i in range(NumSectors):
      angle1 = (i * 2 * math.pi) / NumSectors
      x5 = 0.30 * math.sin(angle1)
      y5 = 0.30 * math.cos(angle1)
      x6 = 0.20 * math.sin(angle1)
      y6 = 0.20 * math.cos(angle1)

      angle2 = ((i + 1) * 2 * math.pi) / NumSectors
      x7 = 0.20 * math.sin(angle2)
      y7 = 0.20 * math.cos(angle2)
      x8 = 0.30 * math.sin(angle2)
      y8 = 0.30 * math.cos(angle2)

      self.quad(x5, y5, x6, y6, x7, y7, x8, y8)

      self.extrude(x6, y6, x7, y7)
      self.extrude(x8, y8, x5, y5)

    GL.glEnd()

    GL.glEndList()
    return list

  def quad(self, x1, y1, x2, y2, x3, y3, x4, y4):
    GL.glNormal3d(0.0, 0.0, -1.0)
    GL.glVertex3d(x1, y1, -0.05)
    GL.glVertex3d(x2, y2, -0.05)
    GL.glVertex3d(x3, y3, -0.05)
    GL.glVertex3d(x4, y4, -0.05)

    GL.glNormal3d(0.0, 0.0, 1.0)
    GL.glVertex3d(x4, y4, +0.05)
    GL.glVertex3d(x3, y3, +0.05)
    GL.glVertex3d(x2, y2, +0.05)
    GL.glVertex3d(x1, y1, +0.05)

  def extrude(self, x1, y1, x2, y2):
    self.setColor(self.trolltechGreen.darker(250 + int(100 * x1)))

    GL.glNormal3d((x1 + x2) / 2.0, (y1 + y2) / 2.0, 0.0)
    GL.glVertex3d(x1, y1, +0.05)
    GL.glVertex3d(x2, y2, +0.05)
    GL.glVertex3d(x2, y2, -0.05)
    GL.glVertex3d(x1, y1, -0.05)

  def normalizeAngle(self, angle):
    while angle < 0:
      angle += 360 * 16
    while angle > 360 * 16:
      angle -= 360 * 16
    return angle

  def createBubbles(self, number):
    for i in range(number):
      position = QPointF(self.width() * (0.1 + 0.8 * random.random()),
                         self.height() * (0.1 + 0.8 * random.random()))
      radius = min(self.width(), self.height()) * (0.0125 + 0.0875 * random.random())
      velocity = QPointF(self.width() * 0.0125 * (-0.5 + random.random()),
                         self.height() * 0.0125 * (-0.5 + random.random()))

      self.bubbles.append(Bubble(position, radius, velocity))

  def animate(self):
    for bubble in self.bubbles:
      bubble.move(self.rect())

    self.update()

  def setupViewport(self, width, height):
    # side = min(width, height)
    # GL.glViewport((width - side) // 2, (height - side) // 2, side,
    #                    side)
    # GL.glViewport(0, -1, width, height)
    GL.glMatrixMode(GL.GL_PROJECTION)
    GL.glViewport(0, height//2, width//2, height)
    # GL.glMatrixMode(GL.GL_PROJECTION)
    # GL.glLoadIdentity()
    # GL.glOrtho(-0.5, +0.5, +0.5, -0.5, 4.0, 15.0)
    GL.glMatrixMode(GL.GL_MODELVIEW)

  def set3DProjection(self):
    GL.glMatrixMode(GL.GL_PROJECTION)
    GL.glLoadIdentity()
    GL.glOrtho(-0.5, +0.5, +0.5, -0.5, 4.0, 15.0)
    GL.glMatrixMode(GL.GL_MODELVIEW)
    GL.glLoadIdentity()

  def set2DProjection(self):
    GL.glMatrixMode(GL.GL_PROJECTION)
    GL.glLoadIdentity()

    # put into a box in the viewport at (50, 50) to (150, 150)
    # GL.glViewport(150, 50, 350, 150)
    h = self.height()
    w = self.width()
    GL.glViewport(0, 35, w-35, h-35)   # leave a 35 width margin for the axes - bottom/right
                                        # (0,0) is bottom-left
    # GLU.gluOrtho2D(-10, 50, -10, 0)

    # testing - grab the coordinates from the plotWidget
    axisRangeL = self.parent.plotWidget.getAxis('bottom').range
    axL = axisRangeL[0]
    axR = axisRangeL[1]
    axisRangeB = self.parent.plotWidget.getAxis('right').range
    axB = axisRangeB[0]
    axT = axisRangeB[1]

    # L/R/B/T   (usually) but 'bottom' is relative to the top-left corner
    GLU.gluOrtho2D(axL, axR, axB, axT)      # nearly!

    # GL.glScalef(1, 1, 1);

    GL.glMatrixMode(GL.GL_MODELVIEW)
    GL.glLoadIdentity()
    # GL.glTranslatef(0.1, 0.1, 0.1)

  def set2DProjectionRightAxis(self):
    GL.glMatrixMode(GL.GL_PROJECTION)
    GL.glLoadIdentity()

    axisLine = 5
    h = self.height()
    w = self.width()
    GL.glViewport(w-35-axisLine, 35, axisLine, h-35)   # leave a 35 width margin for the axes - bottom/right
                                        # (0,0) is bottom-left

    axisRangeL = self.parent.plotWidget.getAxis('bottom').range
    axL = axisRangeL[0]
    axR = axisRangeL[1]
    axisRangeB = self.parent.plotWidget.getAxis('right').range
    axB = axisRangeB[0]
    axT = axisRangeB[1]

    # L/R/B/T   (usually) but 'bottom' is relative to the top-left corner
    GLU.gluOrtho2D(axL, axR, axB, axT)
    GL.glMatrixMode(GL.GL_MODELVIEW)
    GL.glLoadIdentity()

  def set2DProjectionBottomAxis(self):
    GL.glMatrixMode(GL.GL_PROJECTION)
    GL.glLoadIdentity()

    axisLine = 5
    h = self.height()
    w = self.width()
    GL.glViewport(0, 35, w-35, axisLine)   # leave a 35 width margin for the axes - bottom/right
                                    # (0,0) is bottom-left

    axisRangeL = self.parent.plotWidget.getAxis('bottom').range
    axL = axisRangeL[0]
    axR = axisRangeL[1]
    axisRangeB = self.parent.plotWidget.getAxis('right').range
    axB = axisRangeB[0]
    axT = axisRangeB[1]

    # L/R/B/T   (usually) but 'bottom' is relative to the top-left corner
    GLU.gluOrtho2D(axL, axR, axB, axT)
    GL.glMatrixMode(GL.GL_MODELVIEW)
    GL.glLoadIdentity()

  def set2DProjectionFlat(self):
    GL.glMatrixMode(GL.GL_PROJECTION)
    GL.glLoadIdentity()

    # put into a box in the viewport at (50, 50) to (150, 150)
    # GL.glViewport(150, 50, 350, 150)
    h = self.height()
    w = self.width()
    # GL.glViewport(15, 35, w-35, h-50)   # leave a 35 width margin for the axes
    #                                     # '15' is a temporary border at left/top
    GL.glViewport(0, 35, w-35, h-35)      # leave a 35 width margin for the axes
                                          # '15' is a temporary border at left/top

    GLU.gluOrtho2D(0, w, 0, h)
    GL.glMatrixMode(GL.GL_MODELVIEW)
    GL.glLoadIdentity()

  def drawInstructions(self, painter):
    text = "Click and drag with the left mouse button to rotate the Qt " \
           "logo."
    metrics = QFontMetrics(self.font())
    border = max(4, metrics.leading())

    rect = metrics.boundingRect(0, 0, self.width() - 2 * border,
                                int(self.height() * 0.125), Qt.AlignCenter | Qt.TextWordWrap,
                                text)
    painter.setRenderHint(QPainter.TextAntialiasing)
    painter.fillRect(QRect(0, 0, self.width(), rect.height() + 2 * border),
                     QColor(0, 0, 0, 127))
    painter.setPen(Qt.white)
    painter.fillRect(QRect(0, 0, self.width(), rect.height() + 2 * border),
                     QColor(0, 0, 0, 127))
    painter.drawText((self.width() - rect.width()) / 2, border, rect.width(),
                     rect.height(), Qt.AlignCenter | Qt.TextWordWrap, text)

  def setClearColor(self, c):
    GL.glClearColor(c.redF(), c.greenF(), c.blueF(), c.alphaF())

  def setColor(self, c):
    GL.glColor4f(c.redF(), c.greenF(), c.blueF(), c.alphaF())

  def _buildAxes(self, axisList=None, scaleGrid=None, r=0.0, g=0.0, b=0.0, transparency=256.0):
    # this needs making into a GL_LIST

    # self.picture = QtGui.QPicture()
    # p = QtGui.QPainter()
    # p.begin(self.picture)

    # dt = fn.invertQTransform(self.viewTransform())
    # vr = self.getViewWidget().rect()
    # unit = self.pixelWidth(), self.pixelHeight()
    # dim = [vr.width(), vr.height()]
    # lvr = self.boundingRect()
    # ul = np.array([lvr.left(), lvr.top()])
    # br = np.array([lvr.right(), lvr.bottom()])

    # dt = fn.invertQTransform(self.viewTransform())
    # vr = self.getViewWidget().rect()
    # unit = self.pixelWidth(), self.pixelHeight()
    dim = [self.width(), self.height()]
    # lvr = self.boundingRect()

    # TODO:ED not sure this is exactly the correct coords yet
    ul = np.array([self._infiniteLineUL[0], self._infiniteLineUL[1]])
    br = np.array([self._infiniteLineBR[0], self._infiniteLineBR[1]])

    # texts = []

    GL.glEnable(GL.GL_BLEND)
    GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
    GL.glLineWidth(1.0)

    if ul[0] > br[0]:
      x = ul[0]
      ul[0] = br[0]
      br[0] = x
    for i in scaleGrid:       #  [2,1,0]:   ## Draw three different scales of grid
      dist = br-ul
      nlTarget = 10.**i
      d = 10. ** np.floor(np.log10(abs(dist/nlTarget))+0.5)
      ul1 = np.floor(ul / d) * d
      br1 = np.ceil(br / d) * d
      dist = br1-ul1
      nl = (dist / d) + 0.5

      for ax in axisList:           #   range(0,2):  ## Draw grid for both axes
        ppl = np.array( dim[ax] / nl[ax] )                      # ejb
        c = np.clip(3.*(ppl-3), 0., 30.)
        GL.glColor4f(r, g, b, c/transparency)               # make high order lines more transparent

        # if self.parent.gridColour == '#f7ffff':
          # linePen = QtGui.QPen(QtGui.QColor(247, 255, 255, c))

        # GL.glColor3f(247, 255, 255)
        # else:
          # linePen = QtGui.QPen(QtGui.QColor(8, 0, 0, c))
          # GL.glColor3f(8, 0, 0)

        GL.glBegin(GL.GL_LINES)
        bx = (ax+1) % 2
        for x in range(0, int(nl[ax])):
          # linePen.setCosmetic(False)
          # if ax == 0:
          #     # linePen.setWidthF(self.pixelWidth())
          # #     #print "ax 0 height", self.pixelHeight()
          #
          #   GL.glLineWidth(1)
          # else:
          #     # linePen.setWidthF(self.pixelHeight())
          #   GL.glLineWidth(2)
          #     #print "ax 1 width", self.pixelWidth()
          # p.setPen(linePen)
          p1 = np.array([0.,0.])
          p2 = np.array([0.,0.])
          p1[ax] = ul1[ax] + x * d[ax]
          p2[ax] = p1[ax]
          p1[bx] = ul[bx]
          p2[bx] = br[bx]
          if p1[ax] < min(ul[ax], br[ax]) or p1[ax] > max(ul[ax], br[ax]):
              continue
          # p.drawLine(QtCore.QPointF(p1[0], p1[1]), QtCore.QPointF(p2[0], p2[1]))
          GL.glVertex2f(p1[0], p1[1])
          GL.glVertex2f(p2[0], p2[1])
        GL.glEnd()

    GL.glDisable(GL.GL_BLEND)

    # tr = self.deviceTransform()
    # p.setWorldTransform(fn.invertQTransform(tr))
    # for t in texts:
    #     x = tr.map(t[0]) + Point(0.5, 0.5)
    #     p.drawText(x, t[1])
    # p.end()

  def glut_print(self, x, y, font, text, r, g, b, a):

    # blending = False
    # if GL.glIsEnabled(GL.GL_BLEND):
    #   blending = True

    # glEnable(GL_BLEND)
    GL.glColor4f(1.0, 1.0, 1.0, 0.6)
    GL.glRasterPos2f(x, y)
    for ch in text:
      GLUT.glutBitmapCharacter(font, ctypes.c_int(ord(ch)))

    # if not blending:
    #   GL.glDisable(GL.GL_BLEND)

  # def Draw():
  #   glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
  #
  #   glut_print(10, 10, GLUT_BITMAP_9_BY_15, "Hallo World", 1.0, 1.0, 1.0, 1.0)
  #   # draw my scene ......
  #   glutSwapBuffers()

  # def BuildFont():
  #   global base
  #
  #   wgldc = WGL.wglGetCurrentDC ()
  #   # hDC = win32ui.CreateDCFromHandle (wgldc)
  #
  #
  #   base = GL.glGenLists(32+96);					# // Storage For 96 Characters, plus 32 at the start...
  #
  #   # CreateFont () takes a python dictionary to specify the requested font properties.
  #   font_properties = { "name" : "Courier New",
  #             "width" : 0 ,
  #             "height" : -24,
  #             "weight" : 800
  #             }
  #   font = win32ui.CreateFont (font_properties)
  #   # // Selects The Font We Want
  #   oldfont = hDC.SelectObject (font)
  #   # // Builds 96 Characters Starting At Character 32
  #   wglUseFontBitmaps (wgldc, 32, 96, base+32)
  #   # // reset the font
  #   hDC.SelectObject (oldfont)
  #   # // Delete The Font (python will cleanup font for us...)
  #   return
  #
  # def KillFont ():
  #   """ // Delete The Font List
  #   """
  #   global	base
  #   # // Delete All 96 Characters
  #   glDeleteLists (base, 32+96)
  #   return
  #
  #
  # def glPrint (str):
  #   """ // Custom GL "Print" Routine
  #   """
  #   global base
  #   # // If THere's No Text Do Nothing
  #   if (str == None):
  #     return
  #   if (str == ""):
  #     return
  #   glPushAttrib(GL_LIST_BIT);							# // Pushes The Display List Bits
  #   try:
  #     glListBase(base);								# // Sets The Base Character to 32
  #     glCallLists(str)									# // Draws The Display List Text
  #   finally:
  #     glPopAttrib();										# // Pops The Display List Bits
  #   return

  def _loadPNG(self, fileName):
    import imageio

    im = imageio.imread(fileName)
    print (im.shape)
    
    # need to load the offsets file (*.fnt) and put into array
    

if __name__ == '__main__':

  import sys
  from ccpn.framework.Version import applicationVersion

  qtApp = QtWidgets.QApplication(['CcpnGLWidget_test', ])

  QtCore.QCoreApplication.setApplicationName('CcpnGLWidget_test')
  QtCore.QCoreApplication.setApplicationVersion(applicationVersion)

  myGL = CcpnGLWidget()
  myGL._loadPNG('~/PycharmProjects/myfont.png')

  # popup = UpdateAdmin()
  # popup.show()
  # popup.raise_()

  # sys.exit(qtApp.exec_())