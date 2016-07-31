import pdb
import random
from copy import deepcopy

class CheckersEngine(object):
    # red on bottom, black on top
   
    def __init__(self):
        firstrow = ['RC','--','RC','--','RC','--','RC','--'] # RC is a red checker
        wpawnrow = ['--','RC','--','RC','--','RC','--','RC'] # RK is a red king
        blnkrow2 = ['RC','--','RC','--','RC','--','RC','--']
        blnkrow3 = ['--','00','--','00','--','00','--','00']
        blnkrow4 = ['00','--','00','--','00','--','00','--']
        blnkrow5 = ['--','BC','--','BC','--','BC','--','BC']
        bpawnrow = ['BC','--','BC','--','BC','--','BC','--'] # BK is a black king
        #lastrow  = ['--','00','--','00','--','00','--','00']        
        lastrow  = ['--','BC','--','BC','--','BC','--','BC'] # BC is a black checker
        self.board = [firstrow, wpawnrow, blnkrow2, blnkrow3,
                     blnkrow4, blnkrow5, bpawnrow, lastrow]
        self.topcarx    = 0   # the top car starts on the left border
        self.topcary    = 4
        self.topcarwidth = 2
        self.bottomcarx = 6   # the bottom car stars on the right border
        self.bottomcary = 3
        self.bottomcarwidth = 2
        
        self.kingjumpoffsetlist          = [[-2,-2],[-2,2],[2,-2],[2,2]]
        self.kingcaptureoffsetlist       = [[-1,-1],[-1,1],[1,-1],[1,1]]
        self.redjumpoffsetlist           = [[-2,2], [2,2]]
        self.redcaptureoffsetlist        = [[-1,1], [1,1]]
        self.blackjumpoffsetlist         = [[-2,-2],[2,-2]]
        self.blackcaptureoffsetlist      = [[-1,-1],[1,-1]]

    def printboard(self,board):
        for x in range(0,8):
            print board[7-x] 
            
    def getpiece(self, x, y):
        return self.board[y][x]        
            
    def fastcopy(self, b):
        return     [[b[0][0],b[0][1],b[0][2],b[0][3],b[0][4],b[0][5],b[0][6],b[0][7]],
                    [b[1][0],b[1][1],b[1][2],b[1][3],b[1][4],b[1][5],b[1][6],b[1][7]],
                    [b[2][0],b[2][1],b[2][2],b[2][3],b[2][4],b[2][5],b[2][6],b[2][7]],
                    [b[3][0],b[3][1],b[3][2],b[3][3],b[3][4],b[3][5],b[3][6],b[3][7]],
                    [b[4][0],b[4][1],b[4][2],b[4][3],b[4][4],b[4][5],b[4][6],b[4][7]],
                    [b[5][0],b[5][1],b[5][2],b[5][3],b[5][4],b[5][5],b[5][6],b[5][7]],
                    [b[6][0],b[6][1],b[6][2],b[6][3],b[6][4],b[6][5],b[6][6],b[6][7]],
                    [b[7][0],b[7][1],b[7][2],b[7][3],b[7][4],b[7][5],b[7][6],b[7][7]]]
                           
    def updateboardinplace(self,movelist, board):  
        # the first entry in the movelist is the starting position 
        currentpos = movelist[0]      
        currentx = currentpos[0]
        currenty = currentpos[1]
        # for each move in the rest of movelist
        for move in movelist[1:]: 
            piece = board[currenty][currentx]  
            # check for capture
            if abs(move[0]-currentx) == 2:
                capturex = (move[0]+currentx)/2
                capturey = (move[1]+currenty)/2     
                board[capturey][capturex] = '00' 
            # make the move
            board[currenty][currentx] = '00'
            board[move[1]][move[0]] = piece
            currentx = move[0]
            currenty = move[1]
        
        # after the last move, see if we need to promote the checker to a king
        if currenty == 7 and piece[0] == 'R':
            piece = 'RK'
        if currenty == 0 and piece[0] == 'B':
            pice = 'BK'
        board[currenty][currentx] = piece        
        
    def createjumplist(self,color,board):
        """ Function to create all the legal jumps
            If there are any legal jumps, then 
            the only legal move is one of these jumps. 
        """
        outputjumplist = []
        # loop through all the checkers of the given color
        for y in range(0,8):
            for x in range(0,8):
                currentpiece = board[y][x]
                if currentpiece[0] == color:
                    print x,y
                    # find the possible jumps from this piece
                    jumplist = self.addtojumplist([[x,y]],color,board)
                    if len(jumplist) != 1:
                        outputjumplist += jumplist
         
        return outputjumplist     
        
    def addtojumplist(self,jumplist,color,board):
        """ Recursive routine to take the current jump list
            and follow it through to multiple jumps 
            This can only be used on a single checker.
        """
        
        resultjumplist = []  # this is the list we are going to return
        
        # get the current jump position
        currentpos = jumplist[-1]
        #pdb.set_trace()
        currentpiece = board[currentpos[1]][currentpos[0]]
        
        loopsize = 2
        if currentpiece[0] == 'R':
            #pdb.set_trace()
            jumpoffsetlist    = self.redjumpoffsetlist
            captureoffsetlist = self.redcaptureoffsetlist
        else:
            jumpoffsetlist    = self.blackjumpoffsetlist
            captureoffsetlist = self.blackcaptureoffsetlist
        
        if currentpiece[1] == 'K':
            loopsize = 4
            jumpoffsetlist    = self.kingjumpoffsetlist
            captureoffsetlist = self.kingcaptureoffsetlist
        
        # loop through all the possible jumps from the current position
        for i in range(0,loopsize):
            # check if the jump destination is open
            #print i
            #print jumpoffsetlist
            jumpoffset = jumpoffsetlist[i]
            jumpx = currentpos[0]+jumpoffset[0]
            jumpy = currentpos[1]+jumpoffset[1]
            if jumpx < 0 or jumpx > 7: continue
            if jumpy < 0 or jumpx > 7: continue     
            if board[jumpy][jumpx] != '00': continue   
            # check if there is an opposing checker to capture
            captureoffset = captureoffsetlist[i]
            capturex = currentpos[0]+captureoffset[0]
            capturey = currentpos[1]+captureoffset[1]
            capturepiece = board[capturey][capturex] 
            if capturepiece == '00': continue
            if capturepiece[0] == color: continue
        
            # we have found a legal jump
    
            # create a board to account for the jump
            newboard = self.fastcopy(board)
            # create the current move
            movelist = [currentpos]
            movelist.append([jumpx,jumpy])
            # update the board to account for the jump
            self.updateboardinplace(movelist, newboard)
            # create a copy of the jump list
            newjumplist = deepcopy(jumplist)
            # append the new jump to the list
            newjumplist.append([jumpx,jumpy])
            # check if the piece was promoted to king
            currentpiece = newboard[jumpy][jumpx]
            if currentpiece[1] == 'K':
                resultjumplist.append(newjumplist)
            else:
                # if not, recursively call addtojumplist
                outputjumplist = self.addtojumplist(newjumplist,color,newboard)
                # append each list in the output to the resultjumplist
                resultjumplist += outputjumplist
        # return the resultjumplist
        if resultjumplist == []:
            resultjumplist.append(jumplist)
        return resultjumplist          
                         
                         
if __name__ == '__main__':
    import time
    import cProfile
    cb = CheckersEngine()  
    cb.printboard(cb.board)
    jumplist = [[1,1]]
    newjumplist = cb.addtojumplist(jumplist,'R',cb.board)
    print newjumplist
    print "move"
    cb.updateboardinplace([[2,2],[3,3]],cb.board)
    cb.printboard(cb.board)
    print "move"
    cb.updateboardinplace([[1,5],[2,4]],cb.board)
    cb.printboard(cb.board)
    print "move"
    cb.updateboardinplace([[5,5],[4,4]],cb.board)
    cb.printboard(cb.board)
    #jumplist = [[3,3]]
    #newjumplist = cb.addtojumplist(jumplist,'R',cb.board)
    #print newjumplist
    totaljumplist = cb.createjumplist('R',cb.board)
    print totaljumplist
    #pdb.set_trace()