import sys
import numpy
import cv2
import time
import json

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

from player import Player

json_frames_extension = '.frames.json'

start_time = time.time()

source_file = sys.argv[1]
json_frames_file = "%s%s" % (source_file, json_frames_extension)

# Very cheap and unreliable argument parsing, but it'll work for our simple use cases
do_verify = len(sys.argv) > 2 and sys.argv[2] == '--verify'
from_json_frames = sys.argv[-1] == '--from-json-frames'

cap = None
json_frames = None

if from_json_frames:
	with open(json_frames_file) as f:
		json_frames = json.load(f)

	if do_verify:
		cap = cv2.VideoCapture(source_file)
else:
	cap = cv2.VideoCapture(source_file)

font = ImageFont.truetype(r'./prstartk_nes_tetris_8.ttf', 32)

font_size = 32

composite_color = (255, 0, 254, 255)

box_header_xy = (19, 24)
box_value_xy = (21, 58)

p1_line_count_xywh = (629, 235, 90, 28)
p1_score_xywh = (660, 81, 232, 35)
p1_level_xywh = (491, 1003, 59, 28)
p1_trt_box_xy = (451, 842)
p1_tls_box_xy = (451, 176)

p2_line_count_xywh = (1038, 235, 90, 28)
p2_score_xywh = (1069, 81, 232, 35)
p2_level_xywh = (1377, 1003, 59, 28)
p2_trt_box_xy = (1337, 842)
p2_tls_box_xy = (1337, 176)

trt_template = './trts_template.png'
box_template = './trt_box.png'

composite_base = Image.new('RGBA', (1920, 1080), composite_color)

trt_box_img = Image.open(box_template)
draw = ImageDraw.Draw(trt_box_img)
draw.text(box_header_xy, "TRT", (255,255,255), font=font)

tls_box_img = Image.open(box_template)
draw = ImageDraw.Draw(tls_box_img)
draw.text(box_header_xy, "TLS", (255,255,255), font=font)

player1 = Player(p1_line_count_xywh, p1_score_xywh, p1_level_xywh, p1_trt_box_xy, p1_tls_box_xy)
player2 = Player(p2_line_count_xywh, p2_score_xywh, p2_level_xywh, p2_trt_box_xy, p2_tls_box_xy)

players = [player1, player2]

output_file = "%s.trt.mp4" % source_file

if do_verify:
	output_file = "%s.verify.mp4" % source_file

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

if cap:
	total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
else:
	total_frames = len(json_frames)


def drawPlayerData(player, frame, frame_idx):
	label = player.getTRTLabel(frame_idx)

	trt_box = trt_box_img.copy()
	draw = ImageDraw.Draw(trt_box)
	draw.text(
		box_value_xy,
		label,
		(255,255,255,255),
		font=font
	)

	frame.paste(trt_box, player.trt_box_xy, trt_box)

	if do_verify:
		tls_box = tls_box_img.copy()
		draw = ImageDraw.Draw(tls_box)
		draw.text(
			box_value_xy,
			"%03d" % player.derived_data[frame_idx][1], # use a getter damnit!
			(255,255,255,255),
			font=font
		)

		frame.paste(tls_box, player.tls_box_xy, tls_box)


def drawBufferEntry(entry, tag):
	idx, frame = entry

	for player in players:
		drawPlayerData(player, frame, idx)

	frame = cv2.cvtColor(numpy.array(frame), cv2.COLOR_RGB2BGR)
	out.write(frame);

	print("Processed frame %d of %d (at %5.1f fps) (%s)" %
		(
			idx + 1,
			total_frames,
			(idx + 1) / (time.time() - frame_start),
			tag
		),
		end="\r"
	)


frame_buffer_size = 1 # dirty, make a config to synchronize with read delay instead - gee -_-
frame_buffer = []
frame_start = time.time()

if from_json_frames:
	for frame_idx, frame_data in enumerate(json_frames):
		if do_verify:
			cv2_retval, cv2_image = cap.read() # assumes read is successful, since json frames were generated from the source file
			cv2_image = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
			frame = Image.fromarray(cv2_image)
			trt_frame = frame
		else:
			trt_frame = composite_base

		for player_idx, player_frame_data in enumerate(frame_data):
			player = players[player_idx]
			player.setFrameData(player_frame_data)

		frame_buffer.append((frame_idx, trt_frame))

		if len(frame_buffer) > frame_buffer_size:
			drawBufferEntry(frame_buffer.pop(0), "json")

else:
	frame_idx = -1

	while True:
		cv2_retval, cv2_image = cap.read()

		if not cv2_retval:
			break

		frame_idx += 1

		cv2_image = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
		frame = Image.fromarray(cv2_image)

		if do_verify:
			trt_frame = frame
		else:
			trt_frame = composite_base

		for player in players:
			player.setFrame(frame)

		frame_buffer.append((frame_idx, trt_frame))

		if len(frame_buffer) > frame_buffer_size:
			drawBufferEntry(frame_buffer.pop(0), "ocr")


# adds last frames from buffer
while frame_buffer:
	drawBufferEntry(frame_buffer.pop(0), "")

out.release()

# Dump the OCRed values into a json file
with open(json_frames_file, "w+") as frames:
	json.dump(list(zip(player1.getFrames(), player2.getFrames())), frames)

print("\nDone - processed %d frames in %d seconds" % (total_frames, int(time.time() - start_time)))
