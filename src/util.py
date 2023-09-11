import os
import json
import hashlib


def calc_chunk_size(file_path, target_chunks):
    mb = 1048576
    file_size = os.path.getsize(file_path)
    part_size = file_size / target_chunks
    rem = part_size % mb
    if rem > 0:
        chunk_size = part_size + mb - rem
        return int(chunk_size)
    else:
        return int(part_size)


def get_file_md5_hash(file_path, chunk_size=1048576):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            hash_md5.update(chunk)

    return hash_md5.hexdigest()


def get_alternate_hash(file_path, chunk_size=1048576):
    hash_list = []
    hash_md5 = hashlib.md5

    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            hash_list.append(hash_md5(chunk).digest())

    return f"{hashlib.md5(b''.join(hash_list)).hexdigest()}-{len(hash_list)}"


def cleanup_text(text):
    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "*": "",
        "&lt;": "<",
        "&gt;": ">",
        "<br />": "\n",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def get_session_config():
    if not os.path.exists("session_vars.json"):
        raise ValueError("Missing session_vars.json, see README.md for configuration")
    with open("session_vars.json", "r") as jsonFile:
        config = json.load(jsonFile)
        for var in ("USER_ID", "USER_AGENT", "SESS_COOKIE", "X_BC"):
            if len(config.get(var, "")) == 0:
                raise ValueError(f"Config key {var} is missing or empty")
    return config


# TODO: File hashing check redo that handles tagged files
# else:
#     if not self.check_db(os.path.join(profile, path)):
#         # Check file:
#         rh = requests.head(source)
#         remote_file_size = int(rh.headers['Content-Length'])
#         remote_file_hash = rh.headers['ETag'].replace('"', '')
#         local_file_size = int(os.path.getsize(os.path.join('subscriptions', profile, path)))
#         if "-" in remote_file_hash:
#             parts = remote_file_hash.split("-")[1]
#             chunk_size = self.calc_chunk_size(os.path.join('subscriptions', profile, path), int(parts))
#             local_file_hash = self.get_alternate_hash(os.path.join('subscriptions', profile, path), chunk_size)
#         else:
#             local_file_hash = self.get_file_md5_hash(os.path.join('subscriptions', profile, path))

# if local_file_hash != remote_file_hash:
#     if local_file_size != remote_file_size:
#         err = f"BAD DOWNLOAD: \"{os.path.join('subscriptions', profile, path)}\" already exists but both data do not match. (Local size: {local_file_size} | Remote size: {remote_file_size} | Local hash: {local_file_hash} | Remote hash: {remote_file_hash})"
#     else:
#         err = f"BAD DOWNLOAD: \"{os.path.join('subscriptions', profile, path)}\" already exists but hash does not match while sizes do. (Local hash: {local_file_hash} | Remote hash: {remote_file_hash})"

#     log.error(err)
#     log.error(f"[RAW HEADERS]: {rh.headers}")
#     self.insert_into_downloads_failed(os.path.join(profile, path), remote_file_size, remote_file_hash, local_file_size, local_file_hash, err, str(rh.headers))
# else:
#     # Generate contact sheet here
#     self.insert_into_downloads_cleared(os.path.join(profile, path), remote_file_size, remote_file_hash, local_file_size, local_file_hash)
# Just mismatched sizes for now and only for subbed accts
# bad_dl_cur = self.db.cursor()
# bad_dl_sql = "SELECT df.dlf_id, df.source, df.local_file_size, df.remote_file_size FROM downloads_failed df WHERE df.local_file_size != df.remote_file_size AND df.status = 'a';"

# bad_dl_cur.execute(bad_dl_sql)
# bad_files = bad_dl_cur.fetchall()

# bad_files_count = len(bad_files)
# log.info(f"Bad files count: {bad_files_count}")

# if bad_files_count > 0:
#     dlf_cur = self.db.cursor()
#     dlf_sql = "UPDATE downloads_failed SET status = 'd' WHERE dlf_id = ?;"
#     for bad_file in bad_files:
#         id = bad_file["dlf_id"]
#         source = bad_file["source"]
#         db_file_size = bad_file["local_file_size"]
#         remote_file_size = bad_file["remote_file_size"]
#         profile = source.split("\\")[0]
#         file_path = os.path.join(script_path, "subscriptions", source)
#         if profile in subscriptions:
#             # Clear the file for redownload and mark the row in the db
#             log.info(f'Checking bad download file: "{file_path}"')
#             if os.path.exists(file_path):
#                 local_file_size = int(os.path.getsize(file_path))
#                 log.info(
#                     f"File sizes: Database-{db_file_size} | Local File-{local_file_size} | Remote-{remote_file_size}"
#                 )
#                 if local_file_size == remote_file_size:
#                     log.info("Updating record... Done.")
#                     dlf_cur.execute(dlf_sql, (id,))
#                 else:
#                     log.info(f'Deleting bad download file: "{file_path}"')
#                     os.remove(file_path)  # need to check data vs files before running for real
#             dlf_cur.execute(dlf_sql, (id,))
#         else:
#             log.info(f'Profile "{profile}" no longer in active subscriptions.  Skipping.')

#     self.db.commit()
#     dlf_cur.close()
