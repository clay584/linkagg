import sys
import random
from linkagg.hashing import hash_main
from linkagg.utils import gen_frames, egress_intf_picker

num_supported = 256  # number of interfaces supported in a bundle
num_up_links = int(sys.argv[1])  # number of active links in the bundle
num_frames = int(sys.argv[2])  # number of frames to generate

# Generate a lot of frames
frames = gen_frames(num_frames)

# Create struct for interface queues. Frames will be dumped into these queues
interface_queues = {i: [] for i in range(1, num_up_links + 1)}

# Run a lot of frames into the system
for frame in frames:
    resulting_hash = hash_main(frame)
    picked_interface = egress_intf_picker(num_up_links, num_supported, resulting_hash)
    interface_queues[picked_interface].append(frame.frame_tuple())

# print queues
print("One frame for every flow only. We should see a uniform distribution")
print("=" * 50)
for k, v in interface_queues.items():
    print(f"Interface {k}: {len(v)} frames")
print("=" * 50)

# Lets simulate lots of frames for certain flows. This is normal in networking.
# A flow has thousands of frames...not just one. This will show the
# behavior of load-balancing flows does not necessarily ensure uniform interface
# utilization in a bundle. We will set 2 flows to be elephant flows.
more_frames = []
for _ in range(2):
    selected_frame = random.choice(frames)
    for _ in range(10000):
        more_frames.append(selected_frame)

for frame in more_frames:
    resulting_hash = hash_main(frame)
    picked_interface = egress_intf_picker(num_up_links, num_supported, resulting_hash)
    interface_queues[picked_interface].append(frame.frame_tuple())

# print queues again
print()
print(
    "Now lets see it with two elephant flows. Sometimes those will hit the same interface"
)
print("=" * 50)
for k, v in interface_queues.items():
    print(f"Interface {k}: {len(v)} frames")
print("=" * 50)
