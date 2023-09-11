import os
import pathlib
import shutil

from urllib.parse import urlparse


import requests
from loguru import logger as log
from multi_rake import Rake

from models.subscriptions import Subscription
from models.media import MediaItem
from models.purchase import Purchase
from models.post import Post
from models.messages import Message

from windows_metadata import set_metadata
from ofdb import OFDB
from ofapi import OFClient
import util


POSTS_LIMIT = 50


class OFDownloader:
    def __init__(self):
        self.api = OFClient()
        # Database
        self.db = OFDB()

        # Options
        self.albums = False  #
        self.use_subfolders = True  #
        self.enable_tags = False
        self.processed_count = 0
        self.new_files = 0

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
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        with requests.Session() as session:
            request = session.get(source, stream=True, timeout=(5, None))
            request.raise_for_status()
            with open(path, "wb") as destFile:
                shutil.copyfileobj(request.raw, destFile)

    def download_media(self, subscription: Subscription, media: MediaItem, mediaType: str, postdate: str, album=""):
        source = media.get_source()
        if source is None:
            return None
        if not media.is_downloadable():
            return None

        path = self._get_media_path(media, mediaType, album, postdate, source)
        final_path = os.path.join("subscriptions", subscription.username, path)
        self.retrieve_file(source, final_path)
        return final_path

    def tag_media(self, media: Message | Post | Purchase, path: str | None):
        if not self.enable_tags or path is None or media.text is None:
            return
        text = util.cleanup_text(media.text)
        rake = Rake()
        keywords = [item[0] for item in rake.apply(text)[:20]]
        set_metadata(path, "System.Keywords", keywords)
        set_metadata(path, "System.Comment", text)

    def _get_posts(self, subscription: Subscription, mediaType: str):
        if mediaType == "messages":
            posts = self.api.get_messages(subscription)
        elif mediaType == "purchased":
            posts = self.api.get_purchases()
        elif mediaType == "posts":
            posts = self.api.get_posts(subscription)
        else:
            raise NotImplementedError(f"Unhandled mediaType: {mediaType}")
        return posts

    def get_content(self, subscription: Subscription, mediaType: str):
        self.processed_count = 0  # Reset to zero
        posts = self._get_posts(subscription, mediaType)
        log.info("Found " + str(len(posts)) + " " + mediaType)
        for post in posts:
            if not post.is_viewable():
                continue

            # TODO: why would you have purchased from not your username
            # if mediaType == "purchased" and (
            #     "fromUser" not in post or post["fromUser"]["username"] != subscription.username
            # ):
            # continue  # Only get paid posts from profile

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
                    continue

                path = self.download_media(subscription, media, mediaType, postdate, album)
                self.tag_media(post, path)
                self.processed_count += 1
                if self.processed_count % 100 == 0:
                    log.info(f"Processed files: {self.processed_count}")

        log.info(f"Total files processed: {self.processed_count}")
        log.info("Downloaded " + str(self.new_files) + " new " + mediaType)
        self.new_files = 0
        return True

    def cleanup_bad_downloads(self, subscriptions):
        return

    @log.catch
    def run(self, targets):
        try:
            subscription_list = self.api.get_subscriptions()

            log.info(f"Subscriptions: {subscription_list}")
            for subscription in subscription_list:
                subs_dir = os.path.join("subscriptions", subscription.username)
                if os.path.isdir(subs_dir):
                    log.info(subscription.username + " exists. Downloading new media, skipping pre-existing.")
                else:
                    log.info("Downloading content to " + subs_dir)
                if targets == "all":
                    # self.get_content(subscription, "posts")
                    self.get_content(subscription, "archived")
                    self.get_content(subscription, "stories")
                    self.get_content(subscription, "messages")
                    self.get_content(subscription, "purchased")
                else:
                    self.get_content(subscription, targets)

            # self.cleanup_bad_downloads(profile_list)

            return True
        finally:
            self.db.close_db()
