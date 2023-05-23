# BastardChess

* Det unika med BastardChess är att man får reda på några av de bästa dragen innan man gör sitt drag.  
* Detta är alltså en slags hybrid av hybridschack.  
* Meningen är att nya spelare snabbare ska få en känsla för vilka drag som är lämpliga.  
* Genom att det bästa draget utelämnas, uppmuntras man att leta efter det.  
* Hittar man inte det bästa draget, får man försöka välja det bästa draget av de föreslagna.  
* Tänk på att motståndaren har tillgång till samma information.  

# Stockfish är inte perfekt

* Framförallt är utvärdering av spelöppningar en svag punkt.  
* Att spelöppningar är vanliga medför inte automatiskt att de är bra.  
* T ex spelas alla tjugo möjliga öppningsdrag varje månad av mästare på Lichess.  
* Stockfish väljer inte samma drag varje gång.  
* Dessutom påverkas dragens kvalitet av hur lång tid som används.  

# Sortering

* Alfa: alfabetisk sortering (rekommenderas)
* Styrka: starkaste draget först

# Millisekunder

Här anger man hur mycket tid som ska användas för att utvärdera dragen.

# Promovering

Här anges vilken pjäs bonden ska förvandlas till.

# Ledtrådar

* 0: Inga ledtrådar
* 123: De tre starkast dragen
* 1234
* 12345
* 234: Man ser de tre starkaste dragen förutom det bästa.
* 2345
* 23456

# Analys

Dragen kopieras till klippbordet och man skickas till Lichess.  
Där klistrar man in partiet och kan sedan analysera.  

# Nytt parti

# Ångra

Efter tillstånd av motståndaren.

# Avsluta

# Installation

* Stockfish
* Python
* pip install PySimpleGUI
* pip install chess
* pip install pyperclip

# Varför finns inte detta program i närmaste browser?

* För att få prestanda mha Stockfish, vill man köra C++-versionen.
* Det finns en javascriptversion av Stockfish, men den är komplicerad att använda.
* När Web Assembly blir standard i browsern, kan detta program flyttas dit.