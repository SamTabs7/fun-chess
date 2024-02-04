"""
Fichier principal responsable de la gestion des entrées de l'utilisateur et de l'affichage de l'état du jeu en temps réel
"""
import pygame as p
import ChessEngine

WIDTH = HEIGHT = 640  # hauteur et largeur
DIMENSION = 8  # 8*8 cases
SQ_SIZE = HEIGHT // DIMENSION  # on définit ainsi la dimension d'une case avec le 2 variables précédentes
MAX_FPS = 15  # pour les animations (plus tard)
IMAGES = {}  # on crée on dictionnaire
squareColors = [p.Color("white"), p.Color("black")]

"""
Initialiser le dictionnaire d'image. 
Il ne sera appelé qu'une seule fois dans ce programme principal
"""


def loadImages():
    pieces = ["b_b", "b_n", "c_b", "c_n", "k_b", "k_n", "p_b", "p_n", "q_b", "q_n", "t_b", "t_n"]
    for piece in pieces:  # boucle for pour faire rentrer chaque image dans le dictionnaire en les redimensionnant
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
    # On peut accéder à une image en utilisant le dictionnaire en l'appelant par "IMAGES["*_*"]


"""
On introduit maintenant la fonction principale qui prend en compte les entrées utilisateur et rafraîchit l'écran 
"""


def main():
    p.init()  # initialise tous les modules importés de pygame
    screen = p.display.set_mode((WIDTH, HEIGHT))  # on redimensionne l'écran
    clock = p.time.Clock()  # on crée une horloge
    screen.fill(p.Color("white"))  # on colorie l'écran en blanc (pas nécessaire, mais peut éviter de redessiner des cases blanches).
    gs = ChessEngine.GameState()  # on raccourci le nom de la variable
    validMoves = gs.getValidMoves()  # on fait appel à cette fonction qui récupère les mouvements possibles de chaque pièce
    moveMade = False  # indicateur pour quand un mouvement est réalisé
    animate = False  #indicateur pour quand le mouvement doit être animé (éviter une animation lors d'un retour arrière)
    loadImages()  # N'appeler cette instruction qu'une seule fois avant d'entrer dans la boucle while
    running = True  # on crée un booléen qui nous dit si on est en jeu
    sqSelected = ()  # Initialement, aucune case n'est sélectionnée, jusqu'à ce que le joueur clique sur l'une d'elles
    playerClicks = []  # on va conserver les clics du joueur → 2 tuples, un pour la case de départ et un pour celle d'arrivée
    locPawnToUpgrade = ()  #on crée un tuple vide dans lequel on ajoutera lorsque ce sera le cas, les coordonnées d'un pion à améliorer
    gameOver = False  #on crée un indicateur de game over pour mettre fin à une partie

    while running:  # boucle while qui affiche l'écran et relève les actions du joueur
        for e in p.event.get():  #on récupère toutes les actions qui se passent à l'écran
            if e.type == p.QUIT:
                running = False  # Si le joueur quitte la fenêtre, on stoppe le programme
            # si l'évènement est un clic de souris
            elif e.type == p.MOUSEBUTTONDOWN:  #si il y a un clic de souris
                if not gameOver:  #et que la partie n'est pas terminée
                    location = p.mouse.get_pos()  # on récupère les coordonnées de la souris lors du clic
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if sqSelected == (row, col):  # si le joueur clique deux fois sur la même case
                        sqSelected = ()  # on désélectionne la case
                        playerClicks = []  # On nettoie la liste
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)  # on va ajouter le clic à cette liste

                    if len(playerClicks) == 2:  # si la liste contient 2 tuples, donc 2 positions (soit deux clics sur deux cases différentes).
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1],
                                                gs.board)  # On crée le mouvement à l'aide de la classe Move de ChessEngine (sans l'effectuer pour l'instant).
                        if move in validMoves:  # si le mouvement est possible

                            turn = len(gs.moveLog)  #on récupère le numéro du tour

                            gs.checkForEnPassant(playerClicks[0], playerClicks[1], turn)  #on vérifie si le mouvement est un EnPassant et si oui, on agit en conséquence.

                            gs.makeMove(move)  # on appelle la fonction makeMove qui modifie la matrice de l'échiquier, enregistre le déplacement et passe le tour

                            if move.isPawnPromotion:  #si le mouvement amène à promouvoir un pion
                                locPawnToUpgrade = (move.endRow, move.endCol)  #on sauvegarde ses coordonnées dans le tuple prévu à cet effet
                            moveMade = True
                            animate = True  #on utilise cet indicateur pour animer les déplacements
                            sqSelected = ()  # on remet les clics du joueur à zéro → aucune case n'est sélectionnée pour le nouveau tour
                            playerClicks = []  # de même pour cette liste qui n'enregistre que deux clics (sélection et déplacement.)

                            gs.checkForCastling(move, turn)  # on s'occupe de vérifier si les conditions nécessaires pour le roque sont remplies ou pas (fonction adaptée pour être appelée après makeMove).

                        else:
                            playerClicks = [sqSelected]

            # si l'évènement est une touche du clavier
            elif e.type == p.KEYDOWN:
                if e.key == p.K_d:  # quand in appuie sur la touche d (=annuler un coup).
                    turn = len(gs.moveLog) - 1  #on est au tour +1, mais tous les mouvements ont été enregistrés au tour précédent

                    gs.enPassantComeback(turn)  #on regarde si ça réinitialise un en passant

                    gs.castlingComeback(turn)  #on regarde si ça réinitialise l'une des conditions du roque

                    gs.undoMove()  # on revient un tour en arrière
                    moveMade = True
                    animate = False

                if e.key == p.K_r:  #remet à zéro l'échiquier (donc toutes les variables dans leurs états initiaux).
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False

        drawGameState(screen, gs, locPawnToUpgrade, validMoves, sqSelected)  # on affiche l'écran, les cases et les pièces

        if moveMade:  #si le mouvement a été choisi
            if animate:  #si l'animation est demandée, on l'effectue
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()  #on récupère la nouvelle liste des mouvements possibles
            moveMade = False  # et on commence un nouveau tour où le joueur n'a pas encore joué

        if gs.checkmate:  #s'il y a échec et mat
            gameOver = True  #on met fin à la partie
            if gs.WhiteToMove:  # si le tour est passé blanc
                drawText(screen, "Black wins by checkmate")  #alors on affiche le message de victoire des noirs
            else:  #sinon
                drawText(screen, "White wins by checkmate")  #celui des blancs
        elif gs.stalemate:  #s'il y a pat
            gameOver = True  #on met aussi fin à la partie
            drawText(screen, "Stalemate")  #mais avec un message d'égalité
        locPawnToUpgrade = ()  #on remet à chaque fin de tour la localisation du pion à améliorer à zéro
        clock.tick(MAX_FPS)  # on met à jour l'horloge
        p.display.flip()  # on met à jour toute la surface d'affichage sur l'écran


"""
Fonction chargée de l'affichage graphique tout le long de la partie
"""


def drawGameState(screen, gs, localisation, validMoves, sqSelected):
    drawBoard(screen)  # dessiner les cases sur l'échiquier
    highlightSquares(screen, gs, validMoves, sqSelected)  # éclairage des cases
    drawPieces(screen, gs.board)  # dessiner les pièces sur l'échiquier
    drawChoice(screen, gs.board, localisation)  # afficher la sélection des pièces pour améliorer les pions


"""
indiquer la case sélectionnée par le joueur et les déplacements possibles
"""


def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():  #si on a sélectionné une case
        r, c = sqSelected  #on récupère les coordonnées
        if gs.board[r][c][2] == ("b" if gs.WhiteToMove else "n"):  #s'il y a une pièce du joueur sur la case sélectionnée
            s = p.Surface((SQ_SIZE, SQ_SIZE))  # on crée une surface carrée de la taille d'une case
            s.set_alpha(150)  #valeur de "transparence" entre 0 et 255
            s.fill(p.Color("deepskyblue2"))  #on lui ajoute une jolie couleur
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))  #et on l'affiche sur la case sélectionnée (la pièce, dessinée dans un second temps, apparaît par-dessus)
            # on s'occupe maintenant de colorer les cases où le déplacement est possible
            for move in validMoves:  #on récupère tous les mouvements autorisés
                if move.startRow == r and move.startCol == c:  #on s'attarde sur ceux de la pièce concernée
                    if gs.board[move.endRow][move.endCol] == "-_-":  #si l'arrivée du mouvement est une case vide
                        color = squareColors[((move.endRow + move.endCol) % 2)]  #on récupère la couleur de la case d'arrivée
                        s.fill(color)  #on colorie la surface de la couleur de la case (pour qu'elle n'apparaisse pas).
                        p.draw.circle(s, p.Color("chartreuse4"), (SQ_SIZE/2, SQ_SIZE/2), SQ_SIZE//3.5)  #et à la place, on dessine un rond sur cette surface (plus esthétique)
                        if gs.enPassant != () and move.pieceMoved[0] == "p" and move.endCol == gs.enPassant[-1][-1]:  #si on a affaire à un en-passant
                            s2 = p.Surface((SQ_SIZE, SQ_SIZE))  #on crée une deuxième surface
                            s2.set_alpha(150)  #valeur de "transparence" entre 0 et 255
                            s2.fill(p.Color("brown3"))  #qu'on va colorer en rouge
                            screen.blit(s2, (move.endCol * SQ_SIZE, move.startRow * SQ_SIZE))  #et afficher sous le pion pouvant être mangé
                        if move.pieceMoved[0] == "k":  #si la pièce bougée est un roi
                            for i in [-2, 2]:  #et que le mouvement possible est un roque
                                if 0 <= c+i <= 7:  #petite vérification obligatoire des limites du plateau
                                    Move = ChessEngine.Move(sqSelected, (r, c+i), gs.board)  #et qu'il est bel et bien possible
                                    if Move in validMoves:  #et qu'il est bel et bien possible
                                        p.draw.circle(s, p.Color("chartreuse2"), (SQ_SIZE/2, SQ_SIZE/2), SQ_SIZE//6)  # on ajoute un petit cercle vert au milieu de la surface
                                        screen.blit(s, ((c+i) * SQ_SIZE, r * SQ_SIZE))  #qu'on vient redessiner
                                        p.draw.circle(s, p.Color("chartreuse4"), (SQ_SIZE/2, SQ_SIZE/2), SQ_SIZE//3.5)  #on redessine le cercle vert de base par-dessus
                    else:  #si l'arrivée du mouvement est une case occupée par un ennemi
                        s.fill(p.Color("brown3"))  #on colore la surface en rouge
                    screen.blit(s, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))  #et on l'affiche sous la pièce ennemie


"""
Fonction pour dessiner les cases sur le plateau blanc. /!\ le coin en haut à gauche est blanc
"""


def drawBoard(screen):
    for r in range(DIMENSION):  # on parcourt les lignes (r->raw = rangée)
        for c in range(DIMENSION):  # on parcourt les colonnes dans la ligne
            color = squareColors[((r + c) % 2)]  # selon la case, on choisit une couleur
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE,
                                              SQ_SIZE))  # on crée une case de cette couleur au bon emplacement


"""
Fonction pour dessiner les pièces sur le plateau à l'aide de la fonction Gamestate.board
"""


def drawPieces(screen, board):
    for r in range(DIMENSION):  # on parcourt les lignes
        for c in range(DIMENSION):  # on parcourt les colonnes dans la ligne
            piece = board[r][
                c]  # selon la case, on choisit une pièce stockée dans la matrice ChessEngine.GameState.board
            if piece != "-_-":  # si la case n'est pas vide
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))  # on dessine la pièce


"""
Fonction qui va afficher une sélection de pièces pour améliorer un pion
"""


def drawChoice(screen, board, localisation):
    if localisation != ():  #si on a bien un pion qui a atteint sa dernière ligne
        row, col = localisation  #on récupère ses coordonnées
        player = board[row][col][2]  #on récupère la couleur du joueur
        color = p.Color("gray")  #on prend une couleur neutre pour afficher les choix d'améliorations dessus
        p.draw.rect(screen, color, p.Rect(2 * SQ_SIZE, 3 * SQ_SIZE, 4 * SQ_SIZE, SQ_SIZE))  #on dessine un rectangle de cette couleur

        # selon la couleur du joueur, on récupère les pièces possibles pour améliorer le pion (noires ou blanches).
        if player == "b":
            piece = ["q_b", "t_b", "c_b", "b_b"]
        else:
            piece = ["q_n", "t_n", "c_n", "b_n"]

        # on parcourt la liste sélectionnée pour afficher une par une les pièces possibles
        for i in range(4):
            screen.blit(IMAGES[piece[i]], p.Rect((2 + i) * SQ_SIZE, 3 * SQ_SIZE, SQ_SIZE, SQ_SIZE))

        choiceDone = False  #on crée une variable pour vérifier si le joueur a fait son choix
        while not choiceDone:  #on reste dans cette boucle while tant que ce n'est pas le cas
            for e in p.event.get():  #on parcourt les événements qui se produisent
                if e.type == p.QUIT:  #si le joueur veut quitter
                    p.quit()  #on ferme la fenêtre
                    exit()
                elif e.type == p.MOUSEBUTTONDOWN:  #si l'évènement est un clic
                    location = p.mouse.get_pos()  #on récupère ses coordonnées
                    col1 = location[0] // SQ_SIZE  #qu'on convertir en colonne
                    row1 = location[1] // SQ_SIZE  #et en ligne
                    if row1 == 3 and 2 <= col1 <= 5:  #et si le joueur a bien cliqué sur une des propositions
                        board[row][col] = piece[col1 - 2]  #on remplace le pion par la pièce choisie
                        choiceDone = True  #on bascule cette variable sur vrai ce qui est la condition de sortie de boucle
                        break
            p.display.flip()  # Cette ligne permet de rafraichir l'affichage continuellement, sans ça, les choix ne s'affiche que lorsque le joueur clique.


"""
animer un déplacement
"""


def animateMove(move, screen, board, clock):
    dR = move.endRow - move.startRow  #on récupère le nombre de lignes qu'on va devoir traverser
    dC = move.endCol - move.startCol  #on récupère le nombre de colonnes qu'on va devoir traverser
    framesPerSquare = 10  #nombres d'images pour passer un carré (1/6 de seconde à 60 fps)
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare  #on récupère (en valeur absolue) le nombre d'images nécessaires
    for frame in range(frameCount + 1):  #on crée une boucle for (qui est itérée 60 fois/secondes à la fin de celle-ci).
        r, c = (move.startRow + dR*frame/frameCount, move.startCol + dC*frame/frameCount)  #pour chaque frame (60ᵉ de seconde), on actualise la position
        drawBoard(screen)  #on doit redessiner le tableau
        drawPieces(screen, board)  #puis toutes les pièces
        # on doit effacer la pièce en position finale, car de base elle s'y retrouvait directement sans le délai de l'animation
        color = squareColors[(move.endRow + move.endCol) % 2]  #on reprend la couleur de la case sur laquelle elle se trouve
        endSquare = p.Rect(move.endCol*SQ_SIZE, move.endRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)  #on crée un carré à l'emplacement de la case d'arrivée
        p.draw.rect(screen, color, endSquare)  #qu'on vient redessiner par-dessus
        # redessiner la pièce capturée.
        if move.pieceCaptured != "-_-":  #si une pièce adverse est mangée
            screen.blit(IMAGES[move.pieceCaptured], endSquare)  #on la redessine, elle aussi le temps de l'animation
        # et redessiner la pièce qui se déplace.
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()  #on actualise l'écran à chaque passage dans la boucle
        clock.tick(60)  #on met bien le timer à 60 fps


def drawText(screen, text):
    font = p.font.SysFont("Helvitca", 32, True, False)
    textObject = font.render(text, 0, p.Color("black"))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - textObject.get_width()/2, HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)


if __name__ == "__main__":
    main()
