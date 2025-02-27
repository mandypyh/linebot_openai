from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
import tempfile, os
import datetime
import openai
import time
import json
import heapq


app = Flask(__name__)
static_tmp_path = os.path.join(os.path.dirname(__file__), "static", "tmp")
line_bot_api = LineBotApi(os.getenv("CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("CHANNEL_SECRET"))
openai.api_key = os.getenv("OPENAI_API_KEY")


# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=["POST"])
def callback():
    # get X-Line-Signature header value
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"


def GPT_response(text):
    response = openai.Completion.create(
        model="text-davinci-003", prompt=text, temperature=0.5, max_tokens=500
    )
    print(response)
    answer = response["choices"][0]["text"]
    return answer


def remove_first_two_lines(text):
    lines = text.split("\n")
    if len(lines) >= 2:
        lines = lines[2:]
    return "\n".join(lines)


def recommend_article(keyword):
    with open("sentiment_analysis.json", "r", encoding="utf-8") as f:
        whole_text = json.load(f)

    filtered_title = []
    positive_dict = {}
    negative_dict = {}

    for i in whole_text:
        if keyword in i:
            filtered_title.append(i)
        if keyword in whole_text[i]["content"]:
            filtered_title.append(i)

    for filtertitle in filtered_title:
        sentiment = whole_text[filtertitle]["sentiment"]
        if sentiment == "Positive":
            positive_dict[filtertitle] = whole_text[filtertitle]["score"]
        elif sentiment == "Negative":
            negative_dict[filtertitle] = whole_text[filtertitle]["score"]

    result = "好評文章:\n"
    pos_top_keys = heapq.nlargest(3, positive_dict, key=positive_dict.get)
    for j in pos_top_keys:
        result += whole_text[j]["link"]
        result += "\n"

    result += "\n\n負評文章:\n"
    neg_top_keys = heapq.nlargest(3, negative_dict, key=negative_dict.get)
    for j in neg_top_keys:
        result += whole_text[j]["link"]
        result += "\n"

    return result


# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text

    if msg.startswith("@"):
        # GPT_answer = GPT_response(msg[1:])
        # print(remove_first_two_lines(GPT_answer))
        # line_bot_api.reply_message(event.reply_token, TextSendMessage(remove_first_two_lines(GPT_answer)))

        reply_msg = "目前暫停此服務!"
        print(reply_msg)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(reply_msg))

    elif msg == "ChatGPT":
        message = []
        message.append(
            TemplateSendMessage(
                alt_text="Buttons template",
                template=ButtonsTemplate(
                    title="ChatGPT",
                    text='如果需要ChatGPT提供日本旅遊相關資訊的回覆與建議，請在訊息前面加"@"。例如:',
                    actions=[
                        MessageTemplateAction(
                            label="@東京有哪些景點",
                            text="@東京有哪些景點",
                        ),
                        MessageTemplateAction(
                            label="@大阪有哪些景點",
                            text="@大阪有哪些景點",
                        ),
                    ],
                ),
            )
        )
        print("type of msg: {}".format(type(msg)))
        line_bot_api.reply_message(event.reply_token, message)

    elif msg == "功能說明":
        message = []
        message.append(
            TemplateSendMessage(
                alt_text="Buttons template",
                template=ButtonsTemplate(
                    title="功能說明",
                    text='本官方帳號無一對一聊天功能，皆會回覆一樣的文字；如果需要ChatGPT回覆，請在訊息前面加"@"。我們的功能有:',
                    actions=[
                        MessageTemplateAction(
                            label="文字雲",
                            text="文字雲",
                        ),
                        MessageTemplateAction(
                            label="分群結果",
                            text="分群結果",
                        ),
                        MessageTemplateAction(
                            label="推薦文章",
                            text="推薦文章",
                        ),
                        MessageTemplateAction(
                            label="最新文章",
                            text="最新文章",
                        ),
                    ],
                ),
            )
        )
        print("type of msg: {}".format(type(msg)))
        line_bot_api.reply_message(event.reply_token, message)

    elif msg == "最新文章":
        message = []
        message.append(
            TemplateSendMessage(
                alt_text="Buttons template",
                template=ButtonsTemplate(
                    title="最新文章",
                    text="抓取最新日本旅遊網站文章，掌握近期討論熱點！",
                    actions=[
                        MessageTemplateAction(
                            label="Dcard",
                            text="Dcard",
                        ),
                        MessageTemplateAction(
                            label="樂吃購!日本",
                            text="樂吃購!日本",
                        ),
                        MessageTemplateAction(
                            label="聯合新聞網",
                            text="聯合新聞網",
                        ),
                    ],
                ),
            )
        )
        print("type of msg: {}".format(type(msg)))
        line_bot_api.reply_message(event.reply_token, message)

    elif msg == "Dcard":
        reply_msg = "1. 東京六天五夜自由行，Day6晴空塔\nhttps://www.dcard.tw/f/japan_travel/p/242373525 \n\n2. 東京六天五夜自由行，沒有重點的Day5\nhttps://www.dcard.tw/f/japan_travel/p/242373221 \n\n3. #資訊 羽田紅眼航班，夜間巴士這樣搭\nhttps://www.dcard.tw/f/japan_travel/p/242373230"
        print(reply_msg)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(reply_msg))

    elif msg == "樂吃購!日本":
        reply_msg = "1. 繪本般的田園風景！長野縣秘境小鎮「安曇野」2天1夜自由行景點推薦\nhttps://tokyo.letsgojp.com/archives/469084/ \n\n2. 東京出發2.5小時！長野縣秘境「安曇野」，一探北阿爾卑斯山鄉村小鎮的慢活田園美景\nhttps://tokyo.letsgojp.com/archives/394163/ \n\n3. 【2023四國自由行】超完整攻略！瀨戶內小島、溫泉秘境玩透透，10日、7日、5日行程總覽！\nhttps://shikoku.letsgojp.com/archives/347957/"
        print(reply_msg)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(reply_msg))

    elif msg == "聯合新聞網":
        reply_msg = "1. 虎航又促銷！飛澳門799元、飛日多地1,299元，第二波優惠再加碼韓國、曼谷\nhttps://udn.com/news/story/7934/7181370 \n\n2. 限定口味快追！ 2023大阪美食「grenier 超人氣烤布蕾千層酥」 梅田阪急百貨必吃散步甜點\nhttps://udn.com/news/story/9652/7161935 \n\n3. 小樽B級美食！昭和27年至今的在地老店，皮薄肉多汁的炸半雞定食，還出了自家的汽水\nhttps://udn.com/news/story/9650/7078064"
        print(reply_msg)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(reply_msg))

    elif msg == "推薦文章":
        message = []
        message.append(
            TemplateSendMessage(
                alt_text="Buttons template",
                template=ButtonsTemplate(
                    title="推薦文章",
                    text='搜尋特定關鍵字，提供情緒分析後的最新推薦文章! \n請在想查詢的關鍵字前面加＂#"。例如:',
                    actions=[
                        MessageTemplateAction(
                            label="#東京",
                            text="#東京",
                        ),
                        MessageTemplateAction(
                            label="#大阪",
                            text="#大阪",
                        ),
                    ],
                ),
            )
        )
        print("type of msg: {}".format(type(msg)))
        line_bot_api.reply_message(event.reply_token, message)

    if msg.startswith("#"):
        reply_msg = recommend_article(msg[1:])
        print(reply_msg)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(reply_msg))

    elif msg == "文字雲":
        message = []
        message.append(
            TemplateSendMessage(
                alt_text="Buttons template",
                template=ButtonsTemplate(
                    title="文字雲",
                    text="分析近期日本旅遊文章的常見詞彙，分別根據標題與內文文字，掌握近期日本旅遊的流行重點！",
                    actions=[
                        MessageTemplateAction(
                            label="標題結果",
                            text="標題結果",
                        ),
                        MessageTemplateAction(
                            label="內文結果",
                            text="內文結果",
                        ),
                    ],
                ),
            )
        )
        print("type of msg: {}".format(type(msg)))
        line_bot_api.reply_message(event.reply_token, message)

    elif msg == "分群結果":
        message = []
        message.append(
            TemplateSendMessage(
                alt_text="Buttons template",
                template=ButtonsTemplate(
                    title="分群結果",
                    text="分析近期日本旅遊文章的常見詞彙，依據不同分群方式，分類文章類型！",
                    actions=[
                        MessageTemplateAction(
                            label="SVD結果",
                            text="SVD結果",
                        ),
                        MessageTemplateAction(
                            label="t-SNE結果",
                            text="t-SNE結果",
                        ),
                    ],
                ),
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


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
