from ctypes import Structure, c_float, c_uint8
from enum import IntEnum

# structures.h
class Vector2(Structure): _fields_ = [("x", c_float), ("y", c_float)]
class Vector3(Structure): _fields_ = [("x", c_float), ("y", c_float), ("z", c_float)]
class Quat(Structure): _fields_ = [("x", c_float), ("y", c_float), ("z", c_float), ("w", c_float)]
class Transform(Structure): _fields_ = [("quat", Quat), ("location", Vector3), ("scale", Vector3)]
class Color(Structure): _fields_ = [("r", c_uint8), ("g", c_uint8), ("b", c_uint8), ("a", c_uint8)]

# enums.h
class Command(IntEnum):
	# Format (G - Group, C - Command)                = 0xGGGСCCCC,
	GAME                                             = 0x00100000,
	GAME_SET_CHEATS_ENABLED                          = 0x00100001,
	GAME_GET_CHEATS_ENABLED                          = 0x00100002,
	GAME_SET_CHEATS_NOCLIP                           = 0x00100003,
	GAME_GET_CHEATS_NOCLIP                           = 0x00100004,
	GAME_SET_GRAVITY                                 = 0x00100005,
	GAME_GET_GRAVITY                                 = 0x00100006,
	GAME_CHECK_GUID_IS_VALID                         = 0x00100007,
	GAME_INITIALIZE                                  = 0x00100008,
	GAME_DEINITIALIZE                                = 0x00100009,

	PLAYER                                           = 0x00200000,
	PLAYER_SET_LOCATION                              = 0x00200001,
	PLAYER_GET_LOCATION                              = 0x00200002,
	PLAYER_SET_ROTATION                              = 0x00200003,
	PLAYER_GET_ROTATION                              = 0x00200004,
	PLAYER_SPAWN                                     = 0x00200005,
	PLAYER_KILL                                      = 0x00200006,

	SOLVER_GUN                                       = 0x00300000,
	SOLVER_GUN_SET_ENABLED                           = 0x00300001,
	SOLVER_GUN_GET_ENABLED                           = 0x00300002,
	SOLVER_GUN_ACTION_USE                            = 0x00300003,
	SOLVER_GUN_ACTION_RELEASE                        = 0x00300004,
	SOLVER_GUN_ACTION_THROW                          = 0x00300005,

	FLASHLIGHT                                       = 0x00400000,
	FLASHLIGHT_SET_ENABLED                           = 0x00400001,
	FLASHLIGHT_GET_ENABLED                           = 0x00400002,
	FLASHLIGHT_SET_STATE                             = 0x00400003,
	FLASHLIGHT_GET_STATE                             = 0x00400004,

	STATIC_MESH                                      = 0x00500000,
	STATIC_MESH_CREATE                               = 0x00500001,

	REPLACE                                          = 0x05062025,

	DYNAMIC_MESH                                     = 0x00600000,
	DYNAMIC_MESH_CREATE                              = 0x00600001,
	DYNAMIC_MESH_SET_MATERIAL                        = 0x00600002,
	DYNAMIC_MESH_SET_MESH                            = 0x00600003,
	DYNAMIC_MESH_SET_VISIBILITY                      = 0x00600004,
	DYNAMIC_MESH_GET_VISIBILITY                      = 0x00600005,
	DYNAMIC_MESH_SET_TRANSFORM                       = 0x00600006,
	DYNAMIC_MESH_GET_TRANSFORM                       = 0x00600007,
	DYNAMIC_MESH_DESTROY                             = 0x00600008,

	ELEMENT                                          = 0x00700000,
	ELEMENT_CREATE                                   = 0x00700001,
	ELEMENT_SET_CALLBACK                             = 0x00700002,
	ELEMENT_GET_CALLBACK                             = 0x00700003,
	ELEMENT_SET_STATE                                = 0x00700004,
	ELEMENT_GET_STATE                                = 0x00700005,
	ELEMENT_SET_VISIBILITY                           = 0x00700006,
	ELEMENT_GET_VISIBILITY                           = 0x00700007,
	ELEMENT_SET_TRANSFORM                            = 0x00700008,
	ELEMENT_GET_TRANSFORM                            = 0x00700009,
	ELEMENT_SET_CLASS                                = 0x0070000A,
	ELEMENT_GET_CLASS                                = 0x0070000B,
	ELEMENT_SET_REGISTER                             = 0x0070000C,
	ELEMENT_GET_REGISTER                             = 0x0070000D,
	ELEMENT_SET_ALL_REGISTERS                        = 0x0070000E,
	ELEMENT_GET_ALL_REGISTERS                        = 0x0070000F,
	ELEMENT_SET_STATE_AND_CALLBACK_AND_ALL_REGISTERS = 0x00700010,
	ELEMENT_GET_STATE_AND_CALLBACK_AND_ALL_REGISTERS = 0x00700011,
	ELEMENT_DESTROY                                  = 0x00700012,

	NONE                                             = 0xFFFFFFFF

class Event(IntEnum):
	ELEMENT_CHANGED    = 0x00000000,
	GAME_TICK_OVERFLOW = 0x00000001,

	NONE               = 0xFFFFFFFF

class Result(IntEnum):
	SUCCESS                        = 0x00000000,

	ERROR_COMMAND_NOT_FOUND        = 0x00000001,
	ERROR_COMMAND_NOT_IMPLEMENTED  = 0x00000002,
	ERROR_EXECUTION_FAILED         = 0x00000003,
	ERROR_ARRAY_INDEX_OUT_OF_RANGE = 0x00000004,
	ERROR_GUID_NOT_FOUND           = 0x00000005,
	ERROR_INVALID_OBJECT_TYPE      = 0x00000006,
	ERROR_GAME_NOT_INITIALIZED     = 0x00000007,

	NONE                           = 0xFFFFFFFF

class Mesh(IntEnum):
	PLANE               = 0x0000,
	FACE                = 0x0001,
	CUBE                = 0x0002,

	CUP_INNER           = 0x0003,
	CUP_OUTER           = 0x0004,
	II_INNER            = 0x0005,
	II_OUTER            = 0x0006,
	O_INNER             = 0x0007,
	O_OUTER             = 0x0008,
	U_INNER             = 0x0009,
	U_OUTER             = 0x000A,

	DOOR_FRAME          = 0x000B,
	LASER_FRAME         = 0x000C,
	LASER_FRAME_SHIFTED = 0x000D,
	PLANE_Z_SHIFTED     = 0x000E,

class Material(IntEnum):
	WALL_WHITE_SMALL            = 0x0000,
	WALL_WHITE_MEDIUM           = 0x0001,
	WALL_WHITE_DOUBLE           = 0x0002,
	WALL_WHITE_BIG              = 0x0003,
	WALL_WHITE_ABSOLUTE_SCIENCE = 0x0004,

	WALL_BLACK_SMALL            = 0x0005,
	WALL_BLACK_MEDIUM           = 0x0006,
	WALL_BLACK_BIG              = 0x0007,

	FLOOR_WHITE                 = 0x0008,
	FLOOR_BLACK                 = 0x0009,

	WINDOW_METAL_GRID           = 0x000A,
	WINDOW_GLASS_METAL_GRID     = 0x000B,

class Class(IntEnum):
	ENTRY_ELEVATOR           = 0x0000,
	EXIT_ELEVATOR            = 0x0001,

	DOOR                     = 0x0002,
	BUTTON                   = 0x0003,
	ANTI_EXPROPRIATION_FIELD = 0x0004,
	PEDESTAL_BUTTON          = 0x0005,
	SOLVER_BUTTON            = 0x0006,
	INDICATOR                = 0x0007,

	LASER_TX                 = 0x0008,
	LASER_RX                 = 0x0009,
	LASER_RELAY              = 0x000A,
	LASER_PLANE              = 0x000B,

	LASER_CUBE               = 0x000C,
	WEIGHT_CUBE              = 0x000D,

	FAITH_PLATE              = 0x000E,
	PANEL                    = 0x000F,
	STAIRS                   = 0x0010,
	CUBE_DROPPER             = 0x0011,
	SOLVER_GUN_PEDESTAL      = 0x0012,
	FLASHLIGHT               = 0x0013,
	WINDOW                   = 0x0014,

	TRIGGER                  = 0x0015,
	LAMP                     = 0x0016
