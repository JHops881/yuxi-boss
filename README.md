# 📚 Yuxi Boss
*[Lightweight Mandarin pre-study tool with support for Anki]*  

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE.md)

## Use Case 
This tool exists as a workflow solution to native-english Mandarin (simplified) learners while reading native content that contains new or unfamiliar words. Often, it can be cumbersome to continually look up the translation and pinyin for new words while flipping back and forth between dictionary and content tabs. In the end, the reading/learning experience is not seamless and inefficient long term as these new words are forgotten by the next paragraph or sooner. 

This tool will identify your new words within the text using personalized profiles and output them in a fully-featured Anki deck to pre-study prior to reading the content. This supports memory long term and enables a seamless and prepared reading experience - where the context and use of new words can be more focused on. 


## Usage
There are currently no compiled binary releases available. If you would like to use these early versions of the tool, you can run it from source on your machine.

First, clone the repo to your machine
<pre>
git clone https://github.com/JHops881/yuxi-boss.git
</pre>
Next, create a python virtual environment (venv) called "venv" for the project dependencies
<pre>
cd ./yuxi-boss
python3 -m venv venv
</pre>
Activate the venv
<pre>
# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\Activate.ps1
</pre>
Install the dependencies
<pre>
python3 -m pip install -r requirements.txt
</pre>
To run, call main.py
<pre>
python3 ./src/main.py
</pre>

## Development Status
This project is still in early development, and many features are planned.

## Screenshots

Select an HSK level and paste text.
<br>
<img width="401" height="478" alt="image" src="https://github.com/user-attachments/assets/376cd4a4-9fcc-4368-8826-45526d5deb98" />
<br>
Or, optionally, upload a text file instead.
<br>
<img width="249" height="482" alt="image" src="https://github.com/user-attachments/assets/8d32f8aa-bd0e-4eaf-81af-fd989e76f131" />
<br>
Assembled card data from an example set of words extracted from the text with their translations, pinyin, and example sentences.
<br>
<img width="601" height="487" alt="image" src="https://github.com/user-attachments/assets/a6b341ea-8838-40dc-b7e2-2574242d2c72" />
<br>
Anki Deck output file .apkg
<br>
<img width="103" height="32" alt="image" src="https://github.com/user-attachments/assets/0bd04dc7-e111-4ca8-8f05-03adcb411613" />


## Planned Features
- Quick Add Tab - add fully featured cards to a pre-existing deck just by word for quick studying and note taking
- Saving known vocabulary locally
- My Dictionary Tab - browse your known words
- Vocabulary scoring




## Credit
Thank you to CE-DECT for providing the dictionary entries.
https://www.mdbg.net/chinese/dictionary?page=cedict

Thank you to HSK for providing outstanding curriculum as always, and for the vocabulary base levels.
https://www.chinesetest.cn/HSK

Thank you to Tatoeba for providing the example sentences.
https://tatoeba.org/en

Thank you to kerrickstaley and contributors for creating the genanki python module, making this project possible!
https://github.com/kerrickstaley/genanki

Thank you to the Anki team and contributors for making an amazing piece of SRS software.
https://apps.ankiweb.net/


