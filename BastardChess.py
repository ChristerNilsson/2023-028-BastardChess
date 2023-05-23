# TODO

# Visa initiala drag
# Se över promovering
# Dubbla bräden?

import PySimpleGUI as sg
import chess
import chess.pgn
import chess.engine
import pyperclip
import subprocess

URVAL = "234" # Första index är ett. Bästa tre dragen visas förutom det bästa.
SECONDS = 0.1 # thinking time
ORDER = 'Alfa'
PROMO = 'Dam'
BROWSER = "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"

finalized = False
stack = [] # san moves for gui

BLANK = 0

window = None
initial_board = 'r n b q k b n r\np p p p p p p p\n. . . . . . . .\n. . . . . . . .\n. . . . . . . .\n. . . . . . . .\nP P P P P P P P\nR N B Q K B N R'

blank   = './blank.png'

bishopB = './images/bb.png'
bishopW = './images/wb.png'
pawnB   = './images/bp.png'
pawnW   = './images/wp.png'
knightB = './images/bn.png'
knightW = './images/wn.png'
rookB   = './images/br.png'
rookW   = './images/wr.png'
queenB  = './images/bq.png'
queenW  = './images/wq.png'
kingB   = './images/bk.png'
kingW   = './images/wk.png'

images = {
	'.':blank,
	'p':pawnB,
	'n':knightB,
	'b':bishopB,
	'r':rookB,
	'q':queenB,
	'k':kingB,
	'P':pawnW,
	'N':knightW,
	'B':bishopW,
	'R':rookW,
	'Q':queenW,
	'K':kingW}

def render_square(image, key, location):
	color = '#B58863' if (location[0] + location[1]) % 2 else '#F0D9B5'
	return sg.RButton('', image_filename=image, image_size=(75, 75), image_subsample=2, size=(1, 1), button_color=('white', color), pad=(0, 0), key=key)

def redraw_board(window, board):
	b = [row.split(' ') for row in str(board).split("\n")]
	for i in range(8):
		for j in range(8):
			color = '#B58863' if (i + j) % 2 else '#F0D9B5'
			piece_image = images[b[i][j]]
			elem = window[(i, j)]
			elem.Update(button_color=('white', color), image_filename=piece_image, image_size=(75, 75), image_subsample=2, )

def clues(engine,board):
	global SECONDS, URVAL, ORDER, PROMO
	if not finalized: return []
	SECONDS = window['_seconds_'].get()
	URVAL = window['_urval_'].get()
	maximum = int(URVAL[-1])
	ORDER = window['_order_'].get()
	PROMO = window['_promo_'].get()

	info = engine.analyse(board, chess.engine.Limit(time=SECONDS), multipv=maximum)
	n = len(info)
	best_moves = []
	for ch in URVAL:
		i = int(ch)-1
		if len(best_moves) < n:
			best_moves.append(board.san(info[i]['pv'][0]))
	if ORDER == 'Alfa':
		best_moves.sort()
	return best_moves

def PlayGame():
	global window, SECONDS, finalized, stack

	b = [row.split(' ') for row in str(initial_board).split("\n")]
	board_layout = []
	for i in range(8):
		row = []
		for j in range(8):
			piece_image = images[b[i][j]]
			row.append(render_square(piece_image, key=(i, j), location=(i, j)))
		board_layout.append(row)

	filename = "C:/github/2023-018-Python-Chess_Evaluate/stockfish15/stockfish-windows-2022-x86-64-modern.exe"
	engine = chess.engine.SimpleEngine.popen_uci(filename)
	board = chess.Board()

	a = sg.Text('Sortering')
	b = sg.Combo(['Alfa','Styrka'], size=(10, 2), readonly=True, default_value=ORDER, key='_order_')
	c = sg.Column([[a,b]])
	d = sg.Text('Sekunder')
	e = sg.Combo([0.001,0.01,0.1,1], size=(10, 4), readonly=True, default_value=SECONDS, key='_seconds_')
	f = sg.Column([[d,e]])
	g = sg.Text('Ledtrådar')
	h = sg.Combo('123 1234 12345 234 2345 23456'.split(' '), size=(10, 6), readonly=True, default_value=URVAL, key='_urval_')
	k = sg.Column([[g,h]])
	p1 = sg.Text('Promovering')
	p2 = sg.Combo('Dam Torn Löpare Springare'.split(' '), size=(10, 4), readonly=True, default_value=PROMO, key='_promo_')
	p3 = sg.Column([[p1,p2]])
	board_controls = [
		[c],
		[f],
		[p3],
		[k],
		[sg.Text(' '.join(clues(engine,board)), size=(22, 2),  key='_clues_'),],
		[sg.Text('Historik')],
		[sg.Table(values = [], headings=['Nr',' White ',' Black '],size=(10,10),key='_historik_',justification = "center", hide_vertical_scroll=True)],

		[sg.Button('Hjälp')],
		[sg.Button('Analys')],
		[sg.Button('Nytt parti')],
		[sg.Button('Avsluta')],
	]

	layout = [[sg.Column(board_layout), sg.Column(board_controls)]]

	window = sg.Window('Bastardschack',
	default_button_element_size=(10, 1),
	auto_size_buttons=False,
	font='Arial 12',
	icon='kingb.ico').Layout(layout)

	while not board.is_game_over():

		SECONDS = window['_seconds_']

		if finalized:
			window['_clues_'].Update(' '.join(clues(engine, board)))

		move_state = 0
		while True:
			button, value = window.Read()
			if button in (None, 'Exit'): exit()
			if button == 'Avsluta':
				engine.quit()
				window.Close()
				return
			if button == 'Nytt parti':
				board = chess.Board()
				stack = []
				window['_clues_'].Update('')
				window['_historik_'].Update('')
				redraw_board(window,board)
			if button == 'Hjälp':
				subprocess.Popen([BROWSER ,"https:\\lichess.org\paste"])
				break
			if button == 'Analys':
				subprocess.Popen([BROWSER ,"https:\\lichess.org\paste"])
				break
			if type(button) is tuple:
				if move_state == 0:
					move_from = button
					row, col = move_from

					b = [row.split(' ') for row in str(board).split("\n")]
					piece = b[row][col]
					if piece in 'kqrbnp' and len(board.move_stack)%2==1 or piece in 'KQRBNP' and len(board.move_stack)%2==0:
						button_square = window[(button[0], button[1])]
						button_square.Update(button_color=('white', 'red'))
						move_state = 1
				elif move_state == 1:
					move_to = button
					row, col = move_to

					if move_to == move_from:  # cancelled move
						color = '#B58863' if (row + col) % 2 else '#F0D9B5'
						button_square.Update(button_color=('white', color))
						move_state = 0
						continue

					picked_move = '{}{}{}{}'.format('abcdefgh'[move_from[1]], 8 - move_from[0],
													'abcdefgh'[move_to[1]], 8 - move_to[0])

					if (piece == 'P' and 8 - move_to[0] == 8) or (piece == 'p' and 8 - move_to[0] == 1):
						picked_move += {'Dam':'q','Torn':'r','Löpare':'b','Springare':'n'}[PROMO]

					if picked_move in [str(move) for move in board.legal_moves]:
						stack.append(board.san(chess.Move.from_uci(picked_move)))
						pgn = []
						pgnpc = []
						for i in range(0,len(stack),2):
							t = [str(i // 2 + 1), stack[i]]
							if i+1 < len(stack): t.append(stack[i + 1])
							pgn.append(t)
							pgnpc.append(' '.join(t))
						pyperclip.copy("\n".join(pgnpc))
						board.push(chess.Move.from_uci(picked_move))
					else:
						move_state = 0
						color = '#B58863' if (move_from[0] + move_from[1]) % 2 else '#F0D9B5'
						button_square.Update(button_color=('white', color))
						continue

					redraw_board(window, board)

					window['_historik_'].Update(pgn)
					finalized = True

					break

PlayGame()
