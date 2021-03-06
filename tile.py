# -*- coding: cp1254 -*-
import pygame,scrabble
#FONT = 'data/font/FreeSansBold.ttf'
FONT = None
class Tile:
    
    SQUARE_SIZE = 32
    SQUARE_BORDER = 4   
    TILE_OUTLINE = (55, 46, 40)
    TILE_HIGHLIGHT = (100, 100, 255) 
    TILE_BLANK = (110, 92, 80)
    TILE_COLOR = (255, 255, 51)

    def __init__(self, letter, points,coordinate):
	    self.letter = letter
	    self.points = points
	    self.coordinate=coordinate
	    #
	    self.oldPos=coordinate
	    #
	    
    def draw(self, highlight = False):
	    SCREEN = scrabble.getScreen()
	    LETTER_FONT = pygame.font.Font('freesansbold.ttf', 24)
	    POINTS_FONT = pygame.font.Font('freesansbold.ttf', 7)   	
	    #LETTER_FONT = pygame.font.Font(FONT, 24)
	    #POINTS_FONT = pygame.font.Font(FONT, 7) 	
	    
	    if highlight:
		    pygame.draw.rect(SCREEN, Tile.TILE_HIGHLIGHT, (self.coordinate[0], self.coordinate[1], Tile.SQUARE_SIZE, Tile.SQUARE_SIZE))
	    else:
		    pygame.draw.rect(SCREEN, Tile.TILE_OUTLINE, (self.coordinate[0]+1, self.coordinate[1]+1, Tile.SQUARE_SIZE-2, Tile.SQUARE_SIZE-2))
  
	    backColor = self.TILE_COLOR
	    pygame.draw.rect(SCREEN, backColor, (self.coordinate[0]+2, self.coordinate[1]+2, Tile.SQUARE_SIZE-4, Tile.SQUARE_SIZE-4))
	    
	    #Display the letter of the tile
            if self.letter == u'�':
		letterText = LETTER_FONT.render("I", True, Tile.TILE_OUTLINE, backColor)
	    else:
		letterText = LETTER_FONT.render(self.letter, True, Tile.TILE_OUTLINE, backColor)
	    letterRect = letterText.get_rect()
	    letterRect.center = (self.coordinate[0] + Tile.SQUARE_SIZE/2 - 3, self.coordinate[1] + Tile.SQUARE_SIZE/2)
	    SCREEN.blit(letterText, letterRect)
    
	    #Display the points of the tile
	    pointsText = POINTS_FONT.render(str(self.points), True, Tile.TILE_OUTLINE, backColor)
	    pointsRect = pointsText.get_rect()
	    pointsRect.center = (self.coordinate[0] + Tile.SQUARE_SIZE/2 + Tile.SQUARE_SIZE/3, self.coordinate[1] + Tile.SQUARE_SIZE/2 + Tile.SQUARE_SIZE/3)
	    SCREEN.blit(pointsText, pointsRect)
	    
# #####################################   	    
    def setCoordinate(self,coordinate):
            self.coordinate = coordinate
	    self.oldPos=coordinate
# #####################################