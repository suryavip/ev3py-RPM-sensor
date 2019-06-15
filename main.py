#!/usr/bin/env pybricks-micropython

from pybricks import ev3brick as brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor, InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import (Port, Stop, Direction, Button, Color, SoundFile, ImageFile, Align)
from pybricks.tools import print, wait, StopWatch
from pybricks.robotics import DriveBase

from threading import Thread


class ButtonListener():
    lastState = False

    def __init__(self, button, ifPressed):
        self.button = button
        self.ifPressed = ifPressed
        t = Thread(target=self.poll)
        t.start()

    def poll(self):
        while True:
            state = self.button in brick.buttons()
            if state == True and lastState == False:
                self.ifPressed()
            lastState = state
            wait(10)


class RPMSensor():
    lightSensor = ColorSensor(Port.S1)
    calibrateButton = Button.CENTER

    sample = [0, 100]
    mid = 50
    mode = 'measuring'
    rpm = 0
    stopWatch = StopWatch()

    def __init__(self):
        m = Thread(target=self.measure)
        m.start()

        c = ButtonListener(self.calibrateButton, self.calibrate)

        d = Thread(target=self.display)
        d.start()

    def display(self):
        while True:
            brick.display.clear()
            if self.mode == 'measuring':
                brick.display.text('{} RPM'.format(self.rpm), (60, 50))
            elif self.mode == 'calibrating':
                brick.display.text('CALIBRATING...', (60, 50))
            wait(500)

    def calibrate(self):
        self.mode = 'calibrating'
        self.sample = []
        while len(self.sample) < 100:
            v = self.lightSensor.reflection()
            self.sample.append(v)
        self.mid = (max(self.sample) - min(self.sample)) / 2
        self.mode = 'measuring'

    def measure(self):
        while True:
            v = self.lightSensor.reflection()
            if v > self.mid:
                interval = self.stopWatch.time()  # how long it took for 1 rotation
                interval = 1 if interval == 0 else interval
                rotationPerSec = 1 / interval
                self.rpm = rotationPerSec * 60
                self.stopWatch.pause()
            else:
                self.stopWatch.reset()
                self.stopWatch.resume()

RPMSensor()