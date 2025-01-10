#
import os
import re
import json

#
from extract_input import collect_inputs_from_midterm
from dictionary import get_dictionaries

#
from alignment import sort_boxes_in_correct_order, char_alignment

#
from export import export_excel_file

#
from tqdm import tqdm

def get_data(input_dir: str,
             save_dir: str,
             Sino_sim_path: str = "SinoNom_similar_Dic.xlsx",
             QN_Sino_path: str = "QuocNgu_SinoNom_Dic.xlsx"):
    
    #
    char_data = []
    
    #
    dirs, temp_HN, temp_QN = collect_inputs_from_midterm(input_dir = input_dir,
                                                         save_dir = save_dir)
    
    #
    SinoNom_Similar_Dict, QN_SinoNom_Dict = get_dictionaries(Sino_sim_path = Sino_sim_path,
                                                             QN_Sino_path = QN_Sino_path)
    
    #
    for index, filename in enumerate(dirs):
        #
        folder_name = os.path.join(save_dir, filename)
        if (not os.path.isdir(folder_name)):
            break
        
        #
        HN = temp_HN[index]
        QN = temp_QN[index]
        HN_index = 0
        
        #
        pages = sorted(os.listdir(folder_name), key = lambda x: int(x.split()[1]))
        
        #
        for page_index in tqdm(range(len(pages)), desc = f"Processing file {index + 1}"):
            #
            page = pages[page_index]
            images = sorted(os.listdir(os.path.join(folder_name, page)), key = lambda x: int(x.split()[1]))
            
            #
            for image in images:
                #
                label_file = ''.join(image.split()).lower() + "_label.txt"
                char_label_file = ''.join(image.split()).lower() + "_char_bbox.txt"
                
                #
                file_path = os.path.join(folder_name, page, image, label_file)
                char_file_path = os.path.join(folder_name, page, image, char_label_file)
                
                #
                if (not os.path.exists(file_path) or not os.path.exists(char_file_path)):
                    break
                
                boxes = []         #
                char_boxes = []    #

                #
                with open(file_path, "r", encoding = "utf-8") as file:
                    for line in file:
                        json_data = line.replace("'", '"')
                        json_data = re.sub(
                            r'\\U([0-9A-Fa-f]{8})', 
                            lambda match: chr(int(match.group(1), 16)), 
                            json_data
                        )
                        boxes += json.loads(json_data)
                
                #
                with open(char_file_path, "r", encoding = "utf-8") as file:
                    lines = file.readlines()
                    for line in lines:
                        info = [float(x) for x in line.split()]
                        center_x, center_y, width, height = info
                        box = {
                            "points": [
                                [center_x - width / 4, center_y],
                                [center_x, center_y],
                                [center_x, center_y + height / 4],
                                [center_x - width / 4, center_y + height / 4]
                            ]
                        }
                        char_boxes.append(box)
                
                #     
                char_boxes = sort_boxes_in_correct_order(char_boxes, concat = False)
                
                #
                aligned_chars = []
                marked_list = []
                for i in range(HN_index, HN_index + len(boxes)):
                    #
                    HN_sentence = HN[i]
                    QN_sentence = QN[i]
                    QN_list = []
                    
                    #
                    HN_sentence = re.sub('-', '', HN_sentence)
                    
                    #
                    if QN_sentence != "":
                        QN_list = re.sub(r"-", " ", QN_sentence.strip('.,?!:()[];').lower()).strip().split()
                        QN_list = [QN_word.strip(' .,?!:()[];') for QN_word in QN_list]
                        
                    #
                    aligned_char, marked = char_alignment(HN_sentence, QN_list, SinoNom_Similar_Dict, QN_SinoNom_Dict)
                    marked_list.append(marked)
                    aligned_chars.append(aligned_char)
                    
                #
                HN_index = HN_index + len(boxes)
                    
                #
                for box_index in range(len(boxes)):
                    #
                    page_number = f'{int(page[5:]):03}' if int(page[5:]) < 100 else page[5:]
                    box_str = f'{box_index:03}' if box_index < 100 else str(box_index)
                    
                    #
                    temp_index = 0
                    marked = marked_list[box_index]
                    for _, (sino, qn) in enumerate(aligned_chars[box_index]):
                        if (sino == ""):
                            char_record = ["", "", ["", 'n'], ["", []], qn]
                            char_data.append(char_record)
                        else:
                            if (temp_index < len(char_boxes[box_index])):
                                #
                                char_record = [f'{filename[:(len(filename) - 4)]}_page{page_number}.png',
                                            f'{filename[:(len(filename) - 4)]}.{page_number}.{box_str}.{temp_index}']
                                
                                #
                                points = [point for point in char_boxes[box_index][temp_index]['points']]
                                
                                #
                                width, height = (points[1][0] - points[0][0]) * 4, (points[2][1] - points[0][1]) * 4
                                points[1][0] = round(points[1][0] + width / 2, 4)
                                points[2][0] = round(points[2][0] + width / 2, 4)
                                points[0][1] = round(points[0][1] - height / 2, 4)
                                points[1][1] = round(points[1][1] - height / 2, 4)
                                points[0][0] = round(points[0][0] - width / 4, 4)
                                points[3][0] = round(points[3][0] - width / 4, 4)
                                points[2][1] = round(points[2][1] + height / 4, 4)
                                points[3][1] = round(points[3][1] + height / 4, 4)
                                
                                #
                                points = [tuple(point) for point in points]
                                
                                #
                                if qn == "":
                                    char_record.append([f'{points}', 'g'])     # Green color
                                    char_record.append([sino, ['r']])
                                else:
                                    #
                                    char_record.append([f'{points}', 'n'])     # No color
                                    char_record.append([sino, [marked[temp_index]]])
                                    char_record.append(qn)                     # QN word
                            
                                #        
                                char_data.append(char_record)
                                temp_index += 1
                    
    return char_data

#! Get data
char_data = get_data(input_dir = "midterm_result",
                     save_dir = 'OCR_result',
                     Sino_sim_path = "dictionary/SinoNom_similar_Dic.xlsx",
                     QN_Sino_path = "dictionary/QuocNgu_SinoNom_Dic.xlsx")

#! Export the processed and aligned data to an Excel file with color-coded formatting
export_excel_file(file_name = "Output/Prj_19_CK.xlsx", data = char_data)   