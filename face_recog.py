import face_recognition
import cv2
import numpy as np
import tempsensor as temp
from elasticsearch import Elasticsearch
import datetime

temp.temp_init()
es = Elasticsearch("http://192.168.100.31:9200")
found_flag = False
unknown_found_flag = False
video_capture = cv2.VideoCapture("http://192.168.100.12:8080/?action=stream")

known_face_encodings = []
known_face_names = []

res = es.search(index="user_info", doc_type="_doc", body={"query": {"match_all": {}}})
for i in range(len(res["hits"]["hits"])):
    known_face_encodings.append(res["hits"]["hits"][i]["_source"]["face_info"])
    known_face_names.append(res["hits"]["hits"][i]["_source"]["name"])

face_locations = []
face_encodings = []
face_names = []
process_this_frame = True


def utc_time():
    return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


while True:
    ret, frame = video_capture.read()
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = small_frame[:, :, ::-1]

    if process_this_frame:
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(
                known_face_encodings, face_encoding, tolerance=0.52
            )
            name = "Unknown"
            temperature = temp.sense_object() / 100

            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]
                if found_flag == False and 33 < temperature < 37:
                    found_flag = not found_flag
                    doc = {"userID": name, "login_time": utc_time(), "temperature": temperature}
                    es.index(index="login_data", doc_type="_doc", body=doc)
            elif name == "Unknown" and unknown_found_flag == False:
                es.index(
                    index="unknown_login",
                    doc_type="_doc",
                    body={"name": name, "login_time": utc_time()},
                )
                unknown_found_flag = not unknown_found_flag
            face_names.append(name)

    process_this_frame = not process_this_frame
    if not face_locations:
        found_flag = False
        unknown_found_flag = False

    for (top, right, bottom, left), name in zip(face_locations, face_names):
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        temperature = temp.sense_object() / 100
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
        cv2.putText(
            frame, str(temperature + 2) + " C", (left + 6, top - 6), font, 1.0, (255, 255, 255), 1
        )

    cv2.imshow("Video", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


temp.clean_up()
video_capture.release()
cv2.destroyAllWindows()
