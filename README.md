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

# Millisekunder

Här anger man maximal tid som används för att utvärdera dragen.  
20 millisekunder per drag räcker utmärkt för att vinna över Hikaru-bot (2840) på chess.com  

# Promovering

Här anges vilken pjäs bonden ska förvandlas till.

# Ledtrådar

```
🟢🟢🟡🟡🔴🔴🔴🔴🔴🔴
```
* Man får veta det tredje och fjärde bästa draget.
* Gröna är hemliga. Lyckas man hitta något av dem visas draget med grönt.
* Misslyckas man visas draget med rött.

# Material

* Baserat på pjäsernas värde (1,3,5,9).
* Beräknas som Vit minus Svart.
* Visas till vänster om Hjälpknappen.

# Historik

* Här visas de senaste dragen. Färgerna visa dragets styrka.
* Man kan scrolla genom att klicka på översta/nedersta draget.
* I första kolumnen visas aktuellt halvdrag.
* I andra kolumnen visas draget
* I tredje kolumnen visas utvärdering.
* Därefter visas de fyra bästa dragen i fallande styrkeordning.

# Analys

* Dragen kopieras till klippbordet och man skickas till Lichess.  
* Där klistrar man in partiet och kan sedan analysera.  

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
* Det finns en javascriptversion av Stockfish, men den är komplicerad samt långsammare.
* När Web Assembly blir standard i browsern, kan detta program flyttas dit.