import json
def get_tokens():
    tokens_pre = open('tokens.json', 'r', encoding='utf-8')
    tokens = json.load(tokens_pre)
    tokens_pre.close()
    return tokens
def get_conn_data():
    cd = open('ash_conn_data.json', 'r', encoding='utf-8')
    conn_data = json.load(cd)
    cd.close()
    return conn_data