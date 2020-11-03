import argparse
import nbt
import os
import shutil
import threading
import time
from region import RegionFile
from chunk import Chunk

def is_valid_world_folder(check_folder):
	if os.path.exists(check_folder) == False or os.path.isfile(check_folder):
		return False
	
	region_folder = check_folder + '/region/'
	if os.path.exists(region_folder) and os.path.isfile(region_folder) == False:
		return True

	return False

arg_parser = argparse.ArgumentParser()

arg_parser.add_argument('-s', '--source', dest='source', required=True, help='Source world folder')
arg_parser.add_argument('-d', '--destination', '--dest', dest='dest', required=True, help='Destination world folder')
arg_parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', help='Displays verbose debugging messages')
arg_parser.add_argument('-th', '--threads', type=int, dest='threads', help='Set the number of threads to run on')
arg_parser.add_argument('-ti', '--ticks', type=int, dest='ticks', help='Set the number of ticks in which a chunk gets trimmed')
arg_parser.set_defaults(verbose=False)
arg_parser.set_defaults(threads=1)
arg_parser.set_defaults(ticks=72000)

args = arg_parser.parse_args()
verbose_logs = args.verbose

if not is_valid_world_folder(args.source):
	print(args.source + ' is not a valid world folder!')
	exit()

if not is_valid_world_folder(args.dest):
	print(args.dest + ' is not a valid world folder!')
	exit()


source_region_folder = args.source + "/region/"
dest_region_folder = args.dest + "/region/"

failed_regions = []

region_files = os.listdir(source_region_folder)

num_threads = args.threads
chunk_ticks = args.ticks


def process_files(files):
	for file in files:
		source_file_name = source_region_folder + file
		destination_file_name = dest_region_folder + file
		file_exists = os.path.isfile(destination_file_name)
		if file_exists:
			os.remove(destination_file_name)	
			print('Destination "' + destination_file_name + '" exists, deleting...')
		
		shutil.copyfile(source_file_name, destination_file_name)

		try:
			destination = RegionFile(destination_file_name)
			for x in range(0, 32):
				for z in range(0, 32):
					destination_chunk_nbt = destination.get_chunk(x, z)
					if destination_chunk_nbt is not None:
						destination_chunk = Chunk(destination_chunk_nbt)
						inhabited_time = int(str(destination_chunk.inhabited_time))
						if inhabited_time < chunk_ticks:
							#print(inhabited_time)
							destination.unlink_chunk(x, z)
							#if verbose_logs:
							#	print('Removed ' + str(x) + ',' + str(z) + " due to being inactive")
			all_inactive = True
			for x in range(0, 32):
				for z in range(0, 32):
					destination_chunk_nbt = destination.get_chunk(x, z)
					if destination_chunk_nbt is not None:
						all_inactive = False
						break
				if all_inactive == False:
					break
			destination.close()
			if all_inactive:
				os.remove(destination_file_name)
				if verbose_logs:
					print('Deleted ' + destination_file_name + ' due to having no active chunks')
		except Exception as e:
			print("Couldn't deleted chunk in " + destination_file_name)
			print(e)
			print('')
			failed_regions.append(destination_file_name)

def pool_is_alive(pool):
	for th in pool:
		if th.is_alive():
			return True
	return False

if num_threads == 1:
	process_files(region_files)
else:
	split_files = []
	for i in range(0, num_threads):
		split_files.append([])
	
	index = 0
	while (len(region_files) > 0):
		file = region_files.pop(0)
		split_files[index].append(file)
		index += 1
		if index >= len(split_files):
			index = 0
	
	pool = []
	for i in range(1, len(split_files)):
		files = split_files[i]
		new_thread = threading.Thread(target = process_files, args = (files,))
		pool.append(new_thread)
		new_thread.start()
	
	process_files(split_files[0])
	while(pool_is_alive(pool)):
		time.sleep(1)
	

print('\nDone!\n')
if len(failed_regions) == 0:
	print("No regions failed to load")
else:
	print('Regions that failed to trim:')
	print(*failed_regions, sep='\n')