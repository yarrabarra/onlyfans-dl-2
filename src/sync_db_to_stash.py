import requests

from ofdb import OFDB

from models.post_sql import Content, Media, ContentTagLink
from sqlmodel import Session, select
from pathlib import Path
from time import sleep
from loguru import logger as log


def load_gql(query_name):
    gql_path = Path(__file__).parent / "graphql"
    with open(gql_path / f"{query_name}.gql", "r") as fileobj:
        return fileobj.read()


def flatten(items):
    return [item for row in items for item in row]


class GQLAPI:
    base_url = "http://localhost:9999"
    login_url = f"{base_url}/login"
    graphql_url = f"{base_url}/graphql"
    auth = {"username": "admin", "password": "admin", "returnURL": ""}
    headers = {"Content-Type": "application/json"}
    tags: dict[str, str] = {}

    def __init__(self):
        self.session = requests.Session()
        login_result = self.session.post(self.login_url, data=self.auth)
        login_result.raise_for_status()
        self.get_tags()

    def _gql(self, data):
        request = self.session.post(self.graphql_url, json=data, headers=self.headers)
        request.raise_for_status()
        return request.json().get("data", {})

    def metadata_scan(self) -> dict[str, int]:
        metadata_scan_query = {
            "operationName": "MetadataScan",
            "variables": {
                "input": {
                    "scanGenerateCovers": True,
                    "scanGeneratePreviews": True,
                    "scanGenerateImagePreviews": True,
                    "scanGenerateSprites": True,
                    "scanGeneratePhashes": False,
                    "scanGenerateThumbnails": True,
                    "scanGenerateClipPreviews": True,
                }
            },
            "query": load_gql("metadataScan"),
        }
        return self._gql(metadata_scan_query)

    def metadata_auto_tag(self) -> dict[str, int]:
        metadata_auto_tag_query = {
            "operationName": "MetadataAutoTag",
            "variables": {"input": {"performers": ["*"], "studios": ["*"], "tags": ["*"]}},
            "query": load_gql("metadataAutoTag"),
        }
        return self._gql(metadata_auto_tag_query)

    def get_job_queue(self) -> dict[int, dict]:
        job_queue_query = {
            "operationName": "JobQueue",
            "variables": {},
            "query": load_gql("jobQueue"),
        }
        results = self._gql(job_queue_query).get("jobQueue", [])
        if results is None:
            return {}
        data = {item["id"]: item for item in results}
        return data

    def get_tags(self):
        all_tags_query = {
            "operationName": "AllTags",
            "variables": {},
            "query": load_gql("allTags"),
        }
        data = self._gql(all_tags_query)
        for item in data["allTags"]:
            self.tags[item["name"]] = str(item["id"])

    def find_scenes(self):
        find_scene_query = {
            "operationName": "FindScenes",
            "variables": {
                "filter": {"q": "", "page": 1, "per_page": 5000, "sort": "date", "direction": "DESC"},
                "performer_filter": {},
            },
            "query": load_gql("findScenes"),
        }
        data = self._gql(find_scene_query)
        return data["findScenes"]

    def upsert_tag(self, name):
        if name in self.tags:
            return
        create_tag_query = {
            "operationName": "TagCreate",
            "variables": {"input": {"name": name}},
            "query": load_gql("tagCreate"),
        }
        data = self._gql(create_tag_query)
        self.tags[name] = data["tagCreate"]["id"]
        return data

    def update_scene(self, scene_id: int, content: Content):
        date = content.get_date()
        tag_ids = [self.tags[tag.name] for tag in content.tags]
        query = {
            "operationName": "SceneUpdate",
            "variables": {"input": {"id": scene_id, "date": date, "tag_ids": tag_ids, "details": content.text}},
            "query": load_gql("sceneUpdate"),
        }
        result = self._gql(query)
        return result

    def wait_for_jobs(self, jobs):
        job_ids = flatten(job.values() for job in jobs)
        log.info(f"Waiting for {len(job_ids)} jobs to complete: {jobs}")
        while True:
            sleep(0.5)
            queue = self.get_job_queue()
            if any(job_id in queue.keys() for job_id in job_ids):
                continue
            break


if __name__ == "__main__":
    db = OFDB()
    gqlapi = GQLAPI()

    with Session(db.engine) as session:
        jobs: list[dict[str, int]] = []
        jobs.append(gqlapi.metadata_scan())
        jobs.append(gqlapi.metadata_auto_tag())
        gqlapi.wait_for_jobs(jobs)
        scenes = gqlapi.find_scenes()["scenes"]
        for scene in scenes:
            scene_path = scene["files"][0]["path"].replace("..\\of3\\", "")
            if "subscriptions" not in scene_path:
                # print("skipping", scene_path)
                continue
            statement = select(Media).where(Media.file_path == scene_path).limit(1)
            result = session.exec(statement).first()
            if result is None:
                # print("none found", scene_path)
                continue

            statement = select(Content).where(Content.id == result.content_id)  # type: ignore
            content = session.exec(statement).first()
            if content is None:
                continue

            for tag in content.tags:
                gqlapi.upsert_tag(tag.name)
            update_result = gqlapi.update_scene(scene["id"], content)
