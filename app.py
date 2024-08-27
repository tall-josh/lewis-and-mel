from typing import Dict
import requests
from fasthtml import common as fh
import os
import aiohttp

from logger import get_logger

LOGGER = get_logger()


async def make_bible_gateway_links(refs, version="NIV") -> Dict[str, str]:
    ref_links = {}
    for ref in refs:
        search = ref.replace(" ", "%20")
        ref_links[ref] = f"https://www.biblegateway.com/passage/?search={search}&version={version}"
    return ref_links


async def render_response(verse_dict: Dict[str, str]):
    if verse_dict is None:
        return None
    list_items = []
    ref_links = await make_bible_gateway_links(verse_dict.keys())
    for ref, verse in verse_dict.items():
        link = ref_links[ref]
        if ref is not None:
            list_items.append(fh.Li(fh.A(ref, href=link), verse))
    return fh.Ol(*list_items)


async def find_verse(query):
    # Perform the curl request
    MEL_API_TOKEN = os.environ["MEL_API_TOKEN"]
    MEL_ENDPOINT = os.environ.get("MEL_ENDPOINT","http://127.0.0.1:8000/ask-mel")
    headers = {
        "api_key": MEL_API_TOKEN
    }
    params = {
        "query": query
    }
    
    #response = requests.get(MEL_ENDPOINT, headers=headers, params=params)

    async with aiohttp.ClientSession() as session:
        async with session.get(MEL_ENDPOINT, headers=headers, params=params) as response:
            #print(f"GET {url} Status: {response.status}")
            data = await response.json()
            return data


################################################################################

css = fh.Style(':root { --pico-font-size: 100%;}')
app = fh.FastHTML(hdrs=(fh.picolink, css))
rt = app.route

@rt("/")
async def post(search:str):
    if not search:
        return None

    #LOGGER.info(f"search={search}")
    response = await find_verse(search)
    #response = {"aaa": search, "bbb": "bar"}
    #LOGGER.info(f"response={response}")
    new_response = await render_response(response)
    return new_response


@rt("/")
async def get():
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


