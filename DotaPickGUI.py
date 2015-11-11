'''
Created on Nov 5, 2015

@author: Kevin
'''
from tkinter import *
import json
import math
import numpy as np
from operator import itemgetter
maxHero = 112

# Logistic function
def logistic(num):
    return 1/(1+math.pow(math.e,-num))

# Logit funciton (inverse logistic)
def logit(num):
    if num == 0:
        return float('nan')
    return -math.log((1-num)/num)

def heroes():
    with open('heroes.json') as f:
        data = json.load(f)
    heroDict = {}
    for entry in data['heroes']:
        heroDict[entry['localized_name']] =int( entry['id'])
    return heroDict

def loadStats(fileName):
    statFile = open(fileName)
    stats = []
    fileLine = statFile.readline()
    while fileLine != '':
        stats.append([float('nan') if x =='-1' else float(x) for x in fileLine.split(',')])
        fileLine = statFile.readline()
    return stats

def removeHeroes(heroList,remList):
    for hero in remList:
        heroList.remove(hero)

class DotaPickApp(object):
    '''
    Application for finding picks and counter picks to Dota 2 lineups
    '''
    def addAlly(self):
        ally = self.heroList.get(self.heroList.curselection()[0])
        self.allyList.insert(END,ally)
        self.updateStats()
    
    def addEnemy(self):
        enemy = self.heroList.get(self.heroList.curselection()[0])
        self.enemyList.insert(END,enemy)
        self.updateStats()

    def addBan(self):
        ban = self.heroList.get(self.heroList.curselection()[0])
        self.banList.insert(END,ban)
        self.updateStats()
        
    def remAlly(self):
        self.allyList.delete(self.allyList.curselection()[0])
        self.updateStats()
        
    def remEnemy(self):
        self.enemyList.delete(self.enemyList.curselection()[0])
        self.updateStats()
    
    def remBan(self):
        self.banList.delete(self.banList.curselection()[0])
        self.updateStats()
    
    def remAll(self):
        self.banList.delete(0,END)
        self.enemyList.delete(0,END)
        self.allyList.delete(0,END)
        self.updateStats()

    def allyStatYView(self, *args):
        self.allyStatHero.yview(*args)
        self.allyStatStat.yview(*args)
        
    def baseInfo(self):
        heroDict = heroes()
        heroIndDict = {ind-1:key for key,ind in heroDict.items()}
        
        heroWin = []
        for ind in range(maxHero):
            try:
                if not math.isnan(self.baseStats[ind]):
                    heroWin.append((self.baseStats[ind],heroIndDict[ind]))
            except KeyError:
                pass
        heroWin = sorted(heroWin,key=itemgetter(0), reverse = True)
        
        return heroWin
        
    def winRateInfo(self):
        
        global maxHero
        heroDict = heroes()
        heroIndDict = {ind-1:key for key,ind in heroDict.items()}
                       
        stats = np.array([0.0 for x in range(maxHero)])
        
        heroFlag = False
        for hero in self.allyList.get(0,END):
            stats += np.array([logit(x) for x in self.allyStats[heroDict[hero]-1]])
            heroFlag = True
        for hero in self.enemyList.get(0,END):
            stats += [logit(x) for x in self.enemyStats[heroDict[hero]-1]]
            heroFlag = True
        
        if heroFlag:
            heroWin = []
            for ind in range(maxHero):
                try:
                    if not math.isnan(stats[ind]):
                        heroWin.append((logistic(stats[ind]),heroIndDict[ind]))
                except KeyError:
                    pass
            
            heroWin = sorted(heroWin,key=itemgetter(0), reverse = True)
        else:
            heroWin = self.baseInfo()
        return heroWin
    
    def advantageInfo(self):
        global maxHero
        heroDict = heroes()
        heroIndDict = {ind-1:key for key,ind in heroDict.items()}
                       
        stats = np.array([0.0 for x in range(maxHero)])
        
        heroBase = np.array([logit(x) for x in self.baseStats])
        for hero in self.allyList.get(0,END):
            allyBase = logit(self.baseStats[heroDict[hero]-1])
            comboStat = np.array([logit(x) for x in self.allyStats[heroDict[hero]-1]]) 
            stats += comboStat - (allyBase + heroBase)
        for hero in self.enemyList.get(0,END):
            enemyBase = logit(1-self.baseStats[heroDict[hero]-1])
            comboStat = np.array([logit(x) for x in self.enemyStats[heroDict[hero]-1]])
            stats += comboStat - (enemyBase + heroBase)
        
        heroWin = []
        for ind in range(maxHero):
            try:
                if not math.isnan(stats[ind]):
                    heroWin.append((stats[ind],heroIndDict[ind]))
            except KeyError:
                pass
        
        heroWin = sorted(heroWin,key=itemgetter(0), reverse = True)
        return heroWin
    
    def updateStats(self):
        ignoreHero = {}
        for hero in self.allyList.get(0,END):
            ignoreHero[hero]=1
        for hero in self.enemyList.get(0,END):
            ignoreHero[hero]=1
        for hero in self.banList.get(0,END):
            ignoreHero[hero]=1
                
        if self.mode.get():
            heroStats = self.advantageInfo()
        else:
            heroStats = self.winRateInfo()
            
         
        self.allyStatHero.delete(0,END)
        self.allyStatStat.delete(0,END)
        for (winRate,hero) in heroStats:
            self.allyStatHero.insert(END,hero)
            self.allyStatStat.insert(END,"{:.2f}".format(winRate*100))
            '''
            try:
                ignoreHero[hero]
            except KeyError:
                if winRate != float('nan') and hero != '':
                    self.allyStatHero.insert(END,hero)
                    self.allyStatStat.insert(END,"{:.2f}".format(winRate*100))
            '''
        
    def __init__(self, parent):
        '''
        Constructor to initialize the application
        '''
        self.enemyStats = loadStats('counterStats.csv')
        self.allyStats = loadStats('allyStats.csv')
        self.baseStats = loadStats('baseStats.csv')[0]
        
        heroDict = heroes()
        heroList = [str(key) for key in heroDict.keys()]
        heroList.sort()
        
        self.heroContainer = Frame(parent)
        self.heroScrollbar = Scrollbar(self.heroContainer)
        self.heroScrollbar.pack(side=RIGHT,fill=Y)
        self.heroList = Listbox(self.heroContainer,yscrollcommand=self.heroScrollbar.set)
        for hero in heroList:
            self.heroList.insert(END,hero)
        self.heroList.pack(fill=Y,expand=1,side=LEFT)
        self.heroScrollbar.config(command=self.heroList.yview)
        self.heroContainer.pack(side=LEFT,fill=Y)
        
        
        # Frame for buttons to add heroes to ally/enemy/ban list
        self.buttonContainer = Frame(parent)
        self.buttonContainer.pack(side=LEFT, padx=20)
        self.allyButton = Button(self.buttonContainer,text="Add To Allies", command = self.addAlly, bg = 'green')
        self.enemyButton = Button(self.buttonContainer,text="Add To Enemies", command = self.addEnemy, bg = 'red')
        self.banButton = Button(self.buttonContainer,text="Add To Ban List", command = self.addBan, bg = 'yellow')
        self.allyButton.pack(side=TOP, fill=X)
        self.enemyButton.pack(side=TOP, fill=X)
        self.banButton.pack(side=TOP, fill=X)
        
        # Large frame containing both team relevant info and stat info
        self.teamStatContainer = Frame(parent)
        self.teamStatContainer.pack(side=LEFT,fill=Y)
        
        # Large frame of team relevant information
        self.teamContainer = Frame(self.teamStatContainer, borderwidth=1,relief=SUNKEN)
        
        # Reset button to empty team lists
        self.resetButton = Button(self.teamContainer,text='Reset', command = self.remAll)
        self.resetButton.pack(side=TOP)
        
        # Ally information and removal button
        self.allyContainer = Frame(self.teamContainer)
        self.allyLabel = Label(self.allyContainer,text='Allies', bg = 'green')
        self.allyLabel.pack(side=TOP,fill=X)
        self.allyList = Listbox(self.allyContainer)
        self.allyList.pack(side=TOP) 
        self.allyRemove = Button(self.allyContainer, text='Remove Ally', command = self.remAlly)
        self.allyRemove.pack(side=TOP)
        self.allyContainer.pack(side=LEFT)
        
        # Enemy information and removal button
        self.enemyContainer = Frame(self.teamContainer)
        self.enemyLabel = Label(self.enemyContainer,text='Enemies', bg = 'red')
        self.enemyLabel.pack(side=TOP,fill=X)
        self.enemyList = Listbox(self.enemyContainer)
        self.enemyList.pack(side=TOP) 
        self.enemyRemove = Button(self.enemyContainer, text='Remove Enemy', command = self.remEnemy)
        self.enemyRemove.pack(side=TOP)
        self.enemyContainer.pack(side=LEFT)
        
        # Ban list information and removal button
        self.banContainer = Frame(self.teamContainer)
        self.banLabel = Label(self.banContainer,text='Bans', bg = 'yellow')
        self.banLabel.pack(side=TOP,fill=X)
        self.banList = Listbox(self.banContainer)
        self.banList.pack(side=TOP) 
        self.banRemove = Button(self.banContainer, text='Remove Ban', command = self.remBan)
        self.banRemove.pack(side=TOP)
        self.banContainer.pack(side=LEFT)
        
        self.teamContainer.pack(side=TOP) 
        
        # Stat Frame
        self.statContainer = Frame(self.teamStatContainer)
        self.statContainer.pack(side=TOP,fill=Y, pady=20)
        
        # Mode Selection Frame
        self.modeContainer = Frame(self.statContainer,borderwidth=1,relief=RAISED)
        self.mode = BooleanVar()
        self.mode.set(False)
        self.modeButtons = []
        self.modeButtons.append(Radiobutton(self.modeContainer,text = 'Win Rate', variable=self.mode, value = False,width=10, command=self.updateStats))
        self.modeButtons[0].pack(side=TOP, anchor='w')
        self.modeButtons.append(Radiobutton(self.modeContainer,text = 'Advantage', variable=self.mode, value = True,width=10, command=self.updateStats))
        self.modeButtons[1].pack(side=TOP, anchor='w')
        self.modeContainer.pack(side=LEFT,padx=10)
        
        self.allyStatScrollbar = Scrollbar(self.statContainer)
        self.allyStatScrollbar.pack(side=RIGHT,fill=Y)
        self.allyStatHero = Listbox(self.statContainer,yscrollcommand=self.allyStatScrollbar.set)
        self.allyStatHero.pack(side=LEFT,fill=Y)
        self.allyStatStat = Listbox(self.statContainer,yscrollcommand=self.allyStatScrollbar.set,width=10)
        self.allyStatStat.pack(side=LEFT,fill=Y)
        self.allyStatScrollbar.config(command=self.allyStatYView)
        
        self.updateStats()
        mainloop()
        
if __name__ == '__main__':
    root = Tk()
    myApp = DotaPickApp(root)
        
                