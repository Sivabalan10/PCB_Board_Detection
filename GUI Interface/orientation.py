import cv2
from ultralytics import YOLO
import time
import requests


def visit_ip(ip_address):
    print("sds")
    try:
        response = requests.get(f"http://{ip_address}")
        if response.status_code == 200:
            print(f"Successfully visited {ip_address}")
        else:
            print(f"Failed to visit {ip_address}. Status code: {response.status_code}")
    except requests.RequestException as e:
        print(f"Failed to visit {ip_address}. Error: {e}")

def main1():
    ip_addresses = ["192.168.234.74/3", "192.168.234.74/0"]  # Replace x.x.x.x and y.y.y.y with your actual IP addresses
    for ip in ip_addresses:
        visit_ip(ip)

def main2():
    ip_addresses = ["192.168.234.74/1", "192.168.234.74/0"]  # Replace x.x.x.x and y.y.y.y with your actual IP addresses
    for ip in ip_addresses:
        visit_ip(ip)

def main3():
    ip_addresses = ["192.168.234.74/5", "192.168.234.74/0"]  # Replace x.x.x.x and y.y.y.y with your actual IP addresses
    for ip in ip_addresses:
        visit_ip(ip)

# Load the YOLOv8 model
model = YOLO('orientation.pt')

# Open the video file
cap = cv2.VideoCapture(1)

count=0

# Loop through the video frames
while cap.isOpened():
    # Read a frame from the video
    success, frame = cap.read()

    if success:
        # Run YOLOv8 inference on the frame
        results = model(frame)

        # Visualize the results on the frame
        annotated_frame = results[0].plot()
        # print(results[0].verbose())

        lis = results[0].verbose().split(',')
        print(lis)

        if len(lis) == 8:
            cv2.rectangle(annotated_frame, (30, 20), (200, 70), (0, 0, 0), -1)
            cv2.putText(annotated_frame, "ALL OK", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        else:
            if ' 1 regulator' not in lis:
                cv2.rectangle(annotated_frame, (30, 20), (400, 70), (0, 0, 0), -1)
                cv2.putText(annotated_frame, "Regulator Missing", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                if count==0:
                    count+=1
                    main1()
                

            elif ' 1 capacitor' not in lis:
                cv2.rectangle(annotated_frame, (30, 20), (400, 70), (0, 0, 0), -1)
                cv2.putText(annotated_frame, "Capacitor Missing", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                if count==0:
                    count+=1
                    main2()
            elif ' 1 transistor' not in lis:
                cv2.rectangle(annotated_frame, (30, 20), (400, 70), (0, 0, 0), -1)
                cv2.putText(annotated_frame, "Transistor Missing", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                if count==0:
                    count+=1
                    main3()



        # Display the annotated frame
        cv2.imshow("YOLOv8 Inference", annotated_frame)
        # Break the loop if 'q ' is pressed
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord("q"):
            break
        elif key == ord("r"):
            count = 0
            print("Count reset to 0.")
    else:
        # Break the loop if the end of the video is reached
        break

# Release the video capture object and close the display window
cap.release()
cv2.destroyAllWindows()