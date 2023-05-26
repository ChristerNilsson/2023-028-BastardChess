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

CLUES = '0 2 3-4 4-6 5-8'.split(' ')
CLUE = "3-4" # green:1-2 yellow:3-4 red:5-
LOW = 3
HIGH = 4

TIMES = [1,2,5,10,20,50,100,200,500] # milliseconds
TIME = 20 # thinking time

PROMOS = 'Dam Torn Löpare Springare'.split(' ')
PROMO = 'Dam'

finalized = False
stack = [] # [san, green/yellow/red]
mobility = []
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

def makeRow(index,n):
	res = []
	for i in range(n):
		s = str(index)+str(i)
		if i == 0:
			cell = sg.Button('', key=s, size=4, p=(0,0))
		else:
			cell = sg.Text('', key=s, size=7, background_color='black', p=(0,0))
		res.append(cell)
	return [sg.Column([res])]

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
	n = min(len(stack),20)
	# start = len(stack) - n # går mot stacken. historyStart går mot raderna.
	# if start % 2 == 1: start = start + 1
	# if start < 0: start = 0

	start = historyStart * 2

	for i in range(20): # rensa
		row = i // 2
		col = i % 2
		window[str(row) + str(col + 0)].Update('')
		window[str(row) + str(col + 1)].Update('')

	for i in range(n):
		row = i // 2
		col = i % 2
		if start+i < len(stack):
			[san,color] = stack[start + i]
			#if col==0: window[str(row) + str(col)].Update(start//2 + row + 1)  # nr
			if col==0: window[str(row) + str(col)].Update(start//2 + row + 1)  # nr
			window[str(row) + str(col+1)].Update(san, text_color=color)

def score(info):
	color = [False, True][len(stack) % 2]
	factor = [-1, 1][len(stack) % 2]
	value = info['score'].pov(color)
	if type(value) == chess.engine.Cp:
		score = value.cp * factor
	else:
		score = 10000 - value.mate() * factor
	return score

def get_score(item): return -item[0]
def get_san(item): return item[1]


def PlayGame():
	global window, TIME, CLUE, PROMO, finalized, stack, best_moves, historyStart

	def clues(engine, board):
		global info,LOW,HIGH,best_moves
		LOW = int(CLUE[0])
		HIGH = int(CLUE[-1])
		if HIGH == 0: return []
		info = engine.analyse(board, chess.engine.Limit(time=TIME / 1000), multipv=HIGH)
		n = len(info)

		best_moves = [[score(item),board.san(item['pv'][0])] for item in info]
		best_moves.sort(key=get_score)
		print('best',best_moves[0][1])
		yellow_moves = best_moves[LOW-1:n]
		yellow_moves.sort(key=get_san)
		return [move[1] for move in yellow_moves]

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
		hor(d,e),
		hor(p1,p2),
		hor(g,h),
		[sg.Text(' '.join(clues(engine,board)), size=(22, 2), key='_clues_', text_color='yellow')],
		[sg.Text('Tio senaste dragen')],
		[sg.Column([
			makeRow(0, 3),
			makeRow(1, 3),
			makeRow(2, 3),
			makeRow(3, 3),
			makeRow(4, 3),
			makeRow(5, 3),
			makeRow(6, 3),
			makeRow(7, 3),
			makeRow(8, 3),
			makeRow(9, 3),
			],background_color='black'
		)],
		hor(q1,q2),
		hor(r1,r2),
		[sg.Button('Avsluta')]
	]

	row = [
		sg.Text('Material: 0', key='_material_'),
		sg.Text('Mobilitet: 20', key='_mobilitet_'),
		sg.Text('Utvärdering: 0', key='_evaluation_'),
		sg.Text('Vit drar', key='_vidDraget_', text_color = 'white'),
	]
	board_layout.append(row)

	layout = [[ sg.Column(board_layout), sg.Column(board_controls)]]

	window = sg.Window('Bastardschack',
	default_button_element_size=(10, 1),
	auto_size_buttons=False,
	font='Arial 16',
	icon='kingb.ico').Layout(layout)

	while True:
		if finalized and not board.is_game_over():
			window['_clues_'].Update(' '.join(clues(engine, board)))

		move_state = 0
		while True:
			button, value = window.Read()
			print(button)

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
				window['_material_'].Update('Material: 0')
				window['_mobilitet_'].Update('Mobilitet: 20')
				window['_evaluation_'].Update('Utvärdering: 0')
				window['_vidDraget_'].Update('Vit drar', text_color='white')

				for i in range(20):
					row = i // 2
					col = i % 2
					window[str(row) + str(col + 0)].Update('')
					window[str(row) + str(col + 1)].Update('')

				redraw_board(window,board)
			if button == 'Hjälp':
				subprocess.Popen([BROWSER ,HELP])
				break
			if button == 'Analys':
				makeHistory()
				subprocess.Popen([BROWSER ,"https:\\lichess.org\paste"])
				break
			if button == 'Ångra':
				if len(stack) == 0: break
				board.pop()
				stack.pop()
				redraw_board(window,board)

				historyStart = (len(stack) + 1) // 2 - 10
				if historyStart < 0: historyStart = 0

				showStack()
				scorex = getScore(engine, board)
				window['_material_'].Update('Material: ' + str(material(board)))
				window['_mobilitet_'].Update('Mobilitet: ' + str(board.legal_moves.count()))
				window['_evaluation_'].Update('Utvärdering: ' + str(scorex))
				window['_vidDraget_'].Update(['Vit', 'Svart'][len(stack) % 2] + ' drar',text_color=['white', 'black'][len(stack) % 2])
				break
			if button == '00':
				if historyStart > 0: historyStart -= 1
				print("B00",historyStart)
				showStack()
			if button == '90':
				if historyStart < len(stack)//2 - 10: historyStart += 1
				print("B90",historyStart)
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
						picked_move += {'Dam':'q','Torn':'r','Löpare':'b','Springare':'n'}[PROMO]

					if picked_move in [str(move) for move in board.legal_moves]:
						scorex = getScore(engine,board)
						picked_san = board.san(chess.Move.from_uci(picked_move))

						index = 999
						for i in range(len(best_moves)):
							if best_moves[i][1] == picked_san: index = i

						if index+1 < LOW: color = 'green'
						elif LOW <= index+1 <= HIGH: color = 'yellow'
						else: color = 'red'

						stack.append([picked_san, color])
						board.push(chess.Move.from_uci(picked_move))

						historyStart = (len(stack)+1)//2 - 10
						if historyStart < 0: historyStart = 0

						window['_material_'].Update('Material: ' + str(material(board)))
						window['_mobilitet_'].Update('Mobilitet: ' + str(board.legal_moves.count()))
						window['_evaluation_'].Update('Utvärdering: ' + str(scorex))
						window['_vidDraget_'].Update(['Vit', 'Svart'][len(stack) % 2] + ' drar', text_color=['white', 'black'][len(stack) % 2])
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
