import sys
import numpy
import cv2
import time
import json

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

from player import Player

start_time = time.time()

source_file = sys.argv[1]

do_compose = len(sys.argv) > 2 and sys.argv[2] == '--compose'

cap = cv2.VideoCapture(source_file)

font = ImageFont.truetype(r'./prstartk_nes_tetris_8.ttf', 32)

font_size = 32

composite_color = (255, 0, 254, 255)

box_trt_header_xy = (19, 24)
box_trt_value_xy = (21, 58)

p1_line_count_xywh = (629, 235, 90, 28)
p1_score_xywh = (660, 81, 232, 35)
p1_level_xywh = (491, 1003, 59, 28)
p1_trt_box_xy = (451, 841)

p2_line_count_xywh = (1038, 235, 90, 28)
p2_score_xywh = (1069, 81, 232, 35)
p2_level_xywh = (1377, 1003, 59, 28)
p2_trt_box_xy = (1337, 841)

trt_template = './trts_template.png'
box_template = './trt_box.png'

composite_base = Image.new('RGBA', (1920, 1080), composite_color)

box_img = Image.open(box_template)
draw = ImageDraw.Draw(box_img)
draw.text(box_trt_header_xy, "TRT", (255,255,255), font=font)

player1 = Player(p1_line_count_xywh, p1_score_xywh, p1_level_xywh, p1_trt_box_xy)
player2 = Player(p2_line_count_xywh, p2_score_xywh, p2_level_xywh, p2_trt_box_xy)

players = [player1, player2]

output_file = "%s.trt.mp4" % source_file

if do_compose:
	output_file = "%s.composed.mp4" % source_file

print("Generating TRT from file\n%s\ninto overlay file\n%s" % (
	source_file,
	output_file
))

out = cv2.VideoWriter(
	output_file,
	cv2.VideoWriter_fourcc(*'mp4v'),
	23.976,
	(1920, 1080)
)

frame_count = 0
total_frames= cap.get(cv2.CAP_PROP_FRAME_COUNT)

frame_start = time.time()

while True:
	cv2_retval, cv2_image = cap.read()

	if not cv2_retval:
		break

	frame_count += 1

	cv2_image = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
	frame = Image.fromarray(cv2_image)

	if do_compose:
		trt_frame = frame
	else:
		trt_frame = composite_base

	for player in players:
		player.setFrame(frame)

		trt = player.getTRT()

		if trt == None:
			label = "---"
		elif trt >= 1:
			label = "100"
		else:
			label = "%02d%%" % round(trt * 100)

		trt_box = box_img.copy()
		draw = ImageDraw.Draw(trt_box)
		draw.text(
			box_trt_value_xy,
			label,
			(255,255,255,255),
			font=font
		)

		trt_frame.paste(trt_box, player.trt_box_xy, trt_box)

	trt_frame = cv2.cvtColor(numpy.array(trt_frame), cv2.COLOR_RGB2BGR)
	out.write(trt_frame);

	print("Processed frame %d of %d (at %5.1f fps)" % (frame_count, total_frames, frame_count / (time.time() - frame_start)), end="\r")

out.release()

frames_file = "%s.frames.json" % source_file

with open(frames_file, "w+") as frames:
	json.dump({
		"player1": player1.getFrames(),
		"player2": player2.getFrames(),
	}, frames)

print("\nDone - processed %d frames in %d seconds" % (frame_count, int(time.time() - start_time)))
