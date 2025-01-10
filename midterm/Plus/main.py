# Import necessary modules for file operations, regular expressions, and JSON handling
import os
import re
import json

# Import custom functions for extracting input and text processing
from extract_input import extract, thanh_truyen_text_processing, thanh_mau_text_processing
from dictionary import get_dictionaries

# Import alignment functions for sorting, aligning boxes, and characters
from alignment import sort_boxes_in_correct_order, box_alignment, char_alignment

# Import export functions for saving processed data
from export import export_excel_file, export_OCR_result_directory

# Function to process data from a list of filenames
def get_data(filename_list, text_processing_funcs = None,
             extract_save_dir = None,
             Sino_sim_path = "SinoNom_similar_Dic.xlsx",
             QN_Sino_path = "QuocNgu_SinoNom_Dic.xlsx"):
    
    # Initialize a list to hold box data
    box_data = []
    
    # Extract information from the provided filenames using custom text processing functions
    extract_info = extract(filename_list = filename_list, 
                           text_processing_funcs = text_processing_funcs,
                           extract_save_dir = extract_save_dir)
    
    # Load dictionaries for Sino-Nom similarity and QuocNgu-SinoNom mapping
    SinoNom_Similar_Dict, QN_SinoNom_Dict = get_dictionaries(Sino_sim_path = Sino_sim_path,
                                                             QN_Sino_path = QN_Sino_path)
    
    # Process each file in the filename list
    for index, filename in enumerate(filename_list):
        # Extract QuocNgu (QN) sentences for the current file
        QN = [info for info in extract_info[index][1]]
        
        # Create a folder name based on the filename and optional save directory 
        folder_name = filename[:(len(filename) - 4)]        
        if (extract_save_dir):
            if (extract_save_dir[-1] == '/'):
                folder_name = extract_save_dir + folder_name.split('/')[-1]
            else:
                folder_name = extract_save_dir + '/' + folder_name.split('/')[-1]
        
        # Get sorted page directories for the current file
        pages = sorted(os.listdir(folder_name), key = lambda x: int(x.split()[1]))
        for page_index, page in enumerate(pages):
            # Get sorted image files for the current page
            images = sorted(os.listdir(os.path.join(folder_name, page)), key = lambda x: int(x.split()[1]))
            for image in images:
                # Define the path for the label file associated with the image
                label_file = ''.join(image.split()).lower() + "_label.txt"
                file_path = os.path.join(folder_name, page, image, label_file)
                
                # Skip if the label file does not exist
                if (not os.path.exists(file_path)):
                    break
                
                # Initialize a list to hold box data for the current image
                boxes = []

                # Read and parse the label file as JSON
                with open(file_path, "r", encoding = "utf-8") as file:
                    for line in file:
                        json_data = line.replace("'", '"')
                        json_data = re.sub(
                            r'\\U([0-9A-Fa-f]{8})', 
                            lambda match: chr(int(match.group(1), 16)), 
                            json_data
                        )
                        boxes += json.loads(json_data)
                
                # Sort boxes into the correct reading order
                boxes = sort_boxes_in_correct_order(boxes)

                # Align boxes with the corresponding QN sentences
                aligned_boxes = box_alignment(boxes, QN[page_index])
                
                # Initialize lists for character alignment results and marked boxes
                marked_list = []
                aligned_chars = []
                for box, QN_sentence in aligned_boxes:
                    QN_list = []
                    
                    # Preprocess QN sentences for character alignment
                    if QN_sentence != "":
                        QN_list = re.sub(r"-", " ", QN_sentence[-1].strip('.,?!:()[];').lower()).strip().split()
                        QN_list = [QN_word.strip(' .,?!:()[];') for QN_word in QN_list]
                    
                    # Perform character alignment
                    aligned_char, marked = char_alignment(box, QN_list, SinoNom_Similar_Dict, QN_SinoNom_Dict)
                    aligned_chars.append(aligned_char)
                    marked_list.append(marked)
                
                # Record box data with associated information
                for box_index in range(len(aligned_boxes)):
                    # Format page and box identifiers
                    page_number = f'{int(page[5:]):03}' if int(page[5:]) < 100 else page[5:]
                    box_str = f'{box_index:03}' if box_index < 100 else str(box_index)
                    
                    # Create base filename
                    filename = filename.split('/')[-1]
                    box_record = [f'{filename[:(len(filename) - 4)]}_page{page_number}.png', 
                                  f'{filename[:(len(filename) - 4)]}.{page_number}.{box_str}']
                    
                    # Extract points for the current box
                    points = [tuple(point) for point in boxes[box_index]['points']]
                    
                    # Append aligned and marked data for the box
                    if aligned_boxes[box_index][1] == "":
                        box_record.append([f'{points}', 'g'])               # Green color
                        box_record.append([aligned_boxes[box_index][0], marked_list[box_index]])
                    else:
                        box_record.append([f'{points}', 'n'])               # No color
                        box_record.append([aligned_boxes[box_index][0], marked_list[box_index]])
                        box_record.append(aligned_boxes[box_index][1][-1])  # QN word list
                    
                    # Add the box record to the box data list
                    box_data.append(box_record)
                    
    return box_data

#! Define a list of filenames for data processing
filename_list = ["data/Prj_19_CLC_CAC THANH TRUYEN THANG 5 GIROLAMO MAIORICA - AI.pdf",
                 "data/Prj_19_CLC_Thien Chua Thanh Mau q. thuong MAIORICA - AI.pdf"]

#! Define a list of text processing functions
text_processing_funcs = [thanh_truyen_text_processing,
                         thanh_mau_text_processing]

#! Get data
box_data = get_data(filename_list = filename_list,
                    text_processing_funcs = text_processing_funcs,
                    extract_save_dir = 'OCR_result',
                    Sino_sim_path = "dictionary/SinoNom_similar_Dic.xlsx",
                    QN_Sino_path = "dictionary/QuocNgu_SinoNom_Dic.xlsx")

#!
export_OCR_result_directory(in_dir = "OCR_result",
                            out_dir = "../Label/image_label")

#! Export the processed and aligned data to an Excel file with color-coded formatting
export_excel_file(file_name = "../Label/result.xlsx", data = box_data)  