'''
Created on Sep 30, 2015

@author: Kevin
'''

import matplotlib.pyplot as plt
import json
from SQLServer import Server
import re
import math
import numpy as np

maxHero = 112
radList = '(RadHero1, RadHero2, RadHero3, RadHero4, RadHero5)'
dirList = '(DirHero1, DirHero2, DirHero3, DirHero4, DirHero5)'

#
def readJSON(fileName):
    jsondata = readFile(fileName)
    data = json.loads(jsondata)
    return data

#
def readFile(fileName):
    with open(fileName,'r') as f:
        return f.read()
    

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
    
    # SQL Command Template
    # '#' represents the hero's ID
    # '$' represents the counter hero's ID
    command = '''
    SELECT SUM(T1.wins)/SUM(T1.total) FROM
    (SELECT SUM(CAST(Rad_Win as float)) as wins, COUNT(Rad_Win) as total
    FROM Matches WHERE 
    Humans = 10 AND 
    Leavers = 0 AND 
    COUNTER_ID in (Rad_Hero1, Rad_Hero2, Rad_Hero3, Rad_Hero4, Rad_Hero5) AND 
    HERO_ID in (Dir_Hero1, Dir_Hero2, Dir_Hero3, Dir_Hero4, Dir_Hero5)
    UNION
    SELECT SUM(1-CAST(Rad_Win as float)) as wins, COUNT(Rad_Win) as total
    FROM Matches WHERE 
    Humans = 10 AND 
    Leavers = 0 AND 
    COUNTER_ID in (Dir_Hero1, Dir_Hero2, Dir_Hero3, Dir_Hero4, Dir_Hero5) AND 
    HERO_ID in (Rad_Hero1, Rad_Hero2, Rad_Hero3, Rad_Hero4, Rad_Hero5)) T1
    '''
    command = re.sub('HERO_ID',str(heroID),command)
    counterWin = [0 for x in range(maxHero)] 
    for idNum in range(maxHero):
        if heroID is not idNum+1:
            winrate = cursor.execute(re.sub('COUNTER_ID',str(idNum+1),command)).fetchone()[0]
            if winrate is not None:
                counterWin[idNum] = winrate
    return counterWin
        
# Finds the % of wins for every hero along with heroID    
def partner(cursor,heroID):
    global maxHero
    
    # Command Template given hero in Radiance
    command = '''
    SELECT SUM(T1.wins)/SUM(T1.total) FROM
    (SELECT SUM(CAST(Rad_Win as float)) as wins, COUNT(Rad_Win) as total
    FROM Matches WHERE 
    Humans = 10 AND 
    Leavers = 0 AND 
    HERO_ID in (Rad_Hero1, Rad_Hero2, Rad_Hero3, Rad_Hero4, Rad_Hero5) AND 
    PARTNER_ID in (Rad_Hero1, Rad_Hero2, Rad_Hero3, Rad_Hero4, Rad_Hero5)
    UNION
    SELECT SUM(1-CAST(Rad_Win as float)) as wins, COUNT(Rad_Win) as total
    FROM Matches WHERE 
    Humans = 10 AND 
    Leavers = 0 AND 
    HERO_ID in (Dir_Hero1, Dir_Hero2, Dir_Hero3, Dir_Hero4, Dir_Hero5) AND 
    PARTNER_ID in (Dir_Hero1, Dir_Hero2, Dir_Hero3, Dir_Hero4, Dir_Hero5)) T1
    '''
    command = re.sub('HERO_ID',str(heroID),command)
    
    partnerWin = [0 for x in range(maxHero)] 
    for idNum in range(maxHero):
        if heroID is not idNum+1:
            winrate = cursor.execute(re.sub('PARTNER_ID',str(idNum+1),command)).fetchone()[0]
            if winrate is not None:
                partnerWin[idNum] = winrate
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
    
def winTime(cursor,heroID,durations):
    winrates = []
    command = '''
    SELECT SUM(T1.wins)/SUM(T1.total) FROM
    (SELECT SUM(CAST(Rad_Win as float)) as wins, COUNT(Rad_Win) as total
    FROM Matches WHERE 
    Humans = 10 AND 
    Leavers = 0 AND
    Duration Command AND 
    HERO_ID in (Rad_Hero1, Rad_Hero2, Rad_Hero3, Rad_Hero4, Rad_Hero5) 
    UNION
    SELECT SUM(1-CAST(Rad_Win as float)) as wins, COUNT(Rad_Win) as total
    FROM Matches WHERE 
    Humans = 10 AND 
    Leavers = 0 AND
    Duration Command AND 
    HERO_ID in (Dir_Hero1, Dir_Hero2, Dir_Hero3, Dir_Hero4, Dir_Hero5)) T1
    '''
    command = re.sub('HERO_ID',str(heroID),command)
    
    dur_command = 'Duration < ' + str(durations[0])
    cursor.execute(re.sub('Duration Command',dur_command,command))
    winrates.append(cursor.fetchone()[0])
    for ind in range(len(durations)-1):
        dur_command = 'Duration > ' + str(durations[ind]) + 'AND Duration < ' + str(durations[ind+1])
        cursor.execute(re.sub('Duration Command',dur_command,command))
        winrates.append(cursor.fetchone()[0])
    dur_command = 'Duration > ' + str(durations[-1])
    cursor.execute(re.sub('Duration Command',dur_command,command))
    winrates.append(cursor.fetchone()[0])
    return winrates

command = '''
SELECT SUM(T1.wins)/SUM(T1.total) FROM
(SELECT SUM(CAST(Rad_Win as float)) as wins, COUNT(Rad_Win) as total
FROM Matches WHERE 
Humans = 10 AND 
Leavers = 0 AND
Duration Command AND 
1 in (Rad_Hero1, Rad_Hero2, Rad_Hero3, Rad_Hero4, Rad_Hero5) 
UNION
SELECT SUM(1-CAST(Rad_Win as float)) as wins, COUNT(Rad_Win) as total
FROM Matches WHERE 
Humans = 10 AND 
Leavers = 0 AND
Duration Command AND 
1 in (Dir_Hero1, Dir_Hero2, Dir_Hero3, Dir_Hero4, Dir_Hero5)) T1
'''

if __name__ == '__main__':
    conn = Server.connectSQL();
    cursor = conn.cursor()
    dur = [30,35,40,45,50,55,60,65,70]
    durationWins = winTime(cursor,1,[x*60 for x in dur])
    print(durationWins)
    
    fig = plt.figure(1)
    ax = plt.subplot()
    xlabel = ['<' + str(dur[0])]
    [xlabel.append(str(dur[ind]) + '-' + str(dur[ind+1])) for ind in range(len(dur)-1)]
    xlabel.append('>' + str(dur[-1]))
    ind = np.arange(len(durationWins))
    rects1 = ax.bar(ind,[100 for x in ind],.5,color = 'r')
    rects2 = ax.bar(ind,[100*x for x in durationWins],.5,color = 'g')
    ax.set_ylabel('Win/Loss Rates (%)')
    ax.set_xlabel('Game Duration (min)')
    ax.set_title('Antimage Performance Over Game Duration')
    ax.set_xticks(ind+.25)
    ax.set_xticklabels(xlabel)
    ax.legend((rects1,rects2),('Lose','Win'))
    fig.savefig('AM_GameDuration.png',bbox_inches='tight')
    
    partnerWin = partner(cursor,1)
    counterWin = counter(cursor,1)
    heroData = readJSON('heroes.json')
    fig2 = plt.figure(2)
    ax2 = plt.subplot()
    ind = np.arange(5)
    width = .35
    partnerBar = ax2.bar(ind,[100*x for x in partnerWin[1:6]],width,color = 'g')
    counterBar = ax2.bar(ind+width,[100*x for x in counterWin[1:6]],width,color = 'r')
    ax2.set_ylabel('Win Rates (%)')
    ax2.set_xlabel('Heroes')
    ax2.set_title('Performance with Antimage as a Ally/Enemy')
    ax2.set_xticks(ind+width)
    ax2.set_xticklabels([heroData['heroes'][x]['localized_name'] for x in ind+1])
    ax2.legend((partnerBar,counterBar),('Ally','Enemy'))
    fig2.savefig('AM_AllyEnemy.png',bbox_inches='tight')
    plt.show()
    #print(Server.addBatchesBySeq(conn,{'start_at_match_seq_num': 1447667929},50000))
    #antimagePartner = partner(cursor,1)
    #antimageCounter = counter(cursor,1)