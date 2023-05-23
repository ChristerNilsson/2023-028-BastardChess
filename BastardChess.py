# TODO

import PySimpleGUI as sg
import chess
import chess.pgn
import chess.engine
import pyperclip
import subprocess

ENGINE = "C:/github/2023-018-Python-Chess_Evaluate/stockfish15/stockfish-windows-2022-x86-64-modern.exe"
BROWSER = "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
HELP = "https://github.com/ChristerNilsson/2023-028-BastardChess#bastardchess"
HEADER = ' Nr|  Vit  | Svart '.split('|')

CLUES = '0 123 1234 12345 234 2345 23456'.split(' ')
CLUE = "234" # Första index är ett. Bästa tre dragen visas förutom det bästa.

TIMES = [10,20,50,100,200,500,1000,2000] # milliseconds
TIME = 200 # thinking time

ORDERS = 'Alfabetisk Styrka'.split(' ')
ORDER = 'Alfabetisk'

PROMOS = 'Dam Torn Löpare Springare'.split(' ')
PROMO = 'Dam'

finalized = False
stack = [] # san moves for gui

BLANK = 0

window = None
initial_board = 'r n b q k b n r\np p p p p p p p\n. . . . . . . .\n. . . . . . . .\n. . . . . . . .\n. . . . . . . .\nP P P P P P P P\nR N B Q K B N R'

images = {
	'.':'blank',
	'p':'bp',
	'n':'bn',
	'b':'bb',
	'r':'br',
	'q':'bq',
	'k':'bk',
	'P':'wp',
	'N':'wn',
	'B':'wb',
	'R':'wr',
	'Q':'wq',
	'K':'wk'}

def render_square(image, key, location):
	color = '#B58863' if (location[0] + location[1]) % 2 else '#F0D9B5'
	return sg.RButton('', image_filename=image, image_size=(75, 75), image_subsample=2, size=(1, 1), button_color=('white', color), pad=(0, 0), key=key)

def redraw_board(window, board):
	b = [row.split(' ') for row in str(board).split("\n")]
	for i in range(8):
		for j in range(8):
			color = '#B58863' if (i + j) % 2 else '#F0D9B5'
			piece_image = './images/' + images[b[i][j]] + '.png'
			elem = window[(i, j)]
			elem.Update(button_color=('white', color), image_filename=piece_image, image_size=(75, 75), image_subsample=2, )

def hor(a,b): return [sg.Column([[a,b]])]

def makeHistory():
	pgn = []
	pgnpc = []
	for i in range(0, len(stack), 2):
		t = [str(i // 2 + 1), stack[i]]
		if i + 1 < len(stack): t.append(stack[i + 1])
		pgn.append(t)
		pgnpc.append(' '.join(t))
	pyperclip.copy("\n".join(pgnpc))
	return pgn

def PlayGame():
	global window, ORDER, TIME, CLUE, PROMO, finalized, stack

	def clues(engine, board):
		maximum = int(CLUE[-1])
		if maximum == 0: return []
		info = engine.analyse(board, chess.engine.Limit(time=TIME / 1000), multipv=maximum)
		n = len(info)
		best_moves = []
		for ch in CLUE:
			i = int(ch) - 1
			if len(best_moves) < n:
				best_moves.append(board.san(info[i]['pv'][0]))
		if ORDER == 'Alfabetisk': best_moves.sort()
		return best_moves

	b = [row.split(' ') for row in str(initial_board).split("\n")]
	board_layout = []
	for i in range(8):
		row = []
		for j in range(8):
			piece_image = './images/' + images[b[i][j]] + '.png'
			row.append(render_square(piece_image, key=(i, j), location=(i, j)))
		board_layout.append(row)

	engine = chess.engine.SimpleEngine.popen_uci(ENGINE)
	board = chess.Board()

	a = sg.Text('Sortering')
	b = sg.Combo(ORDERS, size=(10, 10), readonly=True, default_value=ORDER, key='_order_')

	d = sg.Text('Millisekunder')
	e = sg.Combo(TIMES, size=(8, 10), readonly=True, default_value=TIME, key='_TIME_')

	g = sg.Text('Ledtrådar')
	h = sg.Combo(CLUES, size=(10, 10), readonly=True, default_value=CLUE, key='_clue_')

	p1 = sg.Text('Promovering')
	p2 = sg.Combo(PROMOS, size=(10, 10), readonly=True, default_value=PROMO, key='_promo_')

	q1 = sg.Button('Hjälp')
	q2 = sg.Button('Ångra')

	r1 = sg.Button('Analys')
	r2 = sg.Button('Nytt parti')

	board_controls = [
		hor(a,b),
		hor(d,e),
		hor(p1,p2),
		hor(g,h),
		[sg.Text(' '.join(clues(engine,board)), size=(22, 2),  key='_clues_'),],
		[sg.Text('Tio senaste dragen')],
		[sg.Table(values = [], headings=HEADER,size=(10,10),key='_historik_',justification = "center", num_rows=10, hide_vertical_scroll=True)],
		hor(q1,q2),
		hor(r1,r2),
		[sg.Button('Avsluta')]
	]

	layout = [[sg.Column(board_layout), sg.Column(board_controls)]]

	window = sg.Window('Bastardschack',
	default_button_element_size=(10, 1),
	auto_size_buttons=False,
	font='Arial 16',
	icon='kingb.ico').Layout(layout)

	while not board.is_game_over():
		if finalized:
			window['_clues_'].Update(' '.join(clues(engine, board)))

		move_state = 0
		while True:
			button, value = window.Read()

			ORDER = value['_order_']
			TIME = value['_TIME_']
			PROMO = value['_promo_']
			CLUE = value['_clue_']

			if button in (None, 'Exit'): exit()
			if button == 'Avsluta':
				engine.quit()
				window.Close()
				return
			if button == 'Nytt parti':
				board = chess.Board()
				stack = []
				window['_clues_'].Update(' '.join(clues(engine,board)))
				window['_historik_'].Update('')
				redraw_board(window,board)
			if button == 'Hjälp':
				subprocess.Popen([BROWSER ,HELP])
				break
			if button == 'Analys':
				subprocess.Popen([BROWSER ,"https:\\lichess.org\paste"])
				break
			if button == 'Ångra':
				if len(stack) == 0: break
				board.pop()
				stack.pop()
				redraw_board(window,board)
				pgn = makeHistory()
				window['_historik_'].Update(pgn[-10:])
				# print(len(board.move_stack),len(stack))
				break
			if type(button) is tuple: # en av 64 rutor
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
						print(picked_move)

					if picked_move in [str(move) for move in board.legal_moves]:
						stack.append(board.san(chess.Move.from_uci(picked_move)))
						pgn = makeHistory()
						board.push(chess.Move.from_uci(picked_move))
					else:
						move_state = 0
						color = '#B58863' if (move_from[0] + move_from[1]) % 2 else '#F0D9B5'
						button_square.Update(button_color=('white', color))
						continue

					redraw_board(window, board)
					window['_historik_'].Update(pgn[-10:])
					finalized = True

					break

PlayGame()
