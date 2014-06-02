import mmap
import functools
import ctypes
from ctypes import c_int32, c_float, c_char, c_wchar, c_bool, c_int


AC_STATUS = c_int32
AC_OFF = 0
AC_REPLAY = 1
AC_LIVE = 2
AC_PAUSE = 3
AC_SESSION_TYPE = c_int32
AC_UNKNOWN = -1
AC_PRACTICE = 0
AC_QUALIFY = 1
AC_RACE = 2
AC_HOTLAP = 3
AC_TIME_ATTACK = 4
AC_DRIFT = 5
AC_DRAG = 6


class SPageFilePhysics(ctypes.Structure):
    _pack_ = 4
    _fields_ = [
        ('packetId' , c_int32),
        ('gas', c_float),
        ('brake', c_float),
        ('fuel', c_float),
        ('gear' , c_int32),
        ('rpms' , c_int32),
        ('steerAngle', c_float),
        ('speedKmh', c_float),
        ('velocity', c_float * 3),
        ('accG', c_float * 3),
        ('wheelSlip', c_float * 4),
        ('wheelLoad', c_float * 4),
        ('wheelsPressure', c_float * 4),
        ('wheelAngularSpeed', c_float * 4),
        ('tyreWear', c_float * 4),
        ('tyreDirtyLevel', c_float * 4),
        ('tyreCoreTemperature', c_float * 4),
        ('camberRAD', c_float * 4),
        ('suspensionTravel', c_float * 4),
        ('drs', c_float),
        ('tc', c_float),
        ('heading', c_float),
        ('pitch', c_float),
        ('roll', c_float),
        ('cgHeight', c_float),
        ('carDamage', c_float * 5),
        ('numberOfTyresOut' , c_int32),
        ('pitLimiterOn' , c_int32),
        ('abs', c_float),
    ]


class SPageFileGraphic(ctypes.Structure):
    _pack_ = 4
    _fields_ = [
        ('packetId' , c_int32),
        ('status', AC_STATUS),
        ('session', AC_SESSION_TYPE),
         # NOTE: if you want str instead bytes, access it without '_'
        ('_currentTime', c_char * 10),
        ('_lastTime', c_char * 10), 
        ('_bestTime', c_char * 10),
        ('_split', c_char * 10),
        ('completedLaps' , c_int32),
        ('position' , c_int32),
        ('iCurrentTime' , c_int32),
        ('iLastTime' , c_int32),
        ('iBestTime' , c_int32),
        ('sessionTimeLeft', c_float),
        ('distanceTraveled', c_float),
        ('isInPit' , c_int32),
        ('currentSectorIndex' , c_int32),
        ('lastSectorTime' , c_int32),
        ('numberOfLaps' , c_int32),
        ('_tyreCompound', c_char * 32),

        ('replayTimeMultiplier', c_float),
        ('normalizedCarPosition', c_float),
        ('carCoordinates', c_float * 3),
    ]


class SPageFileStatic(ctypes.Structure):
    _pack_ = 4
    _fields_ = [
        ('_smVersion', c_char * 10),
        ('_acVersion', c_char * 10),
        # session static info
        ('numberOfSessions' , c_int32),
        ('numCars' , c_int32),
        ('_carModel', c_char * 32),
        ('_track', c_char * 32),
        ('_playerName', c_char * 32),
        ('_playerSurname', c_char * 32),
        ('_playerNick', c_char * 32),
        ('sectorCount' , c_int32),

        # car static info
        ('maxTorque', c_float),
        ('maxPower', c_float),
        ('maxRpm' , c_int32),
        ('maxFuel', c_float),
        ('suspensionMaxTravel', c_float * 4),
        ('tyreRadius', c_float * 4),
    ]

#make _char_p properties return unicode strings
for cls in (SPageFilePhysics, SPageFileGraphic, SPageFileStatic):
    for name, typ in cls._fields_:
        if name.startswith("_"):
            def getter(self, name=None):
                value = getattr(self, name)
                # TODO: real encoding is very strange, it's not utf-8
                return value.decode("utf-8")
            setattr(cls, name.lstrip("_"), 
                    property(functools.partial(getter, name=name)))


class SimInfo:
    def __init__(self):
        self._acpmf_physics = mmap.mmap(0, ctypes.sizeof(SPageFilePhysics), "acpmf_physics")
        self._acpmf_graphics = mmap.mmap(0, ctypes.sizeof(SPageFileGraphic), "acpmf_graphics")
        self._acpmf_static = mmap.mmap(0, ctypes.sizeof(SPageFileStatic), "acpmf_static")
        self.physics = SPageFilePhysics.from_buffer(self._acpmf_physics)
        self.graphics = SPageFileGraphic.from_buffer(self._acpmf_graphics)
        self.static = SPageFileStatic.from_buffer(self._acpmf_static)

    def close(self):
        self._acpmf_physics.close()
        self._acpmf_graphics.close()
        self._acpmf_static.close()

    def __del__(self):
        self.close()


def demo():
    import time
    
    info = SimInfo()
    for _ in range(400):
        print(info.static.track, info.graphics.tyreCompound, 
              info.physics.rpms, info.graphics.currentTime)
        time.sleep(0.1)


if __name__ == '__main__':
    demo()
