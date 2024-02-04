"""
Fichier pour une classe stockant toutes les infos sur l'état actuel du jeu.
Il va aussi permettre de déterminer les mouvements possibles.
Il va garder les mouvements en mémoire
"""


class GameState:
    def __init__(self):
        # le plateau est modélisé par une liste de liste de 8 X 8 chaque case reçoit son nom en fonction de la pièce qui l'occupe initialement
        self.board = [
            ["t_n", "c_n", "-_-", "-_-", "k_n", "-_-", "-_-", "t_n"],
            ["p_n", "p_n", "p_n", "p_n", "p_n", "p_n", "p_n", "p_n"],
            ["-_-", "-_-", "-_-", "-_-", "-_-", "-_-", "-_-", "-_-"],
            ["-_-", "-_-", "-_-", "-_-", "-_-", "-_-", "-_-", "-_-"],
            ["-_-", "-_-", "-_-", "-_-", "-_-", "-_-", "-_-", "-_-"],
            ["-_-", "-_-", "-_-", "-_-", "-_-", "-_-", "-_-", "-_-"],
            ["p_b", "p_b", "p_b", "p_b", "p_b", "p_b", "p_b", "p_b"],
            ["t_b", "c_b", "-_-", "-_-", "k_b", "-_-", "-_-", "t_b"]]
        self.moveFunctions = {"p": self.getPawnMoves, "t": self.getRookMoves, "c": self.getKnightMoves,
                              "b": self.getBishopMoves, "q": self.getQueenMoves,
                              "k": self.getKingMoves}  # on fait ainsi un dictionnaire qui relie chaque pièce à sa fonction déplacement
        self.WhiteToMove = True  # on crée un booléen qui définit à qui est le tour
        self.moveLog = []  # on va compiler dans une liste les actions effectuées
        self.checkmate = False  #indicateur d'échec et mat
        self.stalemate = False  #indicateur de pat
        self.whiteKinglocation = (7, 4)  # on initialise la position du roi blanc
        self.blackKinglocation = (0, 4)  # on initialise la position du roi noir
        self.inCheck = False  # est-ce que le roi du joueur actuel est en échec
        self.pins = []  # liste des mouvements qu'on ne peut pas faire pour ne pas se mettre en échec
        self.checks = []  # liste des pièces qui font échec au roi
        self.enPassant = ()  # on utilise ce tuple pour conserver les coordonnées d'un pion autorisant le "en-passant".
        self.enPassantMemory = []  # on va conserver tous les en passant dans cette liste avec le tour auquel ils sont survenus
        self.blackKingMoved = [False]  #on crée un booléen qui indique si le roi noir a bougé (pour le roque).
        self.whiteKingMoved = [False]  #on crée un booléen qui indique si le roi blanc a bougé (pour le roque).
        self.blackQueenSideCastling = [True]  #on crée une liste qui indique si un roque est possible du côté de la reine pour les noirs
        self.blackKingSideCastling = [True]  #on crée une liste qui indique si un roque est possible du côté du roi pour les noirs
        self.whiteQueenSideCastling = [True]  #on crée une liste qui indique si un roque est possible du côté de la reine pour les blancs
        self.whiteKingSideCastling = [True]  #on crée une liste qui indique si un roque est possible du côté du roi pour les blancs
        self.castlingMemory = []  #on mémorise si un rock a été effectué

    """
    prend un mouvement en argument et l'applique (ne peut appliquer le roque, la promotion du pion et le "en passant")
    """

    def makeMove(self, move):
        print(f"Making move: {move.getChessNotation()}")
        self.board[move.startRow][move.startCol] = "-_-"  #l'emplacement initial de la pièce est remplacé par une case vierge
        self.board[move.endRow][move.endCol] = move.pieceMoved  #la case sélectionnée est remplacée par la pièce déplacée
        self.moveLog.append(move)  # on rajoute le mouvement dans la liste destinée à cet effet
        self.WhiteToMove = not self.WhiteToMove  # Le tour passe à l'autre joueur
        if move.pieceMoved == "k_b":  # si on bouge le roi, on actualise la variable que conserve sa location (permet de vérifier les échecs au roi)
            self.whiteKinglocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "k_n":
            self.blackKinglocation = (move.endRow, move.endCol)

    """
    Fonction qui supprime le dernier mouvement
    """

    def undoMove(self):
        if len(self.moveLog) != 0:  # on vérifie qu'il y a un mouvement à supprimer
            move = self.moveLog.pop()  # On enlève le dernier de mouvement de la liste des mouvements tout en les renvoyant. /!\ il appartient déjà à la classe move
            self.board[move.startRow][move.startCol] = move.pieceMoved  # on remet la pièce initialement sélectionnée à son emplacement de départ
            self.board[move.endRow][move.endCol] = move.pieceCaptured  # on remet la case d'arrivée telle qu'elle était avant le mouvement
            self.WhiteToMove = not self.WhiteToMove  # Le tour passe à l'autre joueur
            if move.pieceMoved == "k_b":  # si le roi avait bougé on réactualise la variable que conserve sa location (permet de vérifier les échecs au roi.)
                self.whiteKinglocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "k_n":
                self.blackKinglocation = (move.startRow, move.startCol)

    """
    Fonction qui établit les mouvements valides
    """
    def getValidMoves(self):
        moves = []  #on crée la liste des mouvements possibles
        # print(len(self.moveLog), self.whiteKingMoved, self.whiteQueenSideCastling, self.whiteKingSideCastling)
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()  #on actualise l'état d'échec, les pièces épinglées et les pièces menaçant le roi
        if self.WhiteToMove:  #on récupère les coordonnées du roi du joueur
            kingRow, kingCol = self.whiteKinglocation
        else:
            kingRow, kingCol = self.blackKinglocation
        if self.inCheck:  #si le roi est en échec
            if len(self.checks) == 1:  # si seulement 1 pièce met le roi en échec (on peut bloquer l'échec ou bouger le roi.)
                moves = self.getAllPossibleMoves()  #on récupère tous les mouvements possibles
                check = self.checks[0]  # on récupère les coordonnées de la pièce qui menace le roi
                checkRow = check[0]  #on récupère la ligne de la pièce menaçante
                checkCol = check[1]  #et sa colonne
                pieceChecking = self.board[checkRow][checkCol]  # on récupère l'identité de la pièce causant l'échec
                validSquares = []  # on crée une nouvelle liste des mouvements réellement autorisés par les pièces autres que le roi
                if pieceChecking[0] == "c":  # si la pièce menaçante est un cavalier
                    validSquares = [(checkRow, checkCol)]  # on ne peut que le manger et non s'interposer
                else:
                    for i in range(1, 8):  #on parcourt toutes les cases entre le roi et la pièce le menaçant
                        validSquare = (kingRow + check[2] * i, kingCol + check[3] * i)  # check[2] et check[3] sont les directions de la pièce menaçante
                        validSquares.append(validSquare)  #chacune de ces cases devient une case valide
                        if validSquare[0] == checkRow and validSquare[1] == checkCol:  #si la case en question est occupée par la pièce menaçante, on s'arrête là
                            break
                for i in range(len(moves) - 1, -1, -1):  # permet de parcourir toute une liste sans oublier des éléments même si on en supprime lors du parcours
                    if moves[i].pieceMoved[0] != "k":  # si ce n'est pas le roi qui est bougé
                        if not (moves[i].endRow, moves[i].endCol) in validSquares:  # si le déplacement ne bloque pas l'échec
                            moves.remove(moves[i])  # on interdit le déplacement
            else:  #si deux pièces mettent le roi en échec
                self.getKingMoves(kingRow, kingCol, moves)
            if len(moves) == 0:  #si aucun mouvement n'est possible
                self.checkmate = True  #alors le joueur est échec est mat
        else:  # si le roi n'est pas en échec
            moves = self.getAllPossibleMoves()  #on récupère tous les mouvements possibles
            if len(moves) == 0:  #si aucun mouvement n'est possible
                self.stalemate = True  #alors le joueur est pat

        return moves

    """
    Fonction qui établit les mouvements valides
    """

    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):  # nombre de lignes
            for c in range(len(self.board[r])):  # nombre de colonnes dans la ligne
                turn = self.board[r][c][2]  # on récupère la couleur de la pièce sélectionnée
                if (turn == "b" and self.WhiteToMove) or (turn == "n" and not self.WhiteToMove):  # si elle est en adéquation avec celle qui doit jouer
                    piece = self.board[r][c][0]  # on récupère la pièce dont il s'agit
                    self.moveFunctions[piece](r, c, moves)  # on appelle directement la bonne fonction déplacement grâce au dictionnaire prévu à cet effet
        return moves

    """
    Récupérer tous les mouvements possibles pour un pion situé sur une ligne, dans une colonne, et les ajouter à la liste
    """

    def getPawnMoves(self, r, c, moves):
        piecePinned = False  #on crée la variable qui définie si la pièce est épinglée ou non
        pinDirection = ()  #on crée la variable qui récupère la potentielle direction dans laquelle une pièce adverse menace le roi
        for i in range(len(self.pins) - 1, -1, -1):  #on parcourt l'ensemble des pièces épinglées
            if self.pins[i][0] == r and self.pins[i][1] == c:  #si la pièce en fait partie, on renseigne les 2 précédentes variables
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])  #on retire ensuit la pièce de la liste
                break

        direction = -1 if self.WhiteToMove else 1
        enemyColor = "n" if self.WhiteToMove else "b"
        rawEnPassant = (1, 3) if self.WhiteToMove else (6, 4)
        startingRaw = 6 if self.WhiteToMove else 1

        if self.board[r + direction][c] == "-_-":  # si la case au-dessus du pion blanc est vide
            if not piecePinned or pinDirection == (direction, 0):
                moves.append(Move((r, c), (r + direction, c), self.board))  # il peut "monter" d'une case
                if r == startingRaw and self.board[r + 2*direction][c] == "-_-":  # s'il est en position de départ et que la deuxième case au-dessus est vide
                    moves.append(Move((r, c), (r + 2*direction, c), self.board))  # il peut "monter" de deux cases

        # captures
        if c - 1 >= 0:  # capture à gauche
            if self.board[r + direction][c - 1][2] == enemyColor:  # s'il y a un ennemi au-dessus à gauche
                if not piecePinned or pinDirection == (direction, -1):
                    moves.append(Move((r, c), (r + direction, c - 1), self.board))  # il peut le manger
        if c + 1 <= 7:  # capture à droite
            if self.board[r + direction][c + 1][2] == enemyColor:  # s'il y a un ennemi au-dessus à droite
                if not piecePinned or pinDirection == (direction, 1):
                    moves.append(Move((r, c), (r + direction, c + 1), self.board))  # il peut le manger

        # en passant
        if r == rawEnPassant[1] and len(self.moveLog) != 0:  # on vérifie d'abord que le pion est placé sur la seule ligne qui autorise le "en-passant" et que la liste des mouvements n'est pas vide
            if c >= 1 and self.moveLog[-1] == Move((rawEnPassant[0], c - 1), (rawEnPassant[1], c - 1), self.board):  #si on est dans les limites du plateau et que le mouvement précédent autorise le "en-passant"
                moves.append(Move((r, c), (r + direction, c - 1), self.board))  # il peut le manger
                self.enPassant = ((r, c), (r + direction, c - 1))  #et on renseigne le mouvement qui serait considéré comme un "en-passant"
            if c <= 6 and self.moveLog[-1] == Move((rawEnPassant[0], c + 1), (rawEnPassant[1], c + 1), self.board):  #si on est dans les limites du plateau et que le mouvement précédent autorise le "en-passant"
                moves.append(Move((r, c), (r + direction, c + 1), self.board))  # il peut le manger
                self.enPassant = ((r, c), (r + direction, c + 1))  #et on renseigne le mouvement qui serait considéré comme un "en-passant"

    """
    Récupérer tous les mouvements possibles pour une tour situé sur une ligne, dans une colonne, et les ajouter à la liste
    """

    def getRookMoves(self, r, c, moves):
        piecePinned = False  #on crée la variable qui définie si la pièce est épinglée ou non
        pinDirection = ()  #on crée la variable qui récupère la potentielle direction dans laquelle une pièce adverse menace le roi
        for i in range(len(self.pins) - 1, -1, -1):  #on parcourt l'ensemble des pièces épinglées
            if self.pins[i][0] == r and self.pins[i][1] == c:  #si la pièce en fait partie, on renseigne les 2 précédentes variables
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][0] != "q":  #apparement ça repart un bug, je ne vois vraiment pas...
                    self.pins.remove(self.pins[i])  #on retire ensuit la pièce de la liste
                break

        val = [1, -1]  # on va aller à droite et à gauche puis en haut et en bas
        enemyColor = "n" if self.WhiteToMove else "b"  # on récupère la couleur adverse
        for i in val:
            j = i  # on crée une variable qui va s'ajouter à chaque itération du "while" à i (pour continuer dans le même sens.)
            while 0 <= r + i <= 7 and self.board[r + i][c] == "-_-":  # tant qu'on se trouve encore sur le plateau et que les cases du dessus ou du dessous sont vides
                if not piecePinned or pinDirection == (1, 0) or pinDirection == (-1, 0):
                    moves.append(Move((r, c), (r + i, c), self.board))  # on ajoute le mouvement à la liste
                i += j  # on ajoute j à i pour passer à la case suivante
            if 0 <= r + i <= 7:  # si on est dans les limites du plateau
                if self.board[r + i][c][2] == enemyColor:  # et que la case suivante est occupée par un adversaire
                    if not piecePinned or pinDirection == (1, 0) or pinDirection == (-1, 0):
                        moves.append(Move((r, c), (r + i, c), self.board))  # on ajoute le mouvement qui permet de le manger

        for k in val:
            l = k  # on crée une variable qui va s'ajouter à chaque itération du "while" à k (pour continuer dans le même sens.)
            while 0 <= c + k <= 7 and self.board[r][c + k] == "-_-":  # tant qu'on se trouve encore sur le plateau et que les cases à droite ou à gauche sont vides
                if not piecePinned or pinDirection == (0, 1) or pinDirection == (0, -1):
                    moves.append(Move((r, c), (r, c + k), self.board))  # on ajoute le mouvement à la liste
                k += l  # on ajoute j à i pour passer à la case suivante
            if 0 <= c + k <= 7:  # si on est dans les limites du plateau
                if self.board[r][c + k][2] == enemyColor:  # et que la case suivante est occupée par un adversaire
                    if not piecePinned or pinDirection == (0, 1) or pinDirection == (0, -1):
                        moves.append(Move((r, c), (r, c + k), self.board))  # on ajoute le mouvement qui permet de le manger

    """
    Récupérer tous les mouvements possibles pour un cavalier situé sur une ligne, dans une colonne, et les ajouter à la liste
    """

    def getKnightMoves(self, r, c, moves):
        piecePinned = False  #on crée la variable qui définie si la pièce est épinglée ou non
        for i in range(len(self.pins) - 1, -1, -1):  #on parcourt l'ensemble des pièces épinglées
            if self.pins[i][0] == r and self.pins[i][1] == c:  #si la pièce en fait partie, on renseigne la précédente variable
                piecePinned = True
                self.pins.remove(self.pins[i])  #on retire ensuit la pièce de la liste
                break

        val = [1, -1]  # tu commences à connaître
        playerColor = "b" if self.WhiteToMove else "n"  # on récupère la couleur du joueur
        if not piecePinned:
            for i in val:  # on va aller en bas puis en haut
                for j in val:  # on va aller à droite puis à gauche par la suite on vérifie les cases une par une tmts
                    if 0 <= r + (2 * i) <= 7 and 0 <= c + j <= 7 and self.board[r + (2 * i)][c + j][2] != playerColor:
                        moves.append(Move((r, c), (r + (2 * i), c + j), self.board))  # on ajoute le mouvement à la liste
                    if 0 <= r + i <= 7 and 0 <= c + (2 * j) <= 7 and self.board[r + i][c + (2 * j)][2] != playerColor:
                        moves.append(Move((r, c), (r + i, c + (2 * j)), self.board))  # on ajoute le mouvement à la liste

    """
    Récupérer tous les mouvements possibles pour un fou situé sur une ligne, dans une colonne, et les ajouter à la liste
    """

    def getBishopMoves(self, r, c, moves):
        piecePinned = False  #on crée la variable qui définie si la pièce est épinglée ou non
        pinDirection = ()  #on crée la variable qui récupère la potentielle direction dans laquelle une pièce adverse menace le roi
        for i in range(len(self.pins) - 1, -1, -1):  #on parcourt l'ensemble des pièces épinglées
            if self.pins[i][0] == r and self.pins[i][1] == c:  #si la pièce en fait partie, on renseigne les 2 précédentes variables
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])  #on retire ensuit la pièce de la liste
                break

        val = [1, -1]  # on va aller à droite et à gauche puis en haut et en bas
        enemyColor = "n" if self.WhiteToMove else "b"  # on récupère la couleur adverse
        for i in val:  # on parcourt le plateau de bas en haut
            j = i  # on crée une variable qui va s'ajouter à chaque itération du "while" à i (pour continuer dans le même sens.)
            for k in val:  # et en même temps de droite à gauche
                l = k  # on crée une variable qui va s'ajouter à chaque itération du "while" à k (pour continuer dans le même sens.)
                while 0 <= r + i <= 7 and 0 <= c + k <= 7 and self.board[r + i][c + k] == "-_-":  # tant qu'on se trouve encore sur le plateau et que les cases de la diagonale concernée sont vides
                    if not piecePinned or pinDirection == (j, l) or pinDirection == (-j, -l):
                        moves.append(Move((r, c), (r + i, c + k), self.board))  # on ajoute le mouvement à la liste
                    i += j  # on ajoute j à i pour passer à la ligne suivante (ou précédente)
                    k += l  # on ajoute l à k pour passer à la colonne suivante (ou précédente)
                if 0 <= r + i <= 7 and 0 <= c + k <= 7:  # si on est dans les limites du plateau
                    if self.board[r + i][c + k][2] == enemyColor:  # et que la case suivante est occupée par un adversaire
                        if not piecePinned or pinDirection == (j, l) or pinDirection == (-j, -l):
                            moves.append(Move((r, c), (r + i, c + k), self.board))  # on ajoute le mouvement qui permet de le manger
                i = j  # après avoir ajouté tous les mouvements, on réinitialise i qui a été modifié, et on retourne dans la boucle.

    """
    Récupérer tous les mouvements possibles pour une dame situé sur une ligne, dans une colonne, et les ajouter à la liste
    """

    def getQueenMoves(self, r, c, moves):  # on copie tout simplement getRookMoves et getBishopMoves
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    """
    Récupérer tous les mouvements possibles pour un roi situé sur une ligne, dans une colonne, et les ajouter à la liste
    """

    def getKingMoves(self, r, c, moves):
        val = [-1, 0, 1]  # on parcourt toutes les cases adjacentes en vérifiant si le déplacement est possible (que la case existe et soit vide ou occupée par une pièce adverse.)
        allyColor = "b" if self.WhiteToMove else "n"  # on récupère la couleur alliée
        for i in val:
            for j in val:
                endRow = r + i
                endCol = c + j
                if (i, j != 0, 0) and 0 <= endRow <= 7 and 0 <= endCol <= 7:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[2] != allyColor:  # si la case choisie est vide ou occupée par une pièce adverse
                        # on place le roi sur la case et on regarde s'il est en échec
                        if allyColor == "b":
                            self.whiteKinglocation = (endRow, endCol)
                        else:
                            self.blackKinglocation = (endRow, endCol)
                        inCheck, pins, checks = self.checkForPinsAndChecks()
                        if not inCheck:
                            moves.append(Move((r, c), (endRow, endCol), self.board))  # on ajoute le mouvement à la liste des mouvements possibles
                        # on replace le roi dans sa position de base (aucun mouvement n'a été effectué, on regarde juste les mouvements possibles.)
                        if allyColor == "b":
                            self.whiteKinglocation = (r, c)
                        else:
                            self.blackKinglocation = (r, c)

        # on pense à ajouter les roques à la liste des mouvements possibles après vérification.
        king = self.whiteKingMoved if self.WhiteToMove else self.blackKingMoved  # on sélectionne le bon roi en fonction du joueur
        tourDroite = self.whiteKingSideCastling if self.WhiteToMove else self.blackKingSideCastling  #on sélectionne la bonne tour de droite en fonction du joueur
        tourGauche = self.whiteQueenSideCastling if self.WhiteToMove else self.blackQueenSideCastling  #on sélectionne la bonne tour de gauche en fonction du joueur
        dictTour = {-1: [tourGauche, 0], 1: [tourDroite, 7]}  #on crée ce dictionnaire auquel on fera appel pour choisir entre la tour de droite, celle de gauche

        for i in [1, -1]:  #on prend cet ordre-là pour éviter tout problème avec le roque côté reine où on utilise un break
            if dictTour[i][0] == [True] and not king[0]:  #si ni le roi, ni la tour concernée n'ont bougé
                if Move((r, c), (r, c+i), self.board) in moves and self.board[r][c+2*i] == "-_-":  #si les cases entre le roi et la tour sont vides
                    if i == -1 and self.board[r][c-3] != "-_-":  #si c'est un roque côté reine, on vérifie que la troisième case est également vide
                        break
                    if self.WhiteToMove:  #on modifie la position du roi
                        self.whiteKinglocation = (r, c+2*i)
                    else:
                        self.blackKinglocation = (r, c+2*i)
                    inCheck, pins, checks = self.checkForPinsAndChecks()  #on récupère ces valeurs
                    if not inCheck:  #si le roque ne met pas le roi en échec
                        moves.append(Move((r, c), (r, c+2*i), self.board))  # on ajoute le mouvement à la liste des mouvements possibles
                    if self.WhiteToMove:  #on remet le roi dans sa vraie position
                        self.whiteKinglocation = (r, c)
                    else:
                        self.blackKinglocation = (r, c)

    """
    Fonction qui retourne si le joueur est en échec, la liste des pins(pièces bloqués) 
    et la liste de pièces mettant le roi en échec
    """

    def checkForPinsAndChecks(self):
        pins = []  # première liste, initialement vierge des pins (pièces épinglées)
        checks = []  # première liste, initialement vierge des pièces menaçant le roi
        inCheck = False  # booléen de condition d'échec, initialement sur faux
        # on va maintenant récupérer les infos essentielles concernant le joueur
        if self.WhiteToMove:
            enemyColor = "n"
            allyColor = "b"
            startRow = self.whiteKinglocation[0]
            startCol = self.whiteKinglocation[1]
        else:
            enemyColor = "b"
            allyColor = "n"
            startRow = self.blackKinglocation[0]
            startCol = self.blackKinglocation[1]
        # on va chercher les checks et les pins
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = ()  # réinitialisation des pins possibles
            for i in range(1, 8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[2] == allyColor and endPiece[0] != "k":
                        if possiblePin == ():
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else:
                            break
                    elif endPiece[2] == enemyColor:
                        Type = endPiece[0]
                        # il y a 5 possibilités à vérifier
                        # si la pièce se trouve sur la même ligne ou colonne que le roi et est une tour
                        # si la pièce se trouve sur une diagonale du roi et est un fou
                        # si la pièce est un pion placé à une case en diagonale sur sa ligne d'attaque du roi
                        # si la pièce se trouve dans n'importe laquelle des précédentes directions et est la dame
                        # si la pièce est un roi à une case de distance (pour empêcher le roi de bouger à côté de l'autre roi.)
                        if (0 <= j <= 3 and Type == "t") or (4 <= j <= 7 and Type == "b") or \
                                (i == 1 and Type == "p" and ((enemyColor == "b" and 6 <= j <= 7) or (enemyColor == "n" and 4 <= j <= 5))) or \
                                (Type == "q") or (i == 1 and Type == "k"):
                            if possiblePin == ():  # aucune pièce n'est en train de bloquer donc échec au roi
                                inCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            else:  # une pièce bloque le passage
                                pins.append(possiblePin)
                                break
                        else:  # aucune pièce ennemie ne menace le roi
                            break
                else:
                    break

        # on vérifie maintenant si un cavalier menace le roi
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knightMoves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                endPiece = self.board[endRow][endCol]
                if endPiece[2] == enemyColor and endPiece[0] == "c":  # si on trouve un cavalier adverse en train de menacer
                    inCheck = True
                    checks.append((endRow, endCol, m[0], m[1]))
        return inCheck, pins, checks

    def checkForEnPassant(self, depart, arrivee, turn):
        if self.enPassant != () and self.enPassant[0] == depart and self.enPassant[1] == arrivee:  # si le joueur a la possibilité d'un "en-passant" et qu'il la saisit
            rawEnemyPawn = depart[0]  # on récupère la ligne du pion qui se fait manger
            colEnemyPawn = arrivee[1]  # on récupère la colonne du pion qui se fait manger
            self.board[rawEnemyPawn][colEnemyPawn] = "-_-"  # on remplace la case du pion qui s'est fait manger par une case vide
            self.enPassantMemory.append([rawEnemyPawn, colEnemyPawn, turn])  # et on enregistre le "en-passant" effectué, nécessaire si on veut revenir en arrière (+1, car le mouvement est ajouté à la liste la ligne suivante)
        self.enPassant = ()  # on réinitialise la variable "en-passant" pour qu'elle ne puisse pas être effectuée au tour suivant

    def enPassantComeback(self, turn):
        if self.enPassantMemory != [] and self.enPassantMemory[-1][-1] == turn:  # si le coup annulé correspond à un "en-passant".
            rawPawnToResurrect = self.enPassantMemory[-1][0]  # on récupère la ligne du pion à ressusciter
            colPawnToResurrect = self.enPassantMemory[-1][1]  # on récupère la colonne du pion à ressusciter
            self.board[rawPawnToResurrect][colPawnToResurrect] = "p_" + self.moveLog[-2].pieceMoved[2]  # c'est un pion adverse qu'il faut ressusciter, on récupère donc la couleur de l'avant-dernier joueur (celui qui a perdu son pion).
            self.enPassantMemory.pop()  # et on n'oublie pas de vider la mémoire des "en-passant".

    def checkForCastling(self, move, turn):
        king = self.whiteKingMoved if not self.WhiteToMove else self.blackKingMoved  # on sélectionne le bon roi en fonction du joueur
        tourDroite = self.whiteKingSideCastling if not self.WhiteToMove else self.blackKingSideCastling  #on sélectionne la bonne tour de droite en fonction du joueur
        tourGauche = self.whiteQueenSideCastling if not self.WhiteToMove else self.blackQueenSideCastling  #on sélectionne la bonne tour de gauche en fonction du joueur
        dictTour = {-1: [tourGauche, 0], 1: [tourDroite, 7], 0: [[False]]}  #on crée ce dictionnaire auquel on fera appel pour choisir entre la tour de droite, celle de gauche ou aucune selon le besoin
        if move.pieceMoved[0] == "k" and len(king) == 1:  #si la pièce bougée est le roi noir et sort de son emplacement initial
            # si c'est pour faire un roque, alors la tour est échangée avec la case vierge concernée
            for i in [-1, 1]:  #on parcourt ces deux valeurs (respectivement équivalentes à gauche et droite).
                if move.endCol == (move.startCol + 2*i):  #si le mouvement effectué est de deux cases à droite ou à gauche du roi (c'est un roque), on va échanger la tour avec la case vide correspondante
                    self.board[move.startRow][move.startCol + i], self.board[move.startRow][dictTour[i][1]] = self.board[move.startRow][dictTour[i][1]], self.board[move.startRow][move.startCol + i]
                    dictTour[i][0][0] = False  #on ajoute que la tour a bougé (ces deux lignes ne sont pas nécessaire, mais beaucoup plus propres).
                    dictTour[i][0].append(turn)  #ainsi que le tour auquel c'est arrivé
                    self.castlingMemory.append([move.startCol - move.endCol, turn])  # on sauvegarde le roque en mémoire
            king[0] = True  #on confirme que le roi a bougé (pour empêcher de refaire un roque).
            king.append(turn)  #ainsi que le tour auquel c'est arrivé

        if move.pieceMoved[0] == "t":  #si la piece bougée est une tour
            i = -1 if move.startCol == 0 else 1 if move.startCol == 7 else 0
            tour = dictTour[i][0]  #on détermine si c'est une tour sortant de son emplacement initial et laquelle grâce au dictionnaire précédemment établi
            if tour[0]:  #on vérifie si la tour n'avait jamais bougé
                tour[0] = False  #on confirme que le roque de ce côté n'est alors plus possible
                tour.append(turn)  #et on sauvegarde le tour auquel c'est arrivé (pour le retour arrière)

    def castlingComeback(self, turn):
        king = self.whiteKingMoved if not self.WhiteToMove else self.blackKingMoved
        tourDroite = self.whiteKingSideCastling if not self.WhiteToMove else self.blackKingSideCastling
        tourGauche = self.whiteQueenSideCastling if not self.WhiteToMove else self.blackQueenSideCastling
        tour = tourDroite if len(tourDroite) > 1 and tourDroite[-1] == turn else tourGauche

        if self.castlingMemory != [] and self.castlingMemory[-1][-1] == turn:  # si le coup annulé correspond à un roque.
            if self.castlingMemory[-1][0] < 0:  #on vérifie de quel côté le roque a été effectué et on échange la tour et la case vierge du coin concerné
                self.board[self.moveLog[-1].startRow][self.moveLog[-1].startCol + 1], self.board[self.moveLog[-1].startRow][7] = self.board[self.moveLog[-1].startRow][7], self.board[self.moveLog[-1].startRow][self.moveLog[-1].startCol + 1]
            if self.castlingMemory[-1][0] > 0:
                self.board[self.moveLog[-1].startRow][self.moveLog[-1].startCol - 1], self.board[self.moveLog[-1].startRow][0] = self.board[self.moveLog[-1].startRow][0], self.board[self.moveLog[-1].startRow][self.moveLog[-1].startCol - 1]
            self.castlingMemory.pop()  #on supprime la sauvegarde du roque

        if len(king) > 1 and king[-1] == turn:  #si le coup annulé correspond au premier déplacement du roi blanc
            king[0] = False  #alors on confirme que ce dernier n'a jamais bougé
            king.pop()  #et on supprime le tour de son premier déplacement qui vient d'être annulé

        if len(tour) > 1 and tour[-1] == turn:  #si le coup annulé correspond au premier déplacement d'une tour
            tour.pop()  #et on supprime le tour de son premier déplacement qui vient d'être annulé
            tour[0] = True  #alors on confirme que ce dernier n'a jamais bougé


class Move:
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1,
                   "8": 0}  # dictionnaire de conversion python vers échecs des lignes
    rowsToRank = {v: k for k, v in ranksToRows.items()}  # permet d'inverser le dictionnaire
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6,
                   "h": 7}  # dictionnaire de conversion python vers échecs des colonnes
    colsToFiles = {v: k for k, v in filesToCols.items()}  # permet d'inverser le dictionnaire

    def __init__(self, startSq, endSq, board):  # fonction qui prend en argument les coordonnées de départ et d'arrivée ainsi que la surface sur laquelle cela se produit
        self.startRow = startSq[0]  # on récupère l'abcisse de la coordonnée de départ
        self.startCol = startSq[1]  # on récupère l'ordonnée de la coordonnée de départ
        self.endRow = endSq[0]  # on récupère l'abcisse de la coordonnée d'arrivée
        self.endCol = endSq[1]  # on récupère l'ordonnée de la coordonnée d'arrivée'
        self.pieceMoved = board[self.startRow][self.startCol]  # on récupère l'élément se trouvant à ces coordonnées de départ sur la matrice
        self.pieceCaptured = board[self.endRow][self.endCol]  # on récupère l'élément se trouvant à ces coordonnées d'arrivée sur la matrice
        self.isPawnPromotion = False
        if (self.pieceMoved == "p_b" and self.endRow == 0) or (self.pieceMoved == "p_n" and self.endRow == 7):
            self.isPawnPromotion = True
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
        # print(self.moveID)

    """
    remplacer la méthode égale
    """

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):  # fonction qui va afficher tous les mouvements effectués
        return self.getRankFile(self.startRow, self.startCol) + " " + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):  # fonction qui permet d'aller chercher dans les dictionnaires précédemment établis la case définie par r et c dans le jargon échecs
        return self.colsToFiles[c] + self.rowsToRank[r]
