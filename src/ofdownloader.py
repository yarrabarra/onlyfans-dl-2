import os
import pathlib
import shutil

from urllib.parse import urlparse

import requests
from loguru import logger as log
from rake_nltk import Rake

from models.profile import Profile
from models.media import MediaItem
from models.purchase import Purchase
from models.post import Post
from models.messages import Message

from windows_metadata import set_metadata
from ofdb import OFDB
from ofapi import OFClient, OFDRMClient
import util

DRM_SUPPORT = False
POSTS_LIMIT = 50


class OFDownloader:
    def __init__(self):
        self.api = OFClient()
        self.drm = OFDRMClient()

        # Database
        self.db = OFDB()

        # Options
        self.albums = False  #
        self.use_subfolders = True  #
        self.enable_tags = False
        self.processed_count = 0
        self.new_files: dict[str, list[str]] = {}

    def _get_media_path(self, media: MediaItem, mediaType: str, album: str, postdate: str, source: str):
        # Pull just the extension out of the source URL
        suffix = pathlib.Path(urlparse(source).path).suffix
        filename = f"{postdate}_{media.id}{suffix}"
        if self.albums and album and media.type == "photo":
            path = os.path.join("photos", f"{postdate}_{album}", filename)
        else:
            path = os.path.join(f"{media.type}s", filename)
        if self.use_subfolders and mediaType != "posts":
            path = os.path.join(mediaType, path)
        return path

    def retrieve_file(self, source: str, dest: str):
        path = pathlib.Path(dest)
        if path.exists():
            return False
        path.parent.mkdir(parents=True, exist_ok=True)
        with requests.Session() as session:
            request = session.get(source, stream=True, timeout=(5, None))
            request.raise_for_status()
            with open(path, "wb") as destFile:
                shutil.copyfileobj(request.raw, destFile)
        return True

    def download_media(
        self, subscription: Profile, media: MediaItem, mediaType: str, postdate: str, album="", post_id=0
    ):
        source = media.get_source()
        if source is None:
            log.debug(f"No source or files for media {media.id}")
            return None
        if not media.is_downloadable():
            return None
        if media.is_drm():
            if not DRM_SUPPORT:
                return None
            pssh = util.parse_pssh_from_mpd(source)
            if pssh is None:
                return None
            license = self.drm.get_drm_license(pssh, media.id, post_id)
            exit()

        path = self._get_media_path(media, mediaType, album, postdate, source)
        final_path = os.path.join("subscriptions", subscription.username, path)
        # TODO: Remove hack to avoid double downloads until local DB is implemented
        if mediaType == "messages":
            purchasedPath = pathlib.Path(final_path.replace("messages", "purchased")).parent
            for matchPath in purchasedPath.glob(f"*_{media.id}*"):
                if matchPath.exists():
                    log.debug(f"Skipping {path} because already exists in {matchPath}")
                    return None
        if self.retrieve_file(source, final_path):
            return final_path
        return None

    def tag_media(self, media: Message | Post | Purchase, path: str | None):
        if not self.enable_tags or path is None or media.text is None:
            return
        text = util.cleanup_text(media.text)
        rake = Rake()
        rake.extract_keywords_from_text(text)
        keywords = [item[0] for item in rake.get_ranked_phrases()[:20]]
        set_metadata(path, "System.Keywords", keywords)
        set_metadata(path, "System.Comment", text)

    def _get_posts(self, subscription: Profile, mediaType: str):
        if mediaType == "messages":
            posts = self.api.get_messages(subscription)
        elif mediaType in "purchased":
            posts = self.api.get_purchases()
        elif mediaType == "posts":
            posts = self.api.get_posts(subscription)
        else:
            raise NotImplementedError(f"Unhandled mediaType: {mediaType}")
        return posts

    def get_content(self, subscription: Profile, mediaType: str):
        self.processed_count = 0  # Reset to zero
        posts = self._get_posts(subscription, mediaType)
        log.info("Found " + str(len(posts)) + " " + mediaType)
        for post in posts:
            if not post.is_viewable():
                continue
            if isinstance(post, Purchase) and post.fromUser is not None:
                if post.fromUser.username != subscription.username:
                    # Skip purchases that are not from the subscription we're querying
                    continue

            postdate = post.get_postdate()
            album = ""
            if len(post.media) > 1:  # Don't put single photo posts in a subfolder
                album = str(post.id)  # Album ID

            for media in post.media:
                # TODO: Find a sub with stories
                # if mediaType == "stories":
                #     postdate = str(media["createdAt"][:10])
                if not media.canView:
                    continue
                if media.source.source is None and media.files is None:
                    log.info(f"No media source: {media.id}")
                    continue
                path = self.download_media(subscription, media, mediaType, postdate, album, post.id)
                self.processed_count += 1
                if self.processed_count % 100 == 0:
                    log.info(f"Processed files: {self.processed_count}")
                if path is not None:
                    self.new_files.setdefault(subscription.name, [])
                    self.new_files[subscription.name].append(path)
                self.tag_media(post, path)

        log.info(f"Total files processed: {self.processed_count}")
        return True

    def cleanup_bad_downloads(self, subscriptions):
        return

    @log.catch
    def run(self, target: str, subscriptions):
        try:
            subscription_list = self.api.get_subscriptions()

            log.info(f"Subscriptions: {subscription_list}")
            for subscription in subscription_list:
                if subscriptions != "all":
                    if subscription.username not in subscriptions.split(","):
                        log.debug(f"Not part of subscription targets, skipping {subscription.username}")
                        continue
                subs_dir = os.path.join("subscriptions", subscription.username)
                if os.path.isdir(subs_dir):
                    log.info(f"{subscription.username} exists. Downloading new media, skipping pre-existing.")
                else:
                    log.info(f" New subscription, downloading content to {subs_dir}")
                if target == "all":
                    # TODO: Archived/stories
                    # self.get_content(subscription, "archived")
                    # self.get_content(subscription, "stories")
                    self.get_content(subscription, "posts")
                    self.get_content(subscription, "purchased")
                    self.get_content(subscription, "messages")
                    continue
                self.get_content(subscription, target)
            return True
        finally:
            self.db.close_db()
