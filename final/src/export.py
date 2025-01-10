from xlsxwriter.workbook import Workbook

def export_excel_file(file_name, data):
    # Create a new workbook and add a worksheet to it
    workbook = Workbook(file_name)
    worksheet = workbook.add_worksheet()
    
    # Define formatting for text in red, green, and with the 'Nom Na Tong' font
    red = workbook.add_format({'color': 'red', 'font_name': 'Nom Na Tong'})
    blue = workbook.add_format({'color': 'blue', 'font_name': 'Nom Na Tong'})
    nom_na_tong = workbook.add_format({'font_name': 'Nom Na Tong'})
    green = workbook.add_format({'color': 'green', 'font_name': 'Nom Na Tong'})
    
    # Set the width for each column to improve readability
    worksheet.set_column('A:A', max(max(len(data[index][0]) for index in range (len(data))), 2) * 1.2)
    worksheet.set_column('B:B', max(max(len(data[index][1]) for index in range (len(data))), 10) * 1.2)
    worksheet.set_column('C:C', max(max(len(data[index][2][0]) for index in range (len(data))), 9) * 0.9)
    worksheet.set_column('D:D', max(max(len(data[index][3][0]) for index in range (len(data))), 12) * 1.5)
    if (len(data[0]) >= 5):
        worksheet.set_column('E:E', max(max(len(data[index][4]) for index in range (len(data)) if len(data[index]) >= 5), 12) * 1.2)
    
    # Write the column headers to the first row with the 'Nom Na Tong' font
    columns = ["Image_name", "ID", "Image Box", "SinoNom OCR", "Chữ Quốc Ngữ"]
    worksheet.write_row(0, 0, columns, nom_na_tong)
    
    numReds = 0
    numRemains = 0
    num_Ins = 0
    num_Del = 0
    # Iterate over the data rows to write each row to the worksheet
    for i in range(len(data)):
        # Write the ID column with 'Nom Na Tong' font
        worksheet.write(i + 1, 0, data[i][0], nom_na_tong)
        worksheet.write(i + 1, 1, data[i][1], nom_na_tong)
        
        # Write SinoNom Char and Chữ Quốc Ngữ data if present in the row
        if len(data[i]) >= 5:
            worksheet.write(i + 1, 4, data[i][4], nom_na_tong)
        
        if (data[i][2][0]):
            # Initialize a list for Image Box format and text elements
            format = []
            # Apply green formatting if specified, otherwise use the default format
            if data[i][2][1] == 'g':
                num_Del += 1
                for j in range(len(data[i][2][0])):
                    format.extend((green, data[i][2][0][j]))
            else:
                for j in range(len(data[i][2][0])):
                    format.extend(data[i][2][0][j])
            # Write the Image Box column with rich text formatting
            worksheet.write_rich_string(i + 1, 2, *format, nom_na_tong)
        else:
            num_Ins += 1
        
        # Initialize a list for SinoNom OCR format and text elements
        format = []
        sino_ocr = data[i][3][0]
        marked = data[i][3][1]
        if marked:
            # Apply red formatting to marked characters
            for j in range(len(sino_ocr)):
                if (marked[j] == 'r'):
                    format.extend((red, sino_ocr[j]))
                    numReds += 1
                elif (marked[j] == 'b'):
                    format.extend((blue, sino_ocr[j]))
                    numRemains += 1
                else:
                    format.append(sino_ocr[j])
                    numRemains += 1
                    
            if (len(format) > 2):
                worksheet.write_rich_string(i + 1, 3, *format, nom_na_tong)
            else:
                if (len(sino_ocr) == 2):
                    worksheet.write(i + 1, 3, sino_ocr, nom_na_tong)
                else:
                    if (marked[-1] == 'r'):
                        worksheet.write(i + 1, 3, sino_ocr, red)
                    elif (marked[-1] == 'b'):
                        worksheet.write(i + 1, 3, sino_ocr, blue)
                    else:
                        worksheet.write(i + 1, 3, sino_ocr, nom_na_tong)
        else:
            # Write SinoNom OCR without formatting if no marking is specified
            worksheet.write(i + 1, 3, sino_ocr, nom_na_tong)
            
    # Close the workbook to save the Excel file
    workbook.close()
    
    print(f"Red letter rate: {numReds / (numReds + numRemains)}") 
    print(f"Insertion or Deletion rate: {(num_Ins + num_Del) / (num_Ins + numReds + numRemains)}")
    print(f"Num Insertion and Deletion: {num_Ins + num_Del}")
    print(f"Total: {num_Ins + numReds + numRemains}")