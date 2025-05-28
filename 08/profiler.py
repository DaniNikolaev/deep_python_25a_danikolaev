# pylint: disable=import-error
import cProfile
import io
import pstats

from classes import (NUM_INSTANCES, NormalClass, SlotsClass, WeakrefClass,
                     access_attributes, create_instances)
from memory_profiler import profile


@profile
def create_and_access(cls, num_instances):
    instances = create_instances(cls, num_instances)
    access_attributes(instances)
    return instances


pr_normal = cProfile.Profile()
pr_normal.enable()
normal_instances = create_and_access(NormalClass, NUM_INSTANCES)
pr_normal.disable()

pr_slots = cProfile.Profile()
pr_slots.enable()
slots_instances = create_and_access(SlotsClass, NUM_INSTANCES)
pr_slots.disable()

pr_weakref = cProfile.Profile()
pr_weakref.enable()
weakref_instances = create_and_access(WeakrefClass, NUM_INSTANCES)
pr_weakref.disable()


def print_stats(pr, class_name):
    s = io.StringIO()
    sortby = 'cumulative'
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats(10)
    print(f"Профилирование CPU для {class_name}:\n{s.getvalue()}")


print_stats(pr_normal, "NormalClass")
print_stats(pr_slots, "SlotsClass")
print_stats(pr_weakref, "WeakrefClass")
