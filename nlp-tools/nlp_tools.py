# -*- coding: utf-8 -*-
"""
This module contains all the NLP Tools required for processing text files.

Running this module shows test outputs for all functions.

Created on Mon Aug  9 18:56:33 2021

@author: Alex "Jal" Counihan
"""
import textstat
import pdf2image
from scipy import signal
import numpy as np
import pytesseract
from matplotlib import pyplot as plt
import PIL
import textract
import os

class nlp_tools():
    """Tools for carrying out NLP tasks."""
    def __init__(self, poppler_path, tesseract_path):
        """
        Initialisation method for the NLP Tools Class.

        Inputs:
        -------
            poppler_path: String
                Path to local poppler installation
            tesseract_path: String
                Path to local tesseract installation
        """
        self.poppler_path = poppler_path
        self.tesseract_path = tesseract_path
        pytesseract.pytesseract.tesseract_cmd = self.tesseract_path

    def text_prepro(self, document):
        """
        """
        try:
            results = textract.process(document)
        except:
            _, extension = os.path.splitext(document) 
            if extension = ".pdf":
                results =self.pdf_phot2text(document)
        #convert files to text required by the class
        return results

    def greyscale(self, image):
        """
        Convert passed image to grayscale.

        Inputs:
        -------
            image: Image File
                Image to be converted.
        Outputs:
        --------
            image: Image File
                Grayscale version of original image.
        """
        image = np.array(image)
        # multiply each dimension to obtain grayscale
        image = np.dot(image[...,:3], [0.2989, 0.5870, 0.1140])
        # convert back to image
        image = PIL.Image.fromarray(image)
        # convert to greyscale
        image = image.convert("L")
        return image

    def pdf_phot2text(self, pdf_path):
        """
        Convert scanned copies of files stored as pdfs to text strings.

        Inputs:
        -------
            pdf_path: String
                The path of the file to convert.
        
        Outputs:
        --------
            results: String
                All the text OCR'd from the document.
        """
        # extract images for denoising (optional)
        images = pdf2image.convert_from_path(pdf_path=pdf_path,
                                     poppler_path=self.poppler_path)
        # convert all images to greyscale (increases accuracy of OCR)
        images = list(map(self.greyscale, images))
        # OCR images using pytesseract
        results = " ".join(list(map(pytesseract.image_to_string, images)))
        # return results
        return results

    def readability(self, text):
        """
        Check the reading level of a document.

        Inputs:
        -------
            text: String
                A string containing the entire document

        Outputs:
        --------
            read_score: String
                Results from text analysis
        """
        # use the flesch reading ease scorer
        reading_ease = textstat.flesch_reading_ease(text)
        # create a dictionary to add the difficulty explanation
        scores = {"Very Confusing" : (0.0, 30.0),
                  "Difficult" : (30.0, 50.0),
                  "Fairly Difficult" : (50.0, 60.0),
                  "Standard" : (60.0, 70.0),
                  "Fairly Easy" : (70.0, 80.0),
                  "Easy" : (80.0, 90.0),
                  "Very Easy" : (90.0, 200.0)}
        # itereate through dictionary values to get correct description
        for score in scores:
            # check the score is greater or equal to lower limit
            # or less than the upper limit
            if reading_ease >= scores[score][0] and reading_ease < scores[score][1]:
                # store the result
                dlevel = score
                break
        # parse the results string
        read_score = "Readability Score: {} \nDifficulty Level: {}".format(reading_ease, dlevel)
        return(read_score)

    def tag(self):
        # auto tag based on themes
        pass

    def gender_neutral(self):
        # checks for gender neutral terminology
        pass

    def acronym_check(self):
        #checks for mad acronyms
        pass


# testing function - only runs at module execution
if __name__ == '__main__':
    nt = nlp_tools(poppler_path=r"C:\poppler\poppler-0.68.0\bin", tesseract_path=r"C:\Program Files\Tesseract-OCR\tesseract.exe")
    print("Readability Example")
    print(nt.readability("This is a supercalifrigistic test text example"))
    print("pdf_phot2text Example")
    print(nt.pdf_phot2text("test_files\JSP507_Part_1_U.pdf"))