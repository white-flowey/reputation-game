import json
import h5py
import numpy as np
import time
import os

# Create a sample data structure
data = {
    "array": np.random.rand(100000),  # large array
    "metadata": {"name": "test", "version": 1.0}
}

# Function to write data to JSON
def write_to_json(data, filename):
    # Convert NumPy array to list before serializing
    with open(filename, 'w') as json_file:
        json.dump(data, json_file)


# Function to write data to HDF5
def write_to_hdf5(data, filename):
    with h5py.File(filename, 'w') as h5_file:
        h5_file.create_dataset('array', data=data["array"])
        h5_file.attrs['name'] = data["metadata"]["name"]
        h5_file.attrs['version'] = data["metadata"]["version"]

# Benchmark writing to JSON
start_time = time.time()
write_to_json(data.copy(), 'data.json')  # Use copy to avoid modifying original data
json_duration = time.time() - start_time

# Benchmark writing to HDF5
start_time = time.time()
write_to_hdf5(data, 'data.h5')  # Directly use data, HDF5 can handle the original array
hdf5_duration = time.time() - start_time

# Print results
print(f"JSON write time: {json_duration:.4f} seconds")
print(f"HDF5 write time: {hdf5_duration:.4f} seconds")

# Cleanup the created files (optional)
if os.path.exists('data.json'):
    os.remove('data.json')
if os.path.exists('data.h5'):
    os.remove('data.h5')
