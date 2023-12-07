from LibUtils.cam_controller import cam_controller
from LibUtils.body_tracking import body_tracking
from LibUtils.hand_tracking import hand_tracking
from LibUtils.face_tracking import face_tracking

import multiprocessing, json

class blendshape_controller(object):
	terminate_process_shm = None
	controller_dict = {
		'cam_controller_obj': None
	}
	shm_dict = {
		'cam': None
	}
	framenum_dict = {}
	

	def __init__(self, cam_index=0):
		self.terminate_process_shm = multiprocessing.Value('i')
		self.terminate_process_shm.value = 1

		# Start Camera
		self.controller_dict['cam_controller_obj'] = cam_controller(self.terminate_process_shm, cam_index)
		self.controller_dict['cam_controller_obj'].run()
		self.shm_dict['cam'] = self.controller_dict['cam_controller_obj'].get_image_shm()

	def run_body_tracking(self):
		self.controller_dict['body_tracking_obj'] = body_tracking(self.terminate_process_shm, self.shm_dict['cam'])
		self.controller_dict['body_tracking_obj'].run()
		self.shm_dict['body'] = self.controller_dict['body_tracking_obj'].get_body_tracking()

	def run_hand_tracking(self):
		self.controller_dict['hand_tracking_obj'] = hand_tracking(self.terminate_process_shm, self.shm_dict['cam'])
		self.controller_dict['hand_tracking_obj'].run()
		self.shm_dict['hand'] = self.controller_dict['hand_tracking_obj'].get_hand_tracking()

	def run_face_tracking(self):
		self.controller_dict['face_tracking_obj'] = face_tracking(self.terminate_process_shm, self.shm_dict['cam'])
		self.controller_dict['face_tracking_obj'].run()
		self.shm_dict['face'] = self.controller_dict['hand_tracking_obj'].get_hand_tracking()

	# [[x,y,z,visibility,presence] x 33]
	def get_body_detections(self):
		if framenum_dict['body'] != self.shm_dict['body']['Frame_Num']:
			framenum_dict['body'] = self.shm_dict['body']['Frame_Num']
			return json.dumps(self.shm_dict['body']['Landmarks'])
		return '[]'
	# [L[[x,y,z] x 21], R[[x,y,z] x 21]]
	def get_body_detections(self):
		if framenum_dict['hand'] != self.shm_dict['hand']['Frame_Num']:
			framenum_dict['hand'] = self.shm_dict['hand']['Frame_Num']
			return json.dumps([self.shm_dict['hand']['Landmarks_Left'], self.shm_dict['hand']['Landmarks_Right']])
		return '[[],[]]'
	# [[[x,y,z]] x 478, [score x 52]]
	def get_face_detections(self):
		if framenum_dict['face'] != self.shm_dict['face']['Frame_Num']:
			framenum_dict['face'] = self.shm_dict['face']['Frame_Num']
			return json.dumps([self.shm_dict['face']['Landmarks'], self.shm_dict['face']['BlendShape']])
		return '[[],[]]'

	def terminate(self):
		self.terminate_process_shm.value = 0

		for key in controller_dict.keys():
			if controller_dict[key] is not None:
				controller_dict[key].end()