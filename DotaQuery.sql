USE Dota

SELECT SUM(T1.wins)/SUM(T1.total) FROM
    (SELECT SUM(CAST(Rad_Win as float)) as wins, COUNT(Rad_Win) as total
    FROM Matches WHERE 
    Humans = 10 AND 
    Leavers = 0 AND
    Duration < 50*60 AND Duration > 40*60 AND 
    1 in (Rad_Hero1, Rad_Hero2, Rad_Hero3, Rad_Hero4, Rad_Hero5) 
    UNION
    SELECT SUM(1-CAST(Rad_Win as float)) as wins, COUNT(Rad_Win) as total
    FROM Matches WHERE 
    Humans = 10 AND 
    Leavers = 0 AND
    Duration < 50*60 AND Duration > 40*60 AND 
    1 in (Dir_Hero1, Dir_Hero2, Dir_Hero3, Dir_Hero4, Dir_Hero5)) T1

--EXEC sp_spaceused  Matches


--SELECT COUNT(*) FROM Matches

--SELECT MAX(Match_Seq), MAX(Start_Time) FROM Matches WHERE Match_Seq < 1650000000


/*
SELECT SUM(T1.wins)/SUM(T1.total) FROM
(SELECT SUM(CAST(Rad_Win as float)) as wins, COUNT(Rad_Win) as total
FROM Matches WHERE 
Humans = 10 AND 
Leavers = 0 AND 
1 in (Rad_Hero1, Rad_Hero2, Rad_Hero3, Rad_Hero4, Rad_Hero5) AND 
50 in (Rad_Hero1, Rad_Hero2, Rad_Hero3, Rad_Hero4, Rad_Hero5)
UNION
SELECT SUM(1-CAST(Rad_Win as float)) as wins, COUNT(Rad_Win) as total
FROM Matches WHERE 
Humans = 10 AND 
Leavers = 0 AND 
1 in (Dir_Hero1, Dir_Hero2, Dir_Hero3, Dir_Hero4, Dir_Hero5) AND 
50 in (Dir_Hero1, Dir_Hero2, Dir_Hero3, Dir_Hero4, Dir_Hero5)) T1


SELECT SUM(T1.wins)/SUM(T1.total) FROM
    (SELECT SUM(CAST(Rad_Win as float)) as wins, COUNT(Rad_Win) as total
    FROM Matches WHERE 
    Humans = 10 AND 
    Leavers = 0 AND 
    1 in (Rad_Hero1, Rad_Hero2, Rad_Hero3, Rad_Hero4, Rad_Hero5) AND 
    50 in (Rad_Hero1, Rad_Hero2, Rad_Hero3, Rad_Hero4, Rad_Hero5)
    UNION
    SELECT SUM(1-CAST(Rad_Win as float)) as wins, COUNT(Rad_Win) as total
    FROM Matches WHERE 
    Humans = 10 AND 
    Leavers = 0 AND 
    1 in (Dir_Hero1, Dir_Hero2, Dir_Hero3, Dir_Hero4, Dir_Hero5) AND 
    50 in (Dir_Hero1, Dir_Hero2, Dir_Hero3, Dir_Hero4, Dir_Hero5)) T1


SELECT SUM(T1.wins)/SUM(T1.total) FROM
(SELECT SUM(CAST(Rad_Win as float)) as wins, COUNT(Rad_Win) as total
FROM Matches WHERE 
Humans = 10 AND 
Leavers = 0 AND 
1 in (Rad_Hero1, Rad_Hero2, Rad_Hero3, Rad_Hero4, Rad_Hero5) AND 
50 not in (Rad_Hero1, Rad_Hero2, Rad_Hero3, Rad_Hero4, Rad_Hero5)
UNION
SELECT SUM(1-CAST(Rad_Win as float)) as wins, COUNT(Rad_Win) as total
FROM Matches WHERE 
Humans = 10 AND 
Leavers = 0 AND 
1 in (Dir_Hero1, Dir_Hero2, Dir_Hero3, Dir_Hero4, Dir_Hero5) AND 
50 not in (Dir_Hero1, Dir_Hero2, Dir_Hero3, Dir_Hero4, Dir_Hero5)) T1



SELECT 1,AVG(CAST(Rad_Win as float)) FROM Matches WHERE  Humans = 10 AND Leavers = 0 AND 1 in (Rad_Hero1, Rad_Hero2, Rad_Hero3, Rad_Hero4, Rad_Hero5) AND 50 in (Rad_Hero1, Rad_Hero2, Rad_Hero3, Rad_Hero4, Rad_Hero5)
SELECT 1,AVG(1-CAST(Rad_Win as float)) FROM Matches WHERE  Humans = 10 AND Leavers = 0 AND 1 in (Dir_Hero1, Dir_Hero2, Dir_Hero3, Dir_Hero4, Dir_Hero5) AND 50 in (Dir_Hero1, Dir_Hero2, Dir_Hero3, Dir_Hero4, Dir_Hero5)
SELECT 1,AVG(CAST(Rad_Win as float)) FROM Matches WHERE Humans = 10 AND Leavers = 0 AND 1 in (Rad_Hero1, Rad_Hero2, Rad_Hero3, Rad_Hero4, Rad_Hero5) AND 50 not in (Rad_Hero1, Rad_Hero2, Rad_Hero3, Rad_Hero4, Rad_Hero5)
SELECT 1,AVG(1-CAST(Rad_Win as float)) FROM Matches WHERE Humans = 10 AND Leavers = 0 AND 1 in (Dir_Hero1, Dir_Hero2, Dir_Hero3, Dir_Hero4, Dir_Hero5) AND 50 not in (Dir_Hero1, Dir_Hero2, Dir_Hero3, Dir_Hero4, Dir_Hero5)
*/