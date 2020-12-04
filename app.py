import subprocess
import os.path
import json
import time
import config


def main():

    # check existing data
    data = None
    if os.path.exists(config.DATA_FILE_PATH):
        with open(config.DATA_FILE_PATH, "r") as fp:
            data_ser = json.load(fp)
            data = json.loads(data_ser)

    if (
        not data
        or abs(time.time() - data["timestamp"]) / 60
        > config.DATA_RENEW_THRESHOLD_IN_MIN
    ):
        # fetcch data
        print("\n-------------Start fetching data-------------")
        r = subprocess.check_output(f"curl {config.DATA_API_URL}", shell=True)
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
        data_ser = json.dumps(data)
        print("\n-------------Finish serializing data-------------")

        print("\n-------------Start data persistence-------------")
        with open(config.DATA_FILE_PATH, "w") as fp:
            json.dump(data_ser, fp)
        print("\n-------------Finish data persistence-------------")

    for i in range(151,161):
        qid = str(i).zfill(config.QID_PADDING_SIZE)
        print(f"\nquestion #{qid}: {data[qid]['stat']['question__title']}")
        print(f"URL: {config.PROBLEM_URL_PREFIX+data[qid]['stat']['question__title_slug']}")
    print("-------------Job done-------------")
    

if __name__ == "__main__":
    main()