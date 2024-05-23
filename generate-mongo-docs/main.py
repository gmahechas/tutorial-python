from pymongo import MongoClient

client = MongoClient(
    "mongodb://root:root@10.1.0.231:30001/smart_flows?authSource=admin", 27017
)
db = client["smart_flows"]
collection = db["flows"]

number_of_documents = 200
documents = []

for i in range(number_of_documents):
    document = {
        "settings": {
            "defaults": {
                "tts": {"cloudProvider": "AWS", "voice": "Joanna"},
                "error_audio": {
                    "timeout": [],
                    "invalid": [],
                    "transfer": [],
                    "maxAttempts": [],
                    "xrefToneMsg": [],
                    "xrefTone": "",
                },
            },
            "endpoints": [],
            "exports": [],
            "utcOffset": "",
            "utcName": "",
            "dstOff": False,
        },
        "smartProducts": {
            "type": None,
            "level": 0,
            "tier": None,
            "typeDeployed": None,
            "levelDeployed": 0,
            "tierDeployed": None,
        },
        "nodes": [
            {
                "disabled": False,
                "id": "1",
                "verb": "ICALL",
                "verbId": "undefined",
                "name": "ICALL",
                "description": "ICALL",
                "settings": {
                    "__verb": "ICALL",
                    "version": "1.0",
                    "pci": False,
                    "pciTTS": False,
                    "single": False,
                    "multi": False,
                },
                "context": {
                    "imported": {},
                    "exported": {
                        "userVariables": [],
                        "variables": [
                            "ICALL_1.CHANNEL_ID",
                            "ANI",
                            "DNIS",
                            "UUI",
                            "DateTime.currentTimeText",
                            "DateTime.currentDateText",
                            "DateTime.currentMonthText",
                            "DateTime.currentDayText",
                            "DateTime.currentYearText",
                            "DateTime.currentDayOfWeekText",
                            "DateTime.currentTime",
                            "DateTime.tzOffsetSeconds",
                            "DateTime.timestamp",
                            "DateTime.currentTimeSec",
                            "SESSION_ID",
                        ],
                        "fromVerb": "ICALL",
                        "keys": "ALL:",
                        "pass": True,
                    },
                },
                "x": 269,
                "y": 176,
            },
            {
                "disabled": False,
                "id": "2",
                "verb": "SMS",
                "verbId": "undefined",
                "name": "SMS",
                "description": "SMS",
                "settings": {
                    "__verb": "SMS",
                    "version": "1.0",
                    "pci": False,
                    "pciTTS": False,
                    "to": "$ANI",
                    "from": "$DNIS",
                    "msg": "dddd",
                    "dlr": False,
                    "requestDeliveryReceipt": False,
                    "media": "",
                    "mediaAttachmentArray": [],
                },
                "context": {
                    "imported": {
                        "1": {
                            "userVariables": [],
                            "variables": [
                                "ICALL_1.CHANNEL_ID",
                                "ANI",
                                "DNIS",
                                "UUI",
                                "DateTime.currentTimeText",
                                "DateTime.currentDateText",
                                "DateTime.currentMonthText",
                                "DateTime.currentDayText",
                                "DateTime.currentYearText",
                                "DateTime.currentDayOfWeekText",
                                "DateTime.currentTime",
                                "DateTime.tzOffsetSeconds",
                                "DateTime.timestamp",
                                "DateTime.currentTimeSec",
                                "SESSION_ID",
                            ],
                            "fromVerb": "ICALL",
                            "keys": "ALL:",
                            "pass": True,
                        }
                    },
                    "exported": {"userVariables": [], "variables": []},
                },
                "x": 453,
                "y": 267,
            },
        ],
        "links": [
            {
                "verb": "L",
                "id": "269830",
                "x1": 429,
                "y1": 191,
                "x2": 443,
                "y2": 288,
                "from": "1",
                "fromPort": "2001",
                "fromSize": 1,
                "to": "2",
                "toPort": "1001",
                "toSize": 1,
                "disabled": False,
            }
        ],
        "nestedItems": [],
        "tags": [],
        "location": "US",
        "versioning": {
            "currentVersion": "664f65ed9f420e291c5dd907",
            "currentHistory": "664f65ed9f420e291c5dd90a",
            "currentVersionDeployed": None,
            "currentHistoryDeployed": None,
        },
        "name": f"Flow_{i + 1}",
        "build": "0",
        "origin": "SF",
        "eventHandlers": {
            "exit": {"nodes": [], "links": []},
            "error": {"nodes": [], "links": []},
        },
        "type": "nested",
        "published": False,
        "flowExt": {"$oid": "664f65ed9f420e291c5dd903"},
        "trigger": "ICALL",
        "version": "2024052315510991",
        "deployed": False,
        "createdDate": {"$date": "2024-05-23T15:51:09.934Z"},
        "createdBy": "gmahecha",
        "customerId": "9999999",
        "modifiedDate": {"$date": "2024-05-23T15:51:09.934Z"},
        "modifiedBy": "gmahecha",
        "__v": 0,
    }
    documents.append(document)

collection.insert_many(documents)
client.close()
print(f"Inserted {number_of_documents} documents")
