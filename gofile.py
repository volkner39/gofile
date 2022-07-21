import requests
from fake_useragent import UserAgent
import ssl
import os
import sys
import json


# Create the folder for the Gofile album
def create_directory(folder_code, path):
	try:
		print('Creating folder...')
		if not os.path.exists(path + "\\" + folder_code):
			os.makedirs(path + "\\" + folder_code)
	except Exception as e:
		sys.exit(e.__class__.__name__ + ": Error creating a folder!")

	return path + "\\" + folder_code


# Download the current media files to download path
def media_scrape(url, folder, cookie):
		print(url)
		filename = url.rsplit('/', 1)[-1]
		new_path = folder + '\\' + filename

		# Check if the downloaded file exists already
		if not os.path.exists(new_path):
			# if not, download the file and write it to disk
			# timeout in case of Connection Error
			# if connection error persists, re-download album again
			try:
				r = requests.get(url, allow_redirects=False, timeout=20, headers={
				"User-Agent":ua.chrome,
				"Connection":"keep-alive",
				"cookie": cookie})
				with open(new_path, 'wb') as outfile:
					outfile.write(r.content)
			except Exception as e:
				# Check if file exists
				if os.path.exists(new_path):
					# Delete downloading file
					shutil.rmtree(new_path)
				sys.exit(e.__class__.__name__ + ": Error writing file!")


# Traverse the Gofile album tree including sub-directories
# Retrieve a list of media links to download for each gofile folder
def rec_scrape(url, code, path, cookie):
	
	print("Currently scraping folder: ", code)

	# Gofile API link
	url = "https://api.gofile.io/getContent?contentId=" + code + "&token=P3aOFMsEbE1XF0esD16squuPoCYITqiq&websiteToken=12345"

	try:
		response = requests.get(url, allow_redirects=False, headers={
		"User-Agent":ua.chrome,
		"Connection":"keep-alive",
		"cookie": cookie})
	except Exception as e:
		sys.exit(e.__class__.__name__ + ": Error connecting to " + url + "!")	
	
	# Extract returned JSON
	extract = json.loads(response.text)
	
	# Check if album exists
	if (extract['status'] == 'error-notFound'):
		print('Album does not exist!')
		return
	else:
		dict1 = extract['data']['contents']
	
	
	sub_folder_list = []
	
	# Create current folder locally to store files
	new_fol = create_directory(code, path);

	# Check if album has atleast 1 file
	if dict1 and len(dict1) > 0:
		
		# Loop through all files in album
		for hash in dict1:
			type = dict1[hash]['type']
		
			# Categorize folder vs file
			if type == 'folder':
				sub_folder_list.append(dict1[hash]['code'])
		
			if type == 'file':
				media_scrape(dict1[hash]['link'], new_fol, cookie)
		
		# If no sub-folders, our base-case is met and we are done! Otherwise, recurse...
		if sub_folder_list == []:
			return
		else:
			for c in sub_folder_list:
				rec_scrape(url, c, new_fol, cookie)


if __name__ == "__main__":
	ua = UserAgent(verify_ssl=False)
	code = input("Input album code: ")
	download_path = input("Enter the full download path: ")
	req_cookie = input("Cookie: ")

	url = "https://api.gofile.io/getContent?contentId=" + code + "&token=P3aOFMsEbE1XF0esD16squuPoCYITqiq&websiteToken=12345"

	# Scrape the album html
	try:
		rec_scrape(url, code, download_path, req_cookie)
		print("Done.")

	except Exception as e:
		sys.exit(e.__class__.__name__ + ": Error connecting to " + url + "!")