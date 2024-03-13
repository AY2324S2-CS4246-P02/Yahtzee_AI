import pygame
import Agent.Yahtzee
from Agent.Yahtzee import Yahtzee
import random

def draw_text(screen, text, rect : pygame.Rect, size = 12, color = (255,255,255)):
    f = pygame.font.Font(size = size)
    text = f.render(text, True, color)
    
    width, height = text.get_size()

    x, y = rect.centerx - width // 2, rect.centery - height // 2

    screen.blit(text, (x,y))

class Table_Rect(pygame.Rect):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.table_rects = []
        self.value_rects = []
        self.table_tl_x = self.centerx - 200
        self.table_tl_y = self.centery - 300
        self.table_col1_width = 250
        self.table_col2_width = 150
        self.n_cells = 15
        self.table_cell_height = 600 // self.n_cells
        for i in range(self.n_cells):
            r1 = pygame.Rect(self.table_tl_x, self.table_tl_y + i * self.table_cell_height, self.table_col1_width, self.table_cell_height)
            r2 = pygame.Rect(self.table_tl_x + self.table_col1_width, self.table_tl_y + i * self.table_cell_height, self.table_col2_width, self.table_cell_height)
            self.table_rects.append(r1)
            self.value_rects.append(r2)

    def draw(self, screen):
        names = Agent.Yahtzee.CATEGORIES_NAMES + ["Total"]
        for i in range(self.n_cells):
            pygame.draw.rect(screen, (255,0,0), self.table_rects[i], width = 2)
            pygame.draw.rect(screen, (255,0,0), self.value_rects[i], width = 2)

            draw_text(screen, names[i], self.table_rects[i], size = 36)

    def draw_scoresheet(self, screen, sheet):
        for rect, val in zip(self.value_rects, sheet):
            draw_text(screen, str(val), rect, 36, 'white')
        


    def get_clicked_row(self, location):
        '''
        Returns the (0 based) index of the row being clicked (the category ID), or None if nothing is clicked
        '''
        for idx, (r1, r2) in enumerate(zip(self.table_rects, self.value_rects)):
            if r1.collidepoint(location) or r2.collidepoint(location):
                return idx
            
        return None


class Dice_Rect(pygame.Rect):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
        self.dice_height = 100
        self.dice_width = 100
        self.spacing_x = (self.width - (5 * self.dice_width)) // 10
        self.spacing_y = (self.height - self.dice_height) // 2
        self.d0 = pygame.Rect(0 * self.dice_width + 1 * self.spacing_x, self.top + self.spacing_y, self.dice_width, self.dice_height)
        self.d1 = pygame.Rect(1 * self.dice_width + 3 * self.spacing_x, self.top + self.spacing_y, self.dice_width, self.dice_height)
        self.d2 = pygame.Rect(2 * self.dice_width + 5 * self.spacing_x, self.top + self.spacing_y, self.dice_width, self.dice_height)
        self.d3 = pygame.Rect(3 * self.dice_width + 7 * self.spacing_x, self.top + self.spacing_y, self.dice_width, self.dice_height)
        self.d4 = pygame.Rect(4 * self.dice_width + 9 * self.spacing_x, self.top + self.spacing_y, self.dice_width, self.dice_height)

        self.dices : list[pygame.Rect] = [self.d0, self.d1, self.d2, self.d3, self.d4]

    def draw(self, screen, selected_dice = None):
        '''
        selected_dice takes in a list of (0 based) indices of dices to be rerolled
        '''
        if selected_dice == None:
            selected_dice = []
        pygame.draw.rect(screen, 'white', self)
        for val, i in enumerate(self.dices):
            if val not in selected_dice:
                pygame.draw.rect(screen, (128,128,128), i) ## Dices that are not to be rerolled are grey
                pygame.draw.rect(screen, 'black', i, width = 4)
            else:
                pygame.draw.rect(screen, 'white', i) ## Dices to be rerolled are white
                pygame.draw.rect(screen, 'black', i, width = 4)

    def draw_dice_values(self, screen, values):
        for dice, val in zip(self.dices, values):
            draw_text(screen, str(val), dice, 60, 'black')

    def get_clicked_dice(self, location):
        '''
        Returns the (0 based) index of the dice being clicked, or None if nothing is clicked
        '''
        for idx, d in enumerate(self.dices):
            if d.collidepoint(location):
                return idx 
            
        return None


def reset_screen(screen, table, dice, **kwargs):
    selected_dice = kwargs.get("selected_dice", None)

    screen.fill('black')
    table.draw(screen)
    dice.draw(screen, selected_dice)

def main():
    pygame.init() 
    
    yahtzee : Yahtzee = Yahtzee()

    # CREATING CANVAS 
    screen = pygame.display.set_mode((640, 800))

    table_rect = Table_Rect(0,0,640,640)
    dice_rect = Dice_Rect(0,640,640,160)
    
    # TITLE OF CANVAAS
    pygame.display.set_caption("Yahtzee") 
    exit = False
    
    clock = pygame.time.Clock()

    selected_dice = []
    while not exit: 
        clock.tick(60)
        reset_screen(screen, table_rect, dice_rect, selected_dice = selected_dice)

        for event in pygame.event.get(): 
            if event.type == pygame.QUIT: 
                exit = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                location = event.pos

                if (a := dice_rect.get_clicked_dice(location)) is not None:
                    if a not in selected_dice:
                        selected_dice.append(a)
                    else:
                        selected_dice.remove(a)
                elif (a := table_rect.get_clicked_row(location)) is not None:
                    print(Agent.Yahtzee.CATEGORIES_NAMES[a])
                    yahtzee.doAction(('KEEP', a))

            elif event.type == pygame.KEYDOWN:
                try:
                    yahtzee.roll_dice(selected_dice)
                    selected_dice = []
                except Exception as e:
                    if e.args[0] == 'You have no rerolls left.':
                        print("No rerolls available")
                        ## To continue adding stuff if necessary


        dice_rect.draw_dice_values(screen, yahtzee.get_dice())
        table_rect.draw_scoresheet(screen, yahtzee.get_display_scoresheet())
        
        
        pygame.display.update() 


if __name__ == '__main__':
    main()

