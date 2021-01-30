## Tetris Rate Adder

This project generates generates stats overlay video file from a TreyVision match rendering.

The program works on the following assumptions about the TreyVision files:
* They are all following the **exact** same layout (meaning the line count is always found at the same location)
* There is one match per file
* The line counter is "clean" -> always increases through the game, and only jumps by 1, 2, 3, or 4.


## Installation

(OSX instruction)

This was only tested in python 3.7.9

```bash
brew update
brew reinstall python@3.7
brew link --overwrite python@3.7
pip3 install -r requirements.txt
```

## Running:

From the chekcout folder, run:

```bash
python3 trt_movie.py <PATH_TO_TREYVISION_GAME_FILE>
```
