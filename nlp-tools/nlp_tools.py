# -*- coding: utf-8 -*-
"""
This module contains all the NLP Tools required for processing text files.

Running this module shows test outputs for all functions.

Created on Mon Aug  9 18:56:33 2021

@author: Alex "Jal" Counihan
"""
import textstat
import pdf2image
import numpy as np
import pytesseract
import PIL
import textract
import os
import logging
import re
import nltk
import string

class nlp_tools():
    """
    Tools for carrying out NLP tasks.

    Functions:
    ----------
    text_prepro - Get text from file.

    greyscale - Used internally to convert images to greyscale.

    pdf_phot2text - Used internally to extract text from scanned pdfs.

    readability - Gives a readability score for a piece of text.

    tag - Suggests tags for a given text.

    gender_neutral - Checks for gender neutral terminology.

    acronym_check - Find acronyms not currently in acronym database.
    """
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
        Extract text from document to carry out NLP.

        Inputs:
        -------
            document: String
                Path to the document to process

        Outputs:
        --------
            results: String
                Extracted text from document
        """
        try:
            results = textract.process(document)
        except:
            _, extension = os.path.splitext(document) 
            if extension == ".pdf":
                results = self.pdf_phot2text(document)
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

    def clean_tokens(self, text):
        # split into words
        tokens = nltk.tokenize.word_tokenize(text)
        # convert to lower case
        tokens = [w.lower() for w in tokens]
        # remove punctuation from each word
        table = str.maketrans('', '', string.punctuation)
        stripped = [w.translate(table) for w in tokens]
        # remove remaining tokens that are not alphabetic
        words = [word for word in stripped if word.isalpha()]
        # filter out stop words
        stop_words = set(nltk.corpus.stopwords.words('english'))
        words = [w for w in words if not w in stop_words]
        return words

    def tag(self, text):
        """
        Suggest tags for the files uploader.

        Inputs:
        -------
            text: String
                Text to get tags from.

        Outputs:
        --------
            results: List
                Top 5 suggestions.
        """
        words = self.clean_tokens(text)
        # create an instance of bigram
        bigram_measures = nltk.collocations.BigramAssocMeasures()
        # change this to read in your data
        finder = nltk.BigramCollocationFinder.from_words(words)
        # only bigrams that appear 3+ times
        finder.apply_freq_filter(3)
        # return the 5 n-grams with the highest PMI
        results = finder.nbest(bigram_measures.pmi, 5)
        return results

    def gender_neutral(self, text):
        """
        Identify terminology that is not gender neutral.

        DEV - Looking for pre-made solution.s

        Current list comprehension not quite working.

        Inputs:
        -------
            text: String
                Text to analyse.
        
        Outputs:
        --------
            results: List
                All found non-gender neutral terminology.
        """
        terminology = ['man', 'woman', 'his', 'her', 'he', 'hers']
        words = self.clean_tokens(text)
        # checks for gender neutral terminology
        results = []
        results = [w for w in words if(i in w for i in terminology)]
        # check if any terminology has been found
        if len(results) == 0:
            results = "No gender neutral terminology found."
        return results

    def acronym_check(self, acronyms, text):
        """
        Find acronyms not on current database.

        DEV - Check for brackets near expression
        as these suggest that the acronym is explained
        If it is explained and not in the database then consider
        writing back.

        Inputs:
        -------
            acronyms: List
                All acronyms within the database
            text: String
                Text to analyse
        
        Outputs:
        --------
            matches: List
                List of unknown acronyms in string
        """
        # regex to find capitals of length 2-4
        pattern = r"\b[A-Z]{2,4}\b"
        # find all matches in source text
        matches = re.findall(pattern, text)
        # remove duplicates
        matches = list(set(matches))
        # remove matches in acronym database
        matches = [x for x in matches if x not in acronyms] 
        if len(matches) == 0:
            return "No unknown acronyms found"
        else:
            return matches


# testing function - only runs at module execution
if __name__ == '__main__':
    logging.basicConfig(filename='nlp_test_log.log', level=logging.DEBUG)
    nt = nlp_tools(poppler_path=r"C:\poppler\poppler-0.68.0\bin", tesseract_path=r"C:\Program Files\Tesseract-OCR\tesseract.exe")
    """
    print("pdf_phot2text")
    text = nt.text_prepro("test_files\JSP507asScannedDoc.pdf")
    logging.info("pdf_phot2text first 1000 characters: \n" + text[:1000])
    print("Textract preprocess")
    text = nt.text_prepro("test_files\JSP507_Part_1_U.pdf")
    logging.info("Textract preprocess first 1000 characters: \n" + text[:1000])
    print("Readability Test")
    text = nt.readability(text)
    logging.info("Readability Test: \n" + text)
    with open(r"test_files\textract_text.txt", "r") as file:
        text = file.read().replace("\n", " ")
    acronyms = ["ADD", "AC", "AND"]
    print(nt.acronym_check(acronyms, text))
    print("tag Test")
    logging.info(nt.tag(text))
    """
    text = "the policewoman put her hand on the criminals bum bums chairman him her his herself hisself"
    print(nt.gender_neutral(text))