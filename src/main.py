import genanki
import json
import csv
import requests
from bs4 import BeautifulSoup
from tools import decode_pinyin as dc
import time

# Path to the text that is going to be analyzed and have a deck made from it's unfamiliar vocab.
INPUT_FILE_PATH: str = "../input/file.txt"

# Path to a (table-like) json file containing the entries of all HSK 2.0 words 1-6 tagged by level.
HSK_PATH: str = "../data/hsk.json"

# Path to the users known words.
SAVED_PATH: str = "../data/saved.json"

# Path to the json-fied CE-DECT dictionary -locally containing a best-effort database of all known chinese words
CEDICT_PATH: str = "../data/cedict.json"

# Path to file containting all our local example sentences
SENTENCES_PATH: str = "../data/sentences.tsv"




def get_example_sentence(w: str) -> dict:
    """Use web scraping to retrieve a dictionary info about a mandarin word. Most importatly,
    it returns an example sentence with its pronounciation and translation. All dictionary
    information is scraped from purpleculture.net.

    Args:
        w (str): Mandarin word.

    Returns:
        dict: Mandarin example sentence that uses the word.\n
        {  
            "word" : ...
            "pinyin" : ...
            "definition" : ...
            "ex_sentence" : ...
            "ex_sentence_pinyin" : ...
            "ex_sentence_transl" : ...
        }
    """
    
    # We are going to scrape from Purple Culture. The team gave me explicit permission.
    url: str = f"https://www.purpleculture.net/dictionary-details/?word={w}"
    
    # We are going to use this user agent to appear more human.
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.0.0 Safari/537.36"
    }   
    
    # Let's make the request to retrieve the dictionary page for our word
    response = requests.get(url, headers=headers)
    
    # For Successful responses:
    if response.status_code == 200:
        
        try:
        
            # let's change the response into something we can parse.
            html_content = response.text

            # Now, we parse it.
            soup = BeautifulSoup(html_content, "html.parser")
            
            # Here's a laundry list of what we want from the page:
            #   - the word
            #   - the word's pinyin pronounciation
            #   - the word's english meaning
            #   - an example sentence
            #   - the example sentence's meaning in english
            
            word:       str = ""
            pinyin:     str = ""
            definition: str = ""
            ex_sentence:        str = ""
            ex_sentence_transl: str = ""
            ex_sentence_pinyin: str = ""
            
            # This element contains the word and it's pinyin.
            word_block = soup.find("ruby", class_="mainsc")
            
            # Step 1: Extract the word.
            word_block_hanzi_elements = word_block.find_all("a", recursive=False)
            for element in word_block_hanzi_elements:
                word += element.text.strip()
            
            # Step 2: Extract the pinyin.
            word_block_pinyin_elements = word_block.find_all("rt")
            for element in word_block_pinyin_elements:
                pinyin += element.text.strip()

            # Step 3: Extract the meaning.
            definition = soup.find("div", class_="en py-2").text.strip()
            
            # Step 4. Extract the Example sentence
            ex_sentence_elements = soup.find(id="sen1").find_all("span", class_="cnchar")
            for element in ex_sentence_elements:
                ex_sentence += element.text.strip()
                
            # Step 5: Extract Example Sentence translation.
            ex_sentence_transl = soup.find(id="ensen1").text.strip()
            
            # Step 6: Get the Sentence Pinyin.
            ex_sentence_pinyin = str(soup.find(id="ppysen1")['value'])
            # Comes out like this: "wo3 xi3 huan1||ting1||liu2 xing2||yin1 yue4|| ||||"
            # Let's fix that.
            ex_sentence_pinyin = ex_sentence_pinyin.replace(" ", "").replace("||", " ").strip()
            # Now we can convert it to proper pinyin letters.
            pinyin_list: list[str] = ex_sentence_pinyin.split()
            for i in range(len(pinyin_list)):
                pinyin_list[i] = dc.decode_pinyin(pinyin_list[i])
            ex_sentence_pinyin = " ".join(pinyin_list)
            
            return {
                "word" : word,
                "pinyin" : pinyin,
                "definition" : definition,
                "ex_sentence" : ex_sentence,
                "ex_sentence_pinyin" : ex_sentence_pinyin,
                "ex_sentence_transl" : ex_sentence_transl
            }
            
        except AttributeError:
            
            return None
            
    else:
        print("Failed to retrieve the webpage:", response.status_code)
        




def segmentate(text: str, lookup_file_path: str, lookup_key: str) -> list[str]:
    """
    Uses a custom algorigthm to break text into dictionary words verified by a 
    local dictionary. Words are returned on a best-guess basis -meaning some 
    three character strings (e.g. 不同意) will/may return two words (同意, 不同)
    because the algorigthm is unable to derive contextual meaning.

    Args:
        text (str): The text to segmentate into dictionary words.
        lookup_file_path (str): path to a (table-like) json file that contains
            the dictionary entries to check against.
        lookup_key: (str): The json key under which the word is stored in each 
            dictionary entry. 

    Returns:
        list: A list of all dictionary words identified from the text, mostly in
            order, and also containing repeats.     
    """
    
    # 不同意
    # 不同意思
    # TODO: fix these situations
    
    ''' This file contains a json list of dictionary entries. Each one has a key
    value pair with the key "lookup_key". We want to retrieve the value afrom all
    of them and store in a in a dict so that we can lookup up values faster than
    iterating through a potentially 119k obj list.'''
    with open(lookup_file_path, encoding="utf8") as file:
    
        lookup_json_dumped: str = file.read()

        # Parse into python obj (dict).
        lookup_json_loaded: dict = json.loads(lookup_json_dumped)
        
        # Let's create our map that is going to store all of the lookup_key values
        lookup_map: dict[str] = {}
        
        # Extract the values from all the entries in the lookup_json_loaded.
        for row in lookup_json_loaded:
            lookup_map[row[lookup_key]] = None
            
        # This will contain the words after it is segmented properly.
        segments: list[str] = []
        
        # Custom algo.. how do I begin to explain. TODO: document.
        def worder(index: int, text: str, seg: str, map: dict, depth: int) -> any:
            if seg + text[index+1] in map:
                return worder(index+1, text, seg+text[index+1], map, depth+1)
            else:
                return seg, depth
        
        # algo v1.0
        is_child: bool = False
        for i, char in enumerate(text):
            
            # is it real?
            if char in lookup_map:
                
                (segment, depth) = worder(i, text, char, lookup_map, 0)
                
                if not is_child or (is_child and depth > 0):
                    segments.append(segment)

                    
                is_child = depth
                    
            # No, Okay we'll deal with this later.
            else:
                pass
        
        return segments
            



# Step 1: Read in the input text.
input_text: str = ""
with open(INPUT_FILE_PATH, encoding="utf8") as input_file:
    input_text = input_file.read()

# Step 2: Get the highest HSK 2.0 level that the user has completed.
waiting_for_level: bool = True
user_hsk_level: int = 0
while waiting_for_level:
    try:
        input_u: str = input("Enter your HSK 2.0 level (highest level which you have fully completed) e.g. '3': ")
        user_hsk_level = int(input_u) # TODO: This may not be the best method.
        if 0 <= user_hsk_level <= 6:
            waiting_for_level = False
    except:
        print("Some sort of invalid input received; just input a whole number.")


# Step 3: Load in a list of all the words that the user knows from both HSK and saved.
known_words: list[str] = []

# First, the HSK words.
with open(HSK_PATH, encoding="utf8") as hsk_file:
    hsk_json: str = hsk_file.read()
    hsk_data: list[dict] = json.loads(hsk_json)
    for word_data in hsk_data:
        if word_data["HSK"] <= user_hsk_level:
            known_words.append(word_data["hanzi"])
            
# Second, the saved known words.
with open(SAVED_PATH, encoding="utf8") as saved_file:
    saved_json: str = saved_file.read()
    saved_data: list[dict] = json.loads(saved_json)
    for word_data in saved_data:
        known_words.append(word_data["hanzi"])

# Step 4: Cut the read-in text into words, and save a list of them without duplicates
words: list[str] = []

# segments has duplicates in it.
segments: list[str] = segmentate(input_text)

for segment in segments:
    if segment not in words:
        words.append(segment)

# Step 5: Now we need to clean up the segment list, by removing punctuation and numbers. (what's left is words only)
        
# Note on 2024-12-26-Thurs-16:11CDT by Joseph. Since removing jieba, the new segmentate() algorigthm only outputs
# verified dictionary words -automatically eliminates punctuation, non-mandarin, and insignificant numbers.

# Step 6: Subtract the known words from the words that we have been left with.
for known_word in known_words:

    if known_word in words:
        i = words.index(known_word)
        words.pop(i)

# Step 7: Let's initialize a data structure that will hold our
# words, pinyin, meaning, example sentence, example sentence pinyin, and example sentence meaning.
# This is the final step before moving on to exporting this data into an ANKI deck.
deck_data: list[dict[str]] = []

# Step 8: populate with words.
for word in words:
    deck_data.append(
        {
            "word" : word
        }
    )

# TODO: solve the 只 issue. it has multiple entries. all 多音字 do.
# Step 9: populate with pinyin and meaning.
with open(CEDICT_PATH, encoding="utf8") as cedict_file:
    cedict_json_str: str = cedict_file.read()
    cedict: list[dict] = json.loads(cedict_json_str)
    for deck_entry in deck_data:
        for cedict_entry in cedict:
            if deck_entry["word"] == cedict_entry["simplified"]:
                deck_entry["pinyin"] = cedict_entry["pinyin"]
                deck_entry["definition"] = cedict_entry["english"]
                
        # Catch erroneous words that don't exit accoarding to cedict. Delete them.
        if "definition" not in deck_entry:
            print(deck_entry)
            deck_data.remove(deck_entry)
                
# Step 10: populate with example sentence, its meaing, and pinyin.
with open(SENTENCES_PATH, encoding="utf8") as sentences_file:
    ex_sentences: list[str] = list(csv.reader(sentences_file, delimiter="\t"))
    for deck_entry in deck_data:
        for ex_sentence in ex_sentences:
            if deck_entry["word"] in ex_sentence[0]:
                
                #TODO: SMART LEVELING
                #TODO: 不同 is in 不同意! Fix this!
                
                deck_entry["ex_sentence"] = ex_sentence[0]
                deck_entry["ex_sentence_pinyin"] = ex_sentence[1]
                deck_entry["ex_sentence_transl"] = ex_sentence[2]
                break
            
# Step 11: Some of the words don't have example sentences. We need to scrape the web to retrieve them.
scrape_count: int = 0
scraped_example: dict[str|list] = {}
for deck_entry in deck_data:
    if "ex_sentence" not in deck_entry:
        
        print(f"No local example found for: {deck_entry["word"]}")
        print("Retrieving one from online.")
        
        if scrape_count == 0:
            scraped_example = get_example_sentence(deck_entry["word"])
        else:
            print("Following ethical scraping conduct. Please wait (10s) . . . ")
            time.sleep(10)
            scraped_example = get_example_sentence(deck_entry["word"])
            
        scrape_count += 1
        
        deck_entry["ex_sentence"] = scraped_example["ex_sentence"]
        deck_entry["ex_sentence_pinyin"] = scraped_example["ex_sentence_pinyin"]
        deck_entry["ex_sentence_transl"] = scraped_example["ex_sentence_transl"]
            
# print(deck_data)
test=json.dumps(deck_data, ensure_ascii=False, indent=4) # Debug
print(test)

# Step 12: Covert to an anki deck


qfmt: str = ""
with open("./front.html") as front:
  qfmt = front.read()

afmt: str = ""
with open("./back.html") as back:
  afmt = back.read()
  
css: str = ""
with open("./style.css") as f:
  css = f.read()
  
my_model = genanki.Model(
    1907462364,
    'Simple Model',
    fields=[
        {'name': 'Word'},
        {'name': 'Pinyin'},
        {'name': 'Definition'},
        {'name': 'ExampleSentence'},
        {'name': 'ExamplePinyin'},
        {'name': 'ExampleTranslation'},
    ],
    css=css,
    templates=[
        {
            'name': 'Card 1',
            'qfmt': qfmt,
            'afmt': afmt
        },
    ]
)

notes: list[genanki.Note] = []
for deck_entry in deck_data:
    notes.append(
        genanki.Note(
            model=my_model,
            fields=[
                deck_entry["word"],
                deck_entry["pinyin"],
                " ".join(deck_entry["definition"]),
                deck_entry["ex_sentence"],
                deck_entry["ex_sentence_pinyin"],
                deck_entry["ex_sentence_transl"]
            ]
        )
    )

my_deck = genanki.Deck(
    1907462364,
    'TestDeck')

for note in notes:  
    my_deck.add_note(note)

genanki.Package(my_deck).write_to_file('../output/output.apkg')