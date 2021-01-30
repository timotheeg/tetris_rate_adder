from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

import numpy
import cv2

out = cv2.VideoWriter('project.avi', cv2.VideoWriter_fourcc(*'DIVX'), 15, (258, 126))
box = Image.open("trt_box.png");

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
