#! /usr/bin/env python

import os, sys, re

global DIFF_THRESHOLD
DIFF_THRESHOLD = 4			# the max number of character edits, as defined by levenshtein, similar files

def levenshtein(s1, s2):
	'''http://en.wikibooks.org/wiki/Algorithm_implementation/Strings/Levenshtein_distance#Python'''
	if len(s1) < len(s2):
	    return levenshtein(s2, s1)
	if not s1:
	    return len(s2)

	previous_row = xrange(len(s2) + 1)
	for i, c1 in enumerate(s1):
	    current_row = [i + 1]
	    for j, c2 in enumerate(s2):
	        insertions = previous_row[j + 1] + 1 # j+1 instead of j since previous_row and current_row are one character longer
	        deletions = current_row[j] + 1       # than s2
	        substitutions = previous_row[j] + (c1 != c2)
	        current_row.append(min(insertions, deletions, substitutions))
	    previous_row = current_row

	distance = previous_row[-1]
	#if distance <= DIFF_THRESHOLD:
	#	print "Levenshtein", s1, s2, distance
	return previous_row[-1]

def lookForPatterns(file1, file2, path):
	# look for differences due to (1) copy naming 
	parenPattern = re.compile(r"\(\d\)")
	if parenPattern.search(file1) and parenPattern.search(file2) is None:
		return 1
	elif parenPattern.search(file2) and parenPattern.search(file1) is None:
		return 2


	# find differences due to track number punctuation 
	# dashPattern: 1 - filename.mp3
	# spacePattern: 1 filename.mp3
	dashPattern = re.compile(r"\d+ ?- ?.+\.mp3")
	spacePattern = re.compile(r"\d +.+\.mp3")

	if dashPattern.search(file1) and spacePattern.search(file2):
		return 2
	elif dashPattern.search(file2) and spacePattern.search(file1):
		return 1


	
	size1 = os.stat(os.path.join(path, file1)).st_size
	size2 = os.stat(os.path.join(path, file2)).st_size

	if size1 > size2:
		return 1
	elif size2 > size1:
		return 2

	if len(file1) < len(file2):
		return 1
	else:
		return 2
		
		
def findDupe(file1, file2, path):
	if file1 == file2:
		return 0
	elif not file1.endswith("mp3") or not file2.endswith("mp3"):
		return 0	
	elif levenshtein(file1, file2) > DIFF_THRESHOLD:
		return 0
	else:	# compare track numbers
		trackNumber = re.compile(r"\d+")
		file1Match = trackNumber.match(file1);
		file2Match = trackNumber.match(file2);
		if (file1Match is not None and file2Match is not None):
			file1Number = int(file1Match.group())
			file2Number = int(file2Match.group())
			# print "track match: ", file1Number, file2Number
			if file1Number != file2Number:
				return 0				# if both have numbers but the numbers don't match, then escape
			else:							# if numbers are the same, then continue looking for patterns
				return (lookForPatterns(file1, file2, path))


	

### MAIN ###

if len(sys.argv) != 2:
	startDir = "./"
else:
	startDir = sys.argv[1]

deleteList = set()
bytes = 0;
	
for root, dirs, files in os.walk(startDir):
	print "********************************"
	print "Processing directory", root
	dupes = set()
	files.sort()
	for i in range(len(files)):
		for j in range(i, len(files)):
			dupe = findDupe(files[i], files[j], root)
			if dupe == 1:
				dupes.add(i)
			elif dupe == 2:
				dupes.add(j)
	
	# print contents, with * for to-be-deleted
	for i, file in enumerate(files):
		if i in dupes:
			fullPath = os.path.join(root, file)
			print "*",
			deleteList.add(fullPath)
			bytes += os.stat(fullPath).st_size
		print file

print "===================================="
print "========== total bytes:", bytes, "================="
print "========== count:", len(deleteList), "=============="
if len(deleteList) > 0:
	menu = raw_input("Delete all of these files? ")
	if menu in ('y', 'ye', 'yes'): 
		for file in deleteList:
			os.remove(file)
else:
	print "Nothing to do. Goodbye."