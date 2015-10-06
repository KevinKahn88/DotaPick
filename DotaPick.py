'''
Created on Sep 30, 2015

@author: Kevin
'''


import json
from SQLServer import Server
import re
import math
import numpy as np

maxHero = 112
radList = '(RadHero1, RadHero2, RadHero3, RadHero4, RadHero5)'
dirList = '(DirHero1, DirHero2, DirHero3, DirHero4, DirHero5)'

# Logistic function
def logistic(num):
    return 1/(1+math.pow(math.e,-num))

# Logit funciton (inverse logistic)
def logit(num):
    return -math.log((1-num)/num)

# Creates dictionary of heroes
def heroes():
    with open('heroes.json') as f:
        data = json.load(f)
    heroDict = {}
    for entry in data['heroes']:
        heroDict[entry['localized_name']] = entry['id']
    return heroDict

# Finds the % of wins for every hero against heroID
def counter(cursor,heroID):
    global maxHero
    
    # Command Template given hero in Radiance
    commandRad = '''
    SELECT RadWin FROM Matches
    WHERE (''' + str(heroID) + 'IN ' + radList + ') AND (# IN ' + dirList + ')'
    # Command Template given hero in Dire
    commandDir = '''
    SELECT RadWin FROM Matches
    WHERE (# IN''' + radList + ') AND (' + str(heroID) + 'IN' + dirList + ')'
    
    counterWin = [None]*maxHero 
    for idNum in range(maxHero):
        dataRad = cursor.execute(re.sub('#',str(idNum+1),commandRad)).fetchall()   
        dataDir = cursor.execute(re.sub('#',str(idNum+1),commandDir)).fetchall()
        wins = [x[0] for x in dataRad] + [1-x[0] for x in dataDir]    #Reformat and concatenate wins between Rad/Dir (radwin=0 is win for dire)
        try:
            counterWin[idNum] = sum(wins)/len(wins)
        except ZeroDivisionError:
            counterWin[idNum] = float('nan')   #If no hits, fill in with NaN
    return counterWin
        
# Finds the % of wins for every hero along with heroID    
def partner(cursor,heroID):
    global maxHero
    
    # Command Template given hero in Radiance
    commandRad = '''
    SELECT RadWin FROM Matches
    WHERE (''' + str(heroID) + 'IN ' + radList + ') AND (# IN ' + radList + ')'
    # Command Template given hero in Dire
    commandDir = '''
    SELECT RadWin FROM Matches
    WHERE (# IN''' + dirList + ') AND (' + str(heroID) + 'IN' + dirList + ')'
    
    partnerWin = [None]*maxHero 
    for idNum in range(maxHero):
        if idNum+1 == heroID:  # NaN for matching to given Hero
            partnerWin[idNum] = float('nan')
        else:
            dataRad = cursor.execute(re.sub('#',str(idNum+1),commandRad)).fetchall()
            dataDir = cursor.execute(re.sub('#',str(idNum+1),commandDir)).fetchall()
            wins = [x[0] for x in dataRad] + [1-x[0] for x in dataDir]    #Reformat and concatenate wins between Rad/Dir (radwin=0 is win for dire)
            try:
                partnerWin[idNum] = sum(wins)/len(wins)
            except ZeroDivisionError:
                partnerWin[idNum] = float('nan')
    return partnerWin

# Function to analyze win % given teammates/opponents
def AnalyzePicks(teammates,opponents):
    conn = Server.connectSQL();
    cursor = conn.cursor()
    
    data = []
    # Transform probabilities to the parameter space (-inf,inf) through logit
    # Each value represents modeled effect of hero interactions on winning/losing
    for idNum in teammates:
        data.append([logit(x) for x in partner(cursor,idNum)])
    for idNum in opponents:
        data.append([logit(x) for x in counter(cursor,idNum)])
    
    dataMat = np.matrix(data)
    totalParam = np.sum(dataMat,axis=0).tolist()[0] #sums of each column (total modeled influence of pick on win/lose)
    probWin = [logistic(x) for x in totalParam]
    return probWin
    
    
if __name__ == '__main__':
    pass