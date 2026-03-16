import json

data = []
with open('gpus.json') as fd:
    data = json.load(fd)

for gpu in data:
    gpu_id = gpu.get("id")
    name = gpu.get("name")
    vendor = gpu.get("vendor")
    manufacturer = gpu.get("manufacturer")
    gpu_name = gpu.get("gpuName")
    architecture = gpu.get("architecture")
    generation = gpu.get("generation")
    process_size = gpu.get("processSize")
    die_size = gpu.get("dieSize")
    release_date = gpu.get("releaseDate")
    bus_interface = gpu.get("busInterface")
    base_clock = gpu.get("baseClock")
    boost_clock = gpu.get("boostClock")
    memory_clock = gpu.get("memoryClock")
    memory_size = gpu.get("memorySize")
    memory_type = gpu.get("memoryType")
    memory_bus = gpu.get("memoryBus")
    memory_bandwidth = gpu.get("memoryBandwidth")
    suggested_psu = gpu.get("suggestedPSU")
    slot = gpu.get("slot")
    url = gpu.get("url")

    print(f"ID: {gpu_id}, Name: {name}, Vendor: {vendor}, Manufacturer: {manufacturer}, GPU Name: {gpu_name}, "
          f"Architecture: {architecture}, Generation: {generation}, Process Size: {process_size}, "
          f"Die Size: {die_size}, Release Date: {release_date}, Bus Interface: {bus_interface}, "
          f"Base Clock: {base_clock}, Boost Clock: {boost_clock}, Memory Clock: {memory_clock}, "
          f"Memory Size: {memory_size}, Memory Type: {memory_type}, Memory Bus: {memory_bus}, "
          f"Memory Bandwidth: {memory_bandwidth}, Suggested PSU: {suggested_psu}, Slot: {slot}, URL: {url}\n")
