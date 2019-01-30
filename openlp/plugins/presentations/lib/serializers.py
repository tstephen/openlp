try:
    from openlp.core.common.path import Path
except ImportError:
    from pathlib import Path

from Pyro4.util import SerializerBase


def path_class_to_dict(obj):
    """
    Serialize a Path object for Pyro4
    """
    return {
        '__class__': 'Path',
        'parts': obj.parts
    }


def path_dict_to_class(classname, d):
    return Path(d['parts'])


def register_classes():
    """
    Register the serializers
    """
    SerializerBase.register_class_to_dict(Path, path_class_to_dict)
    SerializerBase.register_dict_to_class('Path', path_dict_to_class)
