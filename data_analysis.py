#Dain Harmon 2020/12/14

import os
import math

player_per_game=6
total_teams=6
games_per_round=total_teams*(total_teams+1)/2

maxSelfRatioTeam = [1.0, 0.0, False] #0
twiceSelfRatioTeam = [1.0, 0.5, False] #1
equalSelfRatioTeam = [1.0, 1.0, False] #2
halfSelfRatioTeam = [0.5, 1.0, False] #3
zeroSelfRatioTeam = [0.0, 1.0, False] #4
winOnlyRatioTeam = [0.0, 1.0, True] #5
TeamArgs = [maxSelfRatioTeam, twiceSelfRatioTeam, equalSelfRatioTeam, halfSelfRatioTeam, zeroSelfRatioTeam, winOnlyRatioTeam]

scoreTarget=3
maxMoves=2400
moveValue=0
captureValue=1
goalValue=50
winValue=200
capturedValue=-1
maxUtil=winValue+scoreTarget*goalValue*2+(maxMoves/player_per_game-3)*captureValue*2+(maxMoves/player_per_game/2-1)*captureValue

readFile=open("SynthesizedLogs", "r")
teamRoundFile=[]
teamGameFile=[]
for team in range(total_teams):
    teamRoundFile.append(open("Team"+str(team)+"RoundRecords.csv","w"))
    teamRoundFile[team].write("Round, Win, Loss, Goals, Captures, \"Times Captured\", Turns, \"Max Utility\", \"Total Utility\", \"Average Utility\", \"Utility Range\", \"P1 Utility\", \"P2 Utility\", \"P3 Utility\", \n")
    teamGameFile.append(open("Team"+str(team)+"GameRecords.csv","w"))
    teamGameFile[team].write("Round, \"Vs Team\", \"Margine Of Victory\", Captures, \"Times Captured\", Turns, \"Max Utility\", \"Total Utility\", \"Average Utility\", \"Utility Range\", \"P1 Utility\", \"P2 Utility\", \"P3 Utility\", \n")

games=0
roundWins=[0, 0, 0, 0, 0, 0]
roundLoses=[0, 0, 0, 0, 0, 0]
roundGoals=[0, 0, 0, 0, 0, 0]
roundCaptures=[0, 0, 0, 0, 0, 0]
roundTimesCaptured=[0, 0, 0, 0, 0, 0]
roundMoves=[0, 0, 0, 0, 0, 0]
roundMaxUtil=[0, 0, 0, 0, 0, 0]
roundTotalUtil=[0, 0, 0, 0, 0, 0]
roundAverageUtil=[0, 0, 0, 0, 0, 0]
roundUtilRange=[0, 0, 0, 0, 0, 0]
roundPlayerUtil=[[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]]
for line in readFile:
    line=line[26:-3]
    cols=line.split(", ")
    game_round=int(cols[0])
    teams=[int(i) for i in cols[1:3]]
    team_scores=[int(i) for i in cols[3:5]]
    captures=[int(i) for i in cols[5:11]]
    timesCaptured=[int(i) for i in cols[11:17]]
    goals=[int(i) for i in cols[17:23]]
    moves=[int(i) for i in cols[23:29]]

    teamCaptures=[0, 0]
    teamTimesCaptured=[0, 0]
    teamTurns=[0, 0]
    for player in range(player_per_game):
        team=player%2
        teamCaptures[team]+=captures[player]
        teamTimesCaptured[team]+=timesCaptured[player]
        teamTurns[team]+=moves[player]

    playerUtil=[]
    for player in range(player_per_game):
        team=player%2
        personalUtil=captureValue*captures[player]-capturedValue*timesCaptured[player]+goalValue*goals[player]
        teamUtil=captureValue*teamCaptures[team]-capturedValue*teamTimesCaptured[team]+goalValue*team_scores[team]
        if team_scores[team]==3:
            teamUtil+=200
            if TeamArgs[teams[team]][2]:
                teamUtil=200
        totalUtil=TeamArgs[teams[team]][0]*personalUtil+TeamArgs[teams[team]][1]*teamUtil
        playerUtil.append(totalUtil)

    teamMaxUtil=[-math.inf,-math.inf]
    teamMinUtil=[math.inf,math.inf]
    teamTotalUtil=[0,0]
    teamAverageUtil=[0,0]
    teamUtilRange=[0,0]
    for player in range(player_per_game):
        team=player%2
        teamTotalUtil[team]+=playerUtil[player]
        if teamMaxUtil[team]<playerUtil[player]:
            teamMaxUtil[team]=playerUtil[player]
        if teamMinUtil[team]>playerUtil[player]:
            teamMinUtil[team]=playerUtil[player]
    teamAverageUtil[0]=teamTotalUtil[0]/3
    teamAverageUtil[1]=teamTotalUtil[1]/3
    teamUtilRange[0]=teamMaxUtil[0]-teamMinUtil[0]
    teamUtilRange[1]=teamMaxUtil[1]-teamMinUtil[1]

    teamGameFile[teams[0]].write("{round}, {vsTeam}, {margineOfVictory}, {captures}, {timesCaptured}, {turns}, {maxUtil}, {totalUtil}, {averageUtil}, {utilRange}, {P1Util}, {P2Util}, {P3Util}, \n"
                            .format(round=game_round, vsTeam=teams[1], margineOfVictory=team_scores[0]-team_scores[1], captures=teamCaptures[0], timesCaptured=teamTimesCaptured[0], turns=teamTurns[0], maxUtil=teamMaxUtil[0], totalUtil=teamTotalUtil[0], averageUtil=teamAverageUtil[0], utilRange=teamUtilRange[0], P1Util=playerUtil[0], P2Util=playerUtil[2], P3Util=playerUtil[4]))
    teamGameFile[teams[1]].write("{round}, {vsTeam}, {margineOfVictory}, {captures}, {timesCaptured}, {turns}, {maxUtil}, {totalUtil}, {averageUtil}, {utilRange}, {P1Util}, {P2Util}, {P3Util}, \n"
                            .format(round=game_round, vsTeam=teams[0], margineOfVictory=team_scores[1]-team_scores[0], captures=teamCaptures[1], timesCaptured=teamTimesCaptured[1], turns=teamTurns[1], maxUtil=teamMaxUtil[1], totalUtil=teamTotalUtil[1], averageUtil=teamAverageUtil[1], utilRange=teamUtilRange[1], P1Util=playerUtil[1], P2Util=playerUtil[3], P3Util=playerUtil[5]))

    if team_scores[0]==3:
        roundWins[teams[0]]+=1
        roundLoses[teams[1]]+=1
    if team_scores[1]==3:
        roundWins[teams[1]]+=1
        roundLoses[teams[0]]+=1
    
    roundGoals[teams[0]]+=team_scores[0]
    roundGoals[teams[1]]+=team_scores[1]

    roundCaptures[teams[0]]+=teamCaptures[0]
    roundCaptures[teams[1]]+=teamCaptures[1]

    roundTimesCaptured[teams[0]]+=teamTimesCaptured[0]
    roundTimesCaptured[teams[1]]+=teamTimesCaptured[1]

    roundMoves[teams[0]]+=teamTurns[0]
    roundMoves[teams[1]]+=teamTurns[1]

    roundMaxUtil[teams[0]]+=teamMaxUtil[0]
    roundMaxUtil[teams[1]]+=teamMaxUtil[1]

    roundTotalUtil[teams[0]]+=teamTotalUtil[0]
    roundTotalUtil[teams[1]]+=teamTotalUtil[1]

    roundAverageUtil[teams[0]]+=teamAverageUtil[0]
    roundAverageUtil[teams[1]]+=teamAverageUtil[1]

    roundUtilRange[teams[0]]+=teamUtilRange[0]
    roundUtilRange[teams[1]]+=teamUtilRange[1]

    for player in range(player_per_game):
        team=player%2
        team_player_id=int(player/2)
        roundPlayerUtil[teams[team]][team_player_id]+=playerUtil[player]


    games=games+1
    if games == games_per_round:
        games=0
        for team in range(total_teams):
            teamRoundFile[team].write("{round}, {wins}, {losses}, {goals}, {captures}, {timesCaptured}, {turns}, {maxUtil}, {totalUtil}, {averageUtil}, {utilRange}, {P1Util}, {P2Util}, {P3Util}, \n"
                .format(round=game_round, wins=roundWins[team], losses=roundLoses[team], goals=roundGoals[team]/(total_teams+1), captures=roundCaptures[team]/(total_teams+1), timesCaptured=roundTimesCaptured[team]/(total_teams+1), turns=roundMoves[team]/(total_teams+1), maxUtil=roundMaxUtil[team]/(total_teams+1), totalUtil=roundTotalUtil[team]/(total_teams+1), averageUtil=roundAverageUtil[team]/(total_teams+1), utilRange=roundUtilRange[team]/(total_teams+1), P1Util=roundPlayerUtil[team][0]/(total_teams+1), P2Util=roundPlayerUtil[team][1]/(total_teams+1), P3Util=roundPlayerUtil[team][2]/(total_teams+1)))
        roundWins=[0, 0, 0, 0, 0, 0]
        roundLoses=[0, 0, 0, 0, 0, 0]
        roundGoals=[0, 0, 0, 0, 0, 0]
        roundCaptures=[0, 0, 0, 0, 0, 0]
        roundTimesCaptured=[0, 0, 0, 0, 0, 0]
        roundMoves=[0, 0, 0, 0, 0, 0]
        roundMaxUtil=[0, 0, 0, 0, 0, 0]
        roundTotalUtil=[0, 0, 0, 0, 0, 0]
        roundAverageUtil=[0, 0, 0, 0, 0, 0]
        roundUtilRange=[0, 0, 0, 0, 0, 0]
        roundPlayerUtil=[[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]]

for team in range(total_teams):
    teamRoundFile[team].close()
    teamGameFile[team].close()
