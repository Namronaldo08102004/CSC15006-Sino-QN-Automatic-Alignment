import re
from levenstein import levenstein

def sort_boxes_in_correct_order(boxes: list, concat = True):
    """
    Sorts a list of boxes in the correct order by arranging them based on spatial 
    positions (e.g., left-to-right, top-to-bottom). Optionally concatenates boxes 
    that are vertically stacked.

    Args:
        boxes (list): A list of box dictionaries, each containing 'points' (coordinates)
                      and 'transcription' (text).
        concat (bool): Whether to concatenate vertically stacked boxes.

    Returns:
        list: Sorted boxes, either as individual items or concatenated.
    """
    # Create a copy of the input boxes to avoid modifying the original list
    boxes_copy = [box for box in boxes]
    correct_boxes = []  # List to hold the correctly sorted boxes
    num_boxes = len(boxes)  # Total number of boxes to process

    # Main loop: Process all boxes until none are left
    while num_boxes > 0:
        # Initialize variables to identify the rightmost box
        rightmost_box = None
        box_index = None

        # Identify the rightmost box in the current stack
        for i in range(len(boxes_copy)):
            more_right_box = None
            for j in range(len(boxes_copy)):
                if j != i:
                    # Compare the x-coordinates of the boxes to find overlap
                    if (max(boxes_copy[j]['points'][0][0], boxes_copy[j]['points'][3][0]) >= 
                        min(boxes_copy[i]['points'][1][0], boxes_copy[i]['points'][2][0])):

                        more_right_box = boxes_copy[j]
                        break
            
            # If no box is found to the right, current box is the rightmost
            if more_right_box is None:
                rightmost_box = boxes_copy[i]
                box_index = i
                break

        # Collect all boxes that belong to the same vertical stack as the rightmost box
        rightmost_boxes = [rightmost_box]
        box_indices = [box_index]
        for i in range(len(boxes_copy)):
            if (i not in box_indices
                and any(boxes_copy[i]['points'][0][0] <= rightmost_boxes[j]['points'][0][0] <= boxes_copy[i]['points'][1][0] 
                        or boxes_copy[i]['points'][0][0] <= rightmost_boxes[j]['points'][1][0] <= boxes_copy[i]['points'][1][0] 
                        or rightmost_boxes[j]['points'][0][0] <= boxes_copy[i]['points'][0][0] <= boxes_copy[i]['points'][1][0] <= rightmost_boxes[j]['points'][1][0] for j in range(len(rightmost_boxes)))):
                
                rightmost_boxes.append(boxes_copy[i])
                box_indices.append(i)

        # Repeat the above step to ensure no boxes are left out
        for i in range(len(boxes_copy)):
            if (i not in box_indices
                and any(boxes_copy[i]['points'][0][0] <= rightmost_boxes[j]['points'][0][0] <= boxes_copy[i]['points'][1][0] 
                        or boxes_copy[i]['points'][0][0] <= rightmost_boxes[j]['points'][1][0] <= boxes_copy[i]['points'][1][0] 
                        or rightmost_boxes[j]['points'][0][0] <= boxes_copy[i]['points'][0][0] <= boxes_copy[i]['points'][1][0] <= rightmost_boxes[j]['points'][1][0] for j in range(len(rightmost_boxes)))):
                
                rightmost_boxes.append(boxes_copy[i])
                box_indices.append(i)

        # Sort the collected boxes vertically (top-to-bottom)
        rightmost_boxes_copy = [box for box in rightmost_boxes]
        num_rightmost_boxes = len(rightmost_boxes)
        sorted_rightmost_boxes = []

        # Sort the vertical stack of boxes
        while num_rightmost_boxes > 0:
            top_boxes = []  # Boxes at the top of the current stack
            for i in range(len(rightmost_boxes_copy)):
                more_top_box = None
                for j in range(len(rightmost_boxes_copy)):
                    if j != i:
                        # Compare the y-coordinates to determine vertical positioning
                        if (max(rightmost_boxes_copy[i]['points'][0][1], rightmost_boxes_copy[i]['points'][1][1]) >= 
                            min(rightmost_boxes_copy[j]['points'][2][1], rightmost_boxes_copy[j]['points'][3][1])):
                            more_top_box = rightmost_boxes_copy[j]
                            break
                
                # If no box is found above, current box is at the top
                if more_top_box is None:
                    top_boxes.append(rightmost_boxes_copy[i])

            # Sort the top boxes by their x-coordinates and add to the result
            sorted_rightmost_boxes.extend(sorted(top_boxes, key = lambda x: x['points'][0][0], reverse = True))
            num_rightmost_boxes -= len(top_boxes)

            # Remove the identified top boxes from the list
            rightmost_boxes_copy = [box for box in rightmost_boxes_copy if box not in top_boxes]

        # Reduce the total count of boxes and store the sorted stack
        num_boxes -= len(sorted_rightmost_boxes)
        correct_boxes.append(sorted_rightmost_boxes)

        # Remove the processed boxes from the main list
        boxes_copy = [box for box in boxes_copy if box not in sorted_rightmost_boxes]

    # If concatenation is enabled, merge vertically stacked boxes
    if concat:
        concat_correct_boxes = []
        for index in range(len(correct_boxes)):
            box = correct_boxes[index][0]  # Start with the first box in the stack

            for i in range(1, len(correct_boxes[index])):
                # Append the text of subsequent boxes to the first box's transcription
                box["transcription"] += correct_boxes[index][i]["transcription"]
                
                # Adjust the height of the box to include the vertically stacked box
                for j in range(2, 4):
                    box["points"][j][1] += max(correct_boxes[index][i]["points"][3][1] - correct_boxes[index][i]["points"][0][1],
                                               correct_boxes[index][i]["points"][2][1] - correct_boxes[index][i]["points"][1][1])
            
            concat_correct_boxes.append(box)

        return concat_correct_boxes
    else:
        return correct_boxes

def box_alignment(boxes, QN, concat = False):
    """
    Aligns OCR-detected text boxes with a reference list of QN sentences. Optionally concatenates
    all text boxes and QN sentences into a single pair.

    Args:
        boxes (list): List of OCR boxes, where each box contains "points" (coordinates)
                      and "transcription" (text).
        QN (list): List of QN sentences for alignment.
        concat (bool): Whether to concatenate all boxes and sentences.

    Returns:
        list: A list of aligned box and QN sentence pairs, or a single concatenated pair.
    """
    if not concat:
        # Calculate lengths of each OCR box based on vertical height
        box_lengths = []
        for box in boxes:
            box_lengths.append(max(box["points"][3][1] - box["points"][0][1], 
                                   box["points"][2][1] - box["points"][1][1]))
        
        # Process QN list to calculate the word count for each sentence
        QN_lengths = []
        for info in QN:
            # Clean up QN text and split into words
            QN_words = info[-1].strip(' .,-:()[];').lower()
            QN_words = re.sub(r"-", " ", QN_words).strip()
            QN_words = QN_words.split()
            QN_words = [word.strip(' .,?!:()[];') for word in QN_words]
            QN_lengths.append(len(QN_words))  # Store word count
        
        # Calculate average box length per word
        length_for_QN_word = sum(box_lengths) / sum(QN_lengths)
        # Estimate number of words in each box based on its length
        numWords_in_boxes = [round(length / length_for_QN_word) for length in box_lengths]
        
        # Adjust word counts to better match QN lengths, allowing small differences
        for i in range(min(len(numWords_in_boxes), len(QN_lengths))):
            if abs(numWords_in_boxes[i] - QN_lengths[i]) <= 3:
                numWords_in_boxes[i] = QN_lengths[i]

        # Align OCR box word counts with QN sentence word counts using Levenshtein distance
        aligned_box, aligned_QN = levenstein(numWords_in_boxes, QN_lengths)
        index1 = 0  # OCR box index
        index2 = 0  # QN sentence index
        aligned_boxes = []

        # Reconstruct aligned box-QN pairs
        for i in range(len(aligned_box)):
            if aligned_box[i] == "*":  # Missing OCR box
                index2 += 1
            elif aligned_QN[i] == "*":  # Missing QN sentence
                aligned_boxes.append((boxes[index1]['transcription'], ""))
                index1 += 1
            else:
                # Align OCR transcription with the corresponding QN sentence
                aligned_boxes.append((boxes[index1]['transcription'], QN[index2]))
                index1 += 1
                index2 += 1

        return aligned_boxes
    else:
        # Concatenate all OCR box transcriptions and QN sentences into a single pair
        aligned_boxes = [[boxes[0]['transcription'], QN[0]]]
        for index in range(1, len(boxes)):
            aligned_boxes[0][0] += boxes[index]['transcription']
            aligned_boxes[0][1][-1] += " " + QN[index][-1]

        return aligned_boxes

def char_alignment(ocr_sino, QN, SinoNom_Similar_Dict, QN_SinoNom_Dict):
    """
    Aligns SinoNom characters from OCR text with QN words, using a custom similarity
    function for matching.

    Args:
        ocr_sino (str): OCR-detected SinoNom text.
        QN (list): List of QN words for alignment.
        SinoNom_Similar_Dict (dict): Dictionary mapping Sino words to similar Sino words.
        QN_SinoNom_Dict (dict): Dictionary mapping QN words to similar Sino words.

    Returns:
        tuple: A list of aligned Sino-QN pairs and a list of alignment marks.
    """
    # Helper function to compare a Sino word with a QN word
    def Sino_QN_equal(Sino_word, QN_word):
        # Get lists of similar words for Sino and QN
        S1 = SinoNom_Similar_Dict.get(Sino_word, [])
        S2 = QN_SinoNom_Dict.get(QN_word, [])

        # Check for exact match or overlapping similar words
        if Sino_word in S2:
            return 1  # Exact match
        intersection = [symbol for symbol in S1 if symbol in S2]
        if len(intersection) >= 1:
            return 2  # Partial match
        return 0  # No match

    # Convert OCR-detected SinoNom text into a list of characters
    HN = [letter for letter in ocr_sino]
    # Align OCR SinoNom characters with QN words using Levenshtein distance
    aligned_HN, aligned_QN = levenstein(HN, QN, equal_function = Sino_QN_equal)
    alignment = []  # Store aligned pairs
    marked = []  # Store alignment marks for visualization

    # Mark mismatches and matches with different color codes
    for i in range(len(aligned_HN)):
        if aligned_HN[i] != "*":  # Skip placeholders
            if Sino_QN_equal(aligned_HN[i], aligned_QN[i]) == 0:
                marked.append('r')      #! Red: mismatch
                alignment.append((aligned_HN[i], ""))
            else:
                alignment.append((aligned_HN[i], aligned_QN[i]))
                if Sino_QN_equal(aligned_HN[i], aligned_QN[i]) == 1:
                    marked.append('n')  # No color: exact match
                else:
                    marked.append('b')  #? Blue: partial match

    return alignment, marked