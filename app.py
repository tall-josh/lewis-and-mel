from openai import OpenAI
import re
from fasthtml import common as fh
import os

from openai.types.chat import ChatCompletion

from logger import get_logger

# Replace with your OpenAI API key
client = OpenAI(api_key=os.environ["OPENAI_TOKEN"])

LOGGER = get_logger()


MODEL="gpt-4o"
MAX_TOKENS=2048

SYSTEM_PROMPT = ("As a knowledgeable Bible scholar, your task is to provide "
                 "relevant Bible verses based on user descriptions. When "
                 "responding, generate a numbered list of 1 to 5 Bible verses "
                 "that relate to the given topic. Each verse should be "
                 "formatted as follows: [Book Chapter:Verse] [Verse text], "
                 "with each verse appearing on a new line. Ensure that the "
                 "verses are concise, accurate, and directly related to the "
                 "user's description. If fewer than 5 verses are highly "
                 "relevant, it is acceptable to provide a shorter list. Do not "
                 "add anything before of after the numbered list of potential "
                 "verses, just list the verses. Do not number the verses, just "
                 "put each potential verse on a new line. "
                 "An example response is as follows:\n"
                 "\n"
                 "Isaiah 4 2-3: In that day the Branch of the LORD will ...\n"
                 "Genisis 1 1: In the beginning God created the heavens ...\n"
                 "..."
                 )

USER_PROMPT_TEMPLATE = ("Please provide a numbered list of 1 to 5 Bible verses "
                        "that relate to the following description: "
                        "{}.")


def make_bible_gateway_link(verse, version="NIV"):
    search = verse.replace(" ", "%20")
    return f"https://www.biblegateway.com/passage/?search={search}&version={version}"


def extract_bible_reference_and_verse(quote):
    # Regex pattern to match book, chapter, and verse(s)
    pattern = r"^(\d?\s?\w+\s?\w* \d+:\d+(?:-\d+)?)(?::|\s)(.*)"
    
    # Search for the pattern in the quote string
    match = re.search(pattern, quote)
    
    # If a match is found, return the matched groups
    if match:
        bible_reference = match.group(1)
        verse_string = match.group(2).strip()  # Remove any leading/trailing whitespace
        return bible_reference, verse_string
    
    # If no match is found, return None or an appropriate message
    return None, None


def get_query(verse):
    return USER_PROMPT_TEMPLATE.format(verse)


def render_response(response):
    if response is None:
        return None
    list_items = []
    print(f"response: {response}")
    for res in response.split("\n"):
        # ToDo: Link to Bible.org
        print(f"line: {res}")
        if res.strip() == "":   # sfadfsdfd
            print("SKIP")
            continue
        ref, verse = extract_bible_reference_and_verse(res)
        if ref is not None:
            list_items.append(fh.Li(fh.A(ref, href=make_bible_gateway_link(ref)), verse))
    return fh.Ol(*list_items)


def find_verse(query):
    response: ChatCompletion = client.chat.completions.create(
            messages=[
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": USER_PROMPT_TEMPLATE.format(query),
        }
        ],
        model=MODEL,
        max_tokens=MAX_TOKENS,
    )
    return response.choices[0].message.content

################################################################################

css = fh.Style(':root { --pico-font-size: 100%;}')
app = fh.FastHTML(hdrs=(fh.picolink, css))
rt = app.route

@rt("/")
async def post(search:str):
    if not search:
        return None

    LOGGER.info(f"search={search}")
    response = find_verse(search)
    LOGGER.info(f"response={response}")
    new_response = render_response(response)
    return new_response


@rt("/")
def get():
    title = "What's that verse"
    top = fh.Grid(fh.H1(title), style='text-align: center')

    leader = fh.P(fh.I("The verse goes something like ..."))
    new_inp = fh.Input(id="new-search", name="search", placeholder="God created all the stuff")
    search = fh.Form(
        leader,
        fh.Group(
            new_inp, fh.Button("Search")),
        hx_post="/",
        target_id='verse-list',
        hx_swap="innerHTML",
        hx_trigger="click",
    )
    frm = fh.Form(render_response(None), id="verse-list",
               cls='sortable', hx_trigger="end")
    card = fh.Card(frm, header=search, footer=fh.Div(id='current-todo'))
    return fh.Title(title), fh.Container(top, card)

fh.serve()


