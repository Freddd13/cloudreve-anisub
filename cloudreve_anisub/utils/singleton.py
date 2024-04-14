'''
Date: 2023-10-05 12:42:39
LastEditors: Kumo
LastEditTime: 2024-04-14 19:35:47
Description: 
'''
class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
            print(f"created {cls}")
        else:
            print(f"reused {cls}")
        return cls._instances[cls]


class InstanceRegistry:
    _registry = {}

    @classmethod
    def register_instance(cls, instance):
        class_name = instance.__class__._name
        cls._registry[class_name] = instance

    @classmethod
    def get_instance_by_name(cls, name):
        return cls._registry.get(name)


def GetInstance(name):
    return InstanceRegistry.get_instance_by_name(name)