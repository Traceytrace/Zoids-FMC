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


Workflow:
folders:
- iso_dump directory with all the original file structure. fpks are in here and are used as the base for repacking translated content.
- directory "unpacked fpks" with original GC structure containing folders instead of fpks, those folders have same name as fpk but contain the contents of the fpks. Each "fpk folder" contains a folder "original" and "translated" which both contain the contents of the fpks but all at the root of the folder (so no "ory, story and story00_00") but one is left untouched e.g. unpacked_fpks/story/story00_00_fpk/original/bg_00.txd. pngs sit next to their associated txd files while they exist.
- iso_dump_translated directory with original FS. this is the save location of repacked fpks and the source for builds of the test.iso
- original.iso is an iso of the game that is unaltered
- test.iso is the built iso containing edited (translated) content

Ideal world:
1. window pops up with original png side by side with live edited png. there is a field to type text into the live png. (need to     build translation hub)
    clicking a button saves the translated png and goes to next png

2. magic txd builds all translated pngs into txds (pyautogui w/magic txd's mass build)

3. gntool packs those into fpks (get java functions out of source code to automate this? or worst case, use pyautogui again)

4. swap replace fpks in root with their translated counterparts and gc_fst builds iso.

5. test in-game.


Notes: The scrolling text at the start of the game is a png broken up into each line as if it's a piece of paper cut with scissors into strips. Can work within this, but all text is likely treated this way. Aligning to the strips will be hard.


Todo:
- use pyautogui [https://github.com/asweigart/pyautogui] to automate the mass build of pngs into txds 
- somehow automate fpk unpacker from gntool (it's open source... maybe use their java functions? else maybe pyautogui again...)