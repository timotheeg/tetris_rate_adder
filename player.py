from utils import xywh_to_ltrb
from digitocr import scoreImage

class Player:
	def __init__(self, read_loc_xywh, write_loc_xy):
		self.read_loc = xywh_to_ltrb(read_loc_xywh)
		self.write_loc = write_loc_xy
		self.line_clear_events = []
		self.tetris_line_count = 0
		self.total_line_count = None;
		self.has_been_valid = False

	def setFrame(self, frame):
		line_area = frame.crop(self.read_loc)
		line_count = scoreImage(line_area, "TDD")[1]

		self.setLineCount(line_count)

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

