import subprocess
import os.path
import json
import time
from typing import Any
import config


class Data:
    def __init__(
        self, data_file_path: str = config.DATA_FILE_PATH, preload: bool = False
    ) -> None:
        super().__init__()
        self.data_file_path = data_file_path
        data = None
        if preload:
            data = self.load()  # load from existing data file
            if (  # check whether the data file is valid
                not data
                or abs(time.time() - data["timestamp"]) / 60
                > config.DATA_RENEW_THRESHOLD_IN_MIN
            ):
                data = self.fetch()
        self.data = data

    def load(self, path: str = None) -> Any:
        data = None
        if not path:
            path = self.data_file_path

        if os.path.exists(path):
            with open(path, "r") as fp:
                data_ser = json.load(fp)
                data = json.loads(data_ser)

        self.data = data
        return data

    def fetch(self, url: str = config.DATA_API_URL) -> Any:
        # fetcch data
        print("\n-------------Start fetching data-------------")
        r = subprocess.check_output(f"curl {url}", shell=True)
        print("\n-------------Finish fetching data-------------")

        print("\n-------------Start serializing data-------------")
        json_data = json.loads(r.decode("utf-8"))

        # indexing based on question frontend id
        data = {}
        for q in json_data["stat_status_pairs"]:
            qid = q["stat"]["frontend_question_id"]
            if qid in data:
                raise RuntimeError(f"question #{qid} already exists, duplicate!")
            else:
                data[str(qid).zfill(config.QID_PADDING_SIZE)] = q

        print(f"Total feteched questions: {len(data)} ")
        data["timestamp"] = time.time()
        print("\n-------------Finish serializing data-------------")

        return data

    def do_persistence(
        self, data_serialized: str = None, path=config.DATA_FILE_PATH
    ) -> None:
        print("\n-------------Start data persistence-------------")
        if not data_serialized:
            data_serialized = json.dumps(self.data)

        if not data_serialized or not path:
            raise RuntimeError("invalid input data or file path.")

        with open(path, "w") as fp:
            json.dump(data_serialized, fp)
        print("\n-------------Finish data persistence-------------")
