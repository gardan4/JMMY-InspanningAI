import json


def export_dump(to_export, out_file):
    try:
        j = json.dumps(to_export)
        with open(out_file, 'w') as f:
            f.write(j)
            f.close()

    except Exception as e:
        print(e)


def export_pretty(to_export, out_file):
    try:
        # TODO: PRETTY JSON
        json_object = json.loads(str(to_export))
        j = json.dumps(json_object, indent=3)

        with open(out_file, 'w') as f:
            f.write(j)
            f.close()

    except Exception as e:
        print(e)
