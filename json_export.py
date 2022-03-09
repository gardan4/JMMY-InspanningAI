import json

def export(to_export):
    try:
        j = json.dumps(to_export)
        with open('export.json', 'w') as f:
            f.write(j)
            f.close()

    except:
        print("error")


