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

N = 12 # antal visade rader
LOW = 3
HIGH = 4

TIMES = [1,2,5,10,20,50,100,200,500,1000,2000,5000] # milliseconds
TIME = 200 # thinking time

PROMOS = 'Queen Rook Bishop Knight'.split(' ')
PROMO = 'Queen'

finalized = False
stack = [] # [[san,score,1,2,3,4]]
historyStart = 0

info = []
best_moves = []

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
def hor4(a,b,c,d): return [sg.Column([[a,b,c,d]])]
def hor5(a,b,c,d,e): return [sg.Column([[a,b,c,d,e]])]
def hor6(a,b,c,d,e,f): return [sg.Column([[a,b,c,d,e,f]])]

def makeRow(index,n):
	res = []
	for i in range(n):
		s = str(index)+str(i)
		if i == 0:
			cell = sg.Button('', key=s, size=4, p=(0,0))
		else:
			cell = sg.Text('', key=s, size=7, background_color='black', p=(0,0), justification='center')
		res.append(cell)
	return [sg.Column([res], background_color='black')]

def makeHistory():
	pgn = []
	n = len(stack)
	for i in range(0,n,2):
		t = [str(i//2+1), stack[i][0]]
		if i + 1 < n:
			t.append(stack[i + 1][0])
		else:
			t.append('')
		pgn.append(' '.join(t))
	pyperclip.copy("\n".join(pgn))

def material(board):
	res = 0
	hash = {'.':0,'k':0,'r':-5,'q':-9,'b':-3,'n':-3,'p':-1,'K':0,'R':5,'Q':9,'B':3,'N':3,'P':1}
	b = [row.split(' ') for row in str(board).split("\n")]
	for i in range(8):
		for j in range(8):
			res += hash[b[i][j]]
	return res

def getScore(engine,board):
	color = [False, True][len(stack) % 2]
	factor = [-1, 1][len(stack) % 2]
	info = engine.analyse(board, chess.engine.Limit(time=TIME / 1000))
	value = info['score'].pov(color)
	if type(value) == chess.engine.Cp:
		score = value.cp * factor
	else:
		score = '#' + str(value.mate() * factor)
	return score

def showStack():
	n = min(len(stack),N)
	start = historyStart

	for i in range(N): # rensa
		for j in range(7):
			window[str(i) + str(j)].Update('')

	for i in range(n):
		if start+i < len(stack):
			item = stack[start + i] # e4 27 d4 e4 Nf3 Nc3
			window[str(i) + '0'].Update(historyStart + i + 1)  # nr

			index = 4
			for k in range(len(item)-2):
				if item[0] == item[k + 2]: index = k # 0 to 3. 4 if red

			color = ['green', 'green', 'yellow', 'yellow', 'red'][index]
			if (historyStart+i)%2==0:
				window[str(i) + '1'].Update(item[0]+'   •', text_color=color)
			else:
				window[str(i) + '1'].Update('•   '+item[0], text_color=color)

			window[str(i) + '2'].Update(item[1])

			for j in range(len(item)-2):
				if j==index:
					window[str(i) + str(j+3)].Update(item[j+2],text_color='white')
				else:
					window[str(i) + str(j+3)].Update(item[j+2],text_color='gray')

def score(info):
	color = [False, True][len(stack) % 2]
	factor = [-1, 1][len(stack) % 2]
	value = info['score'].pov(color)
	if type(value) == chess.engine.Cp:
		score = value.cp * factor
	else:
		score = 10000 - value.mate() * factor
	return score

def get_white_score(item): return item[0]
def get_black_score(item): return -item[0]
def get_san(item): return item[1]


def PlayGame():
	global window, TIME, PROMO, finalized, stack, best_moves, historyStart

	def clues(engine, board):
		global info,LOW,HIGH,best_moves
		info = engine.analyse(board, chess.engine.Limit(time=TIME / 1000), multipv=HIGH)
		n = len(info)
		if n==0: return ''
		best_moves = [[score(item), board.san(item['pv'][0])] for item in info if len(item)>5]
		if len(stack)%2==1:
			best_moves.sort(key=get_white_score)
		else:
			best_moves.sort(key=get_black_score)
		print(' '.join([move[1] for move in best_moves]), ' '.join([str(move[0]) for move in best_moves]))
		yellow_moves = best_moves[LOW-1:n]
		yellow_moves.sort(key=get_san)
		return '       '.join([move[1] for move in yellow_moves])

	def showHints():
		xx = clues(engine, board)
		if len(stack) % 2 == 1:
			window['_upperHint_'].Update(xx)
			window['_lowerHint_'].Update('')
		else:
			window['_upperHint_'].Update('')
			window['_lowerHint_'].Update(xx)

	b = [row.split(' ') for row in str(initial_board).split("\n")]
	board_layout = []
	row = [sg.Text('', key='_upperHint_', text_color = 'yellow', size=55, justification='center')]
	board_layout.append(row)

	for i in range(8):
		row = [sg.Text(8-i)]
		for j in range(8):
			piece_image = './images/' + images[b[i][j]] + '.png'
			row.append(render_square(piece_image, key=(i, j), location=(i, j)))
		board_layout.append(row)
	row = [sg.Text(' ',p=7)]
	for j in range(8):
		row.append(sg.Text("abcdefgh"[j], size=5, p=7, justification='center'))
	board_layout.append(row)

	engine = chess.engine.SimpleEngine.popen_uci(ENGINE)
	board = chess.Board()

	d = sg.Text('Time:')
	e = sg.Combo(TIMES, size=(5, 10), readonly=True, default_value=TIME, key='_TIME_')
	f = sg.Text('ms')

	p1 = sg.Text('                           Promotion:')
	p2 = sg.Combo(PROMOS, size=(8, 10), readonly=True, default_value=PROMO, key='_promo_')

	q0 = sg.Text('0', key='_material_')
	q1 = sg.Button('Help')
	q2 = sg.Button('Undo')

	r1 = sg.Button('Analyze')
	r2 = sg.Button('New')
	r3 = sg.Button('Close')

	board_controls = [
		hor5(d,e,f,p1,p2),
		[sg.Column([
			makeRow(0, 7),
			makeRow(1, 7),
			makeRow(2, 7),
			makeRow(3, 7),
			makeRow(4, 7),
			makeRow(5, 7),
			makeRow(6, 7),
			makeRow(7, 7),
			makeRow(8, 7),
			makeRow(9, 7),
			makeRow(10, 7),
			makeRow(11, 7),
			],background_color='black'
		)],
		hor6(q0,q1,q2,r1,r2,r3),
	]

	row = [sg.Text(clues(engine,board), key='_lowerHint_', text_color = 'yellow', size=55, justification='center')]
	board_layout.append(row)

	layout = [[ sg.Column(board_layout), sg.Column(board_controls)]]

	window = sg.Window('Bastard Chess',
	default_button_element_size=(8, 1),
	auto_size_buttons=False,
	font='Arial 16',
	icon='kingb.ico').Layout(layout)

	while True:
		if finalized and not board.is_game_over():
			pass

		move_state = 0
		while True:
			button, value = window.Read()

			TIME = value['_TIME_']
			PROMO = value['_promo_']

			if button in (None, 'Exit'): exit()
			if button == 'Close':
				engine.quit()
				window.Close()
				return
			if button == 'New':
				board = chess.Board()
				stack = []
				window['_material_'].Update('0')

				for i in range(N):
					for j in range(7):
						window[str(i) + str(j)].Update('')

				redraw_board(window,board)
				showHints()

			if button == 'Help':
				subprocess.Popen([BROWSER ,HELP])
				break
			if button == 'Analyze':
				makeHistory()
				subprocess.Popen([BROWSER ,"https:\\lichess.org\paste"])
				break
			if button == 'Undo':
				if len(stack) == 0: break
				board.pop()
				stack.pop()
				redraw_board(window,board)

				historyStart = len(stack) - N
				if historyStart < 0: historyStart = 0

				showStack()
				showHints()

				window['_material_'].Update(str(material(board)))
				break
			if button == '00':
				if historyStart > 0: historyStart -= 1
				print("B00",historyStart)
				showStack()
			if button == '110':
				if historyStart < len(stack) - N: historyStart += 1
				print("B110",historyStart)
				showStack()
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
						picked_move += {'Queen':'q','Rook':'r','Bishop':'b','Knight':'n'}[PROMO]

					if picked_move in [str(move) for move in board.legal_moves]:
						picked_san = board.san(chess.Move.from_uci(picked_move))
						board.push(chess.Move.from_uci(picked_move))
						scorex = getScore(engine,board)
						stack.append([picked_san,scorex] + [move[1] for move in best_moves])
						print(picked_san,scorex)

						historyStart = len(stack) - N
						if historyStart < 0: historyStart = 0

						window['_material_'].Update(str(material(board)))
						showHints()
						makeHistory()
					else:
						move_state = 0
						color = '#B58863' if (move_from[0] + move_from[1]) % 2 else '#F0D9B5'
						button_square.Update(button_color=('white', color))
						continue

					redraw_board(window, board)
					showStack()

					finalized = True
					break

PlayGame()
