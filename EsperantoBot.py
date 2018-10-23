from PIL import Image, ImageDraw, ImageFont
import re, subprocess, io, requests, sqlite3, configparser, codecs, urllib.parse, urllib.request, json, time, threading, random, hashlib, os.path, traceback
terminated = False

class Bot(threading.Thread):
    def __init__(self, token, receive, receiveInline = None):
        threading.Thread.__init__(self)

        self.url = "https://api.telegram.org/bot" + token + "/"

        obj = requests.post(self.url + "getMe").json()

        if obj["ok"]:
            self.offset = 0
            self.receive = receive
            self.receiveInline = receiveInline
            self.id = obj["result"]["id"]
            self.name = obj["result"]["first_name"]
            self.username = obj["result"]["username"]
        else:
            self.url = None
            raise Exception(obj["description"])

    def sendMessage(self, id, message, reply = None, keyboard = None, preview = True, forceReply = False, notification = True):
        data = {"chat_id": str(id), "text": str(message)}

        if preview == False:
            data["disable_web_page_preview"] = True

        if notification == False:
            data["disable_notification"] = True

        if reply is not None:
            data["reply_to_message_id"] = str(reply)

        if keyboard is not None:
            data["reply_markup"] = str(keyboard)
        elif forceReply:
            data["reply_markup"] = '{"force_reply":true}'

        data["parse_mode"] = "Markdown"

        try:
            obj = requests.post(self.url + "sendMessage", data=data).json()
            return obj["ok"]
        except Exception as exception:
            print(exception)

    def deleteMessage(self, id, message):
        data = {"chat_id": str(id), "message_id": str(message)}

        try:
            obj = requests.post(self.url + "deleteMessage", data=data).json()
            return obj["ok"]
        except Exception as exception:
            print(exception)

    def run(self):
        global terminated

        while True:
            try:
                obj = requests.post(self.url + "getUpdates", data={"offset": str(self.offset)}).json()

                if obj["ok"]:
                    max = 0

                    for item in obj["result"]:
                        max = item["update_id"]

                        if "inline_query" in item and self.username == "EsperantoBot":
                            userInput = item["inline_query"]["query"][0:1000]
                            inputHash = hashlib.sha1(userInput.encode("UTF-8")).hexdigest()

                            if not os.path.isfile("/var/www/telegramo/sondosieroj/" + inputHash + ".ogg"):
                                devnull = open("/dev/null", "w")
                                espeak = subprocess.Popen(["espeak", "--stdout", "-veo", userInput], stdout=subprocess.PIPE, stderr=devnull)
                                avconv = subprocess.Popen(["avconv", "-i", "pipe:0", "-c:a", "libopus", "-b:a", "128000",  "-f", "ogg", "-"], stdin=espeak.stdout, stdout=subprocess.PIPE, stderr=devnull)
                                espeak.stdout.close()
                                output = avconv.communicate()[0]
                                espeak.wait()

                            with open("/var/www/telegramo/sondosieroj/" + inputHash + ".ogg", "wb") as f:
                                f.write(output)

                            iksoj = userInput.replace("cx", "ĉ").replace("gx", "ĝ").replace("hx", "ĥ").replace("jx", "ĵ").replace("sx", "ŝ").replace("ux", "ŭ").replace("cX", "ĉ").replace("gX", "ĝ").replace("hX", " ĥ").replace("jX", "ĵ").replace("sX", "ŝ").replace("uX", "ŭ").replace("Cx", "Ĉ").replace("Gx", "Ĝ").replace("Hx", "Ĥ").replace("Jx", "Ĵ").replace("Sx", "Ŝ").replace("Ux", "Ŭ").replace("CX", "Ĉ").replace("GX", "Ĝ").replace("HX", "Ĥ").replace("JX", "Ĵ").replace("SX", "Ŝ").replace("UX", "Ŭ")

                            data = {"inline_query_id": item["inline_query"]["id"], "results": '[{ "type": "article", "id": "x' + item["inline_query"]["id"] + '", "title": "Konverti X-sistemon al ĉapelliteroj...", "message_text": "' + iksoj + '", "parse_mode": "Markdown", "description": "' + iksoj + '", "thumb_url": "https://i.imgur.com/sDYvveW.jpg" }, { "type": "voice", "id": "v' + item["inline_query"]["id"] + '", "voice_url": "https://telegramo.org/sondosieroj/' + inputHash + '.ogg", "title": "Elparoli mesaĝon robote..." }]', "is_personal": True, "cache_time": -1}

                            try:
                                requests.post("https://api.telegram.org/botTokenHere/answerInlineQuery", data=data).json()
                            except Exception as exception:
                                print(exception)
                        elif "message" in item:
                            message = item["message"]

                            if "text" in message:
                                if message["chat"]["id"] == 26927785 and message["text"] == "/stopallbots":
                                    terminated = True

                                newUser = ""
                                message["text"] = " ".join(message["text"].split())

                                if message["text"][0] == "/":
                                    splitted = message["text"].split()

                                    foundUser = False
                                    newCommand = ""
                                    newUser = ""

                                    for c in splitted[0]:
                                        if c == "@":
                                            foundUser = True
                                        else:
                                            if foundUser:
                                                newUser += c
                                            else:
                                                newCommand += c

                                    splitted[0] = newCommand.lower()
                                    message["text"] = " ".join(splitted)

                                if newUser == "" or newUser.lower() == self.username.lower():
                                    if self.receive(self, message) == True:
                                        print("[" + self.name + ":" + str(self.offset) + "] " + str(message))
                            elif "new_chat_member" in message and self.username == "EsperantoBot":
                                try:
                                    if message["new_chat_member"]["id"] != 93589888:
                                        welcome = "Bonvenon al <b>" + message["chat"]["title"] + "</b>! Pliaj grupoj estas ĉe <a href=\"https://telegramo.org/\">Telegramo.org</a>. " + random.choice(["🌎", "🌍", "🌏"])

                                        requests.post(self.url + "sendMessage", data={"chat_id": message["chat"]["id"], "text": welcome, "parse_mode": "HTML", "disable_notification": True, "disable_web_page_preview": True}).json()
                                    else:
                                        requests.post(self.url + "sendMessage", data={"chat_id": 26927785, "text": str(message["chat"]["title"]) + " : " + str(message["chat"]["id"])}).json()
                                except Exception as exception:
                                    print(exception)

                    max = int(max) + 1

                    if max != 1:
                        self.offset = max
                else:
                    raise Exception(obj["description"])
            except Exception as exception:
                print("[" + self.name + "] Skipping " + str(self.offset) + "!")
                print(exception)
                traceback.print_exc()
                self.offset += 1

            if terminated:
                requests.post(self.url + "getUpdates", data={"offset": str(self.offset)}).json()
                break

            #time.sleep(1)

#EsperantoBot start
esperantoBots = [
["HangBot", "la ludo Pendumito"],
["PronunciationBot", "teksto-al-parolado en 84 lingvoj"],
["weatherbot", "la nuna vetero kaj prognozoj"],
["filesbot", "konigi viajn dosierojn facile"],
["BlackJackBot", "la ludo Klabeto por pluraj ludantoj"],
["werewolfbot", "la ludo Homlupo por pluraj ludantoj"]
]

esperantoStickerPacks = [
["Akuzativo", "Akuzativo", "komiksaj glumarkoj"],
["Nova", "Espere", "hometoj kun vortoj"],
["😄", "Espero", "glumarkoj kun verduletoj"],
["fek", "fekajxoj", "verdaj glumarkoj kun vortoj"],
["Glumarkoj", "Glumarkaro", "diversaj kun verdaj simboloj"],
["Glumarkoj", "Glumarkoj", "vortoj kun bildetoj"],
["knabineto", "knabineto", "kun simplaj vortoj"],
["Machiko Esperanto", "machikoeo", "parolantaj bildstrietoj (Machiko)"],
["Mojose", "Mojose", "bildstrietoj kun vortoj"],
["Novaj glumarkoj", "Plena", "bildetoj kun vortoj"],
["Stimulantaj Frazoj", "StimulantajFrazoj", "parolantaj bildetoj"],
["Senvizaĝa", "Senvisagxa", "komiksaj glumarkoj kun vortbobeloj"],
["Pepo", "Pepoj", "la bildstria papago"],
["Esperantaĵoj", "esperantajxoj", "bildetoj kun vortoj"],
["glumarkoj-de-neil", "gesinjoroj", "punktoj kun piedoj"],
["gaja Steleto", "gajaSteleto", "emociesprimaj verdaj steletoj"],
["fekajxoj", "fekulo", "parolantaj bildstrietoj"],
["Bovinaro", "Bovinaro", "glumarkoj de Dek Bovinoj"],
["Terpomoj", "Terpomoj", "hazardaj glumarkoj de Ari"],
["Kernpunkto", "kernpunkto", "nuksaj glumarkoj de kernpunkto"],
["Pilketo Esperanto", "PilketoEsperanto", "kataj glumarkoj de Pilketo"]
]

admins = [
26927785,
93589888,
136424018,
305898606
]

def receiveMessage(bot, message):
    if "text" in message:
        splitted = message["text"].split()
        id = message["chat"]["id"]

        if splitted[0] == "/start" or splitted[0] == "/help":
            bot.sendMessage(id, "Ĉi tiu roboto povas sendi al vi la invitligilojn de ĉiuj Esperantaj grupoj per /ligiloj. ✳️\nMi estas kreita de @Robin. 🇳🇱\nhttps://telegramo.org/", message["message_id"], '{"hide_keyboard":true}', preview=False)
        elif splitted[0] == "/robotoj":
            groupList = "*Kelkaj Esperantaj Telegram-robotoj:*"

            random.shuffle(esperantoBots)

            for esperantoBot in esperantoBots:
                 groupList += "\n– @" + esperantoBot[0] + " - _" + esperantoBot[1] + "_"

            bot.sendMessage(id, groupList, message["message_id"], '{"hide_keyboard":true}', preview=False)
        elif splitted[0] == "/glumarkaroj":
            groupList = "*Kelkaj Esperantaj Telegram-glumarkaroj:*"

            random.shuffle(esperantoStickerPacks)

            for esperantoStickerPack in esperantoStickerPacks:
                 groupList += "\n– [" + esperantoStickerPack[0] + "](https://telegram.me/addstickers/" + esperantoStickerPack[1] + ") - _" + esperantoStickerPack[2] + "_"

            bot.sendMessage(id, groupList, message["message_id"], '{"hide_keyboard":true}', preview=False)
        elif splitted[0] == "/for":
            if "reply_to_message" in message and "from" in message["reply_to_message"]:
                blockUser = message["reply_to_message"]["from"]["id"]
                
                if blockUser not in admins and message["from"]["id"] in admins:
                    bot.deleteMessage(str(message["chat"]["id"]), str(message["message_id"]))
                    bot.deleteMessage(str(message["reply_to_message"]["chat"]["id"]), str(message["reply_to_message"]["message_id"]))
        elif splitted[0] == "/ligiloj":
            bot.sendMessage(id, "Momente vi nur povas vidi la ligilojn al ĉiuj grupoj ĉe mia retejo:\nhttps://telegramo.org/", message["message_id"], '{"hide_keyboard":true}', preview=False)
    return True

bot = Bot("TokenHere", receiveMessage)
bot.start()
#EsperantoBot end
