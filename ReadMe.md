This repo contains translation efforts for Zoids: Full Metal Crash. You will not find any distribution of the game itself or any of the text, translated or otherwise within this repo. It is purely for tools only.

ISO > Files: GCRebuilder

Note: Text is in png files, inside txd files, inside fpk files!

Files > ISO:
GCRebuilder can rebuild files to iso so long as the file sizes don't change (GC ISO Tool can too but only Files > Trimmed ISO)
(Both have CLI)

FPK > TXD, TXD > FPK
Use GNTool FPK Unpacker/Repacker (Wii!) to edit the fpks properly without changing file size 
(No CLI, but functions are open source Java)

TXD > PNG: Magic TXD

PNG > Translated PNG: ???

Translated PNG > TXD: Magic TXD
1. click 'new' to create a new txd file (or open an existing one)
2. Change 'Set' to Sonic Heroes (Gamecube)
3. click 'edit' and then add/replace to add a png to the txd file
4. Set 'raster format' to 'palettized' and select PAL8 in the dropdown to it's right
5. Set pixel format to RASTER_565
6. Click Add to add the png to the txd file
7. Click 'Edit' and 'Clear mip-levels' to change the levels to 1
8. File > 'Save as...'


Ponderings:
1. How do I edit the TXDs without changing file size? Does the way I edit it matter? is file size the only import factor here? if so, bring down file size below original by any means necessary. 

Answer: TXDs round to a multiple of 256kb. You need the new png to be close enough such that the txd is the same size. Easy to tell when you're wrong though, since you'll be off by a multiple of 256 KB. Doesn't seem to matter what you edit with, as you define the relevant metadata properties upon loading into magic txd.

2. Somebody on the internet mentioned not even repacking pngs... can I just leave them like that? Maybe the game unpacks at run time and then has paths to the pngs, so I could just make the file system match that. (would fuck with file size though...)

Answer: might work, but unlikely given the need for smaller or equal file size and same amount of files. More trouble than it's worth.


Notes: The scrolling text at the start of the game is a png broken up into each line as if it's a piece of paper cut with scissors into strips. Can work within this, but all text is likely treated this way. Aligning to the strips will be hard.