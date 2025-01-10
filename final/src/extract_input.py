import os
import shutil
import pandas as pd

def read_Sino_QN (excel_file_path: str):
    """
    
    """
    try:
        #
        data = pd.read_excel(excel_file_path) 
        
        #
        if ("Image_name" not in data.columns):
            return "Missing the \"Image_name\" column"
        
        #
        if ("SinoNom OCR" not in data.columns):
            return "Missing the \"SinoNom OCR\" column"
        
        #
        if ("Chữ Quốc Ngữ" not in data.columns):
            return "Missing the \"Chữ Quốc Ngữ\" column"
        
        #
        data = data.fillna("")
        
        #
        image_names = data["Image_name"].to_list()
        HN = data["SinoNom OCR"].to_list()
        QN = data["Chữ Quốc Ngữ"].to_list()
        
        #
        files = list({'_'.join(name.split('_')[:-1]): True for name in image_names}.keys())
        index = 0
        list_HNs = []
        list_QNs = []
        
        #
        for file in files:
            #
            temp_HN = []
            temp_QN = []
            
            #
            while (index < len(image_names) and '_'.join(image_names[index].split('_')[:-1]) == file):
                temp_HN.append(HN[index])
                temp_QN.append(QN[index])
                index += 1
                
            #
            list_HNs.append(temp_HN)
            list_QNs.append(temp_QN)
        
        #
        return list_HNs, list_QNs
        
    except Exception as e:
        print(f"Error in {excel_file_path}: {e}")
        exit()
    
def collect_image_files (image_dir: str):
    """
    
    """
    #
    listItems = os.listdir(image_dir)
    
    #
    image_paths = [os.path.join(image_dir, item) for item in listItems
                   if os.path.isfile(os.path.join(image_dir, item)) 
                   and item.endswith("png")]
    
    #
    with open (os.path.join(image_dir, "Label.txt"), 'r', encoding = "utf-8") as file:
        #
        lines = file.readlines()
        
        #
        labels = [line.split('\t') for line in lines]
        
    return image_paths, labels

def check_input_dir (input_dir: str):
    """
    
    """
    #
    if (not os.path.isdir(input_dir)):
        return False
    
    #
    if (len(os.listdir(input_dir)) != 2):
        return False
    
    #
    if (all([not (os.path.isfile(os.path.join(input_dir, filename)) 
                  and filename.endswith('xlsx'))
             for filename in os.listdir(input_dir)])):
        return False
    
    #
    image_dir = [filename for filename in os.listdir(input_dir)
                 if not (os.path.isfile(os.path.join(input_dir, filename)) 
                         and filename.endswith('xlsx'))][0]
    
    if (not os.path.isdir(os.path.join(input_dir, image_dir))):
        return False
    
    #
    image_path = os.path.join(input_dir, image_dir)
    if ("Label.txt" not in os.listdir(image_path)):
        return False
    
    #
    for item in os.listdir(image_path):
        if (os.path.isfile(os.path.join(image_path, item)) 
            and item.endswith('png')):
            return True
        
    return False

def collect_cleaned_inputs (input_dir: str, save_dir: str = None):
    """
    
    """
    try:
        #
        check_input = check_input_dir(input_dir)
        if (not check_input):
            raise Exception (f"Check the {input_dir} again!")
        
        #
        list_items = os.listdir(input_dir)
        if (list_items[0].endswith('xlsx')):
            excel_file = list_items[0]
            image_dir = list_items[1]
        else:
            excel_file = list_items[1]
            image_dir = list_items[0]
            
        #
        HN, QN = read_Sino_QN(os.path.join(input_dir, excel_file))
        image_paths, labels = collect_image_files(os.path.join(input_dir, image_dir))
        
        #
        image_names = [label[0].split('/')[-1] for label in labels]
        dirs = list({'_'.join(name.split('_')[:-1]): True for name in image_names}.keys())
        index = 0
        
        #
        save_dirs = [dir for dir in dirs]
        if (save_dir is not None):
            save_dirs = [os.path.join(save_dir, dir) for dir in save_dirs]
        
        #
        for dir in save_dirs:
            if (not os.path.exists(dir)):
                os.makedirs(dir)
                
        #
        for idx, dir in enumerate(save_dirs):
            #
            while (index < len(image_names) and '_'.join(image_names[index].split('_')[:-1]) == dirs[idx]):
                #
                page_number = int(image_names[index].split('page')[-1].split('.')[0])
                page = os.path.join(dir, f"Page {page_number}")
                
                #
                if (not os.path.exists(page)):
                    os.makedirs(page)
                    
                #
                image = os.path.join(page, f"Image 1")
                if (not os.path.exists(image)):
                    os.makedirs(image)
                    
                #
                label_file = os.path.join(image, "image1_label.txt")
                with open (label_file, 'w', encoding = 'utf-8') as file:
                    file.write(labels[index][1])
                    
                index += 1
                    
        #
        for image_path in image_paths:
            #
            dir = '_'.join(os.path.basename(image_path).split('_')[:-1])
            if (save_dir is not None):
                dir = os.path.join(save_dir, dir)
            page_number = int(image_path.split('page')[-1].split('.')[0])
            
            #
            if (not os.path.exists(dir)):
                os.makedirs(dir)
                
            #
            page = os.path.join(dir, f"Page {page_number}")
            if (not os.path.exists(page)):
                os.makedirs(page)
                
            #
            image = os.path.join(page, f"Image 1")
            if (not os.path.exists(image)):
                os.makedirs(image)
            
            #
            dest_path = os.path.join(image, "image1.png")
            shutil.copy(image_path, dest_path)
        
        return dirs, HN, QN
        
    except Exception as e:
        print(f"Error: {e}")
        exit()

def collect_inputs_from_midterm (input_dir: str, save_dir: str = None):
    """
    
    """
    dirs = []
    HN = []  #
    QN = []  #
    
    #
    for item in os.listdir(input_dir):
        #
        item_path = os.path.join(input_dir, item)
        
        #
        if (os.path.isdir(item_path)):
            #
            temp_dirs, temp_HN, temp_QN = collect_cleaned_inputs(input_dir = item_path,
                                                                 save_dir = save_dir)
            
            #
            dirs.extend(temp_dirs)
            HN.extend(temp_HN)
            QN.extend(temp_QN)
            
    return dirs, HN, QN