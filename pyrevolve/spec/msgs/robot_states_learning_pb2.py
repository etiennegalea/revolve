# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: robot_states_learning.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from pygazebo.msg import pose_pb2 as pose__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='robot_states_learning.proto',
  package='revolve.msgs',
  syntax='proto2',
  serialized_pb=_b('\n\x1brobot_states_learning.proto\x12\x0crevolve.msgs\x1a\npose.proto\"0\n\rbehaviourData\x12\x1f\n\x04path\x18\x01 \x03(\x0b\x32\x11.gazebo.msgs.Pose\"~\n\x13LearningRobotStates\x12\n\n\x02id\x18\x01 \x02(\r\x12\x0c\n\x04\x65val\x18\x02 \x02(\r\x12\x0c\n\x04\x64\x65\x61\x64\x18\x03 \x01(\x08\x12\x0f\n\x07\x66itness\x18\x04 \x02(\x01\x12.\n\tbehaviour\x18\x05 \x01(\x0b\x32\x1b.revolve.msgs.behaviourData')
  ,
  dependencies=[pose__pb2.DESCRIPTOR,])
_sym_db.RegisterFileDescriptor(DESCRIPTOR)




_BEHAVIOURDATA = _descriptor.Descriptor(
  name='behaviourData',
  full_name='revolve.msgs.behaviourData',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='path', full_name='revolve.msgs.behaviourData.path', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=57,
  serialized_end=105,
)


_LEARNINGROBOTSTATES = _descriptor.Descriptor(
  name='LearningRobotStates',
  full_name='revolve.msgs.LearningRobotStates',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='revolve.msgs.LearningRobotStates.id', index=0,
      number=1, type=13, cpp_type=3, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='eval', full_name='revolve.msgs.LearningRobotStates.eval', index=1,
      number=2, type=13, cpp_type=3, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='dead', full_name='revolve.msgs.LearningRobotStates.dead', index=2,
      number=3, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='fitness', full_name='revolve.msgs.LearningRobotStates.fitness', index=3,
      number=4, type=1, cpp_type=5, label=2,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='behaviour', full_name='revolve.msgs.LearningRobotStates.behaviour', index=4,
      number=5, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=107,
  serialized_end=233,
)

_BEHAVIOURDATA.fields_by_name['path'].message_type = pose__pb2._POSE
_LEARNINGROBOTSTATES.fields_by_name['behaviour'].message_type = _BEHAVIOURDATA
DESCRIPTOR.message_types_by_name['behaviourData'] = _BEHAVIOURDATA
DESCRIPTOR.message_types_by_name['LearningRobotStates'] = _LEARNINGROBOTSTATES

behaviourData = _reflection.GeneratedProtocolMessageType('behaviourData', (_message.Message,), dict(
  DESCRIPTOR = _BEHAVIOURDATA,
  __module__ = 'robot_states_learning_pb2'
  # @@protoc_insertion_point(class_scope:revolve.msgs.behaviourData)
  ))
_sym_db.RegisterMessage(behaviourData)

LearningRobotStates = _reflection.GeneratedProtocolMessageType('LearningRobotStates', (_message.Message,), dict(
  DESCRIPTOR = _LEARNINGROBOTSTATES,
  __module__ = 'robot_states_learning_pb2'
  # @@protoc_insertion_point(class_scope:revolve.msgs.LearningRobotStates)
  ))
_sym_db.RegisterMessage(LearningRobotStates)


# @@protoc_insertion_point(module_scope)
