
import os
import curses
import time
import fnmatch

team1=int(input("Team1: "))
team2=int(input("Team2: "))
game_round=int(input("Round: "))

for file in os.listdir("./game_stats/"):
    if fnmatch.fnmatch(file,"log-Game_Log_"+str(team1)+"v"+str(team2)+"ep"+str(game_round)+"[*.txt"):
        print(file)

fileName=input("Which file: ")
readFile=open("./game_stats/"+fileName, "r")

stdscr = curses.initscr()
curses.noecho()
curses.cbreak()

try:
    stdscr.refresh()
    stdscr.getch()
    line_count=0
    for line in readFile:
        stdscr.addstr(line_count, 0, line)
        stdscr.clrtoeol()
        line_count+=1
        if line_count==9:
            line_count=0
            stdscr.refresh()
            time.sleep(0.5)
    stdscr.refresh()
    stdscr.getch()

finally:
    curses.echo()
    curses.nocbreak()
    curses.endwin()