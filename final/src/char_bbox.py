import os
import torch
from PIL import Image

def load_model (repo_or_dir, optimizer_path):
    """
    
    """
    model = torch.hub.load(repo_or_dir = repo_or_dir, 
                           model = 'custom', 
                           path = optimizer_path)
    
    model.conf = 0.5
    return model

def perform_image_char_ocr (image_path, model, normalize = True):
    """
    
    """
    #
    result = model(image_path)
    
    #
    with Image.open(image_path) as image:
        image_width, image_height = image.size
    
    #
    predictions = result.xywh[0]
    bboxes = []
    
    #
    for *box, _, _ in predictions:
        x_center, y_center, width, height = box
        x_center, y_center, width, height = x_center.item(), y_center.item(), width.item(), height.item()
        
        if (normalize):
            x_center /= image_width
            y_center /= image_height
            width /= image_width
            height /= image_height
            
        bboxes.append((x_center, y_center, width, height))
        
    return bboxes

def perform_extract_images_char_ocr (image_dir, model):
    """

    """
    #
    listItems = os.listdir(image_dir)
    for item in listItems:
        #
        item_path = os.path.join(image_dir, item)
        print(item_path)
        
        #
        if (not os.path.isdir(item_path)):
            #
            item_name = '.'.join(item.split('.')[:-1])
            item_ext = item.split('.')[-1]
            output = item_name + "_char_bbox.txt"
            
            #
            if (item_ext not in ("jpg", "jpeg", "png", "bmp", "tiff")):
                continue
            
            # 
            if (output in listItems):
                continue
            
            #
            ocr_result = perform_image_char_ocr(item_path, model)

            #
            output_path = os.path.join(image_dir, output)
            with open (output_path, 'w', encoding = 'utf-8') as file:
                for bbox in ocr_result:
                    x_center, y_center, width, height = bbox
                    file.write(f"{x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")
            
        else:
            #
            perform_extract_images_char_ocr(item_path, model)
            
model = load_model(repo_or_dir = 'ultralytics/yolov5', optimizer_path = 'optimizer/best.pt')
perform_extract_images_char_ocr(image_dir = "OCR_result/Prj_19_CLC_Thien Chua Thanh Mau q. thuong MAIORICA - AI",
                                model = model)