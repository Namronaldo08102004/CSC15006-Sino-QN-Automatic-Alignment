import os
import re
import fitz
from fitz import Page
from tqdm import tqdm

def extract (filename_list: list[str], text_processing_funcs = None, save_extract_info = True, extract_save_dir = None):
    """
    Extract images and text from a list of PDF files. Optionally, process the text using specific functions
    and save the extracted information.

    Parameters:
    - filename_list: List of file paths to PDF files to be processed.
    - text_processing_funcs: List of functions for processing text from each PDF file.
    - save_extract_info: Boolean indicating whether to save extracted information (images and text).
    - extract_save_dir: Directory to save the extracted information.

    Returns:
    - output_list: List of tuples containing extracted images and processed text for each file.
    """
    # Helper function to extract images from a PDF page
    def extract_image (page: Page):
        # Get images on the page
        image_list = page.get_images(full = True)
        images = []
        
        # Extract image bytes and extensions if images are present
        if (image_list):
            for index in range (len(image_list)):
                xref = image_list[index][0]                   # Get the XREF of the image
                base_image = pdf_file.extract_image(xref)     # Extract the image bytes

                image_bytes = base_image["image"]
                image_ext = base_image["ext"]

                images.append((image_bytes, image_ext))
                
        return images

    # Ensure the number of text processing functions matches the number of files
    if (text_processing_funcs is not None and len(filename_list) != len(text_processing_funcs)):
        raise Exception("The number of function used for processing text must be equal to the number of files")
    
    output_list = []   # List to store extracted information
    
    # Loop through each file in the provided list
    for index, filename in enumerate(filename_list):
        if len(filename) > 4 and filename[-4:] == ".pdf":  # Ensure the file is a PDF
            folder_name = None

            # Create a folder to save extraction info, if required
            if save_extract_info:
                folder_name = filename[:-4]
                if extract_save_dir:
                    if extract_save_dir[-1] == '/':
                        folder_name = extract_save_dir + folder_name.split('/')[-1]
                    else:
                        folder_name = extract_save_dir + '/' + folder_name.split('/')[-1]

                if not os.path.exists(folder_name):
                    os.mkdir(folder_name)

            pdf_file = fitz.open(filename)  # Open the PDF file
            images = []  # Store all extracted images
            text_lines = []  # Store all extracted text lines

            # Loop through each page in the PDF
            for page_index in tqdm(range(len(pdf_file)), desc = "Processing Pages"):
                page = pdf_file.load_page(page_index)  # Load the current page
                temp_images = extract_image(page)  # Extract images from the page

                if temp_images:
                    images += temp_images  # Add images to the list

                # Save images if required
                if temp_images and save_extract_info:
                    page_folder = f"{folder_name}/Page {page_index + 1}"
                    if not os.path.exists(page_folder):
                        os.mkdir(page_folder)

                    for image_index, (image_bytes, image_ext) in enumerate(temp_images):
                        image_folder = f"{page_folder}/Image {image_index + 1}"
                        if not os.path.exists(image_folder):
                            os.mkdir(image_folder)

                        image_name = f"image{image_index + 1}.{image_ext}"
                        image_path = f"{image_folder}/{image_name}"

                        with open(image_path, "wb") as image_file:
                            image_file.write(image_bytes)

                # Extract text from the page if no images are found
                if images and not temp_images:
                    page_text = page.get_text().strip()
                    if page_text:
                        text_lines.append(page_text.split('\n'))

            # Process the extracted text using the provided function, if available
            if text_processing_funcs and text_processing_funcs[index]:
                processed_text = text_processing_funcs[index](text_lines)
                output_list.append((images, processed_text))
            else:
                output_list.append((images, text_lines))

    return output_list

def thanh_truyen_text_processing (text_lines):
    """
    Process text extracted from the "Prj_19_CLC_CAC THANH TRUYEN THANG 5 GIROLAMO MAIORICA - AI.pdf" document.

    Parameters:
    - text_lines: List of text lines extracted from the document.

    Returns:
    - QN_list: Processed Quoc Ngu (QN) sentences organized by page.
    """
    QN_list = []   # Store processed text for each page
    
    # Loop through each page of text 
    for page_index in range (len(text_lines)):
        QN_list_in_page = []   # Store processed text for the current page
        line_index = 0
        
        # Stop processing if the "CHÚ THÍCH" section is encountered
        if ('CHÚ THÍCH' in text_lines[page_index]):
            break
        
        # Process each line of text
        while (line_index < len(text_lines[page_index])):
            # Extract QN sentences separated by tabs
            if (len(text_lines[page_index][line_index].split('\t')) >= 2):
                QN = text_lines[page_index][line_index].split('\t')[-1].strip()
                line_index += 1
                
                # Handle hyphenated lines by concatenating them
                if (QN[-1] == '\xad'):
                    QN = QN[:-1] + '-'
                
                while (line_index < len(text_lines[page_index]) and len(text_lines[page_index][line_index].split('\t')) == 1):
                    if (QN[-1] == '-'):
                        QN += text_lines[page_index][line_index].strip()
                    else:
                        QN += ' ' + text_lines[page_index][line_index].strip()    
                    
                    line_index += 1
                
                # Perform replacements to normalize specific text patterns
                QN = QN.replace("Côntantê", "Côn-tan-tê")
                QN = QN.replace("I-ghê(rê)-gia", "I-giê-rê-gia")
                QN = QN.replace("Bisanriô", "Bi-san-ri-ô")
                QN = QN.replace("Giêraphôli", "Giê-ra-phô-li")
                QN = QN.replace("Nasiansô", "Na-si-an-sô")
                QN = QN.replace("Sacaramentô", "Sa-ca-ra-men-tô")
                QN = QN.replace("Ămsiô", "Ăm-si-ô")
                QN = QN.replace("1594", "một nghìn năm trăm chín mươi bốn")
                QN = QN.replace("1296", "một nghìn hai trăm chín mươi sáu")
                QN = QN.replace("1070", "một nghìn linh bảy mươi")
                QN = QN.replace("1040", "một nghìn linh bốn mươi")
                QN = QN.replace("853", "tám trăm năm mươi ba")
                QN = QN.replace("600", "sáu trăm")
                QN = QN.replace("578", "năm trăm bảy mươi tám")
                QN = QN.replace("526", "năm trăm hai mươi sáu")
                QN = QN.replace("500", "năm trăm")
                QN = QN.replace("389", "ba trăm tám mươi chín")
                QN = QN.replace("378", "ba trăm bảy mươi tám")
                QN = QN.replace("308", "ba trăm linh tám")
                QN = QN.replace("305", "ba trăm linh năm")
                QN = QN.replace("233", "hai trăm ba mươi ba")
                QN = QN.replace("194", "một trăm chín mươi bốn")
                QN = QN.replace("164", "một trăm sáu mươi bốn")
                QN = QN.replace("135", "một trăm ba mươi lăm")
                QN = QN.replace("98", "chín mươi tám")
                QN = QN.replace("81", "tám mươi mốt")
                QN = QN.replace("80", "tám mươi")
                QN = QN.replace("63", "sáu mươi ba")
                QN = QN.replace("56", "năm mươi sáu")
                QN = QN.replace("54", "năm mươi bốn")
                QN = QN.replace("30", "ba mươi")
                QN = QN.replace("20", "hai mươi")
                QN = QN.replace("14", "mười bốn")
                QN = QN.replace("13", "mười ba")
                QN = QN.replace("8", "tám")
                QN = QN.replace("7", "bảy")
                QN = QN.replace("6", "sáu")
                QN = QN.replace("4", "bốn")

                QN_list_in_page.append([QN])
            else:
                line_index += 1
        
        # Add additional processing logic for specific pages, if necessary    
        if (page_index == 0):
            QN_list_in_page[1][-1] = QN_list_in_page[0][-1].split(' ngày ')[1] + ' ' + QN_list_in_page[1][-1]
            QN_list_in_page[0][-1] = QN_list_in_page[0][-1].split(' ngày ')[0] + ' ngày'
                
        if (page_index == 58):
            QN_list_in_page[2][-1] = QN_list_in_page[2][-1].replace("(hay Ca-lai?) ", "")
                
        if (page_index == 59):
            QN_list_in_page[1][-1] += QN_list_in_page[2][-1]
            for i in range (2, 6):
                QN_list_in_page[i][-1] = QN_list_in_page[i + 1][-1]
            QN_list_in_page[6][-1] = QN_list_in_page[7][-1].split('-')[0] + '-'
            QN_list_in_page[7][-1] = QN_list_in_page[7][-1].split('-')[1]
            
        if (page_index == 70):
            QN_list_in_page[2][-1] = QN_list_in_page[2][-1].replace("người thấy ", "")
            
        if (page_index == 89):
            QN_list_in_page[0][-1] += QN_list_in_page[1][-1]
            for i in range (1, 7):
                QN_list_in_page[i][-1] = QN_list_in_page[i + 1][-1]
            QN_list_in_page[7][-1] = QN_list_in_page[8][-1].split(' bày ')[0] + ' bày'
            QN_list_in_page[8][-1] = QN_list_in_page[8][-1].split(' bày ')[1]
            QN_list_in_page[8][-1] = QN_list_in_page[8][-1].replace("chưng, ", "")
            
        if (page_index == 102):
            QN_list_in_page[1][-1] = QN_list_in_page[2][-1].replace(", phúc nhất", "")
            
        if (page_index == 107):
            QN_list_in_page[8][-1] = QN_list_in_page[7][-1].split(' biết ')[1] + ' ' + QN_list_in_page[8][-1]
            QN_list_in_page[7][-1] = QN_list_in_page[7][-1].split(' biết ')[0] + ' biết'
        
        QN_list.append(QN_list_in_page)
    
    # Exclude the last page because it cannot be optically recognized 
    return QN_list[:-1]

def thanh_mau_text_processing (text_lines):
    """
    Process text extracted from the "Prj_19_CLC_Thien Chua Thanh Mau q. thuong MAIORICA - AI.pdf" document.

    Parameters:
    - text_lines: List of text lines extracted from the document.

    Returns:
    - QN_list: Processed Quoc Ngu (QN) sentences organized by page.
    """
    QN_list = []  # Store processed text for each page
    
    # Loop through each page of text
    for page_index in range (len(text_lines)):
        QN_list_in_page = []  # Store processed text for the current page
        line_index = 0
        
        # Stop processing if the "CHÚ THÍCH" section is encountered
        if ('CHÚ THÍCH' in text_lines[page_index]):
            break
        
        # Process each line of text
        while (line_index < len(text_lines[page_index])):
            # Extract QN sentences separated by tabs
            if (len(text_lines[page_index][line_index].split('\t')) >= 2):
                # Extract the last part of the tab-separated line and strip extra whitespace
                QN = text_lines[page_index][line_index].strip('\t').split('\t')[-1].strip()
                
                # Handle cases where QN is a digit; use the second-to-last part instead
                if (QN.isdigit()):
                    QN = text_lines[page_index][line_index].strip('\t').split('\t')[-2].strip()
                
                # Check if the line is blank by looking for a pattern like "number. "
                blank_line = True if (QN.split('.')[0].isdigit() and QN.split('.')[-1] == "") else False
                line_index += 1   # Move to the next line
                
                # Skip processing if it's a blank line
                if (blank_line):
                    continue
                
                # Continue processing while the next line is part of the current QN block
                while (line_index < len(text_lines[page_index]) and 
                       (len(text_lines[page_index][line_index].split('\t')) == 1 
                        or (text_lines[page_index][line_index][-1] == '\t'
                            and len(text_lines[page_index][line_index].split('\t')) <= 2))):
                    # Stop processing if the line is purely numeric
                    if (text_lines[page_index][line_index].isdigit()):
                        break
                    
                    # Stop processing if the line starts with a number and ends with a period
                    if ((len(text_lines[page_index][line_index].split('\t')) == 1 or not blank_line) and
                        text_lines[page_index][line_index].split('.')[0].isdigit()):
                        break
                    
                    # Append content to QN, handling cases where QN ends with a hyphen
                    if (QN[-1] == '-'):
                        QN += text_lines[page_index][line_index].strip('\t ')
                    else:
                        QN += ' ' + text_lines[page_index][line_index].strip('\t ') 
                          
                    line_index += 1  # Move to the next line
                
                # Remove all digits from QN using regex and split/merge logic 
                QN = ' '.join([re.sub(r"\d", "", word) for word in QN.split()])
                # Add the processed QN to the list for the current page
                QN_list_in_page.append([QN])
                
            else:
                # If the line does not contain tab-separated content, move to the next line
                line_index += 1
        
        # Append the processed QN list for the current page to the overall list
        QN_list.append(QN_list_in_page)
    
    # Return the final QN list after processing all pages
    return QN_list