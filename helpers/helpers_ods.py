# -*- coding: utf-8 -*
"""
Fonction pour gerer les fichiers ods
"""


# --------------------------------------------------------------------------- #
# A l'anciennce avec le package uno qui n'est plus maintenu
# ---------------------------------------------------------------------------- #
# def create_doc(path: str):
#     import pylocalc as pyods
#     pyods_doc = pyods.Document(path)
#     try:
#         pyods_doc.connect()
#     except:
#         raise ValueError(" * ERREUR : pas de connection possible à "+path+'\n')
#
# def get_sheet(pyods_doc, sheet_name: str):
#     # sheet = pyods_doc['Adhesions_Adultes']
#     sheet = pyods_doc[sheet_name]
#     return sheet
#
# def append_row_to_sheet(pyods_sheet, data: str):
#     pyods_sheet.append_row(data)
#     return
#
# def save_doc(pyods_doc, path: str):
#     try:
#         pyods_doc.save()
#     except:
#         raise ValueError(" * ERREUR : impossible d'enregistrer le document "+path+'\n')
#     try:
#         pyods_doc.close()
#     except:
#         raise ValueError(" * ERREUR : le document "+path+" ne s'est pas fermé correctement\n")
#     return
#

# --------------------------------------------------------------------------- #
# Gestion des osd directement avec pandas
# ---------------------------------------------------------------------------- #
import pandas as pd
from typing import List, Dict


def read_ods_file(file_path) -> pd.DataFrame:
    """
    Open ods file
    """
    try:
        # Read the ODS file
        df = pd.read_excel(file_path, engine='odf')

        # Display basic information about the dataframe
        print(f"Successfully read file: {file_path}")
        print(f"Number of rows: {len(df)}")
        print(f"Number of columns: {len(df.columns)}")
        print("\nColumn names:")
        print(df.columns.tolist())

        # Display the first few rows
        print("\nFirst few rows of the data:")
        print(df.head())
        return df
    except Exception as e:
        print(f"Error reading file {file_path}: {str(e)}")
        return None


class OdsConnectException(Exception):
    def __init__(self, in_error: str):
        super().__init__(in_error)

class OdsSaveError(Exception):
    def __init__(self, in_error: str):
        super().__init__(in_error)

class OdsCloseError(Exception):
    def __init__(self, in_error: str):
        super().__init__(in_error)

class ODSDocument:
    """
    Util class to handle ods simply an ods document
    """
    def __init__(self, path: str):
        self.path = path
        self.writer = None
        self.sheets = {}
        self.connect()

    def connect(self):
        try:
            existing_sheets = pd.read_excel(self.path, engine="odf", sheet_name=None)
            self.sheets = {name: df for name, df in existing_sheets.items()}
        except FileNotFoundError:
            pass  # Le fichier n'existe pas encore, ce n'est pas une erreur
        except Exception as e:
            raise OdsConnectException(f" * ERREUR : pas de connexion possible à {self.path}\n{str(e)}")

    def add_data_to_sheet(self, sheet_name: str, data: dict):
        if sheet_name not in self.sheets:
            self.sheets[sheet_name] = pd.DataFrame()

        # new_row = pd.DataFrame([data], columns=self.sheets[sheet_name].columns)
        new_row = pd.DataFrame(data)
        self.sheets[sheet_name] = pd.concat(
            [self.sheets[sheet_name], new_row],
            axis=0,
            ignore_index=True
        )
        return


    def save(self):
        try:
            with pd.ExcelWriter(self.path, engine="odf") as writer:
                for sheet_name, df in self.sheets.items():
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
        except Exception as e:
            raise OdsSaveError(f" * ERREUR : impossible d'enregistrer le document {self.path}\n{str(e)}")
        print(f"A bien ecrit {self.path}")
        return


# def create_doc(path: str) -> ODSDocument:
#     doc = ODSDocument(path)
#     return doc

# def append_row_to_sheet(pd_sheet: pd.DataFrame, data: Any):
#     print("data: {}".format(data))
#     new_row = pd.DataFrame([data])
#     print("new_row: {}".format(data))
#     return pd.concat([pd_sheet, new_row], ignore_index=True)


if __name__ == "__main__":
    path = "test_helpers_ods.ods"

    # Créer ou ouvrir un document
    doc = ODSDocument(path)

    # Ajouter des données à la feuille
    data = ["John Doe", 30, "New York"]
    doc.add_data_to_sheet("Feuille1", data)

    # Sauvegarder et fermer le document
    doc.save()

    print("Opération terminée avec succès.")
