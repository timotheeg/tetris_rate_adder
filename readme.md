## Tetris Rate Adder

This project generates stats overlay video file from a TreyVision match rendering. Specifically, adding the Tetris rate where it was missing.

Example of an overlay frame:
![Sample Overlay frame](./sample_overlay_frame.png)


The program works on the following assumptions about the TreyVision files:
* They are all following the **exact** same layout (meaning the line count is always found at the same location)
* The line counter is "clean" -> always increases through the game, and only jumps by 1, 2, 3, or 4.

The Tetris Rate (TRT) can be computed entirely from the lines counter. In a game, the line counter can increase by 1 (for singles), 2 (for doubles), 3 (for triples), and 4 (for tetrises). By cumulating the +4 jumps, the programs aggregates the total number of lines cleared in tetrises, and the Tetris rate forumla is:
```
lines_cleared_in_tetrises / total_lines_cleared
```

In any Tetris game, the Line counter is a "stable" metric in screen. That means it stays constant over many consecutive frames, since it is impossible for a player to clear lines on consecutive frames (one must account for the time a give Tetris piece takes to fall to the bottom).

While the line count is stable, when it does changes, we have seen in the edited TreyVision footage that "fuzzy" frames crept their way in. When the count values changes, it blurs and resulting in incorrect read of the new count, which eventualy leads to an incorrect Tetris Rate computation. To work around this problem, any detected change to the line count will wait one frame to do the actual read of the "real" value. This works thanks to the stability of the metric, as described above.

The read delay could easily be increased to 2 or 3 frames as needed, should the transition fuzziness affect multiple consecutive frames.

Example of a fuzzy frame on line clear
![Fuzzy Frame](./fuzzy_frame.png)




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

Running that command wil generated an overlay file with 2 addition TRT boxes, that can be composited later over the game footage. The file name for the overlay will be:
```
<PATH_TO_TREYVISION_GAME_FILE>.trt.mp4
```

### QA and verification

Looking at the overlay alone, it is very hard to know if the value of the TRT are correct since the gameplay is not visible. Doing the compositing job manually to validate accuracy of the value is quite laborious and slow.

Additionally, even after composition, looking at the game and tetris rate, only partial validation can easily be done. That is because, while one caneasily verify that tetrises do indeed raise the tetris rate, while every other type of line clears  decreases it, but does one know for sure that the TRT value is correct?

As described above the TRT value is simply all the lines cleared in tetrises divided by all the lines cleared in total (then times 100 to make it a percent), The total line count is already visible in the TreyVision UI in the box LINE, and so to validate the Tetris rate, one needs to compute the total lines cleared in tetrises. It is possible to do this by hand, but that would be slow and laborious.

To solve both of these problem, the tool can be run in a verification mode like this:
```bash
python3 trt_movie.py <PATH_TO_TREYVISION_GAME_FILE> --verify
```

Instead of generating just the overlay, that command outputs the original game frames with the Tetris rate boxes already composited into them, AND an additional data box for each player labelled `TLS` (for **T**etris **L**ine**S**). That TLS box cumulates the lines cleared in tetrises.

To then verify the footage, one can watch the video and verify that:
1. The tetris lines counter only increase for tetrises and always increases by 4
2. The computed `TRT` is indeed the divion of `TLS` over `LINE`


When verification is done, the TRT overlay can then be computed by running a second command:
```bash
python3 trt_movie.py <PATH_TO_TREYVISION_GAME_FILE> --from-json-frames
```

Running this second step is much faster, because it uses the frame data from a json file produced by the first command, and does not have to read the source file and ocr again 👍!

Verification mode
![Verification mode](./verify_mode.png)
