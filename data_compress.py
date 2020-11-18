import os
import math

player_per_game=6
total_teams=6
average=90

for team in range(total_teams):

    readFile=open("Team"+str(team)+"RoundRecords.csv", "r")
    writeFile=open("Team"+str(team)+"RoundRecords_"+str(average)+"Average.csv", "w")
    header=readFile.readline()
    writeFile.write(header)

    colCount=len(header[:-3].split(", "))
    lines=0
    averages=[0 for col in range(colCount)]
    for line in readFile:
        cols=line[:-3].split(", ")
        for i in range(colCount):
            if i!=0:
                averages[i]+=float(cols[i])
            else:
                averages[i]=float(cols[i])

        lines=lines+1
        if lines == average:
            lines=0
            for i in range(colCount):
                if i!=0:
                    writeFile.write(str(averages[i]/average)+", ")
                else:
                    writeFile.write(str(averages[i])+", ")
            writeFile.write("\n")
            averages=[0 for col in range(colCount)]

    readFile.close()
    writeFile.close()