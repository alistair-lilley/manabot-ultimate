# To do!

## Core goals

- Telegram interface
- Discord interface
- Run both interfaces simultaneously
- Have it post cards (image + textual data) 
- Have it post rules (by number)
- Have it post rules (by keyword)
- Potential option: post rulings for specific cards

## Underlying structure

- Telegram interface
- Discord interface
- Combined bot object (with both interfaces)
- A card database object (read from json); parsed as cards
- A card object (read from json; card images as urls)
- A rules database object (read from txt); parsed as tree