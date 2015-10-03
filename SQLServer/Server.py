'''
Created on Sep 16, 2015

@author: Kevin
'''

import pypyodbc
import Dotabuff

def createTable(cursor):
    cursor.execute('''
    USE Dota
    IF object_ID('Matches') is null
    create table Matches
    (
        MatchID int NOT NULL UNIQUE,
        Mode int,
        RadWin bit,
        RadHero1 int,
        RadHero2 int,
        RadHero3 int,
        RadHero4 int,
        RadHero5 int,
        DirHero1 int,
        DirHero2 int,
        DirHero3 int,
        DirHero4 int,
        DirHero5 int,
    )
    ''')
    
def addMatchEntry(cursor,details):
    
    cursor.execute('USE Dota')
    cursor.execute('SELECT * FROM Matches WHERE MatchID=' + str(details['MatchID']))
    if len(cursor.fetchall())>0: #Check if MatchID entry exists already
        return 1
    else:   #If new, enter Match Details
        command = ('INSERT INTO Matches')
        first = True
        colStr = '('
        valStr = 'VALUES ('
        for key in iter(details):
            if first:
                first = False
            else:
                colStr += ','
                valStr += ','  
            colStr += str(key)
            valStr += str(details[key])
        colStr += ')'
        valStr += ')'
        command += colStr + '\n' + valStr + ';'
        cursor.execute(command)
        print(command)
        return 0
    
   
def addBatches(conn,prop,n):
    batchSize = 100
    
    lastRequest = 0
    lastMatch = 0
    
    prop['matches_requested']=batchSize
    first = True   # Flag to see if first batch (subsequent batches will have different start_at_match_id
    cursor = conn.cursor()
    
    for bb in range(n):
        print(bb)
        if first:
            first = False
        else:
            prop['start_at_match_id'] = lastMatch-1
        (matchList,lastRequest,e) = Dotabuff.getMatches(prop,lastRequest)
        if e == 0:
            for match in matchList:
                print(match)
                cursor.execute('SELECT * FROM Matches WHERE MatchID=' + str(match))
                if len(cursor.fetchall())==0:
                    (details,lastRequest,e) = Dotabuff.matchDetails(match,lastRequest)
                    if e == 0:
                        if details['Mode'] in [1,2,3,4,5,16,22]:
                            addMatchEntry(cursor,details)
                else:
                    print('Already Added')
                lastMatch = match
            conn.commit()
        else:
            break
    Dotabuff.logError('Exiting Batch Run, Last Match:' + lastMatch)

def addMatches(conn,startID,n):
    lastRequest = 0
    command = ('''INSERT INTO Matches (MatchID,Mode,RadWin,RadHero1,RadHero2,RadHero3,RadHero4,RadHero5,DirHero1,DirHero2,DirHero3,DirHero4,DirHero5)
    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)''')
    keyList = ['MatchID','Mode','RadWin','RadHero1','RadHero2','RadHero3','RadHero4','RadHero5','DirHero1','DirHero2','DirHero3','DirHero4','DirHero5']
    batch_list = []
    for ind in range(n):
        matchID = startID-ind
        print(matchID)
        cursor.execute('SELECT * FROM Matches WHERE MatchID=' + str(matchID))
        if len(cursor.fetchall())==0:
            (details,lastRequest,e) = Dotabuff.matchDetails(matchID,lastRequest)
            if e==0:
                batch_list.append([details[key] for key in keyList])
    print(batch_list)
    if len(batch_list)>0:
        conn.cursor().executemany(command,batch_list)
        conn.commit()
            
    
def connectSQL():
    conn = pypyodbc.connect('DRIVER={SQL Server};SERVER=PHOENIX\DOTASQLSERVER;DATABASE=Dota;Trusted_Connection=Yes;')
    return conn

if __name__ == '__main__':
    conn = connectSQL()
    cursor = conn.cursor()
    createTable(cursor)
    conn.commit()
    #prop = {'matches_request':1}
    #(matchHist,lastRequest,e) = Dotabuff.getMatches(prop,0)
    for i in range(2000):
        print(i)
        addMatches(conn,1838331531-i*50,50)
    conn.close()
    print('done')
    pass