from utils import xywh_to_ltrb
from digitocr import scoreImage

class Player:
	def __init__(self, lines_loc_xywh, score_loc_xywh, level_loc_xywh, trt_write_loc_xy):
		self.lines_loc = xywh_to_ltrb(lines_loc_xywh)
		self.score_loc = xywh_to_ltrb(score_loc_xywh)
		self.level_loc = xywh_to_ltrb(level_loc_xywh)

		self.trt_write_loc = trt_write_loc_xy

		self.frames = []
		self.line_clear_events = []

		self.tetris_line_count = 0
		self.total_line_count = None;
		self.has_been_valid = False

	def setFrame(self, frame):
		lines_img = frame.crop(self.lines_loc)
		lines = scoreImage(lines_img, "TDD")[1]

		score_img = frame.crop(self.score_loc)
		score = scoreImage(score_img, "DDDDDD")[1]

		level_img = frame.crop(self.level_loc)
		level = scoreImage(level_img, "TD")[1]

		self.frames.append((lines, score, level))
		self.setLineCount(lines)

	def getFrames(self):
		return self.frames

	def setLineCount(self, line_count):
		if line_count == self.total_line_count:
			return

		if line_count == None or line_count == 0:
			self.total_line_count = None
			return

		lines = line_count - (self.total_line_count or 0)
		self.total_line_count = line_count

		if lines == 4:
			self.tetris_line_count += 4

		self.line_clear_events.append({
			"lines": lines,
			"trt": self.tetris_line_count / self.total_line_count
		})

	def getTRT(self):
		if self.total_line_count == None:
			return None

		return self.tetris_line_count / self.total_line_count

	def getTRTLabel(self):
		pass

