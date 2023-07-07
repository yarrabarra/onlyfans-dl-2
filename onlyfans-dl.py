import datetime
import hashlib
import os
import pathlib
import sys
import time
import json
import shutil
import requests
import hashlib
import sqlite3
import session_vars
from avologger import Logger

requests.urllib3.disable_warnings()

start_time = time.time()

script_path = sys.path[0]

log_path = os.path.join(script_path, "logs")
log_name = f"{int(start_time)}.log"

log_location = os.path.join(log_path, log_name)

## The default logging level is INFO so we will override to make it DEBUG
log = Logger(log_file_location=log_location, max_log_file_size_in_mb=10, log_file_backup_count=30, logging_level="DEBUG")

## The line below enables uncaught exception logging for the entire script
## by introducing a custom exception hook 
sys.excepthook = log.my_excepthook

class OFDownloader():
    def __init__(self, user_id: str, user_agent: str, sess_cookie: str, x_bc: str) -> None:
        self.user_id = user_id
        self.user_agent = user_agent
        self.sess_cookie = sess_cookie
        self.x_bc = x_bc
        
        self.processed_count = 0
        
        ## Database
        self.db_name = "data_ofd.db"
        
        log.info("Opening DB connection...")

        def dict_factory(cursor, row):
            d = {}
            for idx,col in enumerate(cursor.description):
                d[col[0]] = row[idx]
            return d

        self.create_db_if_not_exists()
        
        self.db = sqlite3.connect(self.db_name)
        self.db.row_factory = dict_factory

        
        log.info("DB connection opened.")
        
        ## Options
        self.albums = False ## Separate photos into subdirectories by post/album (Single photo posts are not put into subdirectories)
        self.use_subfolders = True ## Use content type subfolders (messgaes/archived/stories/purchased), or download everything to /profile/photos and /profile/videos
    
        ## API Info
        self.api_url = "https://onlyfans.com/api2/v2"
        self.new_files = 0
        self.api_headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate",
        "app-token": "33d57ade8c02dbc5a333db99ff9ae26a",
        "User-Agent": self.user_agent,
        "x-bc": self.x_bc,
        "user-id": self.user_id,
        "Cookie": "auh_id=" + self.user_id + "; sess=" + self.sess_cookie
        }
        
        ## Get the rules for the signed headers dynamically, so we don't have to update the script every time they change
        self.dynamic_rules = requests.get('https://raw.githubusercontent.com/DIGITALCRIMINALS/dynamic-rules/main/onlyfans.json').json()


    def create_db_if_not_exists(self):
        if not os.path.exists(self.db_name):
            dlc_table_sql = """CREATE TABLE IF NOT EXISTS downloads_cleared (
    dlc_id           INTEGER        PRIMARY KEY AUTOINCREMENT,
    source           VARCHAR (255)  UNIQUE,
    remote_file_size INTEGER,
    remote_file_hash VARCHAR (255),
    local_file_size  INTEGER,
    local_file_hash  VARCHAR (255),
    added_ts         DATETIME (255) DEFAULT (datetime('now', 'localtime') ) 
                                    NOT NULL,
    last_updated_ts  DATETIME       DEFAULT (datetime('now', 'localtime') ) 
                                    NOT NULL
);"""

            dlc_trigger_sql = """CREATE TRIGGER IF NOT EXISTS downloads_cleared_update_timestamp
        AFTER UPDATE
            ON downloads_cleared
        FOR EACH ROW
            WHEN new.last_updated_ts <= old.last_updated_ts
    BEGIN
        UPDATE downloads_cleared
        SET last_updated_ts = datetime('now', 'localtime') 
        WHERE dlc_id = old.dlc_id;
    END;"""

            dlf_table_sql = """CREATE TABLE IF NOT EXISTS downloads_failed (
    dlf_id           INTEGER        PRIMARY KEY AUTOINCREMENT,
    source           VARCHAR (255),
    remote_file_size INTEGER,
    remote_file_hash VARCHAR (255),
    local_file_size  INTEGER,
    local_file_hash  VARCHAR (255),
    error            VARCHAR (255),
    headers          TEXT,
    status           CHAR (1)       DEFAULT a,
    added_ts         DATETIME (255) DEFAULT (datetime('now', 'localtime') ) 
                                    NOT NULL,
    last_updated_ts  DATETIME       DEFAULT (datetime('now', 'localtime') ) 
                                    NOT NULL
);"""

            dlf_trigger_sql = """CREATE TRIGGER IF NOT EXISTS downloads_failed_update_timestamp
		AFTER UPDATE
            ON downloads_failed
        FOR EACH ROW
            WHEN new.last_updated_ts <= old.last_updated_ts
    BEGIN
        UPDATE downloads_failed
        SET last_updated_ts = datetime('now', 'localtime') 
        WHERE dlf_id = old.dlf_id;
    END;"""

            db = sqlite3.connect(self.db_name)
            cur = db.cursor()
            cur.execute(dlc_table_sql)
            cur.execute(dlc_trigger_sql)
            cur.execute(dlf_table_sql)
            cur.execute(dlf_trigger_sql)
            
            db.commit()
            cur.close()
            db.close()


    def create_signed_headers(self, link, queryParams):
        path = "/api2/v2" + link
        if queryParams:
            query = '&'.join('='.join((key,val)) for (key,val) in queryParams.items())
            path = f"{path}?{query}"
        unixtime = str(int(datetime.datetime.now().timestamp()))
        msg = "\n".join([self.dynamic_rules["static_param"], unixtime, path, self.user_id])
        message = msg.encode("utf-8")
        hash_object = hashlib.sha1(message)
        sha_1_sign = hash_object.hexdigest()
        sha_1_b = sha_1_sign.encode("ascii")
        checksum = sum([sha_1_b[number] for number in self.dynamic_rules["checksum_indexes"]]) + self.dynamic_rules["checksum_constant"]
        self.api_headers["sign"] = self.dynamic_rules["format"].format(sha_1_sign, abs(checksum))
        self.api_headers["time"] = unixtime
        
        return True


    def api_request(self, endpoint, apiType):
        try:
            posts_limit = 50
            getParams = { "limit": str(posts_limit), "order": "publish_date_asc"}
            if apiType == 'messages':
                getParams['order'] = 'desc'
            if apiType == 'subscriptions':
                getParams['type'] = 'active'
            self.create_signed_headers(endpoint, getParams)
            # list_base = requests.get(self.api_url + endpoint, headers=self.api_headers, params=getParams).json()
            status = requests.get(self.api_url + endpoint, headers=self.api_headers, params=getParams)
            if status.ok:
                list_base = status.json()
            else:
                return json.loads('{"error":{"message":"http '+str(status.status_code)+'"}}')

            ## Fixed the issue with the maximum limit of 50 posts by creating a kind of "pagination"
            if (len(list_base) >= posts_limit and apiType != 'user-info') or ('hasMore' in list_base and list_base['hasMore']):
                if apiType == 'messages':
                    getParams['id'] = str(list_base['list'][len(list_base['list'])-1]['id'])
                elif apiType == 'purchased' or apiType == 'subscriptions':
                    getParams['offset'] = str(posts_limit)                
                else:
                        getParams['afterPublishTime'] = list_base[len(list_base)-1]['postedAtPrecise']
                while 1:
                    self.create_signed_headers(endpoint, getParams)
                    # list_extend = requests.get(self.api_url + endpoint, headers=self.api_headers, params=getParams).json()
                    status = requests.get(self.api_url + endpoint, headers=self.api_headers, params=getParams)
                    if status.ok:
                        list_extend = status.json()
                    if apiType == 'messages':
                        list_base['list'].extend(list_extend['list'])
                        if list_extend['hasMore'] == False or len(list_extend['list']) < posts_limit or not status.ok:
                            break
                        getParams['id'] = str(list_base['list'][len(list_base['list'])-1]['id'])
                        continue
                    list_base.extend(list_extend) ## Merge with previous posts
                    if len(list_extend) < posts_limit:
                        break
                    if apiType == 'purchased' or apiType == 'subscriptions':
                        getParams['offset'] = str(int(getParams['offset']) + posts_limit)
                    else:
                        getParams['afterPublishTime'] = list_extend[len(list_extend)-1]['postedAtPrecise']
            
            return list_base
        except json.decoder.JSONDecodeError as e:
            log.error(f"JSON decode error: {e}")
            
            return False


    def get_user_info(self, profile):
        # <profile> = "me" -> info about yourself
        info = self.api_request("/users/" + profile, 'user-info')
        if "error" in info:
            print("\nUSER_ID auth failed\n"+info["error"]["message"]+"\n\nUpdate your browser user-agent variable, then sign back in to OF and update your session variables.\nhttps://ipchicken.com/\n")
            log.critical("USER_ID auth failed "+info["error"]["message"]+" Update your browser user-agent variable, then sign back in to OF and update your session variables. https://ipchicken.com/")
            exit()
            
        return info


    def get_subscriptions(self):
        subs = self.api_request("/subscriptions/subscribes", "subscriptions")
        if "error" in subs:
            print("\nSUBSCRIPTIONS ERROR: " + subs["error"]["message"])
            log.error("SUBSCRIPTIONS ERROR: " + subs["error"]["message"])
            # exit()
            return
            
        return [row['username'] for row in subs]


    def calc_chunk_size(self, file_path, target_chunks):
        mb = 1048576
        file_size = os.path.getsize(file_path)
        part_size = file_size / target_chunks
        rem = part_size % mb
        if rem > 0:
            chunk_size = part_size + mb - rem
            return int(chunk_size)
        else:
            return int(part_size)


    def get_file_md5_hash(self, file_path, chunk_size=1048576):
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(chunk_size), b""):
                hash_md5.update(chunk)
                
        return hash_md5.hexdigest()        


    def get_alternate_hash(self, file_path, chunk_size=1048576):
        hash_list = []
        hash_md5 = hashlib.md5

        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(chunk_size), b""):
                hash_list.append(hash_md5(chunk).digest())
        
        return f"{hashlib.md5(b''.join(hash_list)).hexdigest()}-{len(hash_list)}"


    def check_db(self, source):
        cur_ck = self.db.cursor()
        
        check_cleared_sql = "SELECT count(dlc_id) AS dlc_count FROM downloads_cleared WHERE source = ?;"
        
        check_failed_sql = "SELECT count(dlf_id) AS dlf_count FROM downloads_failed WHERE source = ? AND status = 'a';"
        
        res_c = cur_ck.execute(check_cleared_sql, (source,)).fetchone()
        res_f = cur_ck.execute(check_failed_sql, (source,)).fetchone()
        
        count_c = res_c['dlc_count']
        count_f = res_f['dlf_count']
        total = count_c + count_f
        
        if total == 0:
            return False
            
        elif total == 1:
            return True
        else:
            err = f"Error in DB rows for source: {source} | Rows found: {total}"
            log.critical(err)
            raise(RuntimeError(err))


    def close_db(self):
        log.info("Closing DB...")
        self.db.close()
        log.info("DB closed.")


    def insert_into_downloads_cleared(self, source, remote_file_size, remote_file_hash, local_file_size, local_file_hash):
        cur_c = self.db.cursor()
        
        insert_sql_c = "INSERT OR IGNORE INTO downloads_cleared (source, remote_file_size, remote_file_hash, local_file_size, local_file_hash) VALUES (?, ?, ?, ?, ?);"
        
        cur_c.execute(insert_sql_c, (source, remote_file_size, remote_file_hash, local_file_size, local_file_hash))
        self.db.commit()
        
        cur_c.close()


    def insert_into_downloads_failed(self, source, remote_file_size, remote_file_hash, local_file_size, local_file_hash, error, headers):
        cur_f = self.db.cursor()
        
        insert_sql_f ="INSERT OR IGNORE INTO downloads_failed (source, remote_file_size, remote_file_hash, local_file_size, local_file_hash, error, headers) VALUES (?, ?, ?, ?, ?, ?, ?);"
        
        cur_f.execute(insert_sql_f, (source, remote_file_size, remote_file_hash, local_file_size, local_file_hash, error, headers))
        self.db.commit()

        cur_f.close()


    def download_media(self, profile, media, subtype, postdate, album = ''):
        # profile = os.path.join('subscriptions', profile)
        filename = postdate + "_" + str(media["id"])
        if subtype == "stories":
            source = media["files"]["source"]["url"]
        else:
            source = media["source"]["source"]
        
        if (media["type"] != "photo" and media["type"] != "video" and media["type"] != "audio") or not media['canView']:
            return False

        if source is not None:
            extension = source.split('?')[0].split('.')
            ext = '.' + extension[len(extension)-1]
        else:
            return False
            
        if len(ext) < 3:
            return False

        if self.albums and album and media["type"] == "photo":
            # path = "/photos/" + postdate + "_" + album + "/" + filename + ext
            path = os.path.join("photos", postdate + "_" + album, filename + ext)
        else:
            # path = "/" + media["type"] + "s/" + filename + ext
            path = os.path.join(media["type"] + "s", filename + ext)
        if self.use_subfolders and subtype != "posts":
            # path = "/" + subtype + path
            path = os.path.join(subtype, path)

        profile_and_path = os.path.join('subscriptions', profile, os.path.dirname(path))

        if not os.path.isdir(profile_and_path):
            log.info(f"MKDIR: \"{profile_and_path}\" was not found.  Creating it.")
            pathlib.Path(profile_and_path).mkdir(parents=True, exist_ok=True)
        if not os.path.isfile(os.path.join('subscriptions', profile, path)):
            try:
                log.info(f"FILE: \"{os.path.join('subscriptions', profile, path)}\" was not found.  Downloading it.")
                r = requests.get(source, stream=True, timeout=(5,None), verify=False)
                self.new_files += 1

                if r.status_code != 200:
                    print(r.url + ' :: ' + str(r.status_code))
                    log.error(r.url + ' :: ' + str(r.status_code))
                    
                    return False
                
                with open(os.path.join('subscriptions', profile, path), 'wb') as f:
                    r.raw.decode_content = True
                    shutil.copyfileobj(r.raw, f)
            except:
                print('Error getting: ' + source + ' (skipping)')
                log.error('Error getting: ' + source + ' (skipping)')
                
                return False
            finally:
                if r:
                    r.close()
        else:
            if not self.check_db(os.path.join(profile, path)):
                ## Check file:
                rh = requests.head(source)
                remote_file_size = int(rh.headers['Content-Length'])
                remote_file_hash = rh.headers['ETag'].replace('"', '')
                local_file_size = int(os.path.getsize(os.path.join('subscriptions', profile, path)))
                if "-" in remote_file_hash:
                    parts = remote_file_hash.split("-")[1]
                    chunk_size = self.calc_chunk_size(os.path.join('subscriptions', profile, path), int(parts))
                    local_file_hash = self.get_alternate_hash(os.path.join('subscriptions', profile, path), chunk_size)
                else:
                    local_file_hash = self.get_file_md5_hash(os.path.join('subscriptions', profile, path))
                                    
                
                if local_file_hash != remote_file_hash:
                    if local_file_size != remote_file_size:
                        err = f"BAD DOWNLOAD: \"{os.path.join('subscriptions', profile, path)}\" already exists but both data do not match. (Local size: {local_file_size} | Remote size: {remote_file_size} | Local hash: {local_file_hash} | Remote hash: {remote_file_hash})"
                    else:
                        err = f"BAD DOWNLOAD: \"{os.path.join('subscriptions', profile, path)}\" already exists but hash does not match while sizes do. (Local hash: {local_file_hash} | Remote hash: {remote_file_hash})"

                    log.error(err)
                    log.error(f"[RAW HEADERS]: {rh.headers}")                    
                    self.insert_into_downloads_failed(os.path.join(profile, path), remote_file_size, remote_file_hash, local_file_size, local_file_hash, err, str(rh.headers))
                else:
                    ## Generate contact sheet here
                    self.insert_into_downloads_cleared(os.path.join(profile, path), remote_file_size, remote_file_hash, local_file_size, local_file_hash)
            else:
                pass

            return True


    def get_content(self, profile, mediaType, api_location):
        log.info(f"Params: Profile - {profile} | Media Type - {mediaType} | API Location - {api_location}")
        posts = self.api_request(api_location, mediaType)
        log.info(f"Posts: {len(posts)}")
        if posts is not False:
            # log.info(f"POSTS: {posts}") ## Causes wierd behavior!  Probably a buffer overflow or something.
            if "error" in posts:
                print("\nERROR: " + posts["error"]["message"])
                log.error("ERROR: " + posts["error"]["message"])
                exit()
            if mediaType == "messages":
                posts = posts['list']
            if len(posts) > 0:
                print("Found " + str(len(posts)) + " " + mediaType)
                log.info("Found " + str(len(posts)) + " " + mediaType)
                self.processed_count = 0  ## Reset to zero
                for post in posts:
                    if "media" not in post or ("canViewMedia" in post and not post["canViewMedia"]):
                        continue
                    if mediaType == "purchased" and ('fromUser' not in post or post["fromUser"]["username"] != profile):
                        continue ## Only get paid posts from profile
                    if 'postedAt' in post: ## Get post date
                        postdate = str(post["postedAt"][:10])
                    elif 'createdAt' in post:
                        postdate = str(post["createdAt"][:10])
                    else:
                        postdate = "1970-01-01" ## Epoch failsafe if date is not present
                    if len(post["media"]) > 1: ## Don't put single photo posts in a subfolder
                        album = str(post["id"]) ## Album ID
                    else:
                        album = ""
                    for media in post["media"]:
                        if mediaType == "stories":
                            postdate = str(media["createdAt"][:10])
                        if "source" in media and "source" in media["source"] and media["source"]["source"] and ("canView" not in media or media["canView"]) or "files" in media:                            
                            self.download_media(profile, media, mediaType, postdate, album)
                            self.processed_count += 1
                            if self.processed_count % 100 == 0:
                                print(f"{datetime.datetime.now().strftime('%m/%d/%Y, %H:%M:%S %p')} - Processed files: {self.processed_count}")
                                log.info(f"Processed files: {self.processed_count}")
                            
                print(f"Total files processed: {self.processed_count}")
                log.info(f"Total files processed: {self.processed_count}")
                        
                print("Downloaded " + str(self.new_files) + " new " + mediaType)
                log.info("Downloaded " + str(self.new_files) + " new " + mediaType)
                self.new_files = 0
                
                log.info("+" * 75)
                
                return True
            else:
                log.error("No posts found!")
                
                return False


    def cleanup_bad_downloads(self, subscriptions):
        ## Just mismatched sizes for now and only for subbed accts
        bad_dl_cur = self.db.cursor()
        bad_dl_sql = "SELECT df.dlf_id, df.source, df.local_file_size, df.remote_file_size FROM downloads_failed df WHERE df.local_file_size != df.remote_file_size AND df.status = 'a';"
        
        bad_dl_cur.execute(bad_dl_sql)        
        bad_files = bad_dl_cur.fetchall()
        
        bad_files_count = len(bad_files)
        log.info(f"Bad files count: {bad_files_count}")
        
        if bad_files_count > 0:
            dlf_cur = self.db.cursor()
            dlf_sql = "UPDATE downloads_failed SET status = 'd' WHERE dlf_id = ?;"
            for bad_file in bad_files:
                id = bad_file['dlf_id']
                source = bad_file['source']
                db_file_size = bad_file['local_file_size']
                remote_file_size = bad_file['remote_file_size']
                profile = source.split("\\")[0]
                file_path = os.path.join(script_path, 'subscriptions', source)
                if profile in subscriptions:
                    ## Clear the file for redownload and mark the row in the db
                    log.info(f"Checking bad download file: \"{file_path}\"")
                    if (os.path.exists(file_path)):
                        local_file_size = int(os.path.getsize(file_path))
                        log.info(f"File sizes: Database-{db_file_size} | Local File-{local_file_size} | Remote-{remote_file_size}")
                        if local_file_size == remote_file_size:
                            log.info("Updating record... Done.")
                            dlf_cur.execute(dlf_sql, (id,))
                        else:
                            log.info(f"Deleting bad download file: \"{file_path}\"")
                            os.remove(file_path)  ## need to check data vs files before running for real
                    dlf_cur.execute(dlf_sql, (id,))
                else:
                    log.info(f"Profile \"{profile}\" no longer in active subscriptions.  Skipping.")
            
            self.db.commit()
            dlf_cur.close()


    def run(self):
        try:
            profile_list = self.get_subscriptions()

            log.info(f"Subscriptions: {profile_list}")

            for profile in profile_list:
                profile_id = str(self.get_user_info(profile)["id"])
                subs_dir = os.path.join('subscriptions', profile)
                if os.path.isdir(subs_dir):
                    print("\n" + profile + " exists.\nDownloading new media, skipping pre-existing.")
                    log.info(profile + " exists. Downloading new media, skipping pre-existing.")
                else:
                    print("\nDownloading content to " + subs_dir)
                    log.info("Downloading content to " + subs_dir)

                self.get_content(profile, "posts", "/users/" + profile_id + "/posts")
                self.get_content(profile, "archived", "/users/" + profile_id + "/posts/archived")
                self.get_content(profile, "stories", "/users/" + profile_id + "/stories")
                self.get_content(profile, "messages", "/chats/" + profile_id + "/messages")
                self.get_content(profile, "purchased", "/posts/paid")

            self.cleanup_bad_downloads(profile_list)
        
            return True
        finally:
            self.close_db()


def main():
    ## Session Variables (update every time you login or your browser updates)
    USER_ID = session_vars.USER_ID
    USER_AGENT = session_vars.USER_AGENT
    SESS_COOKIE = session_vars.SESS_COOKIE
    X_BC = session_vars.X_BC

    log.info("Beginning processing...")

    ofd = OFDownloader(USER_ID, USER_AGENT, SESS_COOKIE, X_BC)
    
    ofd.run()
    
    log.info("Processing finished.")
    runtime = time.time() - start_time
    log.info("Run time: {rt} minutes ({secs} seconds)".format(rt=round((runtime/60), 3), secs=round(runtime, 3)))
    log.info("-" * 120)


    

if __name__ == "__main__":
    main()
