#!/usr/bin/python3

import os
import sys
import json
import shutil
import pathlib
import requests
import hashlib
from datetime import datetime, timedelta

######################
# CONFIGURATIONS     #
######################

#Session Variables (update every time you login or your browser updates)
USER_ID = ""
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0"
X_BC = ""
SESS_COOKIE = ""

#Options
ALBUMS = True # Separate photos into subdirectories by post/album (Single photo posts are not put into subdirectories)
USE_SUB_FOLDERS = True # use content type subfolders (messgaes/archived/stories/purchased), or download everything to /profile/photos and /profile/videos

# content types to download
VIDEOS = True
PHOTOS = True
POSTS = True
STORIES = True
MESSAGES = True
ARCHIVED = True
PURCHASED = True

######################
# END CONFIGURATIONS #
######################

API_URL = "https://onlyfans.com/api2/v2"
new_files = 0
MAX_AGE = 0
API_HEADER = {
	"Accept": "application/json, text/plain, */*",
	"Accept-Encoding": "gzip, deflate",
	"app-token": "33d57ade8c02dbc5a333db99ff9ae26a",
	"User-Agent": USER_AGENT,
	"x-bc": X_BC,
	"Cookie": "auh_id=0; sess=" + SESS_COOKIE
}
if('USER_ID' in globals() and USER_ID):
	API_HEADER['user-id'] = USER_ID
else:
	USER_ID = "0"

def create_signed_headers(link, queryParams):
	global API_HEADER
	path = "/api2/v2" + link
	if queryParams:
		query = '&'.join('='.join((key,val)) for (key,val) in queryParams.items())
		path = f"{path}?{query}"
	unixtime = str(int(datetime.now().timestamp()))
	msg = "\n".join([dynamic_rules["static_param"], unixtime, path, USER_ID])
	message = msg.encode("utf-8")
	hash_object = hashlib.sha1(message)
	sha_1_sign = hash_object.hexdigest()
	sha_1_b = sha_1_sign.encode("ascii")
	checksum = sum([sha_1_b[number] for number in dynamic_rules["checksum_indexes"]])+dynamic_rules["checksum_constant"]
	API_HEADER["sign"] = dynamic_rules["format"].format(sha_1_sign, abs(checksum))
	API_HEADER["time"] = unixtime
	return


def api_request(endpoint, apiType):
	posts_limit = 100
	getParams = { "app-token": "33d57ade8c02dbc5a333db99ff9ae26a", "limit": str(posts_limit), "order": "publish_date_asc"}
	if apiType == 'messages':
		getParams['order'] = 'asc'
	if apiType == 'subscriptions':
		getParams['type'] = 'active'
	if MAX_AGE and apiType != 'purchased' and apiType != 'subscriptions': #Cannot be limited by age
		getParams['afterPublishTime'] = str(MAX_AGE) + ".000000"
	create_signed_headers(endpoint, getParams)
	list_base = requests.get(API_URL + endpoint, headers=API_HEADER, params=getParams).json()

	# Fixed the issue with the maximum limit of 100 posts by creating a kind of "pagination"
	if len(list_base) >= posts_limit and apiType != 'user-info':
		if apiType == 'purchased' or apiType == 'subscriptions':
			getParams['offset'] = str(posts_limit) #If the limit for purchased posts is lower than for posts, this won't work. But I can't test it
		else:
			getParams['afterPublishTime'] = list_base[len(list_base)-1]['postedAtPrecise']
		while 1:
			create_signed_headers(endpoint, getParams)
			list_extend = requests.get(API_URL + endpoint, headers=API_HEADER, params=getParams).json()
			list_base.extend(list_extend) # Merge with previous posts
			if len(list_extend) < posts_limit:
				break
			if apiType == 'purchased' or apiType == 'subscriptions':
				getParams['offset'] = str(int(getParams['offset']) + posts_limit)
			else:
				getParams['afterPublishTime'] = list_extend[len(list_extend)-1]['postedAtPrecise']
	return list_base


def get_user_info(profile):
	# <profile> = "me" -> info about yourself
	info = api_request("/users/" + profile, 'user-info')
	if "error" in info:
		global USER_ID, API_HEADER
		USER_ID = "0"
		API_HEADER.pop('user-id', None)
		print('\nUSER_ID auth failed, trying without it...\n(if this persists you can comment out the USER_ID variable)')
		info = api_request("/users/" + profile, 'user-info').json()
		if "error" in info:
			print("\nERROR: " + info["error"]["message"])
			exit()
	return info


def get_subscriptions():
	subs = api_request("/subscriptions/subscribes", "subscriptions")
	if "error" in subs:
		print("\nSUBSCRIPTIONS ERROR: " + info["error"]["message"])
		exit()
	return [row['username'] for row in subs]


def download_media(media, subtype, album = False):
	if('createdAt' in media): #posts
		filename = str(media["createdAt"][:10]) + "_" + str(media["id"])
	else: #messages,paid
		if(album):
			filename = album[:10] + "_" + str(media["id"])
		else:
			filename = str(media["id"])
	source = media["source"]["source"]

	if (media["type"] != "photo" and media["type"] != "video") or not media['canView']:
		return
	if (media["type"] == "photo" and not PHOTOS) or (media["type"] == "video" and not VIDEOS):
		return

	extension = source.split('?')[0].split('.')
	ext = '.' + extension[len(extension)-1]
	if len(ext) < 3:
		return

	if ALBUMS and album and media["type"] == "photo":
		path = "/photos/" + album + "/" + filename + ext
	else:
		path = "/" + media["type"] + "s/" + filename + ext
	if USE_SUB_FOLDERS and subtype != "posts":
		path = "/" + subtype + path

	if not os.path.isdir(PROFILE + os.path.dirname(path)):
		pathlib.Path(PROFILE + os.path.dirname(path)).mkdir(parents=True, exist_ok=True)
	if not os.path.isfile(PROFILE + path):
		print(PROFILE + path)
		global new_files
		new_files += 1
		r = requests.get(source, stream=True)
		with open(PROFILE + path, 'wb') as f:
			r.raw.decode_content = True
			shutil.copyfileobj(r.raw, f)


def get_content(MEDIATYPE, API_LOCATION):
	posts = api_request(API_LOCATION,MEDIATYPE)
	if "error" in posts:
		print("\nERROR: " + posts["error"]["message"])
		exit()
	if MEDIATYPE == "messages":
		posts = posts['list']
	if len(posts) > 0:
		print("Found " + str(len(posts)) + " " + MEDIATYPE)
		for post in posts:
			if ("canViewMedia" in post and not post["canViewMedia"]):
				continue
			if MEDIATYPE == "purchased" and post["fromUser"]["username"] != PROFILE:
				continue # Only get paid posts from PROFILE
			if len(post["media"]) > 1: # Don't put single photo posts in a subfolder
				if('postedAt' in post):
					album = str(post["postedAt"][:10]) + "_" + str(post["id"])
				else:
					album = str(post["createdAt"][:10]) + "_" + str(post["id"])
			else:
				album = False
			for media in post["media"]:
				if "source" in media and ("canView" not in media or media["canView"]):
					download_media(media, MEDIATYPE, album)
		global new_files
		print("Downloaded " + str(new_files) + " new " + MEDIATYPE)
		new_files = 0
 

if __name__ == "__main__":
	if len(sys.argv) < 2:
		print("\nUsage: " + sys.argv[0] + " <list of profiles / all> [optional: only get last <integer> days of posts]\n")
		print("Make sure to update the session variables at the top of this script\nSee readme for instructions")
		print("Update User Agent: https://ipchicken.com/\n")
		exit()
	
	#Get the rules for the signed headers dynamically, so we don't have to update the script every time they change
	dynamic_rules = requests.get('https://raw.githubusercontent.com/DATAHOARDERS/dynamic-rules/main/onlyfans.json').json()
	PROFILE_LIST = sys.argv
	PROFILE_LIST.pop(0)
	if(len(PROFILE_LIST) > 1 and PROFILE_LIST[-1].isnumeric()):
		MAX_AGE = int((datetime.today() - timedelta(int(PROFILE_LIST.pop(-1)))).strftime("%s"))
		print("\nGetting posts newer than " + str(datetime.utcfromtimestamp(int(MAX_AGE))) + " UTC")

	if(PROFILE_LIST[0] == "all"):
		PROFILE_LIST = get_subscriptions()

	for PROFILE in PROFILE_LIST:
		PROFILE_ID = str(get_user_info(PROFILE)["id"])
		if os.path.isdir(PROFILE):
			print("\n" + PROFILE + " exists.\nDownloading new media, skipping pre-existing.")
		else:
			print("\nDownloading content to " + PROFILE)

		if POSTS:
			get_content("posts", "/users/" + PROFILE_ID + "/posts")
		if ARCHIVED:
			get_content("archived", "/users/" + PROFILE_ID + "/posts/archived")
		if STORIES:
			get_content("stories", "/users/" + PROFILE_ID + "/stories")
		if MESSAGES:
			get_content("messages", "/chats/" + PROFILE_ID + "/messages")
		if PURCHASED:
			get_content("purchased", "/posts/paid")


