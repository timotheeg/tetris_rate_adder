from utils import xywh_to_ltrb
from digitocr import scoreImage

FRAMES_READ_DELAY = 1

class Player:
	def __init__(self, lines_loc_xywh, score_loc_xywh, level_loc_xywh, trt_box_xy, ocr_box_xy, tls_box_xy):
		self.lines_loc = xywh_to_ltrb(lines_loc_xywh)
		self.score_loc = xywh_to_ltrb(score_loc_xywh)
		self.level_loc = xywh_to_ltrb(level_loc_xywh)

		self.trt_box_xy = trt_box_xy
		self.ocr_box_xy = ocr_box_xy
		self.tls_box_xy = tls_box_xy

		self.frames = []
		self.derived_data = []

		self.remaining_delay_frames = 0 # controls one frame delay to read line count

		self.tetris_line_count = 0
		self.total_line_count = None

	def setFrame(self, frame):
		lines_img = frame.crop(self.lines_loc)
		lines = scoreImage(lines_img, "TDD")[1]

		#score_img = frame.crop(self.score_loc)
		#score = scoreImage(score_img, "DDDDDD")[1]

		#level_img = frame.crop(self.level_loc)
		#level = scoreImage(level_img, "TD")[1]

		score = level = 0

		self.setFrameData((lines, score, level))

	def setFrameData(self, values): # lines, score, level
		self.frames.append(values)
		self.setLineCount(values[0])

	def getFrames(self):
		return self.frames

	def setLineCount(self, line_count):
		self.derived_data.append((
			line_count,
			self.tetris_line_count,
		))

		if line_count == self.total_line_count:
			return

		if self.remaining_delay_frames <= 0:
			self.remaining_delay_frames = FRAMES_READ_DELAY
			return

		self.remaining_delay_frames -= 1

		if self.remaining_delay_frames > 0:
			return

		if line_count == None or line_count == 0:
			self.tetris_line_count = 0

		else:
			lines = line_count - (self.total_line_count or 0)

			if lines < 0 or lines > 4:
				print('WARNING: Invalid line jump detected: %d lines at frame %d\n' % (lines, len(self.derived_data)))

			if lines == 4:
				self.tetris_line_count += 4

		self.total_line_count = line_count
		derived_values = (self.total_line_count, self.tetris_line_count)

		# Backfill all the frame data
		for delayed_frame_idx in range(FRAMES_READ_DELAY + 1):
			self.derived_data[-1 * delayed_frame_idx - 1] = derived_values

	def getTRTLabel(self, frame_idx):
		total_line_count, tetris_line_count = self.derived_data[frame_idx]

		if total_line_count == None:
			label = ""
		elif total_line_count == 0:
			label = "---"
		else:
			trt = tetris_line_count / total_line_count

			if trt >= 1:
				label = "100"
			else:
				label = "%02d%%" % round(trt * 100) # should this be floor insted of round?

		return label
