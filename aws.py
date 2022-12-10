import os
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *
import requests
from bs4 import BeautifulSoup
import pandas as pd
import pandas_datareader.data as web
import datetime as dt


#line串接資料
line_bot_api = LineBotApi(os.environ["CHANNEL_ACCESS_TOKEN"])
handler = WebhookHandler(os.environ["CHANNEL_SECRET"])

class Portfolio:
    """the personal portfolio"""
    def __init__(self):
        self.risky_asset_ratio = 0 # ex: risky_asset_ratio = 30, means that high risk asset = 30%, low risk asset = 70%
        self.tw_ratio = 0 # taiwan asset ratio ex: tw_ratio = 30, means there are 30% of taiwan stock , 70% of non-taiwan stock in the portfolio
        self.portfolio_return_rate = 0  # portfolio total return rate
        self.tw_asset = [] # list to store Taiwan asset
        self.global_asset = [] # list to store non-Taiwan asset
        self.bond_asset = [] # list to store bond asset
        self.age = 0    # customer's age
        self.emergency_fund = 0 # one year basic spending
        self.PV = 0 # PV = saving - emergency fund
        self.n = 0 # there are still n years before retire
        self.FV = 0 # Future value at retired year
        self.withdrawal_rate = 0.04 # retirement annual withdrawal rate
        self.PMT = 0 # payment per year 
        print("**********initialize portfolio*******")

    def adjust_risky_asset_ratio(self, age):
        """adjust risky_asset_rate based on your age"""
        if(age <= 110):
            self.risky_asset_ratio = 110 - age
            print("*******adjust risky asset rate*********")
    
    def access_risky_asset_ratio(self):
        """access risky _asset_rate"""
        print("*******access risky asset rate*********")
        return self.risky_asset_ratio

class Control:
    """control bit class"""
    def __init__(self):
        self.age = False
        self.experience = False
        self.volatility = False
        self.behavior = False
        self.tw = False
        self.commodity_category = False
        self.choose_tw = False
        self.choose_global = False
        self.choose_bond = False
        self.basic_spending = False
        self.saving = False
        self.retire_age = False
        self.retire_spending = False
        print("**********initialize control bit*******")

class Commodity:
    """commmodity class"""
    def __init__(self, name, description, url):
        self.name = name
        self.description = description
        self.url = url
        self.return_rate = 0
        self.weight = 0 # share of the whole portfolio


portfolio = Portfolio() #portfolio object
control = Control() # control object

# initialize Taiwan commodity list
tw_commodity=[]
tw_commodity.append(Commodity("0050", "內扣費用0.46%, 50檔大型股", "https://reurl.cc/V1ArZZ"))
tw_commodity.append(Commodity("006208", "內扣費用0.35%, 50檔大型股", "https://reurl.cc/Qb0m3O"))
tw_commodity.append(Commodity("006203", "內扣費用0.45%, 以大型股為主, 追蹤MSCI台灣指數中的86檔", "https://reurl.cc/deX89V"))
tw_commodity.append(Commodity("0057", "內扣費用0.74%, 以大型股為主, 追蹤MSCI台灣指數中的86檔", "https://reurl.cc/6LEkKM"))
tw_commodity.append(Commodity("006204", "內扣費用1.17%, 追蹤台股加權指數中的200檔", "https://reurl.cc/MXbDVk"))
# initialize carousel template column of Taiwan commodity
tw_template_column = []
for i in tw_commodity:
    tw_template_column.append( CarouselColumn(
        title= i.name,
        text= i.description,
        thumbnail_image_url="https://doqvf81n9htmm.cloudfront.net/data/crop_article/106800/shutterstock_1315357796.jpg_1140x855.jpg",
        actions=[
            MessageAction(label="加入投資組合", text=i.name),
            URIAction(label="更多資訊", uri=i.url)
        ]
    ))

# initialize Global commodity list
global_commodity=[]
global_commodity.append(Commodity("VT", "內扣費用0.07%, 追蹤全球全市場9451檔股票", "https://reurl.cc/deX6Mz"))
global_commodity.append(Commodity("VTI", "內扣費用0.03%, 追蹤美國全市場4091檔股票", "https://reurl.cc/EXpLba"))
global_commodity.append(Commodity("ITOT", "內扣費用0.03%, 追蹤美國全市場3622檔股票", "https://reurl.cc/lZ9GGQ"))
global_commodity.append(Commodity("IVV", "內扣費用0.03%, 追蹤美國大型股S&P500", "https://reurl.cc/vmd5lj"))
global_commodity.append(Commodity("VXUS", "內扣費用0.07%, 追蹤全球(不含美國)全市場7826檔股票", "https://reurl.cc/Z1rqzp"))
global_commodity.append(Commodity("IXUS", "內扣費用0.07%, 追蹤全球(不含美國)全市場4254檔股票", "https://reurl.cc/DXygmN"))
global_commodity.append(Commodity("SPDW", "內扣費用0.04%, 追蹤非美國已開發市場2594檔股票", "https://reurl.cc/rZQMyZ"))
global_commodity.append(Commodity("IEMG", "內扣費用0.09%, 追蹤新興市場2673檔股票", "https://reurl.cc/85o39j"))
global_commodity.append(Commodity("VPL", "內扣費用0.08%, 追蹤亞太已開發國家全市場2491檔股票", "https://reurl.cc/91Gr0Y"))
global_commodity.append(Commodity("IEUR", "內扣費用0.09%, 追蹤歐洲全市場1052檔股票", "https://reurl.cc/oZ1gAj"))
# initialize carousel template column of Global commodity
global_template_column = []
for i in global_commodity:
    global_template_column.append( CarouselColumn(
        title= i.name,
        text= i.description,
        thumbnail_image_url="https://s3-ap-northeast-1.amazonaws.com/tarobo/articles/cover_imgs/000/001/165/cover/digital_globe11.jpg?1666691795",
        actions=[
            MessageAction(label="加入投資組合", text=i.name),
            URIAction(label="更多資訊", uri=i.url)
        ]
    ))

# initialize Bond commodity list
bond_commodity=[]
bond_commodity.append(Commodity("SCHR", "內扣費用0.04%, 美國中期國債", "https://reurl.cc/DXylMm"))
bond_commodity.append(Commodity("SCHP", "內扣費用0.05%, 美國中期抗通膨國債TIPS", "https://reurl.cc/ROreVZ"))
bond_commodity.append(Commodity("SCHO", "內扣費用0.04%, 美國短期國債", "https://reurl.cc/Wqr8kZ"))
bond_commodity.append(Commodity("VGLT", "內扣費用0.04%, 美國長期國債", "https://reurl.cc/85ob24"))
bond_commodity.append(Commodity("STIP", "內扣費用0.03%, 美國短期抗通膨國債TIPS", "https://reurl.cc/Z1Albl"))
bond_commodity.append(Commodity("LTPZ", "內扣費用0.2%, 美國長期抗通膨國債TIPS", "https://reurl.cc/jR1mWp"))
bond_commodity.append(Commodity("BWZ", "內扣費用0.35%, 全球短期公債", "https://reurl.cc/EXrboR"))
bond_commodity.append(Commodity("IGOV", "內扣費用0.35%, 全球中期公債", "https://reurl.cc/de2qeM"))
bond_commodity.append(Commodity("WIP", "內扣費用0.5%, 全球抗通膨公債", "https://reurl.cc/x19K6V"))
# initialize carousel template column of Bond commodity
bond_template_column = []
for i in bond_commodity:
    bond_template_column.append( CarouselColumn(
        title= i.name,
        text= i.description,
        thumbnail_image_url="https://www.bankrate.com/2021/08/12135903/Corporate-bonds-Here-are-the-risks-and-rewards.jpeg",
        actions=[
            MessageAction(label="加入投資組合", text=i.name),
            URIAction(label="更多資訊", uri=i.url)
        ]
    ))

def lambda_handler(event, context):
    @handler.add(MessageEvent, message=TextMessage)
    def handle_message(event):
        # 程式主體
        print("**********in model********")

        if event.message.text == "start":
            # introduction
            reply_word = "Hi 我是花花，接下來我將利用資產配置理論及被動投資法，帶您邁開投資的第1步，以退休為目標，規劃長期投資組合，跟隨全球市場一起長期成長。\n"
            reply = TemplateSendMessage(
                alt_text="進入新手村",
                template=ButtonsTemplate(
                    text=reply_word,
                    actions=[
                        MessageAction(
                            label="進入新手村",
                            text="進入新手村"
                        )
                    ]
                )
            )
        
        elif event.message.text == "進入新手村":
            # 新手村1: 介紹被動投資
            reply = TemplateSendMessage(
                alt_text="被動投資是什麼",
                template=ButtonsTemplate(
                    title="蛤，被動投資是啥?",
                    text="被動投資就是買進並長期持有市場上所有投資標的，以賺取整體市場長期經濟成長，並降低個股風險。",
                    actions=[
                        URIAction(
                            label="點我看更多被動投資的介紹",
                            uri="https://rich01.com/what-passive-invest/"
                        ),
                        MessageAction(
                            label="如何買進市場上所有投資標的",
                            text="如何買進市場上所有投資標的"
                        )
                    ]
                )
            )

        elif event.message.text == "如何買進市場上所有投資標的":
            # 新手村2: 介紹ETF
            reply = TemplateSendMessage(
                alt_text="ETF是什麼",
                template=ButtonsTemplate(
                    title="利用市場型ETF就能辦到!",
                    text="持有ETF，就能輕鬆分散投資在一籃子的成分股!",
                    actions=[
                        URIAction(
                            label="點我看更多ETF的介紹",
                            uri="https://rich01.com/etf0050/"
                        ),
                        MessageAction(
                            label="那資產配置又是什麼",
                            text="那資產配置又是什麼"
                        )
                    ]
                )
            )

        elif event.message.text == "那資產配置又是什麼":
            # 新手村3: 介紹資產配置
            reply = TemplateSendMessage(
                alt_text="資產配置是什麼",
                template=ButtonsTemplate(
                    text="資產配置就是透過持有不同的資產，來降低投資組合的波動!如果只持有股票，在經濟衰退時，可能有高達40%的跌幅，使投資人忍不住在最差的時候賣出股票; 若持有股票+債劵，因為兩者非完全正相關，故能降低投資組合的波動，避免投資人的不理性行為。",
                    actions=[
                        URIAction(
                            label="點我看更多資產配置的介紹",
                            uri="https://rich01.com/how-asset-allocation-1/"
                        ),
                        MessageAction(
                            label="離開新手村",
                            text="restart"
                        )
                    ]
                )
            )

        elif event.message.text =="restart":
            # initialize and ask age
            portfolio.__init__()
            control.__init__()

            reply_word = "經過了新手村的訓練，相信你已經有能力踏上資產配置的旅程，接下來我將帶領你規劃自己的長期投資組合。\n\n"
            reply_word += "途中如果有任何問題，請點擊功能表左下角的\"名詞解釋\"，花花會幫你解答\n\n"
            reply_word += "首先，請輸入您的年齡"
            reply = TextSendMessage(reply_word)
            control.age = True 

        elif event.message.text == "show":
            reply_word = "建議您的高風險資產占比為:\n"+str(portfolio.access_risky_asset_ratio())+"\n"
            reply_word += "在高風險資產中，台股的占比為:\n"+str(portfolio.tw_ratio)+"%\n"
            reply_word += "緊急備用金: $"+str(portfolio.emergency_fund)+"元\n"
            reply_word += "距離退休還有"+str(portfolio.n)+"年\n"
            reply_word += "PMT = "+str(portfolio.PMT)+"元\n"
            reply_word += "portfolio return rate= "+str(portfolio.portfolio_return_rate)+"\n"
            reply_word += "您選擇的台灣市場型ETF有: \n"
            for i in portfolio.tw_asset:
                reply_word += i.name + " r= " + str(i.return_rate) +"\nw= " + str(i.weight) + "\n"
            reply_word += "您選擇的全球市場型ETF有: \n"
            for i in portfolio.global_asset:
                reply_word += i.name + " r= " + str(i.return_rate) +"\nw= " + str(i.weight) + "\n"
            reply_word += "您選擇的債劵ETF有: \n"
            for i in portfolio.bond_asset:
                reply_word += i.name + " r= " + str(i.return_rate) +"\nw= " + str(i.weight) + "\n"
            reply = TextSendMessage(reply_word)

        elif event.message.text == "FAQ":
            # trigered by 按下功能表上"名詞解釋"按鈕後，display below
            reply_word = "\U0001F638喵 有問題嗎?讓花花來幫你解答:\n\n"

            reply_word += "\U0001F449股票是什麼?\n"
            reply_word += "持有股票，就能讓你成為股東，分享公司成長所結出的果實\nhttps://reurl.cc/MXML3p\n\n"

            reply_word += "\U0001F449緊急預備金是什麼?\n"
            reply_word += "緊急預備金就是一筆用來應付突發意外的資金，適合存在台幣定存中\nhttps://reurl.cc/VRmQqb\n\n"

            reply_word += "\U0001F449什麼是大盤加權指數？\n"
            reply_word += "大盤指數用來反映整個市場的漲跌情況\nhttps://reurl.cc/OERLg9\n\n"

            reply_word += "\U0001F449債券ETF 是什麼?\n"
            reply_word += "https://reurl.cc/eWV7lm\n\n"

            reply_word += "\U0001F449退休需要多少錢?\n"
            reply_word += "https://reurl.cc/91bL8j\n\n"

            reply = TextSendMessage(reply_word)

        elif event.message.text == "more":
            # trigered by 按下功能表上"實踐規劃"按鈕後，display below
            reply_word = "做完配置規劃後，不知道要怎麼實行嗎?\n"
            reply_word += "花花幫你準備了超強懶人包，快來看看喵!\U0001F638\n\n"

            reply_word += "\U0001F449平均成本的法寶:定期定額\nhttps://reurl.cc/58Ry8v\n\n"
            reply_word += "\U0001F449再平衡是啥?能吃嗎\nhttps://reurl.cc/4XN7XD\n\n"
            reply_word += "\U0001F449配息高的一定好? 高股息的迷思\nhttps://reurl.cc/Z1l9O6\n\n"
            reply_word += "\U0001F449台灣ETF要怎麼買?\nhttps://reurl.cc/91b3An\n\n"
            reply_word += "\U0001F449國際型ETF和債劵ETF怎麼買?複委託vs.海外劵商\nhttps://reurl.cc/LXQlr4\n\n"
            reply_word += "\U0001F449國泰證劵複委託\nhttps://reurl.cc/aaMdQQ\n\n"
            reply_word += "\U0001F449富邦證劵複委託\nhttps://reurl.cc/DXblNQ\n\n"
            reply_word += "\U0001F449投資小白必看!花花推薦的投資入門指南: 漫步華爾街的10條投資金律\nhttps://reurl.cc/gQnjW7\n\n"
            reply_word += "\U0001F449如何估算股票的長期報酬率? 讓高登公式來幫你\nhttps://reurl.cc/jRmYbD\n\n"
            reply_word += "\U00002B50想知道花花\U0001F638的秘密嗎? 歡迎來本專案的github賞星星\U00002B50\nhttps://reurl.cc/91b8LV\n\n"
            reply = TextSendMessage(reply_word)

        elif (control.age == True ):
            # receive age, adjust risky rate, and ask experience
            if event.message.text.isdigit():
                portfolio.age = int(event.message.text)
                portfolio.adjust_risky_asset_ratio(int(event.message.text))
                control.age = False 

                reply = TemplateSendMessage(
                    alt_text="請問您是否有投資的經驗?",
                    template=ButtonsTemplate(
                        title="風險適合度評估",
                        text="請問您是否有投資的經驗?",
                        thumbnail_image_url="https://doqvf81n9htmm.cloudfront.net/data/crop_article/104685/shutterstock_1411852109.jpg_1140x855.jpg",
                        actions=[
                            MessageAction(label="無經驗", text="無經驗"),
                            MessageAction(label="1年以下", text="1年以下"),
                            MessageAction(label="1~3年", text="1~3年"),
                            MessageAction(label="3年以上", text="3年以上")
                        ]
                    )
                )
                control.experience = True
            else:
                reply = TextSendMessage(text = "請輸入數字")

        elif (control.experience == True):
            # receive experience and ask volatility
            control.experience = False
            if (event.message.text == "無經驗") and (portfolio.risky_asset_ratio >= 10):
                portfolio.risky_asset_ratio -= 10
            elif (event.message.text == "1年以下") and (portfolio.risky_asset_ratio >= 8):
                portfolio.risky_asset_ratio -= 8
            elif (event.message.text == "1~3年") and (portfolio.risky_asset_ratio >= 4):
                portfolio.risky_asset_ratio -= 4
            elif (event.message.text == "3年以上"):
                portfolio.risky_asset_ratio -= 0

            reply = TemplateSendMessage(
                alt_text="請問您可以接受的價格波動幅度為?",
                template=ButtonsTemplate(
                    title="風險適合度評估",
                    text="請問您可以接受的證劵價格波動幅度為?",
                    thumbnail_image_url="https://doqvf81n9htmm.cloudfront.net/data/crop_article/61261/shutterstock_252511228.jpg_1140x855.jpg",
                    actions=[
                        MessageAction(label="5%", text="5%"),
                        MessageAction(label="10%", text="10%"),
                        MessageAction(label="15%", text="15%"),
                        MessageAction(label="20%以上", text="20%以上")
                    ]
                )
            )
            control.volatility = True
            
        elif (control.volatility == True):
            # receive volatility and ask behavior
            control.volatility = False
            if (event.message.text == "5%") and (portfolio.risky_asset_ratio >= 10):
                portfolio.risky_asset_ratio -= 10
            elif (event.message.text == "10%") and (portfolio.risky_asset_ratio >= 8):
                portfolio.risky_asset_ratio -= 8
            elif (event.message.text == "15%") and (portfolio.risky_asset_ratio >= 4):
                portfolio.risky_asset_ratio -= 4
            elif (event.message.text == "20%以上"):
                portfolio.risky_asset_ratio -= 0

            reply = TemplateSendMessage(
                alt_text="請問下列何者最接近您的投資行為與經驗?",
                template=ButtonsTemplate(
                    title="風險適合度評估",
                    text="請問下列何者最接近您的投資行為與經驗?",
                    thumbnail_image_url="https://storage.googleapis.com/www-cw-com-tw/article/202008/article-5f27d8bc89628.jpg",
                    actions=[
                        MessageAction(label="穩定收益保本", text="穩定收益保本"),
                        MessageAction(label="追求快速獲利高風險高報酬", text="追求快速獲利高風險高報酬")
                    ]
                )
            )
            control.behavior = True

        elif (control.behavior == True):
            # receive behavior and ask loss
            control.behavior = False
            if (event.message.text == "穩定收益保本") and (portfolio.risky_asset_ratio >= 10):
                portfolio.risky_asset_ratio -= 10
            elif (event.message.text == "追求快速獲利高風險高報酬"):
                portfolio.risky_asset_ratio -= 0

            reply = TemplateSendMessage(
                alt_text="若您投資的部位已經損失15%, 這時您會?",
                template=ButtonsTemplate(
                    title="風險適合度評估",
                    text="若您投資的部位已經損失15%, 這時您會?",
                    thumbnail_image_url="https://cimg.cnyes.cool/prod/news/4866274/l/6f735855050b0a5a8f06fa7b91bc25e4.jpg",
                    actions=[
                        MessageAction(label="全部停損賣出", text="全部停損賣出"),
                        MessageAction(label="部分賣出", text="部分賣出"),
                        MessageAction(label="繼續觀察後市", text="繼續觀察後市"),
                        MessageAction(label="逢低加碼", text="逢低加碼")
                    ]
                )
            )
            control.loss = True

        elif (control.loss == True):
            # receive loss and ask taiwan stock ratio
            control.loss = False
            if (event.message.text == "全部停損賣出") and (portfolio.risky_asset_ratio >= 10):
                portfolio.risky_asset_ratio -= 10
            elif (event.message.text == "部分賣出") and (portfolio.risky_asset_ratio >= 8):
                portfolio.risky_asset_ratio -= 8
            elif (event.message.text == "繼續觀察後市") and (portfolio.risky_asset_ratio >= 4):
                portfolio.risky_asset_ratio -= 4
            elif (event.message.text == "逢低加碼"):
                portfolio.risky_asset_ratio -= 0

            reply_word = "建議您的高風險資產占比為:\n" + str(portfolio.risky_asset_ratio) + "%\n"
            reply_word += "為了降低單一地區的系統性風險，分散投資於全球是很重要的工作。"
            reply_word += "接下來您需要決定台灣與外國資產的比重:\n\n"
            reply_word += "若您希望整個投資組合的表現和台股表現(或是親友的投資表現)較為一致，則台灣資產的比重可以高一點，但分散風險的效果可能會降低。\n\n"
            reply_word += "若您希望能充分分散單一地區的系統性風險，則台灣資產的比重需要低一點。\n\n"
            reply_word += "請輸入您希望的台灣資產的占比:"
            reply = TextSendMessage(reply_word)
            control.tw = True


        elif (control.tw == True ):
            # receive tw_ratio, adjust tw_rate, ask client to choose commodity category
            if (event.message.text.isdigit()) and (0 <= int(event.message.text) <= 100) :
                portfolio.tw_ratio = int(event.message.text)
                control.tw = False 

                control.commodity_category = True # reply is at the last paragraph
            else:
               reply = TextSendMessage(text = "請輸入介於0~100的數字")

        elif (control.commodity_category == True):
            #receive commidity category then show the advised commodity 
            if (event.message.text == "台灣市場型ETF"):
                #show 台灣市場型ETF
                control.commodity_category = False 
                control.choose_tw = True
                reply = TemplateSendMessage(
                    alt_text="請選擇想要的台灣市場型ETF",
                    template=CarouselTemplate(columns=tw_template_column)
                )

            elif (event.message.text == "國際市場型ETF"):
                #show 國際市場型ETF
                control.commodity_category = False 
                control.choose_global = True
                reply = TemplateSendMessage(
                    alt_text="請選擇想要的全球市場型ETF",
                    template=CarouselTemplate(columns=global_template_column)
                )

            elif (event.message.text == "債劵ETF"):
                #show 債劵ETF
                control.commodity_category = False 
                control.choose_bond = True
                reply = TemplateSendMessage(
                    alt_text="請選擇想要的債劵ETF",
                    template=CarouselTemplate(columns=bond_template_column)
                )

            elif (event.message.text == "next"):
                # 結束選擇商品，詢問每月基本開銷
                control.commodity_category = False 
                # 計算各商品的比重及整個portfolio的長期報酬率
                for i in portfolio.tw_asset:
                    i.weight = (portfolio.risky_asset_ratio/100) * (portfolio.tw_ratio/100) / len(portfolio.tw_asset)
                    portfolio.portfolio_return_rate += i.weight * i.return_rate
                for i in portfolio.global_asset:
                    i.weight = (portfolio.risky_asset_ratio/100) * (1 - portfolio.tw_ratio/100) / len(portfolio.global_asset)
                    portfolio.portfolio_return_rate += i.weight * i.return_rate
                for i in portfolio.bond_asset:
                    i.weight = (1 - portfolio.risky_asset_ratio/100) / len(portfolio.bond_asset)
                    portfolio.portfolio_return_rate += i.weight * i.return_rate

                control.basic_spending = True
                reply_word = "恭喜您已經挑選完示範投資組合，接下來將為您計算每月需投入多少資金到此投資組合，才有可能達成退休目標\n\n"
                reply_word += "請輸入您目前每個月的最低生活費(含:房租、水電瓦斯費、交通費、基本伙食費、電信費等, 單位: 元)"
                reply = TextSendMessage(reply_word)


        elif (control.choose_global == True):
            #receive the choosed Global good, 放入購物車
            print("*******in choose_global********")
            for i in global_commodity:
                if i.name == event.message.text:
                    # the received answer is in the list, normal situation
                    print("*******find in the list********")
                    control.choose_global = False
                    ticker = i.name

                    annual_div_list = [] # list to store annual dividend in past 5 years
                    for j in range(5):
                        # caculate annual dividend 
                        end = dt.date.today().year - j
                        start = end - 1
                        try:
                            dividends = web.DataReader(ticker, "yahoo-dividends",start, end)
                            annual_div_list.append(dividends["value"].sum())
                        except KeyError:
                            print("*******No data in this year*****")

                    annual_div_list.reverse()   # order the data from old to new
                    c = sum(annual_div_list) / len(annual_div_list)     # average annual dividend in 5 years
                    g = float(pd.DataFrame(annual_div_list).pct_change().dropna().mean()) / 100   # average annual dividend growth rate
                    yesterday_price = web.DataReader(ticker, "yahoo", dt.date.today()+dt.timedelta(-1), dt.date.today()) # dataframe of price
                    p = float( list(yesterday_price["Adj Close"])[-1] ) #目前(今天或昨天)股價, 可能因時區有所差別
                    r = g + c/p # 利用高登公式算出長期報酬率
                    i.return_rate = r
                    print("******c = "+str(c)+"****g = "+str(g)+"****p = "+str(p)+"*****")

                    portfolio.global_asset.append(i) # add this commodity to your portfolio
                    control.commodity_category = True 
                    break
                    
            else:
                reply = TextSendMessage(text="您選擇的商品不在範圍內，請重新點選")

        elif (control.choose_bond == True):
            #receive the choosed bond, 放入購物車
            print("*******in choose_bond********")
            for i in bond_commodity:
                if i.name == event.message.text:
                    # the received answer is in the list, normal situation
                    print("*******find in the list********")
                    control.choose_bond = False
                    ticker = i.name

                    annual_div_list = [] # list to store annual dividend in past 5 years
                    for j in range(5):
                        # caculate annual dividend 
                        end = dt.date.today().year - j
                        start = end - 1
                        try:
                            dividends = web.DataReader(ticker, "yahoo-dividends",start, end)
                            annual_div_list.append(dividends["value"].sum())
                        except KeyError:
                            print("*******No data in this year*****")

                    annual_div_list.reverse()   # order the data from old to new
                    c = sum(annual_div_list) / len(annual_div_list)     # average annual dividend in 5 years
                    g = float(pd.DataFrame(annual_div_list).pct_change().dropna().mean()) / 100   # average annual dividend growth rate
                    yesterday_price = web.DataReader(ticker, "yahoo", dt.date.today()+dt.timedelta(-1), dt.date.today()) # dataframe of price
                    p = float( list(yesterday_price["Adj Close"])[-1] ) #目前(今天或昨天)股價, 可能因時區有所差別
                    r = g + c/p # 利用高登公式算出長期報酬率
                    i.return_rate = r
                    print("******c = "+str(c)+"****g = "+str(g)+"****p = "+str(p)+"*****")

                    portfolio.bond_asset.append(i) # add this commodity to your portfolio
                    control.commodity_category = True 
                    break
                    
            else:
                reply = TextSendMessage(text="您選擇的商品不在範圍內，請重新點選")

        elif (control.choose_tw == True):
            #receive the choosed Taiwan good, 放入購物車
            print("*******in choose_tw********")
            for i in tw_commodity:
                if i.name == event.message.text:
                    # the received answer is in the list, normal situation
                    print("*******find in the list********")
                    control.choose_tw = False

                    # get C, G, and P from Goodinfo to calculate r
                    headers = {
                        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
                    }
                    url = "https://goodinfo.tw/tw/StockBzPerformance.asp?STOCK_ID=" + i.name
                    res = requests.get(url, headers = headers)
                    res.encoding = "utf-8"
                    soup = BeautifulSoup(res.text,"lxml")
                    data = soup.select_one("#txtFinAvgData")
                    dfs = pd.read_html(data.prettify())
                    df = dfs[2]
                    c = float(df[9][10]) # 平均股利
                    dC = float(df[12][10]) # delta C: 平均股利成長(元)
                    g = dC / c  # g: 股利成長率
                    p = float(df[0][0][4:-2])   # p: 目前股價
                    r = g + c/p # 利用高登公式算出長期報酬率
                    i.return_rate = r

                    portfolio.tw_asset.append(i) # add this commodity to your portfolio
                    control.commodity_category = True 
                    break
        
            else:
                reply = TextSendMessage(text="您選擇的商品不在範圍內，請重新點選")

        elif control.basic_spending == True:
            # receive basic budget per month, calculate emergency fund, and ask saving
            if event.message.text.isdigit():
                portfolio.emergency_fund = int(event.message.text) * 12
                control.basic_spending = False
                control.saving = True
                reply = TextSendMessage(text = "請輸入您目前的存款總額(單位: 元)")
            else:
                reply = TextSendMessage(text = "請輸入正整數")

        elif control.saving == True:
            #receiving saving, calculate PV, calculate PV
            if event.message.text.isdigit():
                portfolio.PV = int(event.message.text) - portfolio.emergency_fund
                control.saving = False
                control.retire_age = True
                reply = TextSendMessage(text = "請問您預計在幾歲時退休?")

            else:
                reply = TextSendMessage(text = "請輸入正整數，若您有信貸、卡債等高利息債務，建議您先盡快清償，再來思考如何投資")

        elif control.retire_age == True:
            #receiving retire age, ask retire mounthly spending 
            if event.message.text.isdigit() and (portfolio.age < int(event.message.text)):
                portfolio.n = int(event.message.text) - portfolio.age
                control.retire_age = False
                control.retire_spending = True
                reply = TextSendMessage(text = "請問您預計退休時的每月實質開銷為多少(單位: 元)?\n不需考慮通貨膨脹，以目前的購買力計算即可")

            else:
                reply = TextSendMessage(text = "請輸入正整數且須大於您目前的年齡")

        elif control.retire_spending == True:
            # receiving retire monthly spending, calculate PMT 
            if event.message.text.isdigit():
                control.retire_spending = False
                portfolio.FV = int(event.message.text) * 12 / portfolio.withdrawal_rate
                if portfolio.PV>0 :
                    # 若pv>0，則可以把剩餘存款投入投資組合
                    portfolio.PV *= -1
                else:
                    # 存款不夠付緊急預備金，無法有餘力投入
                    portfolio.PV = 0

                k = portfolio.portfolio_return_rate
                n = portfolio.n
                PV = portfolio.PV
                FV = portfolio.FV
                portfolio.PMT = k/(1-(1+k)**(-n)) * (-PV - FV/((1+k)**n))
                portfolio.PMT *= -1

                reply_word = "大功告成!!\n"
                if portfolio.PV != 0:
                    reply_word += "建議您將存款中的 $"+str(portfolio.emergency_fund)+"元存入定存做為緊急預備金\n\n"
                    reply_word += "其餘存款 $"+str(portfolio.PV * -1)+"您可以投入以下投資組合:\n"
                else:
                    reply_word += "建議您先努力存到$"+str(portfolio.emergency_fund)+"元做為緊急預備金，若您有信貸、卡債等高利息債務，也建議您先盡快清償\n\n"
                    reply_word += "之後再將收入定期定額投入以下投資組合:\n"

                reply_word += " 台灣市場型ETF:\n"
                for i in portfolio.tw_asset:
                    reply_word += f"  {i.name} 占比: {i.weight:.2%}\n "
                reply_word += "\n 全球市場型ETF:\n"
                for i in portfolio.global_asset:
                    reply_word += f"  {i.name} 占比: {i.weight:.2%}\n "
                reply_word += "\n 債劵ETF:\n"
                for i in portfolio.bond_asset:
                    reply_word += f"  {i.name} 占比: {i.weight:.2%}\n "
                reply_word += f"\n另外，建議您在接下來的{portfolio.n}年，每年皆定期定額投入\"實質\"{portfolio.PMT:.1f}元到上述投資組合，以期達成退休目標\n"
                reply_word += f"(ex: 若今年的通膨率為2%，則明年應投入{portfolio.PMT*1.02:.1f}元至投資組合)\n\n"

                reply_word += "做完規劃後不知道如何開始執行嗎?\n"
                reply_word += "別擔心，花花幫你準備新手大禮包，可以解決您的疑問，快點擊功能表的\"實踐規劃\"領取大禮包!\n\n"

                reply_word += "<<免責聲明>>\n"
                reply_word += "本軟體僅做為學術研究使用，不可用於實際投資建議，更不得作為任何交易之依據。投資一定有風險，過往業績並不代表將來表現，投資人應運用個人獨立思考能力，或諮詢其財務、稅務、投資等顧問，自行作出投資決定，本軟體在任何情況下均不會就任何直接、間接或其他損失承擔任何責任。"
                reply_word += "本軟體提供之資訊及被連結之他方網站或系統所提供之任何產品、服務或資訊僅供參考之用，本軟體不就此資料作出任何保證，包括但不限於來源、正確性、即時性、完整性或任何其他用途之適合性等各方面之保證。所有出現的商品僅為教學示範目的，皆不構成要約、招攬、邀請、誘使、任何不論種類及形式之申述或訂立任何建議及推薦。"
                reply_word += "所有觀點僅為個人對市場之看法，並非任何投資勸誘或建議。雖本軟體為了保守起見，採用高登公式來評估商品未來的長期報酬率，但仍不保證按照上述示範建議便可達成目標，所有建議僅為學術範例，而非任何投資建議。"

                reply = TextSendMessage(text=reply_word)

            else:
                reply = TextSendMessage(text = "請輸入正整數")

        else:
            reply = TextSendMessage(text= event.message.text)

        if ((control.commodity_category == True) and (event.message.text != "FAQ")):
            # ask to choose commodity_category
            reply = TemplateSendMessage(
                alt_text="選擇參考商品類型",
                template=ButtonsTemplate(
                    title="已儲存您輸入的結果，請繼續選擇商品類別",
                    text="以下將提供各類型參考商品，做為資產配置的試算範例",
                    thumbnail_image_url="https://storage.googleapis.com/www-cw-com-tw/article/202202/article-6204731485570.jpg",
                    actions=[
                         MessageAction(label="台灣市場型ETF", text="台灣市場型ETF"),
                         MessageAction(label="國際市場型ETF", text="國際市場型ETF"),
                         MessageAction(label="債劵ETF", text="債劵ETF"),
                         MessageAction(label="已經選擇完畢，前往下一步", text="next")
                    ]
                )
            )


        line_bot_api.reply_message(
            event.reply_token,
            reply)

    try:
        # get X-Line-Signature header value
        copy_headers = {key.lower(): value for key, value in event['headers'].items()}
        signature = copy_headers['x-line-signature']

        # get request body as text
        body = event['body']
        print(body)
        
        # handle webhook body
        handler.handle(body, signature)
        
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        return {'statusCode': 400, 'body': 'InvalidSignature'}
        
    except Exception as e:
        print(e)
        return {'statusCode': 400, 'body': str(e)}

    return {'statusCode': 200, 'body': 'OK'}
 





