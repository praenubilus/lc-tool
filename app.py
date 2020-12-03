import subprocess
import json
import config


def main():
    # fetcch data
    print("\n-------------Start fetching data-------------")
    r = subprocess.check_output(f"curl {config.DATA_API_URL}", shell=True)
    str_r = r.decode("utf-8")
    print("\n-------------Finish fetching data-------------")

    json_data = json.loads(str_r)

    print("Job done")

if __name__ == "__main__":
    main()