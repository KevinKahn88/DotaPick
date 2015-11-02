'''
Created on Sep 16, 2015

@author: Kevin
'''

import pypyodbc
from . import Dotabuff

def createTable(cursor):
    cursor.execute('''
    USE Dota
    IF object_ID('Matches') is null
    create table Matches
    (
        Match_ID int NOT NULL UNIQUE,
        Match_Seq int NOT NULL UNIQUE,
        Game_Mode int,
        Lobby_Type int,
        Start_Time int,
        Duration int,
        Tower_Rad int,
        Tower_Dir int,
        Barracks_Rad int,
        Barracks_Dir int,
        FB_Time int,
        Humans int,
        Leavers int,
        Rad_Win bit,
        Rad_Hero1 int,
        Rad_Hero2 int,
        Rad_Hero3 int,
        Rad_Hero4 int,
        Rad_Hero5 int,
        Dir_Hero1 int,
        Dir_Hero2 int,
        Dir_Hero3 int,
        Dir_Hero4 int,
        Dir_Hero5 int,
        Cluster int
    )
    ''')
    
# Adds a batch of match details using 'GetMatchHistoryBySequenceNum'
def addBatchesBySeq(conn,prop,n):
    batchSize = 500
    keyList = ['Match_ID','Match_Seq','Game_Mode','Lobby_Type','Start_Time','Duration','Tower_Rad','Tower_Dir','Barracks_Rad','Barracks_Dir','FB_Time','Humans','Leavers','Rad_Win','Rad_Hero1','Rad_Hero2','Rad_Hero3','Rad_Hero4','Rad_Hero5','Dir_Hero1','Dir_Hero2','Dir_Hero3','Dir_Hero4','Dir_Hero5','Cluster']
    keyStr = ','.join(keyList)
    valStr = (len(keyList)-1)*'?,' + '?'
    command = 'INSERT INTO Matches (' + keyStr + ''')
    VALUES (''' + valStr + ')'
    lastRequest = 0
    cursor = conn.cursor()
    
    try:
        lastMatchSeq = prop['start_at_match_seq_num']
    except KeyError:
        (matchIDs,lastRequest,e) = Dotabuff.getMatches(prop,lastRequest)
        if e != 0:
            return (0,-1)
        (details,lastRequest,e) = Dotabuff.matchDetails(matchIDs[0],lastRequest)
        if e != 0:
            print(e)
            return (0,-2) 
        lastMatchSeq = details['Match_Seq']
    prop['matches_requested'] = batchSize
    for ind in range(n):
        prop['start_at_match_seq_num'] = lastMatchSeq
        (batchInfo,lastMatchSeq,lastRequest,e) = Dotabuff.batchDetails(prop,lastRequest)
        if e == 0:
            batch_list = []
            for match in batchInfo:
                cursor.execute('SELECT * FROM Matches WHERE Match_ID=' + str(match['Match_ID']))
                if len(cursor.fetchall())==0:
                    batch_entry = ['']*len(keyList)
                    for keyInd in range(len(keyList)):
                        try:
                            batch_entry[keyInd] = match[keyList[keyInd]]
                        except KeyError:
                            batch_entry[keyInd] = None
                    batch_list.append(batch_entry)
            if len(batch_list) > 0:
                cursor.executemany(command,batch_list)
                conn.commit()
            print(str(ind) + '-' + str(len(batch_list)) + '-' + str(lastMatchSeq))
            f = open('LastMatchSeq.txt','w')
            f.write(str(lastMatchSeq))
            f.close()
    return lastMatchSeq 


def addMatchEntry(cursor,details):
    
    cursor.execute('USE Dota')
    cursor.execute('SELECT * FROM Matches WHERE MatchID=' + str(details['Match_ID']))
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
    
       
    
def addBatchesByID(conn,prop,n):
    keyList = ['MatchID','MatchSeq','Mode','RadWin','RadHero1','RadHero2','RadHero3','RadHero4','RadHero5','DirHero1','DirHero2','DirHero3','DirHero4','DirHero5']
    keyStr = ','.join(keyList)
    valStr = (len(keyList)-1)*'?,'+'?'
    command = 'INSERT INTO Matches (' + keyStr + ''')
    VALUES (''' + valStr + ')'
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

def updateEntries(conn):
    batchSize = 100
    keyList = keyList = ['Match_ID','Match_Seq','Game_Mode','Lobby_Type','Start_Time','Duration','Tower_Rad','Tower_Dir','Barracks_Rad','Barracks_Dir','FB_Time','Humans','Leavers','Rad_Win','Rad_Hero1','Rad_Hero2','Rad_Hero3','Rad_Hero4','Rad_Hero5','Dir_Hero1','Dir_Hero2','Dir_Hero3','Dir_Hero4','Dir_Hero5']
    lastRequest = 0
    cursor = conn.cursor()
    
    command = '''UPDATE Matches
    SET '''
    command += '=?,'.join(keyList[1:len(keyList)]) + '''=?
    WHERE MatchID=?'''
    print (command)
    
    
    cursor.execute('SELECT MatchID FROM Matches')
    idList = [x[0] for x in cursor.fetchall()]
    
    batchN = int(len(idList)/batchSize)
    for ind in range(batchN):
        print(str(ind) + ' out of ' + str(batchN))
        batch_list = []
        for match in idList[(ind*batchSize):((ind+1)*batchSize)]:
            (details,lastRequest,e) = Dotabuff.matchDetails(match,lastRequest)
            if e == 0:
                batch_list.append([details[key] for key in (keyList[1:len(keyList)]+[keyList[0]])])
        if len(batch_list)>0:
            conn.cursor().executemany(command,batch_list)
            conn.commit()
    for match in idList[(batchN*batchSize):len(idList)]:
        (details,lastRequest,e) = Dotabuff.matchDetails(match,lastRequest)
        if e == 0:
            batch_list.append([details[key] for key in (keyList[1:len(keyList)]+[keyList[0]])])
    if len(batch_list)>0:
        conn.cursor().executemany(command,batch_list)
        conn.commit()        

def addMatches(conn,startID,n):
    keyList = ['MatchID','MatchSeq','Mode','RadWin','RadHero1','RadHero2','RadHero3','RadHero4','RadHero5','DirHero1','DirHero2','DirHero3','DirHero4','DirHero5']
    lastRequest = 0
    command = ('''INSERT INTO Matches (MatchID,MatchSeq,Mode,RadWin,RadHero1,RadHero2,RadHero3,RadHero4,RadHero5,DirHero1,DirHero2,DirHero3,DirHero4,DirHero5)
    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)''')
    cursor = conn.cursor()
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
    conn.cursor().execute('USE Dota')
    return conn

if __name__ == '__main__':
    conn = connectSQL()
    createTable(conn.cursor())
    #
    print(addBatchesBySeq(conn,{'start_at_match_seq_num': 1687412213},50000))
    pass