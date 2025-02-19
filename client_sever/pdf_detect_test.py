import cv2
import numpy as np

def biggest_contour(contours):
    biggest = np.array([])
    max_area = 0
    for i in contours:
        area = cv2.contourArea(i)
        if  area > 45000  :
            print('aree',area)
            peri = cv2.arcLength(i, True)
            approx = cv2.approxPolyDP(i, 0.01 * peri, True)
            if area > max_area and len(approx) == 4:
                biggest = approx
                max_area = area
    return biggest

def detect_pdf(image):
    is_pdf = False
    is_object = False
    is_contract = False
    frame_image = None
    pdf_detected_contours = []
    
    img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(img_gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1,2))
    detected_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)

    # Find contours
    contours, _ = cv2.findContours(detected_lines, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    if contours:
        biggest = biggest_contour(contours)
        if biggest.size != 0:
            is_object = True
            points = biggest.reshape(4, 2)
            input_points = np.zeros((4, 2), dtype="float32")

            # Calculate the four corners of the contour
            points_sum = points.sum(axis=1)
            input_points[0] = points[np.argmin(points_sum)]
            input_points[3] = points[np.argmax(points_sum)]

            points_diff = np.diff(points, axis=1)
            input_points[1] = points[np.argmin(points_diff)]
            input_points[2] = points[np.argmax(points_diff)]

            # Calculate width and height
            bottom_width = np.linalg.norm(input_points[2] - input_points[3])
            top_width = np.linalg.norm(input_points[1] - input_points[0])
            right_height = np.linalg.norm(input_points[1] - input_points[2])
            left_height = np.linalg.norm(input_points[0] - input_points[3])

            max_width = max(int(bottom_width), int(top_width))
            max_height = max(int(right_height), int(left_height))
            # Check if the aspect ratio is close to A4 (1.414)
            ratio = max_height / max_width if max_width != 0 else 0
            print(abs(ratio - 1.414))
            if abs(ratio - 1.414) < 0.2:
                is_pdf = True
                max_width = int(max_height/1.414)
                # Perspective transformation
                converted_points = np.float32([[0, 0], [max_height, 0], [0, max_width], [max_height, max_width]])
                matrix = cv2.getPerspectiveTransform(input_points, converted_points)
                image = cv2.warpPerspective(image, matrix, (max_height, max_width))
                # Find contours again after transformation
                contours, _ = cv2.findContours(detected_lines, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                contours = sorted(contours, key=cv2.contourArea, reverse=True)

                # Filter contours for potential text lines
                pdf_detected_contours = list(set([cv2.boundingRect(c) for c in contours if cv2.boundingRect(c)[3] > image.shape[0]*3/5 and cv2.boundingRect(c)[2] < image.shape[1] - 100]))

        # Convert image to RGBA and then to BGRA
        img_rgba = cv2.cvtColor(detected_lines, cv2.COLOR_GRAY2BGR)
        frame_image = img_rgba.copy()
       
        # Check if the detected lines resemble a contract
        line_count = 0
        if is_pdf:
            for x, y, w, h in pdf_detected_contours:
                if  frame_image.shape[1] /2 < x  < frame_image.shape[1] - 50:
                    line_count += 1
                    cv2.rectangle(frame_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            if 2 < line_count < 7:
                is_contract = True

        # Convert image to bytes
    return image,frame_image, is_object, is_pdf, is_contract

if __name__ == "__main__":
    try:
        cam = cv2.VideoCapture(1,cv2.CAP_MSMF)
        cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1920) 
        while True:
            ret, image = cam.read()
            cv2.imshow("real image", image)
            if cv2.waitKey(1) & 0xFF == ord('f'):
                image,frame_image, is_object, is_pdf, is_contract = detect_pdf(image)
                if is_contract:
                    print("Contract detected")
                    cropped = image[:, int(image.shape[1]*1/3):]
                    cv2.imwrite("image.jpg", cropped)
                else:
                    print(is_pdf,is_object,is_contract)
                    print("No contract detected")
    except Exception as e:
        print(f"An error occurred during pump operation: {e}")
    finally:
        cam.release()
        cv2.destroyAllWindows() 