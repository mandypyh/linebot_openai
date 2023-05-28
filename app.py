from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

#======python的函數庫==========
import tempfile, os
import datetime
import openai
import time
#======python的函數庫==========

app = Flask(__name__)
static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')
# Channel Access Token
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
# Channel Secret
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))
# OPENAI API Key初始化設定
openai.api_key = os.getenv('OPENAI_API_KEY')


# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

def GPT_response(text):
    # 接收回應
    response = openai.Completion.create(model="text-davinci-003", prompt=text, temperature=0.5, max_tokens=500)
    print(response)
    # 重組回應
    answer = response['choices'][0]['text']
    return answer

def remove_first_two_lines(text):
    lines = text.split('\n')
    if len(lines) >= 2:
        lines = lines[2:]
    return '\n'.join(lines)

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text

    if msg.startswith('ai:'):
        GPT_answer = GPT_response(msg)
        print(remove_first_two_lines(GPT_answer))
        line_bot_api.reply_message(event.reply_token, TextSendMessage(remove_first_two_lines(GPT_answer)))
    
    elif msg == "功能說明":
        message = []
        message.append(
                TemplateSendMessage(
                    alt_text='Buttons template',
                    template=ButtonsTemplate(
                        title='功能說明',
                        text='本官方帳號無一對一聊天功能，皆會回覆一樣的文字。如果你需要ChatGPT的回覆與建議，請在訊息前面加＂ai:＂~ 我們有以下功能:',
                        actions=[
                            MessageTemplateAction(
                                label='文字雲',
                                text='文字雲',
                            ),
                            MessageTemplateAction(
                                label='分群結果',
                                text='分群結果',
                            ),
                        ]
                    )
                )
            )
        print("type of msg: {}".format(type(msg)))
        line_bot_api.reply_message(event.reply_token, message) 

    elif msg == "地圖標記":
        reply_msg = None
        print(reply_msg)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(reply_msg))

    elif msg == "文字雲":
        message = []
        message.append(
                TemplateSendMessage(
                    alt_text='Buttons template',
                    template=ButtonsTemplate(
                        title='文字雲',
                        text='請選擇想看的文字雲',
                        actions=[
                            MessageTemplateAction(
                                label='標題',
                                text='標題',
                            ),
                            MessageTemplateAction(
                                label='內文',
                                text='內文',
                            ),
                        ]
                    )
                )
            )
        print("type of msg: {}".format(type(msg)))
        line_bot_api.reply_message(event.reply_token, message)     

    elif msg == "分群結果":
        message = []
        message.append(
                TemplateSendMessage(
                    alt_text='Buttons template',
                    template=ButtonsTemplate(
                        title='分群結果',
                        text='請選擇想看的分群結果',
                        actions=[
                            MessageTemplateAction(
                                label='SVD',
                                text='SVD',
                            ),
                            MessageTemplateAction(
                                label='t-SNE',
                                text='t-SNE',
                            ),
                        ]
                    )
                )
            )
        print("type of msg: {}".format(type(msg)))
        line_bot_api.reply_message(event.reply_token, message)

    else:
        reply_msg = msg
        print(reply_msg)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(reply_msg))
        

@handler.add(PostbackEvent)
def handle_message(event):
    print(event.postback.data)
       
        
import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)