import streamlit as st

from deepllm.api import *
from deepllm.interactors import Agent

from deepllm.qgen.qa_maker import make_agent, one_quest

st.set_page_config(layout="wide")

st.sidebar.title(":blue[DeepLLM with Follow-up Question Generator]")

local = st.sidebar.checkbox('Local LLM?', value=False)

if local:
    LOCAL_PARAMS['API_BASE'] = st.sidebar.text_input('Local LLM server:', value=LOCAL_PARAMS['API_BASE'])
    local_model()
else:
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        key = st.text_input("Enter your OPENAI_API_KEY:", "", type="password")
        if not key:
            # st.write('Please enter your OPENAI_API_KEY!')
            exit(0)
        else:
            set_openai_api_key(key)

    choice = st.sidebar.radio('OpenAI LLM', ['GPT-4', 'GPT-3.5'])
    if choice == 'GPT-4':
        smarter_model()
    else:
        cheaper_model()


def clean_quest(text):
    return ' '.join(text.split())


question = clean_quest(st.sidebar.text_area("ENTER QUESTION:", key='quest'))

agent = None


def do_answers():
    global agent
    if agent is None:
        agent = make_agent()

    st.write('\nQ:', question)

    context = agent.initiator
    if context is None: context = "think like a genius"
    answer, new_question = one_quest(agent, question, context)
    assert agent.initiator

    st.write('\nA:', answer)

    st.session_state.quest = new_question

    mem_stats()
    if agent.initiator is not None:
        st.write('INITIATOR:')
        st.write([agent.initiator])
    show_mem('SORT_TERM MEMORY:', agent.short_mem)
    show_mem('LONG_TERM MEMORY:', agent.long_mem)


def clear_cache():
    global agent
    if agent is None:
        agent = make_agent()
    st.write('CLEARING CACHE AT:', agent.cache_name())
    agent.clear()
    st.cache_resource.clear()


def mem_stats():
    st.write('SHORT_TERM_MEMORY SIZE:',
             len(agent.short_mem),
             'LONG_TERM_MEMORY SIZE:',
             len(agent.long_mem), 'COSTS:', round(agent.dollar_cost(), 4))


def show_mem(name, mem):
    st.write('*' + name + '*')
    qas = []
    for x in mem.values():
        qas.append(x)
    st.write(qas)


st.sidebar.button("COMPUTE ANSWER", on_click=do_answers)

st.sidebar.button('CLEAR CACHES', on_click=clear_cache)

# st.sidebar.button('SHOW HISTORY', on_click=show_mem)
