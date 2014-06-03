import ctypes
import socket
import ac
class TelemetryStructure(ctypes.Structure):
	def to_bytes(self):
		return (ctypes.c_char*ctypes.sizeof(self)).from_buffer_copy(self)
	
	def from_bytes(self,bytes):
		fit = min(len(bytes),ctypes.sizeof(self))
		ctypes.memmove(ctypes.addressof(self),bytes,fit)
		
class Handshaker(TelemetryStructure):
	_fields_ = [
		('identifier',ctypes.c_int),
		('version',ctypes.c_int),
		('operationId',ctypes.c_int),
	]
class HandshakerResponse(TelemetryStructure):
	_fields_ = [
		('carName',ctypes.c_char*50),
		('driverName',ctypes.c_char*50),
		('identifier',ctypes.c_int),
		('version',ctypes.c_int),
		('trackName',ctypes.c_char*50),
		('trackConfig',ctypes.c_char*50),
	]
class RTCarInfo(TelemetryStructure):
	_fields_ = [
		('identifier',ctypes.c_char),
		('size',ctypes.c_int),
		('speed_Kmh',ctypes.c_float),
		('speed_Mph',ctypes.c_float),
		('speed_Ms',ctypes.c_float),
		('isAbsEnabled',ctypes.c_bool),
		('isAbsInAction',ctypes.c_bool),
		('isTcInAction',ctypes.c_bool),
		('isTcEnabled',ctypes.c_bool),
		('isInPit',ctypes.c_bool),
		('isEngineLimiterOn',ctypes.c_bool),
		('accG_vertical',ctypes.c_float),
		('accG_horizontal',ctypes.c_float),
		('accG_frontal',ctypes.c_float),
		('lapTime',ctypes.c_int),
		('lastLap',ctypes.c_int),
		('bestLap',ctypes.c_int),
		('lapCount',ctypes.c_int),
		('gas',ctypes.c_float),
		('brake',ctypes.c_float),
		('clutch',ctypes.c_float),
		('engineRPM',ctypes.c_float),
		('steer',ctypes.c_float),
		('gear',ctypes.c_int),
		('cgHeight',ctypes.c_float),
		('wheelAngularSpeed',ctypes.c_float*4),
		('slipAngle',ctypes.c_float*4),
		('slipAngle_ContactPatch',ctypes.c_float*4),
		('slipRatio',ctypes.c_float*4),
		('tyreSlip',ctypes.c_float*4),
		('ndSlip',ctypes.c_float*4),
		('load',ctypes.c_float*4),
		('Dy',ctypes.c_float*4),
		('Mz',ctypes.c_float*4),
		('tyreDirtyLevel',ctypes.c_float*4),
		('camberRAD',ctypes.c_float*4),
		('tyreRadius',ctypes.c_float*4),
		('tyreLoadedRadius',ctypes.c_float*4),
		('suspensionHeight',ctypes.c_float*4),
		('carPositionNormalized',ctypes.c_float),
		('carSlope',ctypes.c_float),
		('carCoordinates',ctypes.c_float*3)
	]

class InternalTelemetryClient:
	def __init__(self):
		# Properties are the relevant fields from the received data
		self.abs_enabled = False
		self.abs_in_action = False
		self.tc_enabled = False
		self.tc_in_action = False
		self.in_pit = False
		self.limiter = False
		self.sock = None
		self.address = ('127.0.0.1',9996)
		self.handshake_done = False
		self.connected = False
	def connect(self):
		self.sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
		handshake_data = Handshaker(4,1,0)
		ctypes.string_at(ctypes.addressof(handshake_data),ctypes.sizeof(handshake_data))
		self.sock.sendto(handshake_data,self.address)
		ac.log("Sent :-)")
		self.connected = True
	def tick(self):
		if not self.connected:
			return
		data, server = self.sock.recvfrom(max(ctypes.sizeof(HandshakerResponse),ctypes.sizeof(RTCarInfo)))
		if not self.handshake_done:
			handshake = Handshaker(4,1,1)
			self.sock.sendto(handshake.to_bytes(),self.address)
			self.handshake_done = True
		else:
			raw_data = RTCarInfo()
			raw_data.from_bytes(data)
			self.abs_enabled = raw_data.isAbsEnabled
			self.abs_in_action = raw_data.isAbsInAction
			self.tc_enabled = raw_data.isTcEnabled
			self.tc_in_action = raw_data.isTcInAction
			self.in_pit = raw_data.isInPit
			self.limiter = raw_data.isEngineLimiterOn
	def disconnect(self):
		data = Handshaker(4,1,3)
		self.sock.sendto(data.to_bytes(),self.address)
		self.handshake_done = False
		self.connected = False