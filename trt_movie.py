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

font_size = 32

p1_line_count_xywh = (629, 235, 90, 28)
p1_score_xywh = (660, 81, 232, 35)
p1_level_xywh = (491, 1003, 59, 28)
p1_trt_header_xy = (470, 865)
p1_trt_value_xy = (472, 899)

p2_line_count_xywh = (1038, 235, 90, 28)
p2_score_xywh = (1069, 81, 232, 35)
p2_level_xywh = (1377, 1003, 59, 28)
p2_trt_header_xy = (1356, 865)
p2_trt_value_xy = (1358, 899)

trt_template = './trts_template.png'

frame_template = Image.open(trt_template)
draw = ImageDraw.Draw(frame_template)
font = ImageFont.truetype(r'./prstartk_nes_tetris_8.ttf', 32)

draw.text(p1_trt_header_xy, "TRT", (255,255,255), font=font)
draw.text(p2_trt_header_xy, "TRT", (255,255,255), font=font)

player1 = Player(p1_line_count_xywh, p1_score_xywh, p1_level_xywh, p1_trt_value_xy)
player2 = Player(p2_line_count_xywh, p2_score_xywh, p2_level_xywh, p2_trt_value_xy)

players = [player1, player2]

source_file = sys.argv[1]
output_file = "%s.trt.avi" % source_file

print("Generating TRT from file\n%s\ninto overlay file\n%s." % (
	source_file,
	output_file
))

cap = cv2.VideoCapture(source_file)
out = cv2.VideoWriter(
	output_file,
	cv2.VideoWriter_fourcc(*'DIVX'),
	23.976,
	(1920, 1080)
)

frame_count = 0

while True:
	cv2_retval, cv2_image = cap.read()

	if not cv2_retval:
		break

	frame_count += 1

	cv2_image = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
	frame = Image.fromarray(cv2_image)

	trt_frame = frame_template.copy()
	draw = ImageDraw.Draw(trt_frame)

	if frame_count % 250 == 0:
		print("Processing frame %d" % frame_count)

	for player in players:
		player.setFrame(frame)
		trt = player.getTRT()

		if trt == None:
			label = "---"
		elif trt >= 1:
			label = "100"
		else:
			label = "%02d%%" % round(trt * 100)

		draw.text(
			player.write_loc,
			label,
			(255,255,255),
			font=font
		)

	trt_frame = cv2.cvtColor(numpy.array(trt_frame), cv2.COLOR_RGB2BGR)
	out.write(trt_frame);

out.release()

frames_file = "%s.frames" % source_file

with file(frames_file, "w+") as frames:
	json.dump({
		"player1": player1.getFrames(),
		"player2": player2.getFrames(),
	}, frames)

print("\nDone - processed %d frames in %d seconds" % (frame_count, int(time.time() - start_time)))
