import time
import os
import struct
import random

datfile = "aiq.dat"

#CHARACTER/SLOT KEY
STAT_SLOT = 0

#STAT KEY:
ATK_STAT = 0
DEF_STAT = 1
SPC_STAT = 2
SPD_STAT = 3

#TYPES:
#FIRE,WATER,NATURE,DARK,LIGHT,NORMAL
#Water gets 1.5x boost on Fire, resists Fire by 0.66x
#Nature gets 1.5x boost on Water, resists Water by 0.66x
#Fire gets 1.5x boost on Nature, resists Nature by 0.66x
#Dark gets 1.5x boost on Light, no resistance
#Light gets 1.5x boost on Dark, no resistance
#Normal gets no boosts

#Type Key
TYPE_NORMAL = 0
TYPE_FIRE = 1 
TYPE_WATER = 2 
TYPE_NATURE = 3
TYPE_DARK = 4
TYPE_LIGHT = 5

T_EFFECTIVE = 1.5
T_INEFFECTIVE = 2.0/3.0

#Type Effectiveness Key
TYPE_CHART = [[1.0 for i in range(6)] for j in range(6)]
#To get modifier, do
#TYPE_CHART[ATK_TYPE][DEF_TYPE]
TYPE_CHART[TYPE_WATER][TYPE_FIRE] = T_EFFECTIVE
TYPE_CHART[TYPE_NATURE][TYPE_WATER] = T_EFFECTIVE
TYPE_CHART[TYPE_FIRE][TYPE_NATURE] = T_EFFECTIVE
TYPE_CHART[TYPE_DARK][TYPE_LIGHT] = T_EFFECTIVE
TYPE_CHART[TYPE_LIGHT][TYPE_DARK] = T_EFFECTIVE

TYPE_CHART[TYPE_FIRE][TYPE_WATER] = T_INEFFECTIVE
TYPE_CHART[TYPE_WATER][TYPE_NATURE] = T_INEFFECTIVE
TYPE_CHART[TYPE_NATURE][TYPE_FIRE] = T_INEFFECTIVE

# move types
MOVETYPE_PHYSICAL = 0
MOVETYPE_SPECIAL = 1
MOVETYPE_UNIQUE = 2

# load move data

#move storage format:
# (move_type, damage_type,  default learn level, learn level dict)
# move_type: 0 for physical, 1 for special, 2 for unique effect (method call)

allMoves =     {"Tackle":(MOVETYPE_PHYSICAL, TYPE_NORMAL, ),"Quick Punch":(MOVETYPE_PHYSICAL, TYPE_NORMAL),
                "Body Slam":(MOVETYPE_PHYSICAL, TYPE_NORMAL),"Swipe":(MOVETYPE_PHYSICAL, TYPE_NORMAL),
                "Hammer Fist":(MOVETYPE_PHYSICAL, TYPE_NORMAL),    #physical normal attacks
                "Earthquake":(MOVETYPE_SPECIAL,TYPE_NATURE),"Fireball":(MOVETYPE_SPECIAL,TYPE_FIRE),
                "Tsunami":(MOVETYPE_SPECIAL,TYPE_WATER),"Shadow Steal":(MOVETYPE_SPECIAL,TYPE_DARK),
                "Divine Punishment":(MOVETYPE_SPECIAL,TYPE_LIGHT),  #special typed attacks (1)
                "Rock Throw":(MOVETYPE_PHYSICAL, TYPE_NATURE),"Fire Punch":(MOVETYPE_PHYSICAL, TYPE_FIRE),           #TODO: decide on rock throw
                "Aqua Spear":(MOVETYPE_PHYSICAL, TYPE_WATER),"Evil Fist":(MOVETYPE_PHYSICAL,TYPE_DARK),
                "Purging Blow":(MOVETYPE_PHYSICAL, TYPE_LIGHT),  # physical typed attacks               
                "Nature's Wrath":(MOVETYPE_SPECIAL,TYPE_NATURE),"Flamestorm":(MOVETYPE_SPECIAL,TYPE_FIRE),
                "Oceanic Rift":(MOVETYPE_SPECIAL, TYPE_WATER),"Darkness Rising":(MOVETYPE_SPECIAL, TYPE_DARK),
                "God's Fury":(MOVETYPE_SPECIAL, TYPE_LIGHT),  #special typed attacks (2)
                "Starfire":(MOVETYPE_SPECIAL, TYPE_NORMAL),"Energy Beam":(MOVETYPE_SPECIAL, TYPE_NORMAL),
                "Protect":(MOVETYPE_UNIQUE, TYPE_NORMAL),  #special normal attacks/moves
                "Amateur Hacking":(MOVETYPE_UNIQUE, TYPE_NORMAL),"Hacking Mastery":(MOVETYPE_UNIQUE, TYPE_NORMAL), #shwe unique
                "Defense Boost":(MOVETYPE_UNIQUE, TYPE_NORMAL),"Eat Rice":(MOVETYPE_UNIQUE, TYPE_NORMAL), #jerry unique
                "Break Something":(MOVETYPE_UNIQUE, TYPE_NORMAL),  #aneesh unique
                "Goat Blood":(MOVETYPE_UNIQUE, TYPE_NORMAL),"Su-what?":(MOVETYPE_UNIQUE, TYPE_NORMAL), #sujay unique
                "RNG Dance":(MOVETYPE_UNIQUE, TYPE_NORMAL)}  #mihir unique


# load character data
characterpref = ["Aneesh","Shwetark","Jerry","Sujay","Mihir","Justin"]
characterdat = {"Aneesh":[(6,6,6,6)],"Shwetark":[(2,8,10,5)],"Jerry":[(4,12,4,4)],"Sujay":[(10,2,5,7)],"Mihir":[(4,4,4,4)],"Justin":[(6,4,3,11)],"Katherine":[(2,5,10,8)]}
charhometown = {"Aneesh":"Kim Town","Shwetark":"Billington Town","Jerry":"Galanos Town","Sujay":"Rudwick Town","Mihir":"Galanos Town","Justin":"Billington Town","Katherine":"Galanos Town"}
charinformation = {"Aneesh":"An all-arounder, Aneeshes can do everything at a slightly\nsub-average level, with quite average Specials",  
                 "Shwetark":"A Shwetark has low attack, and so relies on surviving\nlong enough to activate his powerful Special Attacks",  
                    "Jerry":"An extremely defensive class, a Jerry uses his Specials\nto regenerate health and outlast his opponent",  
                    "Sujay":"A berseker class who focuses on killing his opponent\nquickly, with Specials that buff SPD and ATK",  
                    "Mihir":"Like an Aneesh, but worse, although his Specials can\nsometimes have good effects",  
                   "Justin":"Relies heavily on speed to hit his opponents before they\ncan deal any damage",
                "Katherine":"A fast special attacker, uses quick hits to charge up\nher heavy damage specials"}  

towntalkpossibilities = {"Galanos Town":["Galanos: I don't know, check the API"], "Kim Town":["Kim: That statement evaluates to Forse"],
                "Rudwick Town":["Rudwick: Sweet!","Rudwick: Well, in general..."], "Billington Town":["Billington: *sigh*","Billington: *stares*",
                "Billington: First, you need to change your variable names to fruits"],
                "Sophomore Village":["Aneesh: Hey, check your .bashrc!","Shwetark: Web web web!","Sujay: All these AI labs are easy...",
                "Jerry: *eats rice*","Mihir: That's what your mom said last night","Aneesh: Why is it crashing?!?",
                "Mihir: Wow, you don't even know that?\n*Mihir's code crashes*","Shwetark: It's simple, just use a bidirectional reversable Kosaraju segment tree",
                "Jerry: Will there be food?"],"Schefer City":["Mayor Jack: Welcome to my town, young adventurer!","Mayor Jack: Hey, wanna play some Kolf?",
                "Mayor Jack: Aneesh, why is my memory at 99% usage?","Mayor Jack: Why is there smite in my .bashrc?",
                "Mayor Jack: Nice! My code now only takes 2 hours to terminate!"]}

#game data format
# store as list:
# index 0 - character data/stats (list, non-static)
# index 1 - current location
# index 2 - cleared locations (list, non-static)
# index 3 - quest data etc ?


#world cities:
# goatville (midgame)
# torbert's castle (endgame)
# dijkstra forest (mid-endgame)
# schefer city (midgame)
# sophomore village (earlygame)
# syslab plains (early/mid)
# sysadmin castle (mid)
# web forest (early)
# python pass (early)

worldmap = [[None for i in range(6)] for j in range(12)]
worldconnections = [[0 for i in range(9)] for j in range(12)]

#y1 < y2
def connectWorld(connections,y1,x1,y2,x2):
        if(x2==x1):
                connections[y1][2*x1-1] = 1
        elif(x2>x1):
                connections[y1][2*x1] = 2
        else:#x1>x2
                connections[y1][2*x1-2] = 3
        #worldconnections[x1][y1] = direction


worldlocationconnections = {}
worldlocationconnections["Starter Town"] = ["Webian Forest"]
worldlocationconnections["Webian Forest"] = ["Starter Town","Python Pass"]
worldlocationconnections["Python Pass"] = ["Webian Forest","Sophomore Village"]
worldlocationconnections["Sophomore Village"] = ["Python Pass", "Syslab Plains"]
worldlocationconnections["Syslab Plains"] = ["Sophomore Village", "Sysadmin Castle"]
worldlocationconnections["Sysadmin Castle"] = ["Syslab Plains","Schefer City"]
worldlocationconnections["Schefer City"] = ["Sysadmin Castle","Goat Jungle"]
worldlocationconnections["Goat Jungle"] = ["Schefer City","Goatville"]
worldlocationconnections["Goatville"] = ["Goat Jungle","Dijkstra Forest"]
worldlocationconnections["Dijkstra Forest"] = ["Goatville","Torbert's Castle"]
worldlocationconnections["Torbert's Castle"] = ["Dijkstra Forest"]

def getTravelLocations(curcity):
        return worldlocationconnections[curcity]

#IDEAS LOG
# (writing them here so I don't forget any ideas)
# Woglom at sysadmin castle, friendly to player, can give relevant story info,
# like, "it's been taken over, up ahead is _____"
# final boss = Gabor/Zacharias (prolly gabor)
# jack schefer, mayor of schefer city, can give a quest relevant to goat jungle,
# then troll or something
# mid-boss is Akshaj, has taken over sysadmin castle, he's an agent of gabor(/zach)
#  - chess like battle? fellow sophomores help you out? idek
# dijkstra forest - flavor text like:
#   magical forest, they say so complex DFS never terminates, and not even ___fastdijkstraimprovement___
#    can find a path out...
# helper in dijkstra forest? helper character who knows way out helps player (with algo (?))

#TODO: make a character data class/structure (class would probably help)



startTownLoc = (10,1)

worldmap[10][1] = "Starter Town"
worldmap[9][2] = "W_e_b_i_a_n_"
worldmap[9][3] = "_F_o_r_e_s_t"
worldmap[8][4] = "Python Pass"
worldmap[1][4] = "Torbert's Castle"
worldmap[2][3] = "Dijkstra Forest"
worldmap[7][3] = "Sophomore Village"
worldmap[6][2] = "Syslab Plains"
worldmap[5][2] = "Sysadmin Castle"
worldmap[4][2] = "Schefer City"
worldmap[2][1] = " Goat"
worldmap[3][1] = "_Jungle"
worldmap[1][2] = "Goatville"

cities = {"Starter Town":None,"Sophomore Village":None,"Schefer City":None,"Goatville":None}

connectWorld(worldconnections,9,2,10,1)
connectWorld(worldconnections,8,4,9,3)
connectWorld(worldconnections,7,3,8,4)
connectWorld(worldconnections,6,2,7,3)
connectWorld(worldconnections,5,2,6,2)
connectWorld(worldconnections,4,2,5,2)
connectWorld(worldconnections,3,1,4,2)
connectWorld(worldconnections,1,2,2,1)
connectWorld(worldconnections,1,2,2,3)
connectWorld(worldconnections,1,4,2,3)

#worldmap[3][1] = "Goat Jungle"


#worldmap[1][1] = "Galanos Town"
#worldmap[3][4] = "Billington Town"
#worldmap[9][3] = "Kim Town"

# use 8 spaces on either side, preferably
def displayMap_old():
        print("")
        print("")
        for row in worldmap:
                line = ""
                for element in row:
                        if(element == None):
                                line += 8*" "+"."+8*" "
                        else:
                                line += ((8-(len(element)//2))*" "+element+(9-(len(element)//2))*" " if len(element)%2==0 else (8-(len(element)//2))*" "+
                                        element+(8-(len(element)//2))*" ")
                print(line)
                print("")
                print("")


def displayMap(curloc = None):
        print("")
        print("")
        for i in range(len(worldmap)):
                row = worldmap[i]
                line1 = ""
                line2 = ""
                for element in row:
                        if(element == None):
                                line1 += 6*" "+"."+6*" "
                                line2 += 13*" "
                        elif(" " in element):
                                part1 = element[:element.index(" ")].replace("_"," ")
                                part2 = element[element.index(" "):].replace("_"," ")
                                p1len = 6-(len(part1)//2)
                                p2len = 6-(len(part2)//2)
                                line1  += p1len*" "+part1+(p1len+1)*" " if len(part1)%2==0 else p1len*" "+part1+p1len*" "
                                line2 += p2len*" "+part2+(p2len+1)*" " if len(part2)%2==0 else p2len*" "+part2+p2len*" "
                        else:
                                plen = 6-(len(element)//2)
                                line1 += plen*" "+element.replace("_"," ")+((plen+1)*" " if len(element)%2==0 else plen*" ")
                                line2 += 13*" "
                print(line1)
                print(line2)
                connect1 = 7*" "
                connect2 = 7*" "
                for j in range(len(worldconnections[i])):
                        v = worldconnections[i][j]
                        if(j%2==1):
                                if(v==1):
                                        connect1 += 4*" "+"|"
                                        connect2 += 4*" "+"|"
                                else:
                                        connect1 += 5*" "
                                        connect2 += 5*" "
                        else:
                                if(v==2):
                                        connect1 += 5*" "+"\\  "
                                        connect2 += 6*" "+"\\ "
                                elif(v==3):
                                        connect1 += 6*" "+"/ "
                                        connect2 += 5*" "+"/  "
                                else:
                                        connect1 += 8*" "
                                        connect2 += 8*" "
                print(connect1)
                print(connect2)
        if(curloc != None):
                print("Current Location: " + curloc)
        #if(worldmap[curloc[0]][curloc[1]] != None):
         #       print("Current Location: " + worldmap[curloc[0]][curloc[1]])



def playTutorial():
        print("Sorry, there is no tutorial at this time!")
        input("")

def getSaveDisplay(datr):
        datp = datr[2:]
        return None if datp == "-" else "?????"

def startGame(dt):
        saveslot = int(dt[0])
        odata = dt[2:]
        # Character class, current location
        actualdata = ["no_class","no_location"]
        if(odata == "-"):
                print("For a new game, first choose your starting class:")
                printchars = lambda : print("\nClasses:\n" + "".join(" - " + character + "\n" for character in characterpref))
                printchars()
                print("Type a class name to see details, or 'list' to list them again")
                selected = None
                inp = "list"
                while inp != selected or selected == None:
                        inp = input("> ")
                        inp = inp[0].upper() + inp[1:]
                        if(inp == "List"):
                                printchars()
                                selected = None
                        elif(inp != selected):
                                selected = inp
                                inp = None
                                if(selected in characterdat):
                                        print("")
                                        print("")
                                        print("              Class: <<" + selected + ">>")
                                        print("Stats:")
                                        print("ATK " + "|" * characterdat[selected][STAT_SLOT][ATK_STAT])
                                        print("DEF " + "|" * characterdat[selected][STAT_SLOT][DEF_STAT])
                                        print("SPC " + "|" * characterdat[selected][STAT_SLOT][SPC_STAT])
                                        print("SPD " + "|" * characterdat[selected][STAT_SLOT][SPD_STAT])
                                        print("")
                                        print("Hometown:")
                                        print(charhometown[selected])
                                        print("")
                                        print("Information:")
                                        print(charinformation[selected])
                                        print("")
                                        print("Type '" + selected + "' again to select this class")
                                        print("")
                                else:
                                        print("u dumb that's not a class")
                                        selected = None
                        else:
                                print("Selected class <<" + selected + ">>")
                                actualdata[0] = selected
                print("Starting game...")
        else:
                #here we would load data, but right now just [end up] crash[ing]
                pass
                #TODO: Make program crash here
        time.sleep(0.5)
        #print("Sorry, there is no game at this time!")
        print("")
        curlocation = "Starter Town"
        #curlocation = charhometown[actualdata[0]]
        #atcity = True
        lasttown = None
        while True:
                print("curlocation: " + curlocation)
                if(curlocation in cities):
                        lasttown = curlocation
                        displocation = (curlocation if curlocation!="Starter Town" else charhometown[actualdata[0]])
                        print("Welcome to " + displocation)
                        s = ""
                        thislocation = curlocation
                        while curlocation == thislocation:
                                print("What would you like to do?")
                                print("1 - Talk")
                                print("2 - Quest")
                                print("3 - Shop")
                                print("4 - Save")
                                print("5 - Leave")
                                print("")
                                s = input("> ")
                                if(s == "1"):
                                        print(random.choice(towntalkpossibilities[displocation]))
                                        input("")
                                elif(s == "2"):
                                        print("Quests have not been implemented yet!")
                                        input("")
                                elif(s == "3"):
                                        print("Shops have not been implemented yet!")
                                        input("")
                                elif(s == "4"):
                                        print("Saving has not been implemented yet!")
                                        input("")
                                elif(s == "5"):
                                        worldmap[startTownLoc[0]][startTownLoc[1]] = displocation
                                        displayMap()
                                        worldmap[startTownLoc[0]][startTownLoc[1]] = "Starter Town"
                                        #input("")
                                        print("")
                                        print("Where would you like to go?")
                                        poslocs = getTravelLocations(curlocation)
                                        print("".join(str(j+1) + " - " + poslocs[j] + "\n" for j in range(len(poslocs))))
                                        dest = None
                                        while dest not in [str(j+1) for j in range(len(poslocs))]:
                                                dest = input("> ")
                                        curlocation = poslocs[int(dest)-1]
                else: # do battle stuffs
                        print("")

def doBattle(playerinfo, enemyinfo):
        pass

#displayMap("Starter Town")
#input("")

firsttime = not os.path.isfile(datfile)
if(firsttime):
        print("Welcome, young adventurer, to AIQuest!")
        time.sleep(1)
        print("Press [ENTER] to advance dialogue")
        input("")
        print("AIQuest is a text-based adventure game, based")
        print("on the antics that happen in Dr. Torbert's")
        print("7th period AI class")
        input("")
        print("Would you like to view the tutorial?")
        print("1 - Yes")
        print("2 - No")
        if(input("> ").strip()=="1"):
                playTutorial()
        print("Alright, then you're all set to start playing AIQuest!")
        s = open(datfile,"w")
        s.write("1 -\n2 -\n3 -")
        s.close()
        input("")
        print("Good luck!")
        time.sleep(1)
# load aiq.dat
f = open(datfile,"r")
dat = f.read().split("\n")
f.close()

# main menu display
playing = True
while playing:
        print("")
        print("")
        print("/========================\\")
        print("|     -- AI Quest --     |")
        print("|                        |")
        print("| by Neil Thistlethwaite |")
        print(">========================/")
        print("| 1 - Play")
        print("| 2 - Tutorial")
        print("| 3 - Settings")
        print("| 4 - Quit")
        print("")
        o = input("> ").strip()
        if(o == "1"):
                print("")
                print("Save Slots: ")
                for d in dat:
                        print(d[:2] + "- " +  ("New Game" if getSaveDisplay(d)==None else getSaveDisplay(d)))
                toplay = input("> ")
                startGame(dat[int(toplay)-1])
        elif(o == "2"):
                playTutorial()
        elif(o == "3"):
                print("Sorry, there are no settings at this time!")
                input("")
        elif(o == "4"):
                print("Thanks for playing!")
                playing = False
