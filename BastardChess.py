# TODO

# Spara till Github
# Visa vem som är vid draget. Färgad cirkel
# Gör visade drag valbara.

import PySimpleGUI as sg
import chess
import chess.pgn
import chess.engine
import pyperclip
import subprocess

URVAL = "123" # Första index är ett. Bästa tre dragen visas.
SECONDS = 0.1 # thinking time
ORDER = 'Alfa'
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
	if not finalized: return []
	SECONDS = window['_seconds_'].get()
	URVAL = window['_urval_'].get()
	maximum = int(URVAL[-1])
	ORDER = window['_order_'].get()
	info = engine.analyse(board, chess.engine.Limit(time=SECONDS), multipv=maximum)
	best_moves = []
	for ch in URVAL:
		i = int(ch)-1
		best_moves.append(' ' + board.san(info[i]['pv'][0]))
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

	board_controls = [
		[sg.Text('Sortering')],
		[sg.Combo(['Alfa','Styrka'], size=(10, 2), readonly=True, default_value=ORDER, key='_order_')],
		[sg.Text('Sekunder')],
		[sg.Combo([0.001,0.01,0.1,1], size=(10, 4), readonly=True, default_value=SECONDS, key='_seconds_')],
		[sg.Text('Ledtrådar')],
		[sg.Combo(['123','234','357'], size=(10, 4), readonly=True, default_value=URVAL, key='_urval_')],
		[sg.Text('\n'.join(clues(engine,board)), size=(10, 3), text_color='black', background_color='white', key='suggestions'),],
		[sg.Text('Historik')],
		[sg.Text('', size=(10, 3), text_color='black', background_color='white', key='_historik_')],
		[sg.Button('Hjälp')],
		[sg.Button('Analys')],
		[sg.Button('Nytt parti')],
		[sg.Button('Avsluta')],
	]

	layout = [[sg.Column(board_layout), sg.Column(board_controls)]]

	window = sg.Window('Bastardschack',
	default_button_element_size=(10, 1),
	auto_size_buttons=False,
	icon='kingb.ico').Layout(layout)

	while not board.is_game_over():

		SECONDS = window['_seconds_']

		if finalized:
			window['suggestions'].Update('\n'.join(clues(engine, board)))

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
				window['suggestions'].Update('')
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

					button_square = window[(row, col)]
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

					if piece == 'P' and 8 - move_to[0] == 8: picked_move += 'q'
					if piece == 'p' and 8 - move_to[0] == 1: picked_move += 'q'

					if picked_move in [str(move) for move in board.legal_moves]:
						stack.append(board.san(chess.Move.from_uci(picked_move)))
						pgn = []
						for i in range(0,len(stack),2):
							t = str(i//2+1) + ". " + stack[i]
							if i+1 < len(stack): t += ' ' + stack[i + 1]
							pgn.append(t)
						pyperclip.copy("\n".join(pgn))

						board.push(chess.Move.from_uci(picked_move))
					else:
						move_state = 0
						color = '#B58863' if (move_from[0] + move_from[1]) % 2 else '#F0D9B5'
						button_square.Update(button_color=('white', color))
						continue

					redraw_board(window, board)

					window['_historik_'].Update('\n'.join(pgn))
					finalized = True

					break

PlayGame()
