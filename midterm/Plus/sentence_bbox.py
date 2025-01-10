import os
import requests

# Base URL for the API
API_BASE_URL = "https://tools.clc.hcmus.edu.vn"
UPLOAD_ENDPOINT = "/api/web/clc-sinonom/image-upload"
OCR_ENDPOINT = "/api/web/clc-sinonom/image-ocr"

# Default header for HTTP requests
HEADER = {"User-Agent": "SinoCharImg"}

def upload_image (file_path):
    """
    Upload an image to server and return its filename saving on the server
    """
    # Full URL for the image upload endpoint
    URL_UPLOAD_ENDPOINT = API_BASE_URL + UPLOAD_ENDPOINT
    with open (file_path, 'rb') as image:
        # Create payload with the image file
        payload = {"image_file": image}
        
        # Make a POST request to upload the image
        response = requests.post(url = URL_UPLOAD_ENDPOINT,
                                 headers = HEADER,
                                 files = payload)
        
    # Parse the response
    response_data = response.json()
    if response_data.get("is_success"):
        # Return the server filename if the upload is successful
        return response_data["data"]["file_name"]
    else:
        # Raise an exception if the upload fails
        raise Exception(f"Error uploading {file_path}:", (response_data.get("message")))
    
def perform_image_ocr (file_name, ocr_id = 1):
    """
    Perform OCR on the uploaded image
    """
    # Full URL for the OCR endpoint
    URL_OCR_ENDPOINT = API_BASE_URL + OCR_ENDPOINT
    # Create payload with OCR ID and file name
    payload = {"ocr_id": ocr_id, "file_name": file_name}
    
    # Make a POST request to perform OCR
    response = requests.post(url = URL_OCR_ENDPOINT,
                             headers = HEADER,
                             json = payload)
    
    # Parse the response
    response_data = response.json()
    if response_data.get("is_success"):
        # Return the OCR result if the operation is successful
        return response_data["data"]
    else:
        # Raise an exception if OCR fails
        raise Exception (f"Error performing OCR on {file_name}:", (response_data.get("message")))
    
def perform_extract_images_ocr (image_dir):
    """
    Perform OCR on extract images from PDF file
    """
    listItems = os.listdir(image_dir)
    for item in listItems:
        # Construct the full path of the item
        item_path = os.path.join(image_dir, item)
        print(item_path)
        
        # Check if the item is not a directory
        if (not os.path.isdir(item_path)):
            # Get the file name without extension and file extension
            item_name = '.'.join(item.split('.')[:-1])
            item_ext = item.split('.')[-1]
            
            # Construct the output file name
            output = item_name + "_label.txt"
            
            # Skip files that are not images
            if (item_ext not in ("jpg", "jpeg", "png", "bmp", "tiff")):
                continue
            
            # Skip if the output file already exists
            if (output in listItems):
                continue
            
            # Upload the image and get the server filename
            image_file_path = upload_image(item_path)
            # Perform OCR on the uploaded image
            ocr_result = perform_image_ocr(image_file_path)

            # Extract OCR data for bounding boxes
            ocr_data = []
            for bbox in ocr_result["result_bbox"]:
                ocr_data.append({
                    "transcription": bbox[1][0],   # Extracted text
                    "points": bbox[0]              # Coordinates of the bounding box
                })
                
            # Write OCR data to the output file
            output_path = os.path.join(image_dir, output)
            with open (output_path, 'w', encoding = 'utf-8') as file:
                file.write(str(ocr_data))
            
        else:
            # Recursively process subdirectories
            perform_extract_images_ocr(item_path)

#! Usage     
perform_extract_images_ocr(image_dir = "OCR_result/CÁC THÁNH TRUYỆN THÁNG 01 GIROLAMO MAIORICA - AI")