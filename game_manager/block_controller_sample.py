#!/usr/bin/python3
# -*- coding: utf-8 -*-

from datetime import datetime
import pprint
import copy

class Block_Controller(object):

    # init parameter
    board_backboard = 0
    board_data_width = 0
    board_data_height = 0
    ShapeNone_index = 0
    CurrentShape_class = 0
    NextShape_class = 0
    
    CurrentShape_index = 0

    # GetNextMove is main function.
    # input
    #    nextMove : nextMove structure which is empty.
    #    GameStatus : block/field/judge/debug information. 
    #                 in detail see the internal GameStatus data.
    # output
    #    nextMove : nextMove structure which includes next shape position and the other.
    def GetNextMove(self, nextMove, GameStatus):

        t1 = datetime.now()

        # print GameStatus
        print("==== 2/20 GameStatus block_info currentShape index ====")
        print(GameStatus["block_info"]["currentShape"]["index"])
        print("=================================================>")
        pprint.pprint(GameStatus, width = 61, compact = True)

        # get data from GameStatus
        # current shape info
        CurrentShapeDirectionRange = GameStatus["block_info"]["currentShape"]["direction_range"]
        
        CurrentShape_index = GameStatus["block_info"]["currentShape"]["index"] # NISHIDA       
        # print("CurrentShape_index = ")
        # print(CurrentShape_index) 
        
        nextShape_index = GameStatus["block_info"]["nextShape"]["index"]
        #print("nextShape_index = ")
        #print(nextShape_index) 

        
        self.CurrentShape_class = GameStatus["block_info"]["currentShape"]["class"]
        # next shape info
        NextShapeDirectionRange = GameStatus["block_info"]["nextShape"]["direction_range"]
        self.NextShape_class = GameStatus["block_info"]["nextShape"]["class"]
        # current board info
        self.board_backboard = GameStatus["field_info"]["backboard"]
        # default board definition
        self.board_data_width = GameStatus["field_info"]["width"]
        self.board_data_height = GameStatus["field_info"]["height"]
        self.ShapeNone_index = GameStatus["debug_info"]["shape_info"]["shapeNone"]["index"]

        # search best nextMove -->
        strategy = None
        LatestEvalValue = -100000
        # search with current block Shape
        for direction0 in CurrentShapeDirectionRange:
            # search with x range
            x0Min, x0Max = self.getSearchXRange(self.CurrentShape_class, direction0)
            for x0 in range(x0Min, x0Max):
                # get board data, as if dropdown block
                board, xxdy = self.getBoard(self.board_backboard, self.CurrentShape_class, direction0, x0)
                xxdy = self.board_data_height -1 - xxdy
                
                # evaluate board
                EvalValue = self.calcEvaluationValueSample(board, CurrentShape_index, xxdy, self.board_backboard, direction0, x0)
                # update best move
                if EvalValue > LatestEvalValue:
                    strategy = (direction0, x0, 1, 1)
                    LatestEvalValue = EvalValue
                #elif (EvalValue == LatestEvalValue) and (x0 % 2 != 0) and (direction0 % 2 != 0): # only case of odd number
                #    strategy = (direction0, x0, 1, 1)
                #    LatestEvalValue = EvalValue
                print('direction0=' + str(direction0) + '　x0=' + str(x0) + '---------------------------')
                #xxcoordArray = self.Currentshape_class.getCoords(direction0, x0, self.board_data_height - xxdy) # get array from shape direction, x, y.
                #xxcoordArray = Shape_class.getCoords(direction0, x0, self.board_data_height - xxdy) # get array from shape direction, x, 
                #print('xxcoordArray=' + str(xxcoordArray))    
                
                ###test
                ###for direction1 in NextShapeDirectionRange:
                ###  x1Min, x1Max = self.getSearchXRange(self.NextShape_class, direction1)
                ###  for x1 in range(x1Min, x1Max):
                ###        board2 = self.getBoard(board, self.NextShape_class, direction1, x1)
                ###        EvalValue = self.calcEvaluationValueSample(board2)
                ###        if EvalValue > LatestEvalValue:
                ###            strategy = (direction0, x0, 1, 1)
                ###            LatestEvalValue = EvalValue
        # search best nextMove <--

        print("===", datetime.now() - t1)
        nextMove["strategy"]["direction"] = strategy[0]
        nextMove["strategy"]["x"] = strategy[1]
        nextMove["strategy"]["y_operation"] = strategy[2]
        nextMove["strategy"]["y_moveblocknum"] = strategy[3]
        
      #  if CurrentShape_index == 1:
      #      nextMove["strategy"]["direction"] = 0
      #      nextMove["strategy"]["x"] = -5
      #      nextMove["strategy"]["y_operation"] = 1
      #      nextMove["strategy"]["y_moveblocknum"] = 1        
        
        print(nextMove)
        print("###### SAMPLE CODE SATOMI.NISHIDA ######")
        return nextMove

    def getSearchXRange(self, Shape_class, direction):
        #
        # get x range from shape direction.
        #
        minX, maxX, _, _ = Shape_class.getBoundingOffsets(direction) # get shape x offsets[minX,maxX] as relative value.
        xMin = -1 * minX
        xMax = self.board_data_width - maxX
        return xMin, xMax

    def getShapeCoordArray(self, Shape_class, direction, x, y):
        #
        # get coordinate array by given shape.
        #
        coordArray = Shape_class.getCoords(direction, x, y) # get array from shape direction, x, y.
        return coordArray

    def getBoard(self, board_backboard, Shape_class, direction, x):
        # 
        # get new board.
        #
        # copy backboard data to make new board.
        # if not, original backboard data will be updated later.
        board = copy.deepcopy(board_backboard)
        _board, xxdy = self.dropDown(board, Shape_class, direction, x)
        return _board, xxdy

    def dropDown(self, board, Shape_class, direction, x):
        # 
        # internal function of getBoard.
        # -- drop down the shape on the board.
        # 
        dy = self.board_data_height - 1
        coordArray = self.getShapeCoordArray(Shape_class, direction, x, 0)
        # update dy
        for _x, _y in coordArray:
            _yy = 0
            while _yy + _y < self.board_data_height and (_yy + _y < 0 or board[(_y + _yy) * self.board_data_width + _x] == self.ShapeNone_index):
                _yy += 1
            _yy -= 1
            if _yy < dy:
                dy = _yy
        # get new board
        _board, xxdy = self.dropDownWithDy(board, Shape_class, direction, x, dy)    
        return _board, xxdy

    def dropDownWithDy(self, board, Shape_class, direction, x, dy):
        #
        # internal function of dropDown.
        #
        _board = board
        coordArray = self.getShapeCoordArray(Shape_class, direction, x, 0)
        #print('coordArray=' + str(coordArray))
        for _x, _y in coordArray:
            _board[(_y + dy) * self.board_data_width + _x] = Shape_class.shape
        xxdy = _y + dy
        return _board, xxdy
    
    def calcEvaluationValueSample(self, board, CurrentShape_index, xxdy, xxbackboard, direction0, x0):
        #
        # sample function of evaluate board.
        #
        #if CurrentShape_index == 1:
        width = self.board_data_width
        #else:
        #    width = self.board_data_width - 1
        height = self.board_data_height

        # evaluation paramters
        ## lines to be removed
        fullLines = 0
        ## number of holes or blocks in the line.
        nHoles, nIsolatedBlocks = 0, 0
        ## absolute differencial value of MaxY
        
        absDy = 0
        ## how blocks are accumlated
        BlockMaxY = [0] * width
        holeCandidates = [0] * width
        holeConfirm = [0] * width

        ### check board
        # each y line
        for y in range(height - 1, 0, -1):
            hasHole = False
            hasBlock = False
            # each x line
            for x in range(width):
                ## check if hole or block..
                if board[y * self.board_data_width + x] == self.ShapeNone_index:
                    # hole
                    hasHole = True
                    holeCandidates[x] += 1  # just candidates in each column..
                else:
                    # block
                    hasBlock = True
                    BlockMaxY[x] = height - y                # update blockMaxY
                    if holeCandidates[x] > 0:
                        holeConfirm[x] += holeCandidates[x]  # update number of holes in target column..
                        holeCandidates[x] = 0                # reset
                    if holeConfirm[x] > 0:
                        nIsolatedBlocks += 1                 # update number of isolated blocks

            if hasBlock == True and hasHole == False:
                # filled with block
                fullLines += 1
            elif hasBlock == True and hasHole == True:
                # do nothing
                pass
            elif hasBlock == False:
                # no block line (and ofcourse no hole)
                pass

        # nHoles
        for x in holeConfirm:
            nHoles += abs(x)

        ### absolute differencial value of MaxY
        BlockMaxDy = []
        for i in range(len(BlockMaxY) - 1):
            val = BlockMaxY[i] - BlockMaxY[i+1]
            BlockMaxDy += [val]
        for x in BlockMaxDy:
            absDy += abs(x)

        #### maxDy
        #maxDy = max(BlockMaxY) - min(BlockMaxY)
        ### maxHeight
        maxHeight = max(BlockMaxY) - fullLines

        ## statistical data
        #### stdY
        #if len(BlockMaxY) <= 0:
        #    stdY = 0
        #else:
        #    stdY = math.sqrt(sum([y ** 2 for y in BlockMaxY]) / len(BlockMaxY) - (sum(BlockMaxY) / len(BlockMaxY)) ** 2)
        #### stdDY
        #if len(BlockMaxDy) <= 0:
        #    stdDY = 0
        #else:
        #    stdDY = math.sqrt(sum([y ** 2 for y in BlockMaxDy]) / len(BlockMaxDy) - (sum(BlockMaxDy) / len(BlockMaxDy)) ** 2)


       # calc Evaluation Value *******************************************
        score = 0
        emergency = 0
        #unsafe = 0
        for xx in range(2, self.board_data_width - 2, +1):
            if xxbackboard[7 * self.board_data_width + xx] != 0:
                emergency = 1
                #print('///row7: %d' % board[7 * self.board_data_width + xx])
                print('///////emergency: ' + str(emergency)) 
                break
        #if emergency == 0:
        #    for xx in range(3, self.board_data_width - 3, +1):
        #        if xxbackboard[14 * self.board_data_width + xx] != 0:
        #            unsafe = 1
        #            #print('///row14: %d' % board[14 * self.board_data_width + xx])
        #            print('///////unsafe: ' + str(unsafe)) 
        #            break       
        if (CurrentShape_index == 1) and (emergency == 0) and (maxHeight <=19):  # 1 NOT IN Emergency
            score = score + fullLines * 10.0           # try to delete line
            score = score - nHoles * 10.0               # try not to make hole 10
            score = score - nIsolatedBlocks * 1.5      # try not to make isolated bloc
            score = score - absDy * 1.5                # try to put block smoothly
            #score = score - maxHeight * 0.01              # maxHeigh
            score = score - xxdy * 0.01                # block_minHeight 0.01
            if fullLines == 1:
                score = score - fullLines * 30.0           # try to delete line 
            elif fullLines == 2:
                score = score - fullLines * 30.0           # try to delete line
            elif fullLines == 3:
                score = score + fullLines * 1000.0           # try to delete line 
            elif fullLines == 4:
                score = score + fullLines * 1000.0           # try to delete line
            #if (direction0 == 0) and ((x0 == 0) or (x0 == 9)):
            #    score = score + 1                       
        
        elif ((CurrentShape_index >= 2) and (CurrentShape_index <= 3)) and (emergency == 0) and (maxHeight <=19): 
            score = score + fullLines * 10.0           # try to delete line
            score = score - nHoles * 10.0               # try not to make hole
            score = score - nIsolatedBlocks * 1.5      # try not to make isolated bloc
            score = score - absDy * 1.5                # try to put block smoothly
            #score = score - maxHeight * 0.01              # maxHeigh
            score = score - xxdy * 0.01                # block_minHeight 0.01
            if fullLines == 1:
                score = score - fullLines * 30.0           # try to delete line 
            elif fullLines == 2:
                score = score - fullLines * 20.0           # try to delete line
            elif fullLines == 3:
                score = score + fullLines * 10.0           # try to delete line 1000
                     
        #elif (CurrentShape_index >= 4) and (emergency == 0) and (unsafe == 1) and (maxHeight <=19): # In safe
        #    #score = score + fullLines * 10.0           # try to delete line
        #    score = score - nHoles * 10.0               # try not to make hole
        #    score = score - nIsolatedBlocks * 1.5      # try not to make isolated bloc
        #    score = score - absDy * 1.5                # try to put block smoothly
        #    #score = score - maxHeight * 0.01              # maxHeigh
        #    score = score - xxdy * 0.01                # block_minHeight
        #    if fullLines == 1:
        #        score = score - fullLines * 15.0           # try to delete line
        #    elif fullLines == 2:
        #        score = score - fullLines * 5.0           # try to delete line

        elif (CurrentShape_index >= 4) and (emergency == 0) and (maxHeight <=19):   # In unsafe
            score = score + fullLines * 10.0           # try to delete line
            score = score - nHoles * 10.0               # try not to make hole
            score = score - nIsolatedBlocks * 1.5      # try not to make isolated bloc
            score = score - absDy * 1.5                # try to put block smoothly
            #score = score - maxHeight * 0.01              # maxHeigh
            score = score - xxdy * 0.01                # block_minHeight
            if fullLines == 1:
                score = score - fullLines * 10.0           # try to delete line
            #elif fullLines == 2:
            #    score = score - fullLines * 2.0           # try to delete line

        else:   # IN EMERGENCY
            score = score + fullLines * 10.0           # try to delete line
            score = score - nHoles * 5.0               # try not to make hole
            score = score - nIsolatedBlocks * 1.5      # try not to make isolated bloc
            score = score - absDy * 1.0                # try to put block smoothly
            #score = score - maxHeight * 0.01              # maxHeigh
            score = score - xxdy * 0.1                  # block_minHeight 0.01
            #if fullLines == 1:
            #    score = score - fullLines * 5.0           # try to delete line
            #elif fullLines == 3:
            #    score = score + fullLines * 1000.0           # try to delete line
            #elif fullLines == 4:
            #    score = score + fullLines * 1000.0           # try to delete line
            if xxdy <= 12:
                score = score + (22 - xxdy) * 0.1           # try to delete line
            #if xxdy >= 19:
            #    score = score - xxdy * 1000.0           # try to delete line
                
        #if (CurrentShape_index == 4) and ((direction0 == 0) or (direction0 == 2)) and (emergency == 0) and (fullLines == 1): 
        #    score = score - fullLines * 5.0           # try to delete line 
            #elif fullLines == 2:
            #    score = score - fullLines * 20.0           # try to delete line            
        #********************************************************************************
        #score = score - maxDy * 0.3                # maxDy
        #score = score - stdY * 1.0                 # statistical data
        #score = score - stdDY * 0.001               # statistical data


        #print("score, fullLines, nHoles, nIsolatedBlocks, absDy, BlockMaxY")
        print(str(score) + ' fullLines=' + str(fullLines) + ' nHoles=' + str(nHoles) + ' nIsolatedBlocks=' + str(nIsolatedBlocks) + ' absDy=' + str(absDy) + ' maxHeight=' + str(maxHeight))
        print('BlockMaxY=' + str(BlockMaxY) + ' xxdy=' + str(xxdy) )
        return score


BLOCK_CONTROLLER_SAMPLE = Block_Controller()
