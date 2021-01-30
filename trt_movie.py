import sys

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

import numpy
import cv2

from utils import xywh_to_ltrb

font_size = 32

p1_line_count_xywh = (629, 235, 90, 28)
p1_trt_header_xy = (475, 865)
p1_trt_value_xy = (475, 865)

p2_line_count_xywh = (1038, 235, 90, 28)
p2_trt_header_xy = (1361, 865)
p2_trt_value_xy = (1361, 865)

trt_template = './trts_template.png'

source_file = sys.argv[1]
output_file = "%s.trt.avi" % source_file

cap = cv2.VideoCapture(source_file)

frame_count = 0

while True:
	cv2_retval, cv2_image = cap.read()

	if not cv2_retval:
		break


	frame_count += 1

	cv2_image = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)

	frame = Image.fromarray(cv2_image)

	if frame_count < 500:
		continue

	p1_lines_img = frame.crop(xywh_to_ltrb(p1_line_count_xywh))
	p2_lines_img = frame.crop(xywh_to_ltrb(p2_line_count_xywh))

	p1_lines_img.show()
	p2_lines_img.show()
	frame.show()

	break







'''
out = cv2.VideoWriter(output_file, cv2.VideoWriter_fourcc(*'DIVX'), 15, (258, 126))
box = Image.open(trt_template);

for n in range(1, 100):
	img = box.copy();
	draw = ImageDraw.Draw(img)
	font = ImageFont.truetype(r'./prstartk_nes_tetris_8.ttf', 32, )
	draw.text(
	 	(85, 69),
	 	"%d%%" % n,
	 	(255,255,255),
	 	font=font
	 ) # this will draw text with Blackcolor and 16 size

	frame = cv2.cvtColor(numpy.array(img), cv2.COLOR_RGB2BGR)

	out.write(frame);

out.release()
'''
