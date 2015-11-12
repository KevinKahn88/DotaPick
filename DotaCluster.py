'''
Created on Nov 7, 2015

@author: Kevin
'''
import random
from DotaPickGUI import heroes
from DotaPickGUI import loadStats
from DotaPickGUI import logit
from DotaPickGUI import logistic
import statistics as stat
from math import isnan

class HeroCluster(object):
    '''
    classdocs
    '''


    def __init__(self, num_cluster):
        '''
        Constructor
        '''
        self.maxHero = 112
        
        self.num_cluster = num_cluster
        self.cluster = [int(random.random()*num_cluster) for x in range(self.maxHero)]
        
        self.baseStats = [logit(x) for x in loadStats('baseStats.csv')[0]]
        allyStats = loadStats('allyStats.csv')
        
        self.groupStat = []
        for i in range(self.maxHero):
            tempStat = []
            for j in range(i):
                tempStat.append(logit(allyStats[i][j]) - self.baseStats[i] - self.baseStats[j])
            self.groupStat.append(tempStat)
            
        self.cost = self.clusterCost()
        
        self.heroIndDict = {ind-1:key for key,ind in heroes().items()}
    
    def calcTeamStats(self):
        teamStats = [[[] for x in range(y+1)] for y in range(self.num_cluster)]
        for hero1 in range(self.maxHero):
            for hero2 in  range(hero1):
                cluster_list = sorted([self.cluster[hero1],self.cluster[hero2]],reverse=True)
                hero_list = sorted([hero1,hero2],reverse=True)
                if not isnan(self.groupStat[hero_list[0]][hero_list[1]]):
                    teamStats[cluster_list[0]][cluster_list[1]].append(self.groupStat[hero_list[0]][hero_list[1]])
        return teamStats

    def calcStatFunc(self,func):
        funcStat = []
        teamStats = self.calcTeamStats()
        for clust1 in range(self.num_cluster):
            temp = []
            for clust2 in range(clust1+1):
                if func == stat.variance and len(teamStats[clust1][clust2])<2:
                    temp.append(0)
                else:
                    temp.append(func(teamStats[clust1][clust2]))
            funcStat.append(temp)
        return funcStat                  
    
    def clusterCost(self):
        # teamStats[cluster1][cluster2] = list of group stats that fall in cluster1,cluster2 team
        varStat = self.calcStatFunc(stat.variance)
        nStat = self.calcStatFunc(len)
        cost = 0
        for x in range(len(varStat)):
            for y in range(len(varStat[x])):
                cost += varStat[x][y]*(nStat[x][y]-1)
        return cost
        
    def iterate(self):
        new_clust = self.cluster
        changeCount = 0
        for hero in range(self.maxHero):
            if not isnan(self.baseStats[hero]):
                orig_cluster = self.cluster[hero]
                test_clust = list(set(range(self.num_cluster)).difference([orig_cluster]))  # All clusters not in the original cluster
                
                new_ind = -1
                min_cost = self.cost
                
                # Cycle through new clusters to see if any have a smaller cost
                for ind in range(len(test_clust)):
                    self.cluster[hero] = test_clust[ind]
                    new_cost = self.clusterCost()  
                    if new_cost < min_cost:
                        min_cost = new_cost
                        new_ind = ind
                self.cluster[hero]=orig_cluster
                if new_ind >= 0:
                    changeCount += 1
                    #print('Changed ' + self.heroIndDict[hero] + ' from ' + str(self.cluster[hero]) + '(' + str(self.cost) + ') to ' + str(test_clust[new_ind]) + '(' + str(min_cost) + ')')
                    new_clust[hero] = test_clust[new_ind]
        
        self.cluster = new_clust
        self.cost = self.clusterCost()
        print(str(self.cost) + ' ' + str(changeCount))
        return changeCount
    
    def iterate2(self):
        changeCount = 0
        for hero in range(self.maxHero):
            if not isnan(self.baseStats[hero]):
                orig_clust = self.cluster[hero]
                test_clust = list(set(range(self.num_cluster)).difference([orig_clust]))
                new_ind = -1
                min_cost = self.cost
                for ind in range(len(test_clust)):
                    self.cluster[hero] = test_clust[ind]
                    new_cost = self.clusterCost()
                    if new_cost < min_cost:
                        new_ind = ind
                        min_cost = new_cost
                if new_ind >= 0:
                    changeCount += 1
                    self.cluster[hero] = test_clust[new_ind]
                    self.cost = min_cost
                else:
                    self.cluster[hero] = orig_clust
        print(str(self.cost) + ' ' + str(changeCount))
        return changeCount
    
    def findCluster(self,delta):
        changeCount = self.iterate2()
        while changeCount > delta:
            changeCount = self.iterate2()
            
    def fileWrite(self,fname):
        heroDict = heroes()
        heroIndDict = {ind-1:key for key,ind in heroDict.items()}
        clusterFile = open(fname,'w')
        clusterFile.write(str(self.cost) + '\n')
        clusterFile.write(str(self.num_cluster) + '\n')
        for i in range(self.num_cluster):
            clusterFile.write(str(i) + '\n')
            for j in range(self.maxHero):
                if self.cluster[j] == i:
                    try:
                        clusterFile.write(heroIndDict[j] + '\n')
                    except KeyError:
                        pass
        clusterFile.close()
        
    def fileRead(self,fname):
        heroDict = heroes()
        clusterFile = open(fname)
        self.cost = float(clusterFile.readline().split('\n')[0])
        self.num_cluster = int(clusterFile.readline().split('\n')[0])
        fileLine = clusterFile.readline().split('\n')[0]
        while fileLine != '':
            try:
                clust = int(fileLine)
            except ValueError:
                self.cluster[heroDict[fileLine]-1] = clust
            fileLine = clusterFile.readline().split('\n')[0]
            
    
    
'''
for num_clust in range(2,7):
    dotaCluster = HeroCluster(num_clust)
    dotaCluster.findCluster(0)
    n = 10
    for i in range(n):
        print('Run Through ' + str(i+1))
        test = HeroCluster(num_clust)
        test.findCluster(0)
        if dotaCluster.cost > test.cost:
            dotaCluster = test
    dotaCluster.fileWrite(str(num_clust) + 'clusterFile.txt')
''' 