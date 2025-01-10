import pandas as pd
import ast
from tqdm import tqdm

def get_dictionaries(Sino_sim_path = "SinoNom_similar_Dic.xlsx",
                     QN_Sino_path = "QuocNgu_SinoNom_Dic.xlsx"):
    # Load two Excel files into pandas DataFrames
    SinoNom_Similar_Dict_temp = pd.read_excel(Sino_sim_path)
    QN_SinoNom_Dict_temp = pd.read_excel(QN_Sino_path)

    # Initialize a dictionary to store SinoNom character similarities
    SinoNom_Similar_Dict = dict()
    for i in tqdm(range(len(SinoNom_Similar_Dict_temp)), desc = "Load Sino_Sim dictionary"):
        #
        top_20 = ast.literal_eval(SinoNom_Similar_Dict_temp['Top 20 Similar Characters'][i])
        
        # If the character does not already have an entry, create one with its top similar characters
        if SinoNom_Similar_Dict.get(SinoNom_Similar_Dict_temp['Input Character'][i]) is None:
            # Parse 'Top 20 Similar Characters' into a list and add it to the dictionary entry
            SinoNom_Similar_Dict[SinoNom_Similar_Dict_temp['Input Character'][i]] = (
                [SinoNom_Similar_Dict_temp['Input Character'][i]] + top_20
            )
        else:
            # If the character already exists in the dictionary, append the similar characters to its list
            SinoNom_Similar_Dict[SinoNom_Similar_Dict_temp['Input Character'][i]] += (
                list(set(top_20) - set(SinoNom_Similar_Dict[SinoNom_Similar_Dict_temp['Input Character'][i]]))
            )
            
        # Iterate through the list of top 20 similar characters
        for letter in top_20:
            # If the similar character does not have an entry, create one with the input character and its similar characters
            if (SinoNom_Similar_Dict.get(letter) is None):
                # Add the input character and its similar characters to the dictionary entry
                SinoNom_Similar_Dict[letter] = (
                    [SinoNom_Similar_Dict_temp['Input Character'][i]] + top_20
                )
            else:
                # If the character already exists in the dictionary, update its list by adding unique characters
                SinoNom_Similar_Dict[letter] += (
                    list(set([SinoNom_Similar_Dict_temp['Input Character'][i]] + top_20) - 
                         set(SinoNom_Similar_Dict[letter]))
                )

    # Initialize a dictionary to store mappings from Quoc Ngu to SinoNom characters
    QN_SinoNom_Dict = dict()
    for i in tqdm(range(len(QN_SinoNom_Dict_temp)), desc = "Load QN_Sino dictionary"):
        # If the Quoc Ngu word does not have an entry, create one with its associated SinoNom character
        if QN_SinoNom_Dict.get(QN_SinoNom_Dict_temp['QuocNgu'][i]) is None:
            QN_SinoNom_Dict[QN_SinoNom_Dict_temp['QuocNgu'][i]] = [QN_SinoNom_Dict_temp['SinoNom'][i]]
        else:
            # If an entry already exists, append the SinoNom character to its list
            QN_SinoNom_Dict[QN_SinoNom_Dict_temp['QuocNgu'][i]].append(QN_SinoNom_Dict_temp['SinoNom'][i])

    # Return both dictionaries
    return SinoNom_Similar_Dict, QN_SinoNom_Dict