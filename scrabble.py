#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pygame,sys,codecs
from pygame.locals import *
import scrabble
from modul_utils import textrect,button,progressbar
import board,bag,menu,human,tile,player,ai
from collections import OrderedDict
from itertools import *
#from Tkinter import *
#import tkMessageBox

pygame.init()
BG =(132,24,2)
MIDDLE_SQUARE = (257, 257) #middle point of the board.  
#FONT = None
FONT = 'data/font/FreeSansBold.ttf'
#Simple sound effects
TIC = pygame.mixer.Sound('data/sound/tic.ogg')
TICTIC = pygame.mixer.Sound('data/sound/tictic.ogg')
DINGDING = pygame.mixer.Sound('data/sound/dingding.ogg')
SHUFFLE = pygame.mixer.Sound('data/sound/scriffle.ogg')
CLICK = pygame.mixer.Sound('data/sound/click.ogg')
GAMEOVER = False

#Run the game
def run(isDemo): 
    display() #display screen!
    draw(isDemo)#draw game board,game menu and player tiles
    loadDictionary()
    loadImage()
    #window = Tk()
    #window.wm_withdraw()  
# #############################################################
    MousePressed=False # Pressed down THIS FRAME
    MouseDown=False # mouse is held down
    MouseReleased=False # Released THIS FRAME
    global Target
    Target=None # target of Drag/Drop    
# ################################################################
# ##############save initial image
    global asurf,board_bonus,bonus_coordX,bonus_coordY

    global playedTiles
    playedTiles = [] #keep the array of the played tiles in a move
    global active
    active = 0
    global infoMessage,turnMessage,wordAndMeaning,wordPoint,invalidWords
    infoMessage = u"Oyun başladı.Şimdi oynama sırası sizde..."
    turnMessage = players[active].name
    wordAndMeaning = " "
    invalidWords = " "
    wordPoint = 0
# ##################### All positions that any tile can be at and their status of occupy, both board and tray 
    
    global squares
    squares = {} # it is a map that keeps the squares[(x,y)] = 0 or 1 , empty of not the position x,y of board
    global boardTiles
    boardTiles = {} # keeps the tiles that are played to the board with boardTiles[(x,y)] = tile
    global isFirstMove,isAccepted,isInPlayArea 
    isFirstMove = True   
    
    global PASS_COUNT 
    PASS_COUNT = 0

    #shows that the squares[(x,y)]=0 x,y positions of the board is empty
    for i in range (board.Board.GRID_SIZE):
	for j in range (board.Board.GRID_SIZE):
	    squares[(5 + j * (board.Board.SQUARE_SIZE + board.Board.SQUARE_BORDER), 5 + i * (board.Board.SQUARE_SIZE + board.Board.SQUARE_BORDER))] = 0
	    boardTiles[(5 + j * (board.Board.SQUARE_SIZE + board.Board.SQUARE_BORDER), 5 + i * (board.Board.SQUARE_SIZE + board.Board.SQUARE_BORDER))] = None
	    
    # shows that the positions of the tray is not empty.    
    for i in range (player.Player.TRAY_SIZE):
	    squares[human.Human.TRAY_FIRSTLEFT + i * (board.Board.SQUARE_SIZE + board.Board.SQUARE_BORDER), human.Human.TRAY_FIRSTTOP] = 1                    
            squares[ai.AI.TRAY_FIRSTLEFT + i * (board.Board.SQUARE_SIZE + board.Board.SQUARE_BORDER), ai.AI.TRAY_FIRSTTOP] = 1 
# ##################### All positions that any tile can be at and their status of occupy, both board and tray 

    Target=None # target of Drag/Drop   
    while GAMEOVER == False: #show SCREEN until not close
	# #####################################
	rePaint()
	#gamemenu.createButtons() #draw game menu
	# ####################################
	if isinstance(players[active],ai.AI):
	    aiOperations()
    
	else:
	    isPressedChange = False
	    pos=pygame.mouse.get_pos() #get the mouse position
	    for event in pygame.event.get(): #get event from pygame
		if event.type == pygame.QUIT: #if user click close button
		    pygame.quit()#finish pygame
		    sys.exit()
			
		if event.type == pygame.MOUSEBUTTONDOWN:
		    MousePressed = True 
		    MouseDown = True 
			       
		if event.type == pygame.MOUSEBUTTONUP:
		    MouseReleased = True
		    MouseDown = False	 
		    
		if MousePressed == True:
		    if menu.playButton.pressed(pygame.mouse.get_pos()) and len(playedTiles) == 0:
			CLICK.play()
			drawWarnMessage(u"Lütfen önce taş çekiniz.")
		    if menu.playButton.pressed(pygame.mouse.get_pos()) and len(playedTiles) != 0:
			CLICK.play()
			# !!! VALID MOVE CONTROL
			controlOfValidMove()
			# !!!
			if isFirstMove and squares[MIDDLE_SQUARE] == 0:
			    drawWarnMessage(u"ilk kelime tahtanın ortasında olmalı!")
			elif isFirstMove and len(playedTiles)== 1:
			    infoMessage= u"Geçersiz kelime!"	    
			elif not isAccepted:
			    drawWarnMessage(u"Harflerin hepsi aynı düzlemde olmalı!")
			    
			elif not isInPlayArea and not isFirstMove:
			    drawWarnMessage(u"Harf, bir kelimeye değmeli!")
			    
			else:
			    # ###############################################
			    playTheWord()  			     
			    #  ##############################################			    
		    if menu.changeButton.pressed(pygame.mouse.get_pos()):
			# #####################
			isPressedChange = True
			changeTiles()

		    if menu.backButton.pressed(pygame.mouse.get_pos()): #retrieves the tiles of the player back to the tray from board
			# ##################
			TICTIC.play()
			retrieveBack()
			# ##################	    
			
		    if menu.mixButton.pressed(pygame.mouse.get_pos()): # shuffles the tiles
			# ##################
			mixTray()
			# ##################    
    
		    if menu.passButton.pressed(pygame.mouse.get_pos()):
			CLICK.play()
			infoMessage= u"Pas geçtiniz."
			# ##################
			retrieveBack()
			# ##################
			PASS_COUNT = PASS_COUNT + 1
			changePlayer()		
			refreshTray()
			
		    if menu.surrenderButton.pressed(pygame.mouse.get_pos()):
			TIC.play()
			showGameResult("surrender")

		    if menu.exitButton.pressed(pygame.mouse.get_pos()):
			TIC.play()
			showGameResult("exit")

		    if menu.homeButton.pressed(pygame.mouse.get_pos()):
			TIC.play()
			menu.main()
			
		    if not isPressedChange:
			for item in players[active].tray: # search all items
			    if (pos[0] >= (item.coordinate[0]) and 
				pos[0] <= (item.coordinate[0] + item.SQUARE_SIZE) and 
				pos[1] >= (item.coordinate[1]) and 
				pos[1] <= (item.coordinate[1] + item.SQUARE_SIZE)): # inside the bounding box
				Target = item # "pick up" item
				# ####   NEW
				squares[Target.coordinate[0],Target.coordinate[1]] = 0 # Update the position as empty
				# ####   NEW
				Target.oldPos = Target.coordinate[:]
				
				# setting the target as the last element of the player's tray[] list
				indexofTarget = players[active].tray.index(Target)
				temp = players[active].tray[-1] #last element of tray
				players[active].tray[indexofTarget] = temp
				players[active].tray[-1] = Target# now last element is Target
				# setting the target as the last element of the player's tray[] list
				break
		      
		if MouseDown and Target is not None: # if we are dragging something
		    Target.coordinate = (pos[0] - tile.Tile.SQUARE_SIZE/2, pos[1] - tile.Tile.SQUARE_SIZE/2) # move the target with mouse ############Holds the tile from the middle
		
		if MouseReleased and Target is not None:
		    # #### CONTROL OF MOUSE DRAG AND DROP OPERATIONS
			mouseDragAndDropOperations()
		    # ####
		    
		MousePressed = False # Reset these to False
		MouseReleased = False # Ditto

# ###############
	players[active].drawTray(SCREEN)#draw tiles of the player 
	
# #############
        pygame.display.update()    

# ####################################DRAW#############################################
def draw(isDemo):
    global tilebag
    tilebag = bag.Bag() #create a bag of tiles
    global gameboard
    gameboard = board.Board()#create game board
    global gamemenu
    gamemenu = menu.GameMenu()#create game menu
    SCREEN.fill(BG)
    
    ai.AI.IS_DEMO = isDemo
    
    # ######## tile trial #######
    global players,active
    players = []
    active = 0 # MIGHT 0 represents the first player	 
    if not isDemo:
        players.append(human.Human("Sen", gameboard, tilebag))
	#players.append(human.Human("Sen", gameboard, tilebag))
	players.append(ai.AI("Bilgisayar", gameboard, tilebag))
    else:
	players.append(ai.AI("Oyuncu", gameboard, tilebag))
	players.append(ai.AI("Bilgisayar", gameboard, tilebag))	
    # ########### tile trial end  ################
    gameboard.draw() #draw game board
    players[active].drawTray(SCREEN)#draw tiles of the player
    gamemenu.createButtons() #draw game menu
# ####################################DRAW#############################################

def loadImage():
    global asurf,board_bonus,bonus_coordX,bonus_coordY
    asurf = pygame.image.load('data/images/Board.jpg') 
    SCREEN.blit(asurf.convert_alpha(),[0,0])
    
    # draw start point
    start_point = pygame.image.load('data/images/start_point.png').convert()
    SCREEN.blit(start_point,MIDDLE_SQUARE)  
    
    # draw bonus ######################
    board_bonus = pygame.image.load('data/images/board_bonus.png').convert()
    from random import randint
    bonus_coordX = randint(0,14)*36+5
    bonus_coordY = randint(0,14)*36+5
    while gameboard.squares[(bonus_coordX-5)/36][(bonus_coordY-5)/36] != (None, 'normal') or (bonus_coordX,bonus_coordY) == MIDDLE_SQUARE or bonus_coordX == 221 or bonus_coordX == 185 or bonus_coordX == 293 or bonus_coordX == 329 or bonus_coordY == 221 or bonus_coordY == 185 or bonus_coordY == 293 or bonus_coordY == 329:
	from random import randint
	bonus_coordX = randint(0,14)*36+5
	bonus_coordY = randint(0,14)*36+5
  
    SCREEN.blit(board_bonus,(bonus_coordX,bonus_coordY))
    # ###############    
    rect = pygame.Rect(0, 0, 545, 545)
    sub = SCREEN.subsurface(rect) 
    pygame.image.save(sub, "data/images/Board.png")
    asurf = pygame.image.load('data/images/Board.png')  

def drawScoreTable():   
    pygame.draw.rect(SCREEN,  (219,166,100), (590, 100, 150, 100)) #table
    pygame.draw.rect(SCREEN,  (187, 121,63), (590, 100, 5, 100))
    pygame.draw.rect(SCREEN,  (187, 121,63), (590, 100, 150, 6))
    pygame.draw.rect(SCREEN,  (187, 121,63), (740, 100, 5, 100))
    pygame.draw.rect(SCREEN,  (187, 121,63), (590, 200, 155, 6))
    pygame.draw.rect(SCREEN,  (141,124,0), (598, 126, 126, 2)) #green line
    pencil = pygame.image.load('data/images/pencil.png')
    SCREEN.blit(pencil,(690,130))
    SCREEN.blit(pygame.font.Font(FONT, 16).render("SKOR TABLOSU", True, (141,124,0)), (598, 106))
    for i in range(0,len(players)):
	SCREEN.blit(pygame.font.Font(FONT, 15).render(players[i].name+": "+str(players[i].score), True,(70,35,0)), (600, 136+i*20))     
     
def drawInfoMessage(message,turnMessage):  
    SCREEN.blit(pygame.font.Font(FONT, 13).render(u"Kalan Taş Sayısı: "+str(len(tilebag.tiles)), True, (255,192, 0)), (550, 50)) 
    SCREEN.blit(pygame.font.Font(FONT, 14).render(u"OYUN SIRASI: "+turnMessage, True, (255,192, 0)), (550, 70))  
    pygame.draw.rect(SCREEN, (80,148,216), (560, 240, 210, 30))
    SCREEN.blit(pygame.font.Font(FONT, 16).render(u"            Oyun Bilgisi", True,  (255,255,255)), (565, 246))
    message ="\n " +  message 
    message = textrect.render_textrect(unicode(message), pygame.font.Font(None, 22),pygame.Rect((560,290, 210, 180)), (55, 46, 40), (255,255,255), 0)
    SCREEN.blit(message, (560, 270)) 
    pygame.draw.rect(SCREEN, (80,148,216), (560, 445, 210, 5)) #bottom
    pygame.draw.rect(SCREEN, (80,148,216), (555, 240, 5, 210)) #left
    pygame.draw.rect(SCREEN, (80,148,216), (770, 240, 5, 210)) #right   

def drawWarnMessage(message):
    pop_change = pygame.image.load('data/images/warn.png')
    message ="\n  " +  message 
    i = 0
    while i < 120:
        players[active].drawTray(SCREEN)
	SCREEN.blit(pop_change,(150, 200))
	messageshow = textrect.render_textrect(unicode(message), pygame.font.Font(FONT, 12),pygame.Rect((155,225, 247, 120)), (78,77,73), (246,245,240), 0)
	SCREEN.blit(messageshow, (155, 221))
	pygame.display.update()
	i = i + 1	    

def showGameResult(type): 
    global infoMessage
    players0score = players[0].score
    players1score = players[1].score   
    remainingTilesPoints = 0
    if type == "gameover":		
	if len(players[1].tray) == 0: #winner player1 players[0].score < players[1].score and 
	    remainingTilesPoints = 0	    
	    for t in players[0].tray:
		remainingTilesPoints = remainingTilesPoints+t.points				
	    players0score = players[0].score - remainingTilesPoints
	    players1score = players[1].score + remainingTilesPoints
	elif len(players[0].tray) == 0: #winner player0 players[0].score > players[1].score and 
	    remainingTilesPoints = 0
	    for t in players[1].tray:
		remainingTilesPoints = remainingTilesPoints+t.points				
	    players1score = players[1].score - remainingTilesPoints
	    players0score = players[0].score + remainingTilesPoints
    
    MousePressed = False
    surrender = True
    rePaint()	
    while surrender is True: #show SCREEN until not close
	# #####################################
	rePaint()
	#gamemenu.createButtons() #draw game menu
	#players[active].drawTray(SCREEN)
	if type == "surrender":
	    gamemenu.createOkCancelButtons("surrender") #draw OKANDCANCELBUTTONS  
	if type == "exit":
	    gamemenu.createOkCancelButtons("exit") #draw OKANDCANCELBUTTONS  	
	
	pos=pygame.mouse.get_pos() #get the mouse position
	for event in pygame.event.get(): #get event from pygame
	    if event.type == pygame.QUIT: #if user click close button
		pygame.quit()#finish pygame
		sys.exit()
				
	    if event.type == pygame.MOUSEBUTTONDOWN:
		MousePressed = True 
		MouseDown = True 
			   
	    if event.type == pygame.MOUSEBUTTONUP:
		MouseReleased = True
		MouseDown = False	 

	    if MousePressed == True or type == "gameover" :				
		if type == "gameover" or (type == "surrender" and menu.cancelButton.pressed(pygame.mouse.get_pos())):
		    isPressed = True
		    infoMessage= u"Oyun Bitti!"
		    while isPressed is True:
			rePaint()
			#gamemenu.createButtons() #draw game menu
			#players[active].drawTray(SCREEN)
		        gamemenu.drawGameResult(players0score,players1score,type,remainingTilesPoints)
			pos=pygame.mouse.get_pos() #get the mouse position
			for event in pygame.event.get(): #get event from pygame
			    if event.type == pygame.QUIT: #if user click close button
				pygame.quit()#finish pygame
				sys.exit()		
			    if event.type == pygame.MOUSEBUTTONDOWN:
				MousePressed = True 
				MouseDown = True 
					   
			    if event.type == pygame.MOUSEBUTTONUP:
				MouseReleased = True
				MouseDown = False
				
			    if MousePressed == True:				
				if menu.closeButton.pressed(pygame.mouse.get_pos()):
				    isPressed = False
				    pygame.quit()#finish pygame
				    sys.exit()
				    return
				elif menu.againButton.pressed(pygame.mouse.get_pos()):
				    run(False)
			    MousePressed = False # Reset these to False
			    MouseReleased = False # Ditto
			    
			pygame.display.update()	
		    surrender =  False
		elif ((type == "surrender" or type == "exit") and menu.okButton.pressed(pygame.mouse.get_pos())):
		    surrender =  False	
	        elif type == "exit" and menu.cancelButton.pressed(pygame.mouse.get_pos()):
		    pygame.quit()#finish pygame
		    sys.exit()
	    MousePressed = False # Reset these to False
	    MouseReleased = False # Ditto
	    
	pygame.display.update()
    
def rePaint():
    SCREEN.fill(BG) # clear screen
    SCREEN.blit(asurf.convert_alpha(),[0,0])
    pygame.draw.rect(SCREEN, BG, (5, 545, 785, 150)) #bottom side
    drawScoreTable()
    drawInfoMessage(infoMessage,turnMessage) 
    gamemenu.createButtons() #draw game menu
    players[active].drawTray(SCREEN)

#retun global SCREEN
def getScreen():
    return SCREEN

#retun global SCREEN
def getPlayers():
    return players

#Create a display
def display():
    #Initialize pygame
    pygame.init()    
    global SCREEN #create a global Screen
    size = (800,700) #size of the SCREEN   
    SCREEN = pygame.display.set_mode(size) # show SCREEN   
    #SCREEN=  pygame.display.set_mode((0,0), NOFRAME , 16)
    pygame.display.set_caption("KELiME OYUNU") #name of the window
    
def loadDictionary():
    global DICTIONARY
    DICTIONARY = OrderedDict()
    #load word list
    with codecs.open("data/db/db.txt", 'r', 'utf-8') as openfile:
	for word in openfile.read().splitlines():
	    if word not in DICTIONARY:		
		DICTIONARY[word] = ""		
    openfile.close()   
 
def isInTurkishDictionary(currentWord):
# check the database
    currentWord = unicode(currentWord.lower())
    isExist = False
    global wordAndMeaning,isInBonusSquare,invalidWords,wordPoint
    if currentWord in DICTIONARY.keys():
	wordAndMeaning = wordAndMeaning+ currentWord+" ("+str(wordPoint)+")\n "
	isExist = True
    else:
	invalidWords = currentWord + " (X) "    
    return isExist

def refreshTray(): # #####Refresh tray part of squares[] for new players tray
    # ###################### GET NEW TILES FROM BAG WHEN THE TILES ARE PLACED TO BOARD
    # shows that the positions of the tray is not empty.
    if isinstance(players[active], human.Human):
	for t in players[active].tray:
	    if t.coordinate == (None, None):
		for i in range (player.Player.TRAY_SIZE):
		    #if isinstance(players[active], ai.AI):
			#coor = (ai.AI.TRAY_FIRSTLEFT + i * (board.Board.SQUARE_SIZE + board.Board.SQUARE_BORDER), ai.AI.TRAY_FIRSTTOP)
		    #else:
		    coor = (human.Human.TRAY_FIRSTLEFT + i * (board.Board.SQUARE_SIZE + board.Board.SQUARE_BORDER), human.Human.TRAY_FIRSTTOP)
		    if squares[coor] == 0:
			t.setCoordinate(coor)
			squares[coor] = 1
			break
	#i = 0
	#for t in players[active].tray:
		#top = human.Human.TRAY_FIRSTTOP
		#left = (human.Human.TRAY_FIRSTLEFT + (i * (tile.Tile.SQUARE_SIZE + tile.Tile.SQUARE_BORDER)))					
		#t.setCoordinate((left,top))
		#squares[(left,top)] = 1
		#i += 1		
    #  ##############################################################################
    #Draw each tile
    if isinstance(players[active], ai.AI):
	i = 0
	for t in players[active].tray:
		top = ai.AI.TRAY_FIRSTTOP
		left = (ai.AI.TRAY_FIRSTLEFT + (i * (tile.Tile.SQUARE_SIZE + tile.Tile.SQUARE_BORDER)))					
		t.setCoordinate((left,top))
		squares[(left,top)] = 1
		i += 1	
    
    for x in range(player.Player.TRAY_SIZE):   
	full = False
	
	if isinstance(players[active], ai.AI):
	    coor = (ai.AI.TRAY_FIRSTLEFT + x * (board.Board.SQUARE_SIZE + board.Board.SQUARE_BORDER), ai.AI.TRAY_FIRSTTOP)
	else:
	    coor = (human.Human.TRAY_FIRSTLEFT + x * (board.Board.SQUARE_SIZE + board.Board.SQUARE_BORDER), human.Human.TRAY_FIRSTTOP)	
	
	for t in players[active].tray:
	    if t.coordinate == coor:
		squares[coor[0], coor[1]] = 1
		full = True
		break
	if full == False:
	    squares[coor[0], coor[1]] = 0    

def retrieveBack():
    global playedTiles
    j = 0
    for k in range (len(playedTiles)):
	for i in range (player.Player.TRAY_SIZE):
	    if squares[human.Human.TRAY_FIRSTLEFT + i * (board.Board.SQUARE_SIZE + board.Board.SQUARE_BORDER), human.Human.TRAY_FIRSTTOP] == 0:
		squares[playedTiles[k].coordinate[0], playedTiles[k].coordinate[1]] = 0
		playedTiles[k].coordinate = human.Human.TRAY_FIRSTLEFT + i * (board.Board.SQUARE_SIZE + board.Board.SQUARE_BORDER), human.Human.TRAY_FIRSTTOP
		j = j + 1
		squares[human.Human.TRAY_FIRSTLEFT + i * (board.Board.SQUARE_SIZE + board.Board.SQUARE_BORDER), human.Human.TRAY_FIRSTTOP] = 1
		
    playedTiles = []
    players[active].justTray = players[active].tray[:]
  
def mixTray():
    from random import randint 
    players[active].justTray.sort(key = lambda x: x.coordinate[0], reverse = False) # ## Sort the tiles that are in the tray of the player by their coordinates
    # We need to do sorting so we can go through them by order, if there is a gap before any tile, it is going to be shifted to left until there is no gap
    SHUFFLE.play()
    for t in players[active].justTray: # shift all squares to left, without empty squares
	for x in range(player.Player.TRAY_SIZE):
	    if ((t.coordinate[0], t.coordinate[1]) != (human.Human.TRAY_FIRSTLEFT, human.Human.TRAY_FIRSTTOP)): 
		if (squares[t.coordinate[0] - (board.Board.SQUARE_SIZE + board.Board.SQUARE_BORDER), t.coordinate[1]] == 0):
		    squares[t.coordinate[0], t.coordinate[1]] = 0
		    t.coordinate = [t.coordinate[0] - (board.Board.SQUARE_SIZE + board.Board.SQUARE_BORDER), t.coordinate[1]]
		    squares[t.coordinate[0], t.coordinate[1]] = 1
		else:
		    break
	    else:
		break    
    #print players[active].justTray
    for t in players[active].justTray:
	x = randint(0, (len(players[active].justTray)-1))
	temp = t.coordinate
	t.coordinate = players[active].justTray[x].coordinate
	players[active].justTray[x].coordinate = temp   

def changeTiles():
    global infoMessage,active
    if tilebag.isEmpty():
	if isinstance(players[active],ai.AI):
	    infoMessage= players[active].name+ u" pas geçti, sıra sizde.."
	    drawInfoMessage(infoMessage, players[active].name)	
	    changePlayer()	    
	else:
	    drawWarnMessage(u"Torbada taş kalmadı...")	

    elif isinstance(players[active],human.Human) :
	retrieveBack()
	MousePressed = False
	change = True
	rePaint()	
	changedTiles = []
	isPressedOk = False
	players[active].ISCHANGE = "changing"
	while change is True: #show SCREEN until not close
	    # #####################################
	    rePaint()				
	    gamemenu.createOkCancelButtons("change") #draw OKANDCANCELBUTTONS  
	    pos=pygame.mouse.get_pos() #get the mouse position
	    for event in pygame.event.get(): #get event from pygame
		if event.type == pygame.QUIT: #if user click close button
		    pygame.quit()#finish pygame
				    
		if event.type == pygame.MOUSEBUTTONDOWN:
		    MousePressed = True 
		    MouseDown = True 
			       
		if event.type == pygame.MOUSEBUTTONUP:
		    MouseReleased = True
		    MouseDown = False	 
    
		if MousePressed == True:				
		    if menu.cancelButton.pressed(pygame.mouse.get_pos()):
			change = False
			players[active].ISCHANGE = "finishchanging"
			players[active].drawTray(SCREEN)
			pygame.display.update()
			players[active].ISCHANGE = "no"					    
		    elif menu.okButton.pressed(pygame.mouse.get_pos()) and len(changedTiles)==0:
			isPressedOk = True
		    elif menu.okButton.pressed(pygame.mouse.get_pos()) and len(changedTiles)>len(tilebag.tiles):
			drawWarnMessage(u"Torbada yalnızca %d taş kaldı.Lütfen değiştirmek istediğiniz %d taşı seçiniz." % (len(tilebag.tiles),len(tilebag.tiles)))			    
		    elif menu.okButton.pressed(pygame.mouse.get_pos()):
			for Tar in changedTiles:          
			    players[active].tray.remove(Tar) #firstly we remove the selected tiles from the tray of the player
			    players[active].justTray.remove(Tar)

			# # grab new tiles from bag
			if players[active].grab() == False:
			    infoMessage= u"Torbada taş kalmadı."
			    change = False
			    			
			else:
			    for t in changedTiles:
				#squares[t.coordinate] = 0
				t.coordinate = (None,None)
				t.oldPos = (None,None)
				tilebag.putBack(t) #secondly we put back these tiles to the bag
			    			    
			    change = False
			    players[active].ISCHANGE = "finishchanging"
			    players[active].drawTray(SCREEN)
			    refreshTray()
			    pygame.display.update()
			    players[active].ISCHANGE = "no"
			    infoMessage= u"Taş değişikliği yaptınız, sıra Bilgisayarda.."
			    drawInfoMessage(infoMessage, players[active].name)			    
			    changePlayer()
			break							    
		    
		    for item in players[active].tray: # search all items
			if (pos[0] >= (item.coordinate[0]) and 
		            pos[0] <= (item.coordinate[0] + item.SQUARE_SIZE) and 
		            pos[1] >= (item.coordinate[1]) and 
		            pos[1] <= (item.coordinate[1] + item.SQUARE_SIZE) ): # inside the bounding box
			    Tar = item # "pick up" item
			    if Tar not in changedTiles:
				changedTiles.append(Tar)
				TICTIC.play()
			    elif Tar in changedTiles:
				changedTiles.remove(Tar)
						
		MousePressed = False # Reset these to False
		MouseReleased = False # Ditto
		
	       
	    players[active].drawTray(SCREEN)
	    if change:
		for t in changedTiles:
		    pygame.draw.rect(SCREEN, tile.Tile.TILE_HIGHLIGHT, (t.coordinate[0], t.coordinate[1], tile.Tile.SQUARE_SIZE, tile.Tile.SQUARE_SIZE), 2) #highlight the selected tiles
			
	    pop_change = pygame.image.load('data/images/pop_change.png')
	    if isPressedOk is True and len(changedTiles)==0:
		i = 0
		while i < 100:
		    SCREEN.blit(pop_change,(150, 200))
		    SCREEN.blit(pygame.font.Font(FONT, 12).render(u"         Lütfen en az bir taş seçiniz ..", True, (78,77,73)), (160, 230))
		    players[active].drawTray(SCREEN)
		    pygame.display.update()
		    i = i + 1
		isPressedOk = False
	    elif change:
		SCREEN.blit(pygame.font.Font(FONT, 11).render(u"Değiştirmek istediğiniz harfleri seçiniz..", True, (78,77,73)), (160, 230))				    
	    pygame.display.update()

    else:
	changedTiles = []  
	for Tar in players[active].tray: # search all items
	    if len(changedTiles) <= len(tilebag.tiles):
		changedTiles.append(Tar)
	    if len(changedTiles) == len(tilebag.tiles):
		break
	    
	for Tar in changedTiles:          
	    players[active].tray.remove(Tar) #firstly we remove the selected tiles from the tray of the player
    
	#grab new tiles from bag    
	players[active].grab()
	
	for t in changedTiles:
	    #squares[t.coordinate] = 0
	    t.coordinate = (None,None)
	    t.oldPos = (None,None)
	    tilebag.putBack(t) #secondly we put back these tiles to the bag
	    
	#Refresh the ai tray		
	refreshTray()	    	
	infoMessage= players[active].name+ u" taş değişikliği yaptı, sıra sizde.."
	drawInfoMessage(infoMessage, players[active].name)
	players[active].drawTray(SCREEN)
	pygame.display.update()	
	pygame.time.wait(2000) 	
	changePlayer()	

def changePlayer():
    global active,turnMessage,infoMessage,PASS_COUNT
    currentActive = active

    if PASS_COUNT == 3:
	infoMessage= u"Oyun Bitti!"
	showGameResult("gameover")    

    if active == len(players)-1:
	active = 0
    else:
	active = active + 1
    turnMessage = players[active].name
    
    if wordPoint != 0:
	if active:
	    infoMessage = u"'%d' puan kazandınız. Şimdi Bilgisayar oynuyor.." % (wordPoint)
	else:
	    #infoMessage = u"Bilgisayar '%d' puan kazandı. Şimdi oynama sırası sizde.." % (wordPoint)    
	    infoMessage = u"Şimdi oynama sırası sizde.."

    
    #players[active].drawTray(SCREEN)
    rePaint()

def aiOperations():
    global letters, infoMessage, wordPoint, wordAndMeaning, PASS_COUNT,isInBonusSquare,isFirstMove
    global candList
    candList = []    #candidate words that ai might play, best option will be calculated by points
    global candWord
    infoMessage = ""
    letters = ""
    global wList
    wList = []
    bestOp = 0
    bestWord = ""
    trayLetters = ""
    global firstTurn
    firstTurn = False

    for t in players[active].tray:
	trayLetters = trayLetters + t.letter 
	
    if not isFirstMove:
	#create progress bar  
	thinkingMessage= players[active].name +  u" düşünüyor.."
	pb = progressbar.ProgressBar(1000, 10, (160,40), (200,200,255), (100,150,55))
	SCREEN.blit(pygame.font.Font(FONT, 14).render(thinkingMessage, True,  (255,255,255)), (565, 465))	
	
    #search board tiles and find all possible words choose the best one
    for y in range(15):
	for x in range(15):
	    
	    for event in pygame.event.get():
		if event.type == pygame.QUIT:
		    pygame.quit()#finish pygame
		    sys.exit()  
		    
	    if not isFirstMove: 
		#show progress bar
		slice = float(x + y*14)/float(14 + 14*14)
		pb.makestep(slice)	    

	    if not (x*36+5 <= 509 or y*36+5 <= 509):
		continue
	    til = boardTiles[x*36+5, y*36+5]
	    
	    candList = []
	    
	    if x == 7 and y == 7 and til == None: #if isFirstMove:  # if the middle square is empty which is 7th from top and 7th from left
		firstTurn = True
		rightneighLetters = []
		currLetters = trayLetters
		candList = candidateWords(currLetters,til)
		maxRight = findMax(til, "R", rightneighLetters, candList)
		subneighLetters = []
		maxLeft = findMax(til, "S", subneighLetters, candList)
		if maxLeft[0] >= maxRight[0]:
		    tempBestOp = maxLeft
		else:
		    tempBestOp = maxRight
		bestOp = tempBestOp[0] 
		bestWord = tempBestOp[1]
		bOr = tempBestOp[2][:]
		bNL = tempBestOp[3][:]
		bTil = til		
		break
	    
	    if not til == None:
		firstTurn = False
		
		# right
		currLetters = trayLetters + til.letter	# will hold the letters that going to be in process
                
		rightneighLetters = getRightAndSubList(til,"right")
		for l in rightneighLetters:
		    currLetters = currLetters + l[0]
	    
		candList = candidateWords(currLetters,til)
		
		maxRight = findMax(til, "R", rightneighLetters, candList)#return (maxP, bestWord, til)
		
		#sub		
		currLetters = trayLetters + til.letter	# here it stays for reset
		
		subneighLetters = getRightAndSubList(til,"sub")
		for l in subneighLetters:
		    currLetters = currLetters + l[0]
		
		candList = candidateWords(currLetters,til)
		
		maxLeft = findMax(til, "S", subneighLetters, candList)#return (maxP, bestWord, til)
		
		# max of right and sub option
		
		if maxLeft[0] >= maxRight[0]:
		    tempBestOp = maxLeft
		else:
		    tempBestOp = maxRight
		    
		# tempbestop ile bestop karsilastir
		if tempBestOp[0] > bestOp:
		    bestOp = tempBestOp[0] 
		    bestWord = tempBestOp[1]
		    bOr = tempBestOp[2][:]
		    bNL = tempBestOp[3][:]
		    bTil = til
		
	if firstTurn == True:
	    break
	
    #thinking_thread.sleep()
    if bestWord == "":#ai cannot find any word to play so change tiles and pass to other player
	PASS_COUNT = PASS_COUNT + 1
	changeTiles()
    else:
	# ######## play the best option
	placeWord(bestWord, bTil, bOr, bNL)
	wordPoint = bestOp
	wordAndMeaning = players[active].name+" '"+ unicode(bestWord[0][:].lower()) + "' kelimesinden "+str(wordPoint)+ u" puan kazandı.."
	playTheWord()

def findMax(til, orient, neighLetters = [], candidateW = []):
    global letters, infoMessage, wordPoint, playedTiles, firstTurn
    bOr = orient[:]
    bNL = neighLetters[:]
    wList = []
    maxP = 0    # will hold the max point for this tile
    bestWord = "" # will hold the best word option that could be played in the current orientation
    candWord = True
     
    if firstTurn == False:
	for w in candidateW:  # candidate words are going to be eleminated depending on the neighboors of the current letter
	    candWord = True
	    wrd = w[0]
	    pos = w[1]
	    
	    for nl in neighLetters:    
		if pos+nl[1] <  len(wrd): #wrd[pos + nl[1]] != None:
		    if wrd[pos + nl[1]] != nl[0]:
			candWord = False
			break
		else:
		    candWord = False
		    break		
    
	    if candWord == True:
		wList.append(w)
					    
	candidateW = wList[:]
    
    for wo in candidateW: 
	if placeWord(wo, til, orient, neighLetters) == False:	# if there is another tile in one of the squares that word is tried to be placed
	    for t in players[active].tray:	# gets the tiles back from the table to tray
		squares[t.coordinate] = 0
		t.coordinate = t.oldPos	    
		squares[t.coordinate] = 1
	    playedTiles = []
	    continue
	
	# update best word that has max point to play
	if playedTiles and checkWord() is True and wordPoint > maxP:
	    bestWord = wo
	    maxP = wordPoint
	    bNL = neighLetters[:]
	    bOr = orient[:]

	wordPoint = 0	# this global variable is reset for each word
	
	for tl in playedTiles:
	    boardTiles[(tl.coordinate[0], tl.coordinate[1])] = None
	    squares[(tl.coordinate[0], tl.coordinate[1])] = 0	
		
	for t in players[active].tray:	# point calculation of the current word is done, reset the board by removing the tiles of the word
	    t.coordinate = t.oldPos	
	    
	playedTiles = []    # reset for next word's point calculation

    #tkMessageBox.showinfo(title="Return FindMax", message="MaxP="+str(maxP)+" BestWord="+str(bestWord))   
    return (maxP, bestWord, bOr, bNL)	

def placeWord(w, tl, ori, neighLets = []):
    global squares, playedTiles
    word = w[0][:]
    tilIndx = w[1]
    if firstTurn == True:   # if the first turn is going to be played by AI
	tilOrMid = MIDDLE_SQUARE    # start placing the letters of the word from middle square
	counter = 0
    else:
	tilOrMid = tl.coordinate
	counter = tilIndx  # placement is going to  start	from the "current tiles coordinate - (index of current tile's letter in the current word)" coordinate
    illegalWordPlacement = False

    for l in word:
	if firstTurn == False:
	    passIt = False
	    if counter == 0:  # # If it is the current Tile's place then do not set any tile coordinate
		counter = counter - 1
		continue
	     # # If it is the place of one of the neighboor letters of the current tile then do not set any tile coordinate
	    for nl in neighLets:
		if -(counter) == nl[1]:
		    passIt = True
		    break
		
	    if passIt == True:
		counter = counter - 1
		continue
	    
	for t in players[active].tray:        # ### each word on tray that is used in this word is going to be placed on board
	    if unicode(t.letter.lower()) == l and t.coordinate == t.oldPos:
		
                try:
		    if ori == "R":
			
			if boardTiles[tilOrMid[0] - (counter)*36, tilOrMid[1]] != None:
			    illegalWordPlacement = True
			    break
			else:
			    squares[t.coordinate] = 0
			    t.coordinate = tilOrMid[0] - (counter)*36, tilOrMid[1]
			    squares[t.coordinate] = 1
			    playedTiles.append(t)
			    break
		    
		    else:
			if boardTiles[tilOrMid[0], tilOrMid[1] - (counter)*36] != None:
			    illegalWordPlacement = True
			    break
			
			else:
			    squares[t.coordinate] = 0
			    t.coordinate = tilOrMid[0], tilOrMid[1] - (counter)*36
			    squares[t.coordinate] = 1	
			    playedTiles.append(t)
			    break
		except KeyError:
		    illegalWordPlacement = True
		    break		    
		    		    
	if illegalWordPlacement == True:
	    return False
	
	counter = counter - 1
    
    return True

def getRightAndSubList(tile,type):
    rightList = [] #keep the tuple like neigbour letter,distance of it to the current tile
    subList = []   #keep the tuple like neigbour letter,distance of it to the current tile
    
    if type == "right":
	# right neighbours of a tile 
	currentLastLetterX = tile.coordinate[0] 
	while currentLastLetterX+36<=509:
	    currentTile = boardTiles[(currentLastLetterX+36,tile.coordinate[1])]
	    if currentTile!=None:
		rightList.append((currentTile.letter.lower(),(currentTile.coordinate[0]-tile.coordinate[0])/36))
	    currentLastLetterX = currentLastLetterX+36
	
	return rightList
    
    elif type == "sub":
	# sub neighbours of a tile 
	currentLastLetterY = tile.coordinate[1] 
	while currentLastLetterY+36<=509:
	    currentTile = boardTiles[(tile.coordinate[0],currentLastLetterY+36)]
	    if currentTile!=None:
		subList.append((currentTile.letter.lower(),(currentTile.coordinate[1]-tile.coordinate[1])/36))
	    currentLastLetterY = currentLastLetterY+36
	  
	return subList

def candidateWords(letters,til):
    letters = unicode(letters.lower())
    candList = []
   				     
    lowLetters = list(letters)
     
    for w in DICTIONARY.keys():
	candWord = True
	ltsTemp = lowLetters[:]
	
	if not til == None:
	    if not unicode(til.letter.lower()) in w:  # if current tile is not exist in the word, skip the word
		continue
	
	tempCount = 0
	index = -1 # will hold that which index is current letter in the corresponding word
	for l in w:
	    if not l in ltsTemp:
		candWord = False
		break
	    else:
		ltsTemp.remove(l)
		if not til == None:
		    if l == unicode(til.letter.lower()):
			index = tempCount # index 0 if til.letter does not exit otherwise it is the index in word for ex. a-->> ikaz -->>index = 2
		    
	    tempCount = tempCount + 1
	
	if candWord == True:
	    candList.append((w,index))   # w has the current letter at the index: (w,indx) 
    
    return candList
 
def playTheWord():
    isValidWord = True
    global infoMessage, turnMessage, wordAndMeaning, wordPoint, isFirstMove, playedTiles, active, squares, boardTiles, asurf,invalidWords,PASS_COUNT
    # Check the Turkish dictionary for the word
    if not isinstance(players[active], ai.AI):
	isValidWord = checkWord()
    else:
	for til in playedTiles:
		boardTiles[(til.coordinate[0],til.coordinate[1])] = til
		squares[(til.coordinate[0],til.coordinate[1])] = 1	
		
    if isValidWord:
	DINGDING.play()
	PASS_COUNT = 0
	infoMessage = wordAndMeaning
	drawInfoMessage(infoMessage,turnMessage)   
	players[active].drawTray(SCREEN)	#draw tiles of the player 
	
	# Change the color of the played tiles
	tile.Tile.TILE_COLOR = (255,128,114) #pink
	tile.Tile.TILE_HIGHLIGHT =  (255,128,114) #pink
	for Tar in playedTiles:
	    Tar.draw(False)	
	    
	#color of the current tiles in tray
	tile.Tile.TILE_COLOR =  (255, 255, 51)#yellow
	tile.Tile.TILE_HIGHLIGHT = (100, 100, 255) #blue
	
	pygame.display.update()
	pygame.time.wait(2000)
	wordAndMeaning = ""
	invalidWords = ""
	if isFirstMove:
	    isFirstMove = False		    
    # #################save image when the tiles are played#########
	players[active].drawTray(SCREEN)
	for Targ in playedTiles:
	    players[active].tray.remove(Targ)

	# # grab new tiles from bag
	if players[active].grab() == False:
	    infoMessage= u"Oyun Bitti!"
	    showGameResult("gameover")
        
        # refresh tray of the player
        refreshTray()

	players[active].drawTray(SCREEN)
	
	# Change the color of the played tiles
	tile.Tile.TILE_COLOR = (246, 226, 111) #brown
	tile.Tile.TILE_HIGHLIGHT =  (246, 226, 111) #brown
	for Tar in playedTiles:
	    Tar.draw(True)	
	    
	#save image
	playedTiles = []
	rect = pygame.Rect(0, 0, 545, 545)
	sub = SCREEN.subsurface(rect)
	pygame.image.save(sub, "data/images/Board.png")
	asurf = pygame.image.load('data/images/Board.png')
	
	#color of the current tiles in tray
	tile.Tile.TILE_COLOR =  (255, 255, 51)#yellow
	tile.Tile.TILE_HIGHLIGHT = (100, 100, 255) #blue
	
	# pass to the next player
	players[active].score += wordPoint
	changePlayer()
	wordPoint=0
	
	refreshTray()			    
	return True
    else:
	infoMessage= u"Geçersiz kelime!" + "\n " + invalidWords
	wordAndMeaning = ""
	invalidWords = ""
	wordPoint = 0
	for til in playedTiles:
	    boardTiles[(til.coordinate[0], til.coordinate[1])] = None
	    if isinstance(players[active],ai.AI):
		squares[(til.coordinate[0], til.coordinate[1])] = 0
	
	return False  
#Check database for played word and return true if the word is valid
def checkWord():
    global originalWord, wordPoint,isInBonusSquare,wordAndMeaning
    originalWord= True	# Holds if the "currently played word" is checked, the currently generated word by AI is already taken from Dictionary so for this word dictionary check will not be done
    isInBonusSquare = False
    xArr = []
    yArr = []
    for til in playedTiles:
	xArr.append(til.coordinate[0])
	yArr.append(til.coordinate[1])
	boardTiles[(til.coordinate[0],til.coordinate[1])] = til
	squares[(til.coordinate[0],til.coordinate[1])] = 1

    # find the min and max value for x and y coordinate
    
    minX = min(xArr)
    maxX = max(xArr)	
    minY = min(yArr)
    maxY = max(yArr)    

    if(minY == maxY): #word is horizontally placed
	if calculateWordPoint(minX,maxX,minY,maxY,"horizontal") == False:  #check the word as horizontally
	    return False
	originalWord = False
	
	for til in playedTiles:#now check for each new placed letter for connected vertical words
	    if calculateWordPoint(til.coordinate[0],til.coordinate[0],til.coordinate[1],til.coordinate[1],"vertical") == False:
	        return False
	
    elif(minX == maxX): #word is vertically placed
        if calculateWordPoint(minX,maxX,minY,maxY,"vertical") == False:#check the word as vertically
	    return False
	originalWord = False
	
	for til in playedTiles:#now check for each new placed letter for connected vertical words
	    if calculateWordPoint(til.coordinate[0],til.coordinate[0],til.coordinate[1],til.coordinate[1],"horizontal") == False:
		return False	
	
    if isInBonusSquare:
	wordPoint=wordPoint+25 	
	wordAndMeaning = wordAndMeaning+ u"\n+25 Bonus puan\n"
	
    return True

def calculateWordPoint(minX,maxX,minY,maxY,controlType):
    currentWord = ""
    global wordPoint, isInBonusSquare, originalWord,bonus_coordX,bonus_coordY
    # ############### HORIZONTALLY WORD CONTROL #################################
    if controlType == "horizontal":
	currentFirstLetterX = minX
	#slide through to the left to find the first letter in row
	while currentFirstLetterX-36>=5 and boardTiles[(currentFirstLetterX-36,minY)]!=None:
	    currentFirstLetterX = currentFirstLetterX-36
		    
	currentLastLetterX = maxX
	#slide through to the right to find the last letter in row
	while currentLastLetterX+36<=509 and boardTiles[(currentLastLetterX+36,minY)]!=None:
	    currentLastLetterX = currentLastLetterX+36	
	
	if currentFirstLetterX == currentLastLetterX:
	    return True	

        numberOfdoubleword = 0
	numberOftripleword = 0
	#get the word that created horizontally  
	while currentFirstLetterX <= currentLastLetterX:
	    try:
		currentWord+=boardTiles[(currentFirstLetterX,minY)].letter
		if boardTiles[(currentFirstLetterX,minY)] in playedTiles:
		    (none,bonus) = gameboard.squares[(minY-5)/36][(currentFirstLetterX-5)/36]
		    if bonus == "normal":
			wordPoint=wordPoint+boardTiles[(currentFirstLetterX,minY)].points
		    elif bonus == "doubleletter":
			wordPoint=wordPoint+boardTiles[(currentFirstLetterX,minY)].points*2
		    elif bonus == "tripleletter":
			wordPoint=wordPoint+boardTiles[(currentFirstLetterX,minY)].points*3
		    elif bonus == "doubleword":
			numberOfdoubleword =  numberOfdoubleword + 1
			wordPoint=wordPoint+boardTiles[(currentFirstLetterX,minY)].points
		    elif bonus == "tripleword":
			numberOftripleword =  numberOftripleword + 1
			wordPoint=wordPoint+boardTiles[(currentFirstLetterX,minY)].points
		    if (currentFirstLetterX,minY) == (bonus_coordX, bonus_coordY):
			isInBonusSquare = True
		else:
		    wordPoint=wordPoint+boardTiles[(currentFirstLetterX,minY)].points
		currentFirstLetterX = currentFirstLetterX + 36
	    except Exception as ex:
		for til in playedTiles:
		    print til.letter
	    
	if numberOfdoubleword != 0:
	    wordPoint=wordPoint*(2**numberOfdoubleword)
	
	if numberOftripleword != 0:
	    wordPoint=wordPoint*(3**numberOftripleword) 
	

	# check the database   
	#if not (isinstance(players[active], ai.AI) and originalWord == True):	# The currently placed word that AI play is already taken from the dictionary
	if isInTurkishDictionary(currentWord) is False:
	    return False  
    # ############### VERTICALLY WORD CONTROL #################################
    elif controlType == "vertical":
	currentFirstLetterY = minY
	#slide through to the upper to find the first letter in column
	while currentFirstLetterY-36>=5 and boardTiles[(minX,currentFirstLetterY-36)]!=None:
	    currentFirstLetterY = currentFirstLetterY-36
		
	currentLastLetterY = maxY
	#slide through to the bottom to find the last letter in column
	while currentLastLetterY+36<=509 and boardTiles[(minX,currentLastLetterY+36)]!=None:
	    currentLastLetterY = currentLastLetterY+36	
	
	if currentFirstLetterY == currentLastLetterY:
	    return True
	
	numberOfdoubleword = 0
	numberOftripleword = 0	
	#get the word that created vertically
	while currentFirstLetterY <= currentLastLetterY:
	    try:
		currentWord+=boardTiles[(minX,currentFirstLetterY)].letter
		if boardTiles[(minX,currentFirstLetterY)] in playedTiles:
		    (none,bonus) = gameboard.squares[(currentFirstLetterY-5)/36][(minX-5)/36]
		    if bonus == "normal":
			wordPoint=wordPoint+boardTiles[(minX,currentFirstLetterY)].points
		    elif bonus == "doubleletter":
			wordPoint=wordPoint+boardTiles[(minX,currentFirstLetterY)].points*2
		    elif bonus == "tripleletter":
			wordPoint=wordPoint+boardTiles[(minX,currentFirstLetterY)].points*3
		    elif bonus == "doubleword":
			numberOfdoubleword =  numberOfdoubleword + 1
			wordPoint=wordPoint+boardTiles[(minX,currentFirstLetterY)].points
		    elif bonus == "tripleword":
			numberOftripleword =  numberOftripleword + 1
			wordPoint=wordPoint+boardTiles[(minX,currentFirstLetterY)].points
		    if (minX,currentFirstLetterY) == (bonus_coordX, bonus_coordY):
			isInBonusSquare = True		
		else:
		    wordPoint=wordPoint+boardTiles[(minX,currentFirstLetterY)].points	    
		currentFirstLetterY = currentFirstLetterY + 36
	    except Exception as ex:
		for til in playedTiles:
		    print til.letter
	    
	if numberOfdoubleword != 0:
	    wordPoint=wordPoint*(2**numberOfdoubleword)
	
	if numberOftripleword != 0:
	    wordPoint=wordPoint*(3**numberOftripleword)	    
	
	# check the database	
	if isInTurkishDictionary(currentWord) is False:
	    return False  
    return True

def controlOfValidMove():
    global isFirstMove,isAccepted,isInPlayArea 
    # take the list of x and y coordinates of the played tiles
    xArr = []
    yArr = []
    cArr = []
    for til in playedTiles:
	xArr.append(til.coordinate[0])
	yArr.append(til.coordinate[1])
	cArr.append((til.coordinate[0],til.coordinate[1]))
    
    # find the min and max value for x and y coordinate
    minX = min(xArr)
    maxX = max(xArr)	
    minY = min(yArr)
    maxY = max(yArr)

    isAccepted = True # accepted move or not?->same row or same column control
    isInPlayArea = True #played tiles are in play area or not
    
    # if in the same row all, there will be no gap between the first and last tile
    if minY == maxY: # if all played tiles in the same row
	for xCoor in range(minX,maxX,36):
	    if squares[(xCoor,playedTiles[0].coordinate[1])] == 0:  # playedTiles[0].coordinate[1] = because same row,y coordinate is same for all
		isAccepted = False
		break
    elif minX == maxX:# if all played tiles in the same column
	# if in the same column all, there will be no gap between the first and last tile
	for yCoor in range(minY,maxY,36):
	    if squares[(playedTiles[0].coordinate[0],yCoor)] == 0:
		isAccepted = False
		break
    #played tiles must be same row or same column otherwise not will be accepted
    else:
	isAccepted = False
    
    # CONTROL for the played tiles are in PLAY AREA or not!!
    if isAccepted:
	for i in range(0, len(playedTiles)):
					
	    right = (playedTiles[i].coordinate[0]+36,playedTiles[i].coordinate[1])
	    left = (playedTiles[i].coordinate[0]-36,playedTiles[i].coordinate[1])
	    up = (playedTiles[i].coordinate[0],playedTiles[i].coordinate[1]-36)
	    down = (playedTiles[i].coordinate[0],playedTiles[i].coordinate[1]+36)	
	    
	    #the played tiles must be in played tiles that means the right or left or up or down of the played tiles must be filled ,1.
	    if (right not in cArr and right in squares.keys() and squares[right] == 1) or (left not in cArr  and left in squares.keys() and squares[left] == 1) or (down not in cArr and down in squares.keys() and squares[down] == 1) or (up not in cArr and up in squares.keys() and squares[up] == 1):
		isInPlayArea = True
		break
	    else:
		isInPlayArea = False	

def mouseDragAndDropOperations():
    global Target
    # #  fit the tile in the positions
    
    # if the tile put on board
    if (Target.coordinate[0] < board.Board.GRID_SIZE * (board.Board.SQUARE_SIZE + board.Board.SQUARE_BORDER) - board.Board.SQUARE_SIZE/2 + 1 and Target.coordinate[1] < board.Board.GRID_SIZE * (board.Board.SQUARE_SIZE + board.Board.SQUARE_BORDER) - board.Board.SQUARE_SIZE/2 + 1 and Target.coordinate[0] > board.Board.SQUARE_BORDER + 1 - board.Board.SQUARE_SIZE/2 and Target.coordinate[1] > board.Board.SQUARE_BORDER + 1 - board.Board.SQUARE_SIZE/2) :
	i = 5
	a = Target.coordinate[:]
	while i <= Target.coordinate[0] + 16 :
	    i = i + 36
	    
	Target.coordinate = (i - 36, Target.coordinate[1])
	
	
	i = 5
	while i <= Target.coordinate[1] + 16 :
	    i = i + 36
	
	Target.coordinate = (Target.coordinate[0], i - 36)	
	# ###############will remove from tray when played######
	if(Target not in playedTiles):
	    playedTiles.append(Target)
	    players[active].justTray.remove(Target)  # will remove from the tiles that are just on tray
	# ######################################################		    
	
    # if the tile put on tray
    elif (Target.coordinate[0] + 16 > human.Human.TRAY_LEFT and Target.coordinate[1] + 16 > human.Human.TRAY_TOP and Target.coordinate[0] + 16 < human.Human.TRAY_LEFT + (tile.Tile.SQUARE_SIZE + tile.Tile.SQUARE_BORDER)*8 and Target.coordinate[1] + 16 < human.Human.TRAY_TOP + tile.Tile.SQUARE_SIZE + tile.Tile.SQUARE_BORDER*2):
	i = human.Human.TRAY_FIRSTLEFT
	a = Target.coordinate[:]
	while i <= Target.coordinate[0] + 16 :
	    i = i + 36		    
	    
	Target.coordinate = (i - 36, human.Human.TRAY_FIRSTTOP)
	# ###############will add back to tray when played######
	if(Target in playedTiles):
	    playedTiles.remove(Target)
	    players[active].justTray.append(Target) # will remove from the tiles that are just on tray
	# ######################################################		    
	
    else:
	Target.coordinate = Target.oldPos # if tile put out of board bring it back
    # fit the tile in the positions - end
    
    
    # slide the tile if it is dropped on another tile
    try:
	slidingTo = 4
	if squares[Target.coordinate] == 1:
	    if Target.coordinate[0] <= a[0] and Target.coordinate[1] <= a[1]:
		if a[0]-Target.coordinate[0]>=a[1]-Target.coordinate[1]:
		    Target.coordinate = (Target.coordinate[0] + 36, Target.coordinate[1])
		    slidingTo = 1
		else:
		    Target.coordinate = (Target.coordinate[0], Target.coordinate[1] + 36)
		    slidingTo = 3
		    
	    elif Target.coordinate[0] > a[0] and Target.coordinate[1] <= a[1]:
		if Target.coordinate[0] - a[0] >= a[1] - Target.coordinate[1]:
		    Target.coordinate = (Target.coordinate[0] - 36, Target.coordinate[1])
		    slidingTo = 0
		else:
		    Target.coordinate = (Target.coordinate[0], Target.coordinate[1] + 36)
		    slidingTo = 3
		    
	    elif Target.coordinate[0] > a[0] and Target.coordinate[1] > a[1]:
		if Target.coordinate[0] - a[0] >= Target.coordinate[1] - a[1]:
		    Target.coordinate = (Target.coordinate[0] - 36, Target.coordinate[1])
		    slidingTo = 0
		else:
		    Target.coordinate = (Target.coordinate[0], Target.coordinate[1] - 36)
		    slidingTo = 2
		    
	    elif Target.coordinate[0] <= a[0] and Target.coordinate[1] > a[1]:
		if a[0]-Target.coordinate[0] >= Target.coordinate[1] - a[1]:
		    Target.coordinate = (Target.coordinate[0] + 36, Target.coordinate[1])
		    slidingTo = 1
		else:
		    Target.coordinate = (Target.coordinate[0], Target.coordinate[1] - 36)
		    slidingTo = 2
		    
	    while squares[Target.coordinate] == 1: # #slide the tile until there is an empty square
		if slidingTo == 0:
		    Target.coordinate = (Target.coordinate[0] + 36, Target.coordinate[1])
		elif slidingTo == 1:
		    Target.coordinate = (Target.coordinate[0] - 36, Target.coordinate[1])
		elif slidingTo == 2:
		    Target.coordinate = (Target.coordinate[0], Target.coordinate[1] + 36)
		elif slidingTo == 3:
		    Target.coordinate = (Target.coordinate[0], Target.coordinate[1] - 36)
			
    except KeyError:
	Target.coordinate = Target.oldPos # if tile slid out of board bring it back	
	    
# slide the tile if it is dropped on another tile
		
    squares[Target.coordinate] = 1

    Target = None # Drop item, if we have any
    
#initially create main menu
if __name__ == '__main__': # if the SCREEN module is firstly run then call the main of menu.
    menu.main()