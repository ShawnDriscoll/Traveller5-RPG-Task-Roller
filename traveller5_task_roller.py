#
#   Traveller5 Task Roller 0.4.0 Beta for Windows 11
#   Written for Python 3.11.6
#
##############################################################

"""
Traveller5 Task Roller 0.4.0 Beta for Windows 11
--------------------------------------------------------

This program makes various dice rolls and calculates their graphs if needed.
"""

import pyttsx3

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from mainwindow import Ui_MainWindow
from aboutdialog import Ui_aboutDialog
from alertdialog import Ui_alertDialog
from rpg_tools.pydice import roll
import sys
import time
import os
import numpy as np
from matplotlib import font_manager
import logging

__author__ = 'Shawn Driscoll <shawndriscoll@hotmail.com>\nshawndriscoll.blogspot.com'
__app__ = 'Traveller5 Task Roller 0.4.0 Beta'
__version__ = '0.4.0b'
__py_version_req__ = (3,11,6)
__expired_tag__ = False

engine = pyttsx3.init()
voice_list = engine.getProperty('voices')
voices = ['Mute Voice']
voice = {}
rate = -50
volume = 1.0

# Look for installed TTS voices
for i in voice_list:
    rec = {}
    name_found = i.name[i.name.find(' ')+1:]
    name_found = name_found[:name_found.find(' ')]
    voices.append(name_found)
    rec['Name'] = i.id
    rec['Rate'] = rate
    rec['Volume'] = volume
    voice[name_found] = rec

rate = engine.getProperty('rate')
volume = engine.getProperty('volume')

task_difficulties = ['Easy', 'Average', 'Difficult', 'Formidable', 'Staggering', 'Hopeless', 'Impossible', 'Beyond Impossible']
roll_accuracies = ['50', '100', '500', '1000', '5000', '10000', '50000', '100000', '500000']
rough_estimates = ['Optional', 'Minutes', 'An Hour', 'All Day', 'A Week', 'A Month']

class aboutDialog(QDialog, Ui_aboutDialog):
    def __init__(self):
        '''
        Open the About dialog window
        '''
        super().__init__()
        log.info('PyQt5 aboutDialog initializing...')
        self.setWindowFlags(Qt.Drawer | Qt.WindowStaysOnTopHint)
        self.setupUi(self)
        self.aboutOKButton.clicked.connect(self.acceptOKButtonClicked)
        log.info('PyQt5 aboutDialog initialized.')
        
    def acceptOKButtonClicked(self):
        '''
        Close the About dialog window
        '''
        log.info('PyQt5 aboutDialog closing...')
        self.close()

class alertDialog(QDialog, Ui_alertDialog):
    def __init__(self):
        '''
        Open the Alert dialog window
        '''
        super().__init__()
        log.info('PyQt5 alertDialog initializing...')
        self.setWindowFlags(Qt.Drawer | Qt.WindowStaysOnTopHint)
        self.setupUi(self)
        self.aboutOKButton.clicked.connect(self.acceptOKButtonClicked)
        log.info('PyQt5 alertDialog initialized.')
        
    def acceptOKButtonClicked(self):
        '''
        Close the Alert dialog window
        '''
        log.info('PyQt5 alertDialog closing...')
        self.close()

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        '''
        Display the Main window.
        Connect all the buttons to their functions.
        Initialize their value ranges.
        '''
        super().__init__()
        log.info('PyQt5 MainWindow initializing...')
        self.setupUi(self)
        
        self.taskDifficulty.currentIndexChanged.connect(self.taskDifficulty_changed)
        
        for i in range(len(task_difficulties)):
            self.taskDifficulty.addItem(task_difficulties[i])
        self.taskDifficulty.setCurrentIndex(1)

        self.variableDuration.currentIndexChanged.connect(self.variableDuration_changed)
        
        for i in range(len(rough_estimates)):
            self.variableDuration.addItem(rough_estimates[i])
        self.variableDuration.setCurrentIndex(0)

        self.cautiousButton.clicked.connect(self.cautiousButton_clicked)
        self.hastyButton.clicked.connect(self.hastyButton_clicked)
        self.extrahastyButton.clicked.connect(self.extrahastyButton_clicked)
        self.tihButton.clicked.connect(self.tihButton_clicked)

        self.fluxButton.clicked.connect(self.fluxButton_clicked)
        self.goodfluxButton.clicked.connect(self.goodfluxButton_clicked)
        self.badfluxButton.clicked.connect(self.badfluxButton_clicked)
        
        for i in range(len(roll_accuracies)):
            self.rollaccuracyType.addItem(roll_accuracies[i])
        self.roll_accuracy = 5000
        log.info('Roll accuracy set to: ' + str(self.roll_accuracy))
        self.rollaccuracyType.setCurrentIndex(3)
        self.rollaccuracyType.currentIndexChanged.connect(self.rollaccuracyType_changed)
        
        self.characteristic.valueChanged.connect(self.characteristic_changed)
        self.phantom_char.toggled.connect(self.phantom_char_toggled)
        self.skill.valueChanged.connect(self.skill_changed)
        self.phantom_skill.toggled.connect(self.phantom_skill_toggled)
        self.modifier.valueChanged.connect(self.modifier_changed)
        
        self.rollButton.clicked.connect(self.rollButton_clicked)
        self.actionRoll_Dice.triggered.connect(self.rollButton_clicked)

        self.clear_rollButton.clicked.connect(self.clear_rollButton_clicked)
        self.actionClear_Roll_History.triggered.connect(self.clear_rollButton_clicked)

        self.clear_graphButton.clicked.connect(self.clear_graphButton_clicked)
        self.actionClear_Graph.triggered.connect(self.clear_graphButton_clicked)
        
        self.clearButton.clicked.connect(self.clear_allButton_clicked)
        self.actionClear_All.triggered.connect(self.clear_allButton_clicked)
        
        self.actionAbout_Traveller5_Task_Roller.triggered.connect(self.actionAbout_triggered)
        
        # Set the About menu item
        self.popAboutDialog=aboutDialog()
        
        # Set the Alert menu item
        self.popAlertDialog=alertDialog()
        
        self.quitButton.clicked.connect(self.quitButton_clicked)
        self.actionQuit.triggered.connect(self.quitButton_clicked)
        
        self.rollInput.returnPressed.connect(self.manual_roll)

        # Build voice button (hopefully this computer has voices)
        j = 0
        for i in voices:
            self.voiceBox.addItem(i)
            if j > 0:
                log.info('SAPI voice added: ' + i)
            j += 1
        self.voiceBox.setCurrentIndex(0)
        self.voiceBox.currentIndexChanged.connect(self.voiceBox_changed)

        # Look for installed GUI styles
        self.styles_installed = []
        for i in QStyleFactory.keys():
            self.styleButton.addItem(i)
            self.styles_installed.append(i)
            log.info("Found '" + i + "' style")
        self.styleButton.setCurrentIndex(0)
        self.styleButton.currentIndexChanged.connect(self.styleButton_changed)

        # Initialize variables before they're called on (will add more if found)
        self.clear_graph = False
        self.rolled_manually = False
        self.ms_voice_muted = True
        self.cautious = False
        self.cautious_die = 0
        self.hasty = False
        self.hasty_die = 0
        self.extrahasty = False
        self.extrahasty_die = 0
        self.tih = False
        self.tih_die = 0
        self.tihButton_clicked()
        self.phantom_skillBox_checked = False
        self.rollButton.setDisabled(True)
        self.actionRoll_Dice.setDisabled(True)

        log.info('PyQt5 MainWindow initialized.')
        
        if __expired_tag__ == True:
            '''
            Beta for this app has expired!
            '''
            log.warning(__app__ + ' expiration detected...')
            self.alert_window()
            '''
            Display alert message and disable all the things
            '''
            self.taskDifficulty.setDisabled(True)
            self.variableDuration.setDisabled(True)
            self.diceType.setDisabled(True)
            self.rollaccuracyType.setDisabled(True)
            self.voiceBox.setDisabled(True)
            self.characteristic.setDisabled(True)
            self.phantom_char.setDisabled(True)
            self.skill.setDisabled(True)
            self.phantom_skill.setDisabled(True)
            self.modifier.setDisabled(True)
            self.cautiousButton.setDisabled(True)
            self.hastyButton.setDisabled(True)
            self.extrahastyButton.setDisabled(True)
            self.tihButton.setDisabled(True)
            self.rollButton.setDisabled(True)
            self.clear_rollButton.setDisabled(True)
            self.actionClear_Roll_History.setDisabled(True)
            self.clear_graphButton.setDisabled(True)
            self.clearButton.setDisabled(True)
            self.rollInput.setDisabled(True)
            self.rollBrowser.setDisabled(True)
            self.sampleBrowser.setDisabled(True)
            self.styleButton.setDisabled(True)
            self.actionAbout_Traveller5_Task_Roller.setDisabled(True)
            self.actionRoll_Dice.setDisabled(True)
            self.actionClear_Graph.setDisabled(True)
            self.actionClear_All.setDisabled(True)

    def taskDifficulty_changed(self):
        '''
        Clear values when Task Difficulty is changed
        '''
        self.num_dice = self.taskDifficulty.currentIndex() + 1
        self.diceType.setText(str(self.num_dice) + 'D')
        log.info('Task Difficulty: ' + self.taskDifficulty.currentText() + ' (' + str(self.num_dice) + 'D)')
        self.variableDuration.setCurrentIndex(0)
        self.characteristic.setValue(0)
        self.phantom_char.setChecked(False)
        self.skill.setValue(0)
        self.phantom_skill.setChecked(False)
        self.modifier.setValue(0)
        self.diceRoll.setText('')
        self.taskResult.setText('')
        self.rollInput.clear()
        self.cautious = False
        self.cautiousLabel.setText('')
        self.cautiousButton.setDisabled(False)
        self.cautious_die = 0
        self.hasty = False
        self.hastyLabel.setText('')
        self.hastyButton.setDisabled(False)
        self.hasty_die = 0
        self.extrahasty = False
        self.extrahastyLabel.setText('')
        self.extrahastyButton.setDisabled(False)
        self.extrahasty_die = 0
        self.tih = False
        self.tihLabel.setText('')
        self.tih_die = 0
        self.tihButton_clicked()
        self.clear_graph = True
        self.draw_graph()

    def variableDuration_changed(self):
        '''
        Ignore Task Duration if not selected (value 0)
        '''
        self.chosen_duration = self.variableDuration.currentIndex()
        log.info('Variable Duration: ' + self.variableDuration.currentText())

        if self.chosen_duration == 0:
            self.taskDuration.setText('')
            self.dice_were_rolled = False
        if self.dice_were_rolled:
            if self.chosen_duration == 1:
                self.taskDuration.setText(str(10 + roll('flux')) + ' Minutes')
            if self.chosen_duration == 2:
                self.taskDuration.setText(str(60 + roll('flux') * 10) + ' Minutes')
            if self.chosen_duration == 3:
                self.taskDuration.setText(str(10 + roll('flux')) + ' Hours')
            if self.chosen_duration == 4:
                self.taskDuration.setText(str(6 + roll('flux')) + ' Days')
            if self.chosen_duration == 5:
                self.taskDuration.setText(str(6 + roll('flux')) + ' Weeks')
        else:
            self.taskDuration.setText('')

    def rollaccuracyType_changed(self):
        '''
        Choose the accuracy of the roll chart
        '''
        self.roll_accuracy = int(roll_accuracies[self.rollaccuracyType.currentIndex()])
        log.info('Roll accuracy set to: ' + str(self.roll_accuracy))
            
    def characteristic_changed(self):
        '''
        Clear last roll result if characteristic is changed
        '''

        self.clear_graph = True
        self.draw_graph()

        if not self.phantom_skillBox_checked:
            self.skill.setValue(0)
        self.modifier.setValue(0)
        self.diceRoll.setText('')
        self.taskResult.setText('')
        self.rollInput.clear()
        
        # disable roll button if target number <= 0
        if self.characteristic.value() + self.skill.value() + self.modifier.value() <= 0:
            self.rollButton.setDisabled(True)
            self.actionRoll_Dice.setDisabled(True)
        else:
            self.rollButton.setDisabled(False)
            self.actionRoll_Dice.setDisabled(False)
    
    def skill_changed(self):
        '''
        Clear last roll result if skill is changed
        '''

        self.clear_graph = True
        self.draw_graph()

        self.modifier.setValue(0)
        self.diceRoll.setText('')
        self.taskResult.setText('')
        self.rollInput.clear()
        if self.skill.value() < self.num_dice:
            self.tih = False
            self.tihButton_clicked()
        else:
            self.tih = True
            self.tihButton_clicked()
    
        # disable roll button if target number <= 0
        if self.characteristic.value() + self.skill.value() + self.modifier.value() <= 0:
            self.rollButton.setDisabled(True)
            self.actionRoll_Dice.setDisabled(True)
        else:
            self.rollButton.setDisabled(False)
            self.actionRoll_Dice.setDisabled(False)
    
    def modifier_changed(self):
        '''
        Clear last roll result if modifier is changed
        '''

        self.clear_graph = True
        self.draw_graph()

        self.diceRoll.setText('')
        self.taskResult.setText('')
        self.rollInput.clear()

        # disable roll button if target number <= 0
        if self.characteristic.value() + self.skill.value() + self.modifier.value() <= 0:
            self.rollButton.setDisabled(True)
            self.actionRoll_Dice.setDisabled(True)
        else:
            self.rollButton.setDisabled(False)
            self.actionRoll_Dice.setDisabled(False)

    def cautiousButton_clicked(self):
        '''
        Cautious has been pressed
        '''
        if self.cautious:
            self.cautious = False
            self.cautiousLabel.setText('')
            self.cautious_die = 0
            self.hastyButton.setDisabled(False)
            self.extrahastyButton.setDisabled(False)
        else:
            self.cautious = True
            self.cautiousLabel.setText('-1D')
            self.cautious_die = -1
            self.hastyButton.setDisabled(True)
            self.extrahastyButton.setDisabled(True)
        self.hasty = False
        self.hastyLabel.setText('')
        self.hasty_die = 0
        self.extrahasty = False
        self.extrahastyLabel.setText('')
        self.extrahasty_die = 0

        # Update variable duration if not optional
        self.chosen_duration = self.variableDuration.currentIndex()
        if self.chosen_duration != 0:
            if not self.cautious:
                if self.chosen_duration > 1:
                    self.variableDuration.setCurrentIndex(self.chosen_duration - 1)
            if self.cautious:
                if self.chosen_duration < 5:
                    self.variableDuration.setCurrentIndex(self.chosen_duration + 1)
    
    def hastyButton_clicked(self):
        '''
        Hasty has been pressed
        '''
        if self.hasty:
            self.hasty = False
            self.hastyLabel.setText('')
            self.hasty_die = 0
            self.cautiousButton.setDisabled(False)
            self.extrahastyButton.setDisabled(False)
        else:
            self.hasty = True
            self.hastyLabel.setText('+1D')
            self.hasty_die = 1
            self.cautiousButton.setDisabled(True)
            self.extrahastyButton.setDisabled(True)
        self.cautious = False
        self.cautiousLabel.setText('')
        self.cautious_die = 0
        self.extrahasty = False
        self.extrahastyLabel.setText('')
        self.extrahasty_die = 0

        # Update variable duration if not optional
        self.chosen_duration = self.variableDuration.currentIndex()
        if self.chosen_duration != 0:
            if self.hasty:
                if self.chosen_duration > 1:
                    self.variableDuration.setCurrentIndex(self.chosen_duration - 1)
            if not self.hasty:
                if self.chosen_duration < 5:
                    self.variableDuration.setCurrentIndex(self.chosen_duration + 1)
    
    def extrahastyButton_clicked(self):
        '''
        Extra Hasty has been pressed
        '''
        if self.extrahasty:
            self.extrahasty = False
            self.extrahastyLabel.setText('')
            self.extrahasty_die = 0
            self.cautiousButton.setDisabled(False)
            self.hastyButton.setDisabled(False)
        else:
            self.extrahasty = True
            self.extrahastyLabel.setText('+2D')
            self.extrahasty_die = 2
            self.cautiousButton.setDisabled(True)
            self.hastyButton.setDisabled(True)
        self.cautious = False
        self.cautiousLabel.setText('')
        self.cautious_die = 0
        self.hasty = False
        self.hastyLabel.setText('')
        self.hasty_die = 0

        # Update variable duration if not optional
        self.chosen_duration = self.variableDuration.currentIndex()
        if self.chosen_duration != 0:
            if self.extrahasty:
                if self.chosen_duration > 2:
                    self.variableDuration.setCurrentIndex(self.chosen_duration - 2)
            if not self.extrahasty:
                if self.chosen_duration < 4:
                    self.variableDuration.setCurrentIndex(self.chosen_duration + 2)

    def tihButton_clicked(self):
        '''
        This is Hard! has been pressed
        '''
        if self.tih:
            self.tih = False
            self.tihLabel.setText('')
            self.tih_die = 0
        else:
            self.tih = True
            self.tihLabel.setText('<span style=" color:#ff0000;">+1D!</span>')
            self.tih_die = 1
    
    def fluxButton_clicked(self):
        '''
        Do a Flux roll
        '''
        self.clear_graph = False
        self.rolled_manually = False
        self.dice_type = 'FLUX'
        log.debug('Rolling ' + self.dice_type)
        roll_returned = roll(self.dice_type)
        returned_line = self.dice_type + ' = ' + str(roll_returned)
                
        # Display the roll result inside the text browser
        self.rollBrowser.append(returned_line)
        sample = '[ '
        for x in range(10):
            sample += str(roll(self.dice_type)) + ' '
        sample += ']'
        self.sampleBrowser.clear()
        self.sampleBrowser.append(sample)
        log.info('Sample for die type: ' + sample)
        self.roll_result = roll_returned
        self.diceRoll.setText('')
        self.taskResult.setText('')
        if not self.ms_voice_muted:
            engine.say('Calculating ' + self.dice_type)
            engine.runAndWait()
        self.bar_color = 'black'
        self.draw_graph()
        if not self.ms_voice_muted:
            engine.say(str(self.roll_result))
            engine.runAndWait()

    def goodfluxButton_clicked(self):
        '''
        Do a Good Flux roll
        '''
        self.clear_graph = False
        self.rolled_manually = False
        self.dice_type = 'GOOD FLUX'
        log.debug('Rolling ' + self.dice_type)
        roll_returned = roll(self.dice_type)
        returned_line = self.dice_type + ' = ' + str(roll_returned)
                
        # Display the roll result inside the text browser
        self.rollBrowser.append(returned_line)
        sample = '[ '
        for x in range(10):
            sample += str(roll(self.dice_type)) + ' '
        sample += ']'
        self.sampleBrowser.clear()
        self.sampleBrowser.append(sample)
        log.info('Sample for die type: ' + sample)
        self.roll_result = roll_returned
        self.diceRoll.setText('')
        self.taskResult.setText('')
        if not self.ms_voice_muted:
            engine.say('Calculating ' + self.dice_type)
            engine.runAndWait()
        self.bar_color = 'black'
        self.draw_graph()
        if not self.ms_voice_muted:
            engine.say(str(self.roll_result))
            engine.runAndWait()

    def badfluxButton_clicked(self):
        '''
        Do a Bad Flux roll
        '''
        self.clear_graph = False
        self.rolled_manually = False
        self.dice_type = 'BAD FLUX'
        log.debug('Rolling ' + self.dice_type)
        roll_returned = roll(self.dice_type)
        returned_line = self.dice_type + ' = ' + str(roll_returned)
                
        # Display the roll result inside the text browser
        self.rollBrowser.append(returned_line)
        sample = '[ '
        for x in range(10):
            sample += str(roll(self.dice_type)) + ' '
        sample += ']'
        self.sampleBrowser.clear()
        self.sampleBrowser.append(sample)
        log.info('Sample for die type: ' + sample)
        self.roll_result = roll_returned
        self.diceRoll.setText('')
        self.taskResult.setText('')
        if not self.ms_voice_muted:
            engine.say('Calculating ' + self.dice_type)
            engine.runAndWait()
        self.bar_color = 'black'
        self.draw_graph()
        if not self.ms_voice_muted:
            engine.say(str(self.roll_result))
            engine.runAndWait()

    def rollButton_clicked(self):
        '''
        Roll button was clicked.
        Try to roll under or equal to the characteristic asset + skills asset + modifiers.
        '''
        self.die_pool = self.num_dice
        log.info('Starting die pool: ' + str(self.num_dice) + 'D')

        # Cautious?
        if self.cautious == True:
            self.die_pool += self.cautious_die
            log.info('Cautious die: ' + str(self.cautious_die))
        
        # Hasty?
        if self.hasty == True:
            self.die_pool += self.hasty_die
            log.info('Hasty die: ' + str(self.hasty_die))
        
        # Extra Hasty?
        if self.extrahasty == True:
            self.die_pool += self.extrahasty_die
            log.info('Extra Hasty die: ' + str(self.extrahasty_die))
        
        # TIH!?
        if self.tih == True:
            self.die_pool += self.tih_die
            log.info('TIH! die: ' + str(self.tih_die))
        
        log.info('Total die pool: ' + str(self.die_pool) + 'D')

        # Display Task Duration if one was chosen
        self.dice_were_rolled = True
        self.variableDuration_changed()
        self.dice_were_rolled = False

        #Auto success?
        if self.die_pool > 0:
            # No.
            self.dice_type = str(self.die_pool) + 'D'

            self.value_to_beat = self.characteristic.value() + self.skill.value() + self.modifier.value()
            log.info('Value to beat: ' + str(self.characteristic.value()) + ' + ' + str(self.skill.value()) + ' + ' + str(self.modifier.value()))
            #self.roll_result = roll(self.dice_type + '# roll made')
            self.roll_result = 0
            number_of_sixes = 0
            number_of_ones = 0
            for i in range(self.die_pool):
                number_rolled = roll('1D # part of die pool')
                self.roll_result += number_rolled
                if number_rolled == 6:
                    number_of_sixes += 1
                if number_rolled == 1:
                    number_of_ones += 1
            self.diceRoll.setText(str(self.roll_result))
            log.info('Rolled: ' + str(self.roll_result))
            if number_of_ones == 3 and number_of_sixes == 3:
                temp = 'Spectacularly\nInteresting!'
                self.bar_color = 'y'
                log.info('Task is spectacularly interesting!')
            elif number_of_ones == 3:
                temp = 'Spectacular\nSuccess!'
                self.bar_color = 'g'
                log.info('Task is a spectacular success!')
            elif number_of_sixes == 3:
                temp = 'Spectacular\nFailure!'
                self.bar_color = 'r'
                log.info('Task is a spectacular failure!')
            elif self.roll_result <= self.value_to_beat:
                temp = 'Succeeded'
                self.bar_color = 'g'
                log.info('Task succeeded!')
            else:
                temp = 'Failed'
                self.bar_color = 'r'
                log.info('Task failed!')
            self.taskResult.setText(temp)
            self.rollBrowser.append(self.dice_type + ' = ' + self.diceRoll.text())
            sample = '[ '
            for x in range(10):
                sample += str(roll(self.dice_type)) + ' '
            sample += ']'
            self.sampleBrowser.clear()
            self.sampleBrowser.append(sample)
            log.info('Sample for die type: ' + sample)
            self.rollInput.clear()
            if not self.ms_voice_muted:
                engine.say('Rolling ' + self.dice_type)
                engine.runAndWait()
            self.draw_graph()
            if not self.ms_voice_muted:
                engine.say(temp)
                engine.runAndWait()
        else:
            # Yes.
            log.info('0D roll. Auto success!')
            self.taskResult.setText('Succeeded')
            self.clear_graph = True
            self.draw_graph()
            if not self.ms_voice_muted:
                engine.say('automatically succeeded')
                engine.runAndWait()
    
    def manual_roll(self):
        '''
        A roll was inputed manually
        '''
        dice_entered = self.rollInput.text()
        dice_entered = dice_entered.upper()
        self.manual_dice_entered = dice_entered
        if dice_entered == 'INFO' or dice_entered == 'TEST' or dice_entered == 'MINMAXAVG' or dice_entered == 'HEX' or dice_entered == 'EHEX':
            roll_returned = roll(dice_entered)
        else:
            log.debug('Rolling manually.')
            roll_returned = roll(dice_entered)
            
            # Was the roll a valid one?
            if roll_returned == -9999:
                returned_line = dice_entered + ' = ' + '<span style=" color:#ff0000;">' + str(roll_returned) + '</span>'
            else:
                returned_line = dice_entered + ' = ' + str(roll_returned)
                
            # Display the roll result inside the text browser
            self.rollBrowser.append(returned_line)
            if roll_returned != -9999:
                sample = '[ '
                for x in range(10):
                    sample += str(roll(dice_entered)) + ' '
                sample += ']'
            else:
                sample = ''
            self.sampleBrowser.clear()
            self.sampleBrowser.append(sample)
            log.info('Sample for die type: ' + sample)
            self.roll_result = roll_returned
            self.diceRoll.setText('')
            self.taskResult.setText('')
            self.rolled_manually = True
            if self.roll_result != -9999:
                if not self.ms_voice_muted:
                    engine.say('Calculating ' + dice_entered)
                    engine.runAndWait()
                self.bar_color = 'black'
                self.draw_graph()
                if not self.ms_voice_muted:
                    engine.say(str(self.roll_result))
                    engine.runAndWait()
            else:
                if not self.ms_voice_muted:
                    engine.say('invalid input')
                    engine.runAndWait()
                self.clear_graph = True
                self.draw_graph()
    
    def phantom_char_toggled(self):
        self.phantom_charBox_checked = self.phantom_char.isChecked()
        if self.phantom_charBox_checked:
            self.characteristic.setValue(7)
            self.characteristic.setDisabled(True)
        else:
            self.characteristic.setValue(0)
            self.characteristic.setDisabled(False)

    def phantom_skill_toggled(self):
        self.phantom_skillBox_checked = self.phantom_skill.isChecked()
        if self.phantom_skillBox_checked:
            self.skill.setValue(3)
            self.skill.setDisabled(True)
        else:
            self.skill.setValue(0)
            self.skill.setDisabled(False)
    
    def clear_rollButton_clicked(self):
        '''
        Clear the roll history
        '''
        self.rollInput.clear()
        self.rollBrowser.clear()
        self.sampleBrowser.clear()
    
    def clear_graphButton_clicked(self):
        '''
        Clear the graph
        '''
        self.clear_graph = True
        self.draw_graph()

    def clear_allButton_clicked(self):
        '''
        Clear/reset all fields
        '''
        self.taskDifficulty.setCurrentIndex(1)
        self.characteristic.setValue(0)
        self.phantom_char.setChecked(False)
        self.skill.setValue(0)
        self.phantom_skill.setChecked(False)
        self.modifier.setValue(0)
        self.diceRoll.setText('')
        self.taskResult.setText('')
        self.rollInput.clear()
        self.rollBrowser.clear()
        self.sampleBrowser.clear()
        self.cautious = False
        self.cautiousLabel.setText('')
        self.cautiousButton.setDisabled(False)
        self.cautious_die = 0
        self.hasty = False
        self.hastyLabel.setText('')
        self.hastyButton.setDisabled(False)
        self.hasty_die = 0
        self.extrahasty = False
        self.extrahastyLabel.setText('')
        self.extrahastyButton.setDisabled(False)
        self.extrahasty_die = 0
        self.tih = True
        self.tihLabel.setText('<span style=" color:#ff0000;">+1D!</span>')
        self.tih_die = 1
        self.clear_graph = True
        self.draw_graph()
        
    def actionAbout_triggered(self):
        '''
        Display the About window
        '''
        self.popAboutDialog.show()
    
    def alert_window(self):
        '''
        open the Alert window
        '''
        log.warning(__app__ + ' show Beta expired PyQt5 alertDialog...')
        self.popAlertDialog.show()
    
    def draw_graph(self):
        '''
        Graph button was clicked.
        Construct the string argument needed for graphing (if a valid roll type).
        '''
        if self.clear_graph:
            #print('clear graph')
            xper_range = ''
            yper_range = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            percent = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            bar_height = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            die_range = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            max_percent = len(yper_range)

            self.mpl.canvas.ax.clear()
            self.mpl.canvas.ax.bar(np.arange(len(die_range)), percent, width=0.6, alpha=.3, color='b')
            self.mpl.canvas.ax.set_xlim(xmin=-0.25, xmax=len(die_range)-0.75)
            self.mpl.canvas.ax.set_xticks(range(len(die_range)))
            self.mpl.canvas.ax.set_xticklabels(die_range)
            #ticks_font = font_manager.FontProperties(family='Optima', style='normal', size=6, weight='normal', stretch='normal')
            ticks_font = font_manager.FontProperties(style='normal', size=6, weight='normal', stretch='normal')
            for label in self.mpl.canvas.ax.get_xticklabels():
                label.set_fontproperties(ticks_font)
            #title_font = font_manager.FontProperties(family='Optima', style='normal', size=10, weight='normal', stretch='normal')
            title_font = font_manager.FontProperties(style='normal', size=10, weight='normal', stretch='normal')
            label = self.mpl.canvas.ax.set_title(xper_range)
            label.set_fontproperties(title_font)
            self.mpl.canvas.ax.set_yticks(range(0, max_percent, 1))
            self.mpl.canvas.ax.set_yticklabels(yper_range)
            #ticks_font = font_manager.FontProperties(family='Optima', style='normal', size=6, weight='normal', stretch='normal')
            ticks_font = font_manager.FontProperties(style='normal', size=6, weight='normal', stretch='normal')
            for label in self.mpl.canvas.ax.get_yticklabels():
                label.set_fontproperties(ticks_font)
            #ylabel_font = font_manager.FontProperties(family='Optima', style='normal', size=10, weight='normal', stretch='normal')
            ylabel_font = font_manager.FontProperties(style='normal', size=10, weight='normal', stretch='normal')
            #self.mpl.canvas.ax.set_ylabel('Percentages')
            label = self.mpl.canvas.ax.set_ylabel('Percentages')
            label.set_fontproperties(ylabel_font)
            #self.mpl.canvas.ax.get_xaxis().grid(True)
            self.mpl.canvas.ax.get_yaxis().grid(True)
            
            self.mpl.canvas.draw()

            log.debug('Graph Cleared')
            self.clear_graph = False
            self.rolled_manually = False

        else:
            if self.rolled_manually:
                self.dice_type = self.manual_dice_entered
                self.rolled_manually = False
            print('dice_type:', self.dice_type)
            
            die_range = []
            percent = []
            bar_height = []
            min_die_roll = 99999
            max_die_roll = -99999
            
# calculate the range of the die rolls (using a smaple of 10000 rolls)

            for i in range(self.roll_accuracy):
                rolled_value = roll(self.dice_type)
                if min_die_roll > rolled_value:
                    min_die_roll = rolled_value
                if max_die_roll < rolled_value:
                    max_die_roll = rolled_value
            print(min_die_roll, '-', max_die_roll)
            
            for i in range(min_die_roll, max_die_roll + 1):
                die_range.append(i)
                percent.append(0)
                bar_height.append(0)
            
            if self.dice_type == 'D44' or self.dice_type == 'D66' or self.dice_type == 'D88' or self.dice_type.find('S6') != -1 \
                or self.dice_type.find('S10') != -1:
                print('No die_range')
                print('No mean_avg')
            else:
            
# calculate the mean average for die_range

                print('die_range:', die_range)
                j = 0
                for i in range(len(die_range)):
                    j += die_range[i]
                print('mean_avg:', j / len(die_range))
            
            n = self.roll_accuracy
            num_errors = 0
            
# calculate the percentage for each die roll (using a sample of n=10000 rolls)

            for i in range(n):
                roll_not_in_range = True
                while roll_not_in_range:
                    temp = roll(self.dice_type)
                    if temp >= min_die_roll and temp <= max_die_roll:
                        percent[temp - min_die_roll] += 1
                        roll_not_in_range = False
                    else:
                        # we just rolled ouside of our calculated die roll range, so don't count that one
                        print("Index error:", temp)
                        num_errors += 1
            print('num_errors:', num_errors)
            
            max_percent = 0
            
            for i in range(len(die_range)):
                percent[i] = percent[i] * 100. / (n - num_errors)
                if percent[i] > max_percent:
                    max_percent = int(percent[i]) + 3
            
            yper_range = range(0, max_percent)
            print('yper_range:', list(yper_range))
            print('percent:', percent)
            
            log.debug('Generate ' + self.dice_type + ' graph')
            
            xper_range = self.dice_type + ' Roll'

            for i in range(len(percent)):
                if i + min_die_roll == self.roll_result:
                    bar_height[i] = percent[i]

            print('bar_height:',bar_height)
            print()

            self.mpl.canvas.ax.clear()
            self.mpl.canvas.ax.bar(np.arange(len(die_range)), percent, width=0.6, alpha=.3, color='b')
            self.mpl.canvas.ax.set_xlim(xmin=-0.25, xmax=len(die_range)-0.75)
            self.mpl.canvas.ax.set_xticks(range(len(die_range)))
            self.mpl.canvas.ax.set_xticklabels(die_range)
            #ticks_font = font_manager.FontProperties(family='Optima', style='normal', size=6, weight='normal', stretch='normal')
            ticks_font = font_manager.FontProperties(style='normal', size=6, weight='normal', stretch='normal')
            for label in self.mpl.canvas.ax.get_xticklabels():
                label.set_fontproperties(ticks_font)
            #title_font = font_manager.FontProperties(family='Optima', style='normal', size=10, weight='normal', stretch='normal')
            title_font = font_manager.FontProperties(style='normal', size=10, weight='normal', stretch='normal')
            label = self.mpl.canvas.ax.set_title(xper_range)
            label.set_fontproperties(title_font)
            self.mpl.canvas.ax.set_yticks(range(0, max_percent, 1))
            self.mpl.canvas.ax.set_yticklabels(yper_range)
            #ticks_font = font_manager.FontProperties(family='Optima', style='normal', size=6, weight='normal', stretch='normal')
            ticks_font = font_manager.FontProperties(style='normal', size=6, weight='normal', stretch='normal')
            for label in self.mpl.canvas.ax.get_yticklabels():
                label.set_fontproperties(ticks_font)
            #ylabel_font = font_manager.FontProperties(family='Optima', style='normal', size=10, weight='normal', stretch='normal')
            ylabel_font = font_manager.FontProperties(style='normal', size=10, weight='normal', stretch='normal')
            #self.mpl.canvas.ax.set_ylabel('Percentages')
            label = self.mpl.canvas.ax.set_ylabel('Percentages')
            label.set_fontproperties(ylabel_font)
            #self.mpl.canvas.ax.get_xaxis().grid(True)
            self.mpl.canvas.ax.get_yaxis().grid(True)

            self.mpl.canvas.ax.bar(np.arange(len(die_range)), bar_height, width=0.6, alpha=1.0, color=self.bar_color)
            self.mpl.canvas.ax.set_xlim(xmin=-0.25, xmax=len(die_range)-0.75)
            self.mpl.canvas.ax.set_xticks(range(len(die_range)))
            self.mpl.canvas.ax.set_xticklabels(die_range)
            #ticks_font = font_manager.FontProperties(family='Optima', style='normal', size=6, weight='normal', stretch='normal')
            ticks_font = font_manager.FontProperties(style='normal', size=6, weight='normal', stretch='normal')
            for label in self.mpl.canvas.ax.get_xticklabels():
                label.set_fontproperties(ticks_font)
            #title_font = font_manager.FontProperties(family='Optima', style='normal', size=10, weight='normal', stretch='normal')
            title_font = font_manager.FontProperties(style='normal', size=10, weight='normal', stretch='normal')
            label = self.mpl.canvas.ax.set_title(xper_range)
            label.set_fontproperties(title_font)
            self.mpl.canvas.ax.set_yticks(range(0, max_percent, 1))
            self.mpl.canvas.ax.set_yticklabels(yper_range)
            #ticks_font = font_manager.FontProperties(family='Optima', style='normal', size=6, weight='normal', stretch='normal')
            ticks_font = font_manager.FontProperties(style='normal', size=6, weight='normal', stretch='normal')
            for label in self.mpl.canvas.ax.get_yticklabels():
                label.set_fontproperties(ticks_font)
            #ylabel_font = font_manager.FontProperties(family='Optima', style='normal', size=10, weight='normal', stretch='normal')
            ylabel_font = font_manager.FontProperties(style='normal', size=10, weight='normal', stretch='normal')
            #self.mpl.canvas.ax.set_ylabel('Percentages')
            label = self.mpl.canvas.ax.set_ylabel('Percentages')
            label.set_fontproperties(ylabel_font)
            #self.mpl.canvas.ax.get_xaxis().grid(True)
            self.mpl.canvas.ax.get_yaxis().grid(True)

            self.mpl.canvas.draw()

    def voiceBox_changed(self):
        '''
        Was a text-to-speech voice selected?
        '''
        speaker = voices[self.voiceBox.currentIndex()]
        if speaker == 'Mute Voice':
            self.ms_voice_muted = True
        else:
            self.ms_voice_muted = False
            engine.setProperty('rate', rate + voice[speaker]['Rate'])
            engine.setProperty('volume', volume + voice[speaker]['Volume'])
            engine.setProperty('voice', voice[speaker]['Name'])
    
    def styleButton_changed(self):
        '''
        A style was chosen
        '''
        chosen_style = self.styles_installed[self.styleButton.currentIndex()]
        QApplication.setStyle(chosen_style)
        log.info('Chosen style: ' + chosen_style)

    def quitButton_clicked(self):
        '''
        Exit this app (using task tray icon)
        '''
        self.close()
        
    def activate(self, reason):
        '''
        Toggle showing/hiding the app when clicking the system tray icon
        '''
        if reason == QSystemTrayIcon.Trigger:  # systray icon clicked.
            if self.isVisible():
                self.hide()
            else:
                self.show()
    
    def display_app(self, reason):
        '''
        Use task tray icon menu to display app
        '''
        self.show()
    
    def hide_app(self, reason):
        '''
        Use task tray icon menu to hide app
        '''
        self.hide()
        
        
if __name__ == '__main__':

    '''
    Technically, this program starts right here when run.
    If this program is imported instead of run, none of the code below is executed.
    '''

#     logging.basicConfig(filename = 'Traveller5_Task_Roller.log',
#                         level = logging.DEBUG,
#                         format = '%(asctime)s %(levelname)s %(name)s - %(message)s',
#                         datefmt='%a, %d %b %Y %H:%M:%S',
#                         filemode = 'w')

    log = logging.getLogger('Traveller5 Task Roller')
    log.setLevel(logging.INFO)
    #log.setLevel(logging.DEBUG)
    #log.setLevel(logging.WARNING)

    if not os.path.exists('Logs'):
        os.mkdir('Logs')
    
    fh = logging.FileHandler('Logs/Traveller5_Task_Roller.log', 'w')
 
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s - %(message)s', datefmt = '%a, %d %b %Y %H:%M:%S')
    fh.setFormatter(formatter)
    log.addHandler(fh)

    log.info('Logging started.')
    log.info(__app__ + ' starting...')

    trange = time.localtime()

    log.info(__app__ + ' started, and running...')
    
    if len(sys.argv) < 2:

        if trange[0] > 2024 or trange[1] > 12:
            __expired_tag__ = True
            __app__ += ' [EXPIRED]'

        app = QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(True)
        
        #print(QStyleFactory.keys()) #use to find a different setStyle
        
        #app.setStyle('Fusion')
        
        # darkPalette = QPalette()
        # darkPalette.setColor(QPalette.Window, QColor(53, 53, 53))
        # darkPalette.setColor(QPalette.WindowText, Qt.white)
        # darkPalette.setColor(QPalette.Disabled, QPalette.WindowText, QColor(127, 127, 127))
        # darkPalette.setColor(QPalette.Base, QColor(42, 42, 42))
        # darkPalette.setColor(QPalette.AlternateBase, QColor(66, 66, 66))
        # darkPalette.setColor(QPalette.ToolTipBase, Qt.white)
        # darkPalette.setColor(QPalette.ToolTipText, Qt.white)
        # darkPalette.setColor(QPalette.Text, Qt.white)
        # darkPalette.setColor(QPalette.Disabled, QPalette.Text, QColor(127, 127, 127))
        # darkPalette.setColor(QPalette.Dark, QColor(35, 35, 35))
        # darkPalette.setColor(QPalette.Shadow, QColor(20, 20, 20))
        # darkPalette.setColor(QPalette.Button, QColor(53, 53, 53))
        # darkPalette.setColor(QPalette.ButtonText, Qt.white)
        # darkPalette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(127, 127, 127))
        # darkPalette.setColor(QPalette.BrightText, Qt.red)
        # darkPalette.setColor(QPalette.Link, QColor(42, 130, 218))
        # darkPalette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        # darkPalette.setColor(QPalette.Disabled, QPalette.Highlight, QColor(80, 80, 80))
        # darkPalette.setColor(QPalette.HighlightedText, Qt.white)
        # darkPalette.setColor(QPalette.Disabled, QPalette.HighlightedText, QColor(127, 127, 127))
        
        MainApp = MainWindow()
        MainApp.show()
        
        #app.setPalette(darkPalette)
        
        # Create the systray icon
        icon = QIcon(":/icons/t5_die_icon.ico")
        
        # Create the systray
        tray = QSystemTrayIcon()
        tray.setIcon(icon)
        tray.setVisible(True)
        
        # Create the systray menu
        menu = QMenu()
        
        showApp = QAction("Show App")
        showApp.triggered.connect(MainApp.display_app)
        menu.addAction(showApp)
        
        hideApp = QAction("Hide App")
        hideApp.triggered.connect(MainApp.hide_app)
        menu.addAction(hideApp)

        quit = QAction("Exit")
        quit.triggered.connect(app.quit)
        menu.addAction(quit)
        
        tray.setToolTip("Traveller5 Task Roller")
        
        # Add the menu to the tray
        tray.setContextMenu(menu)
        
        tray.activated.connect(MainApp.activate)
        
        app.exec_()
    
    elif trange[0] > 2024 or trange[1] > 12:
        __app__ += ' [EXPIRED]'
        '''
        Beta for this app has expired!
        '''
        log.warning(__app__)
        print()
        print(__app__)
        
    elif sys.argv[1] in ['-h', '/h', '--help', '-?', '/?']:
        log.info('Traveller5 Task Roller was run from the CMD prompt.  Help will be sent if needed.')
        print()
        print('     Using the CMD prompt to make dice rolls:')
        print("     C:\>traveller5_task_roller.py roll('2d6')")
        print()
        print('     Or just:')
        print('     C:\>traveller5_task_roller.py 2d6')
    elif sys.argv[1] in ['-v', '/v', '--version']:
        print()
        print('     Traveller5 Task Roller, release version ' + __version__ + ' for Python ' + str(__py_version_req__))
        log.info('Reporting: Traveller5 Task Roller release version: %s' % __version__)
    else:
        print()
        dice = ''
        if len(sys.argv) > 2:
            for i in range(len(sys.argv)):
                if i > 0:
                    dice += sys.argv[i]
        else:
            dice = sys.argv[1]
        if "roll('" in dice:
            num = dice.find("')")
            if num != -1:
                dice = dice[6:num]
                dice = str(dice).upper().strip()
                if dice == '':
                    dice = '2D6'
                    log.debug('Default roll was made')
                num = roll(dice)
                if dice != 'TEST' and dice != 'INFO' and dice != 'MINMAXAVG':
                    print("Your '%s' roll is %s." % (dice, num))
                    log.info("The direct call to Traveller5 Task Roller with '%s' resulted in %s." % (dice, num))
                elif dice == 'INFO':
                    print('Traveller5 Task Roller, release version ' + __version__ + ' for Python ' + str(__py_version_req__))
                    log.info('Reporting: Traveller5 Task Roller release version: %s' % __version__)
            else:
                print('Typo of some sort --> ' + dice)
        else:
            dice = str(dice).upper().strip()
            if dice == 'ROLL()':
                dice = '2D6'
                log.debug('Default roll was made')
            num = roll(dice)
            if dice != 'TEST' and dice != 'INFO' and dice != 'MINMAXAVG':
                print("Your '%s' roll is %s." % (dice, num))
                log.info("The direct call to Traveller5 Task Roller with '%s' resulted in %s." % (dice, num))
            elif dice == 'INFO':
                print('Traveller5 Task Roller, release version ' + __version__ + ' for Python ' + str(__py_version_req__))
                log.info('Reporting: Traveller5 Task Roller release version: %s' % __version__)
                