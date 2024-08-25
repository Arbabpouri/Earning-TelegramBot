from telethon import Button, TelegramClient
from telethon.events import NewMessage, CallbackQuery
from telethon.custom import Message
from telethon.errors import UserNotParticipantError, ChatAdminRequiredError, ChannelPrivateError
from telethon.tl.types import PeerUser, PeerChannel
from telethon.tl.functions.channels import GetParticipantRequest, GetFullChannelRequest
from re import match

from config import Config
from database import Database

try:

    client = TelegramClient(
        session=Config.SESSION_NAME,
        api_id=Config.API_ID,
        api_hash=Config.API_HASH
    ).start(
        bot_token=Config.BOT_TOKEN
    )

except Exception as error:
    
    print(error)

step = dict()
referraler = {}

class Buttons:

    START_MENU = [
        [
            Button.text("🔷 دریافت بنر 🔷", resize=True, single_use=True),
        ],
        [
            Button.text("👥 حساب کاربری", resize=True, single_use=True),
            Button.text("💰 تسویه حساب", resize=True, single_use=True),
        ],
        [
            Button.text("🔹 راهنما", resize=True, single_use=True),
            Button.text("☎ پشتیبانی", resize=True, single_use=True),
        ],
        [
            Button.text("📍 کانال اعتماد 📍", resize=True, single_use=True),
        ],
    ]

    ADMIN_MENU = [
        [
            Button.text("🎇ده نفر برتر", resize=True, single_use=True)
        ],
        [
            Button.text("✅ افزودن چنل", resize=True, single_use=True),
            Button.text("❌ حذف چنل", resize=True, single_use=True)
        ],
    ]

    SUPPORTER = [
        [
            Button.url("☎ پشتیبان ☎", f"t.me/{Config.SUPPORTED_ID}")
        ]
    ]

    CHANNEL = [
        [
            Button.url("✅ کانال اعتماد ✅", Config.CHANNEL_URL)
        ]
    ]

    HELP = [
        [
            Button.inline("🔷 دریافت بنر", "Get-Banner"),
            Button.inline("💰 تسویه حساب", "Check-Out")
        ]
    ]

    BACK_TO_HELP = [
        [
            Button.inline("Back", "Back-To-Help")
        ]
    ]

    CANCEL = [
        [
            Button.text("❌ کنسل کردن ❌", resize=True, single_use=True)
        ]
    ]

    PHONE_GET = [
        [
            Button.request_phone("⚠ ارسال شماره ⚠", resize=True, single_use=True)
        ]
    ]


class Tools:

    @staticmethod
    async def forced_to_join(user_id: int, referraler: int = 0) -> bool:

        channels_id = Database.channel.get_channels()

        if channels_id == []:
            
            return True
        
        try:

            no_joined = []

            for i in channels_id:

                try:

                    Channel = await client.get_entity(PeerChannel(i))
                    await client(GetParticipantRequest(Channel, PeerUser(int(user_id))))

                except UserNotParticipantError:
                    
                    channel_link = await client(GetFullChannelRequest(Channel))
                    no_joined.append(channel_link.full_chat.exported_invite.link)

                except ChatAdminRequiredError:

                    Database.channel(int(i)).channel_edit("remove")
                    Admins = Config.ADMINS

                    for ii in Admins:

                        try:

                            await client.send_message(PeerUser(ii), f'چنل با ایدی عددی __{i}__ از لیست چنل ها حذف شد زیرا ربات را از ادمینی دراورده بود')
                        
                        except: pass
                    
                    if channels_id == []:

                        return True

            if no_joined != []:

                Buttons, Num = [], 1

                for i in no_joined:

                    Buttons.append([Button.url(f'📌 عضویت در کانال {str(Num)} 📌', str(i))])
                    Num += 1

                Buttons.append([Button.url('💢 جوین شدم 💢', f't.me/{Config.BOT_USERNAME}?start={referraler}')])
                await client.send_message(PeerUser(int(user_id)), '🔷 برای استفاده از ربات عضو کانال ها شوید 💥', buttons=Buttons)
                return False
            
            else:

                return True
            
        except Exception as ex:

            print(ex)
            return True

    @staticmethod
    async def phone_chack(user_id: int) -> bool:

        user_data = Database.user(user_id)
        user_status = user_data.there_is_user

        if (not user_status):
            
            try:

                await client.send_message(
                    PeerUser(int(user_id)),
                    "🔷 برای فعالیت در ربات نیاز به ارسال شماره دارید\n\n❌ فقط شماره های ایرانی قادر به استفاده از این سرویس هستند",
                    buttons= Buttons.PHONE_GET
                )
                return False
            
            except:
                
                return False

        else:

            try:

                user_data.user_informations.phone_number
                return True

            except AttributeError: return False

            except: return True

@client.on(NewMessage(func=lambda event: event.is_private and not str(event.sender_id) in list(step.keys())))
async def user_move(event: Message):
    
    text = str(event.message.message)

    if (not await Tools.forced_to_join(
        event.sender_id,
        text.replace("/start ", "") if (match(r"^/start [0-9]", text)) else "0")
    ): return

    if (match(r"^/start [0-9]", text)): 

        user_id = text.replace("/start ", "")
        user_data = Database.user(user_id)
        if (user_data.there_is_user): referraler[str(event.sender_id)] = user_id
        text = "/start"
        

    if ("phone_number" in dir(event.media)):
        
        phone = str(event.media.phone_number)
        user = Database.user(event.sender_id)
        user_status = user.there_is_user

        if (not user_status):

            if (match(r"^989[0-9]{9}$", phone) or match(r"\+989[0-9]{9}$", phone)):
                
                user.add_user(
                    event.media.phone_number,
                    referraler[str(event.sender_id)] if (str(event.sender_id) in list(referraler.keys())) else None
                )

                if (str(event.sender_id) in list(referraler.keys())):

                    user_referraler = str(referraler[str(event.sender_id)])
                    
                    if (
                        user_referraler.isnumeric() and
                        user_referraler != str(event.sender_id) and
                        user_referraler != "0"
                    ):

                        add_balance = Database.user(referraler[str(event.sender_id)]).edit_balance(Config.MONEY_FOR_REFERRAL,
                                                                                                   "sum")

                    del referraler[str(event.sender_id)]

                text = "/start"

            elif (not await Tools.phone_chack(int(event.sender_id))): return
        
    elif (not await Tools.phone_chack(int(event.sender_id))): return


    match (text):

        case ("🔷 دریافت بنر 🔷" | "/start"):

            message = await client.send_file(
                entity=event.chat_id,
                file=r"./referral.jpg",
                caption=(
                    " سلام👋بچها یه ربات گیر آوردیم براتون که روزانه بالای 10.000.000 میلیون ریال میشه ازش درآمد کسب کرد😍💎"
                    "\n\n"
                    f"و بابت هر نفر که با لینک زیرمجموعه‌گیری شما به ربات اضافه بشه، شما {(Config.MONEY_FOR_REFERRAL * 10):,} هزار ریال پاداش دریافت می‌کنید 💸"
                    "\n\n"
                    f"🌐 [  https://t.me/{Config.BOT_USERNAME}?start={event.sender_id} ]"
                    "\n\n"
                    "💠برید به ربات و کلیک کنید روی [دریافت بنر] و لینک زیرمجموعه‌ گیریتون رو بفرستید برای دوستانتون⚡️"
                    "\n"
                    "-"
                    "\n"
                    "-خودم،مدیر کانالم و تستش کردم تضمینه✅⭐️"
                )
            )

            await client.send_message(
                entity=event.chat_id,
                message=(
                    f"✅ کاربر عزیز بنر ارسال شده را به دوستان خود ارسال کرده و با عضویت هر یک از یک کاربران مبلغ {Config.MONEY_FOR_REFERRAL:,} تومان دریافت کنید."
                    "\n\n"
                    "⚠️ کاربران دعوت شده حتما باید با اکانت ایران ربات را استارت نمایند."
                ),
                buttons=Buttons.START_MENU,
                reply_to=message
            )

            del text

        case ("👥 حساب کاربری"):

            informations = Database.user(int(event.sender_id)).user_informations
            await client.send_message(
                entity=event.chat_id,
                message=(
                    f"💎 نام اکانت : {event.chat.first_name}"
                    "\n"
                    f"🔢 ایدی عددی : {event.sender_id}" 
                    "\n"
                    f"💰 موجودی شما : {informations.balance}"
                    "\n"
                    f"🔗 تعداد زیرمجموعه های شما : {len(informations.referral)}"
                    "\n\n\n"
                    f"🤖 @{Config.BOT_USERNAME}"
                ),
                buttons=Buttons.START_MENU
            )
            del text
        
        case ("💰 تسویه حساب"):

            for i in range(2):
                try:
                    balance = Database.user(int(event.sender_id)).user_informations
                    balance = balance.balance
                    break
                except:
                    pass


            if (balance < Config.MIN_FOR_CHECKOUT + Config.MONEY_FOR_REFERRAL):
                
                await client.send_message(
                    entity=event.chat_id,
                    message=(
                        "💰 موجودی شما برای تسویه حساب کافی نیست"
                        "\n"
                        f"برای این کار نیاز دارید به {((Config.MIN_FOR_CHECKOUT + Config.CHECK_OUT_FEE) - balance):,} تومان"
                    ),
                    buttons=Buttons.START_MENU
                )
                
            else:

                await client.send_message(
                    entity=event.chat_id,
                    message=f"شماره کارت خود را ارسال کنید (با اعداد لاتین)",
                    buttons=Buttons.CANCEL
                )
                step[str(event.sender_id)] = {
                    "part": "Get-Number-Card",
                    "last-message": event.message
                }
                del text
   
        case ("🔹 راهنما"):

            await client.send_message(
                entity=event.chat_id,
                message="✅ کاربر عزیز جهت دسترسی به راهنما، لطفا بخش مورد نظر را انتخاب کنید.",
                buttons=Buttons.HELP
            )
            del text

        case ("☎ پشتیبانی"):

            await client.send_message(
                entity=event.chat_id,
                message="🔸 برای برقراری ارتباط با پشتیبانی روی دکمه زیر کلیک کنید 🔸",
                buttons=Buttons.SUPPORTER
            )
            del text

        case ("📍 کانال اعتماد 📍"):

            await client.send_message(
                entity=event.chat_id,
                message="📍 برای مشاهده کانال اعتماد ما روی دکمه زیر کلیک کنید ✅",
                buttons=Buttons.CHANNEL
            )
            del text


@client.on(NewMessage(func=lambda event: event.is_private and event.sender_id in Config.ADMINS and not str(event.sender_id) in list(step.keys())))
async def admin_move(event: Message):

    text = str(event.message.message)

    match (text):

        case ("panel" | "پنل" | "/panel"):

            await client.send_message(
                entity=event.chat_id,
                message="🔷 سلام و درود بر سرور من, به پنل مدیریت خوش امدید ⚙",
                buttons=Buttons.ADMIN_MENU
            )
            del text

        case ("🎇ده نفر برتر"):

            best_members = Database.user.best_member(10)

            await client.send_message(
                entity=event.chat_id,
                message=(
                    "🏆  10 نفر زیرمجموعه گیر برتر به شرح زیر است 👇" + "\n\n\n" + "".join([f"📍 {num}) ایدی عددی : {user[1]}, تعداد زیرمجموعه : {user[0]}\n\n" for num, user in enumerate(best_members, 1)])
                ),
                buttons=Buttons.ADMIN_MENU
            )

        case ("✅ افزودن چنل"):

            await client.send_message(
                entity=event.chat_id,
                message="ابتدا ربات رو در چنل مد نظر ادمین کرده سپس یک پیام از ان چنل برای ربات فوروراد کنید",
                buttons=Buttons.CANCEL
            )

            step[str(event.sender_id)] = {
                "part": "Add-Channel",
                "last-message": event.message
            }

        case ("❌ حذف چنل"):

            message = await client.send_message(
                entity=event.chat_id,
                message="صبر کنید 😅"
            )

            channels_id = Database.channel.get_channels()
            channels = []

            for channel in channels_id:

                try:

                    channel_inforamtions = await client.get_entity(PeerChannel(channel))
                    channel_inforamtions = await client(GetFullChannelRequest(channel_inforamtions))
                    channel_link = channel_inforamtions.full_chat.exported_invite.link
                    channels.append(
                        (
                            channel,
                            channel_link
                        )
                    )

                except: pass
            
            await message.delete()
            await client.send_message(
                event.sender_id,

                "ایدی چنل مد نظر رو ارسال کن\n\n" + "".join(
                    [f"📌 {num}) ایدی عددی کانال : {channel[0]} , 📍 لینکش: {channel[1]}\n\n" for num, channel in enumerate(channels, 1)]
                ),

                buttons=Buttons.CANCEL
            )

            step[str(event.sender_id)] = {
                "part": "Del-Channel",
                "last-message": event.message,
                "channels": list(map(lambda x: x[0], channels))
            }

            del (message, channels_id, channels)


@client.on(NewMessage(func=lambda event: event.is_private and str(event.sender_id) in list(step.keys())))
async def get_informations(event: Message):

    if (not await Tools.forced_to_join(event.sender_id)): 
        del step[str(event.sender_id)]
        return

    part = step[str(event.sender_id)]["part"]
    text = str(event.message.message)

    if (text == "❌ کنسل کردن ❌"):

        await client.send_message(
            entity=event.chat_id,
            message="عملیات کنسل شد\nبه صفحه اصلی بازگشتید",
            buttons=Buttons.START_MENU
        )
        del step[str(event.sender_id)]
        return

    if (str(event.sender_id) in list(step.keys()) and
        "last-message" in step[str(event.sender_id)] and 
        step[str(event.sender_id)]["last-message"] == event.message): return

    match (part):

        case ("Get-Number-Card"):

            text = text.replace(" ", "")

            if (text.isnumeric() and 
                text.__len__() == 16):

                await client.send_message(
                    entity=event.chat_id,
                    message="📍 نام دارنده کارت را وارد کنید",
                    buttons=Buttons.CANCEL
                )

                step[str(event.sender_id)] = {
                    "part": "Get-OwnerName-Card",
                    "NumberCard": str(text),
                    "last-message": event.message
                }

                del (part, text)

            else:

                await client.send_message(
                    entity=event.chat_id,
                    message="❌ شماره کارت ارسالی اشتباه است, شماره کارت باید شمال 16 رقم با اعداد لاتین باشد"
                )

                del (part, text)

        case ("Get-OwnerName-Card"):

            if (len(text) >= 100):

                await client.send_message(
                    entity=event.chat_id,
                    message="نام ارسالی بیش از حد طولانی است, باید شمال 100 کاراکتر باشد",
                    buttons=Buttons.CANCEL
                )
            
            else:

                for i in range(2):

                    try:
                        balance = Database.user(int(event.sender_id)).user_informations.balance
                        break
                    except:
                        pass
                
                if (balance >= (Config.MIN_FOR_CHECKOUT + Config.CHECK_OUT_FEE)):
                    
                    Database.user(int(event.sender_id)).edit_balance(balance, "sub")
                    message = f"🔷 مقدار {Config.CHECK_OUT_FEE} از شما کسر گردید و درخواست تسویه برای پشتیبانی ارسال شد\nموفق یاشید❤"

                else:

                    message = f"⚠ موجودی شما به حد برداشت نرسیده است\n اقدام به جمع اوردی زیرمجموعه کنید\nشما نیاز داریم به {Config.MIN_FOR_CHECKOUT + Config.CHECK_OUT_FEE} تومان"

                await client.send_message(
                    entity=event.chat_id,
                    message=message,
                    buttons=Buttons.START_MENU
                )

                for admin in Config.ADMINS:

                    try:

                        await client.send_message(
                            entity=PeerUser(int(admin)),
                            message=(
                                "🔺 درخواست برداشت"
                                "\n"
                                f"🔹 از طرف : {event.chat.first_name}"
                                "\n"
                                f"🔢 با ایدی عددی : {event.sender_id}"
                                "\n"
                                f"💲 مبلغ : {balance - Config.MONEY_FOR_REFERRAL}"
                                "\n"
                                f"💳 شماره کارت : {step[str(event.sender_id)]['NumberCard']}"
                                "\n"
                                f"👤 به نام : {text}"
                                "\n\n\n"
                                f"🆔 @{Config.BOT_USERNAME}"
                            )
                        )
                    
                    except:
                        
                        pass


                
                del step[str(event.sender_id)]

        case ("Add-Channel"):

            if event.fwd_from:

                try:

                    Channels = Database.channel.get_channels()
                    channel_id = int(event.fwd_from.from_id.channel_id)
                    
                    if (not channel_id in Channels):
                        
                        
                        full_chat = await client(GetFullChannelRequest(PeerChannel(int(channel_id))))
                        link = full_chat.full_chat.exported_invite.link
                        admins = full_chat.full_chat.admins_count

                        if (not admins is None):

                            Database.channel(int(channel_id)).channel_edit("add")

                            await client.send_message(
                                entity=event.sender_id,
                                message=f"کانال با ایدی عددی {channel_id} و لینک {link} به لیست چنل های قفل شده اضافه شد :)\n\n\nبه پنل مدیریت بازگشتید",
                                buttons=Buttons.ADMIN_MENU
                            )

                            del (text, part, step[str(event.sender_id)])
                        
                        else:

                            await client.send_message(
                                event.sender_id, 
                                "رفیق مثل اینکه منو ادمین کانال نکردی\nلطفا اول منو ادمین کن بعد پیامو فوروارد کن", 
                                buttons=Buttons.CANCEL
                            )

                            del (text, part)
                    else:

                        await client.send_message(
                            event.sender_id, 
                            "🤭 این کانال در لیست کانال های قفل شده هست 🤖", 
                            buttons=Buttons.CANCEL
                        )
                        del (text, part)
                
                except AttributeError:
                    
                    await client.send_message(
                        event.sender_id, 
                        "❌ پیام رو از کانال برام بفرست نه از چیز دیگه , فقط و فقط از کانال مورد نظرت 😐", 
                        buttons=Buttons.CANCEL
                    )

                    del (text, part)
                
                except ChannelPrivateError:

                    await client.send_message(
                        event.sender_id, 
                        "❌ هنوز منو توی چنل ادمین نکردی سلطان\nگفتم بهت که اول تو کانال ادمینم کن بعد فوروارد کن ❌", 
                        buttons=Buttons.CANCEL
                    )

                    del (text, part)

                except Exception as ex:

                    await client.send_message(
                        event.sender_id, 
                        "❌ هنوز منو توی چنل ادمین نکردی سلطان\nگفتم بهت که اول تو کانال ادمینم کن بعد فوروارد کن ❌", 
                        buttons=Buttons.CANCEL
                    )

                    print(ex)

                    del (text, part)

            else:
                
                await client.send_message(
                    event.sender_id, 
                    "❌ جناب برای اضافه کردن کانال به لیست لطفا ابتدا اموزش رو بخونید سپس دست به کار بشید ❌\n⭕️ شما پیام رو از کانال فوروراد نکردید ⭕️", 
                    buttons=Buttons.CANCEL
                )

                del (text, part)

        case ("Del-Channel"):

            if (not str(text).isnumeric()):

                await client.send_message(
                    entity=event.chat_id,
                    message="⚠ فقط ایدی عددی کانال را ارسال کنید (به صورت اعداد لاتین)",
                    buttons=Buttons.CANCEL
                )

                return
            
            channels_id = step[str(event.sender_id)]["channels"]
            channels_id = list(map(lambda x: str(x), channels_id))

            if (str(text) in channels_id):

                Database.channel(int(text)).channel_edit("remove")
                
                await client.send_message(
                    entity=event.chat_id,
                    message="📌 چنل با موفقیت حذف شد",
                    buttons=Buttons.START_MENU
                )

                del step[str(event.sender_id)]

            else:

                await client.send_message(
                    entity=event.chat_id,
                    message="📍 چنین چنلی با این ایدی عددی وجود ندارد\nلطفا دقت کنید.",
                    buttons=Buttons.CANCEL
                )


@client.on(CallbackQuery(func=lambda event: event.is_private and not str(event.sender_id) in list(step.keys())))
async def user_move_inline(event: CallbackQuery.Event):

    data = bytes(event.data).decode()

    match (data):

        case "Get-Banner":

            await event.edit(
                (
                    "⭕️ دریافت بنر ⭕️"
                    "\n"
                    "1- جهت دریافت بنر بر روی دکمه \"📈 دریافت بنر\" کلیک نمایید."
                    "-"
                    "\n"
                    "2- شما هنگام ارسال بنر دریافتی به دوستان خود میتوا انید کسب درآمد کنید."
                    "\n\n"
                    f"هر فردی که با لینک شما ربات را استارت کرده و عضو کانال  های اسپانسر شود، حساب {Config.MONEY_FOR_REFERRAL:,} تومان شارژ می شود."
                    "⚠️ زیر مجموعه گیری با این روش به صورت نامحدود می باشد.  شما با ارسال بنر خود به دوستان، میتوانید کسب درآمد کنید."
                ),
                buttons=Buttons.BACK_TO_HELP
            )
            del data
        
        case "Check-Out":

            await event.edit(
                (
                    "⭕️ تسویه حساب ⭕️\n"
                    "✅ بخش تسویه حساب شامل دو بخش می‌باشد:\n"
                    "1️⃣- تسویه با کارت به کارت\n"
                    "2️⃣ تسویه با ارز ووچر یا ترون \n"
                    "➕➖➕➖➕➖➕     ➕➖➕➖\n"
                    "چگونه بصورت کارت به کارت تسویه حساب کنیم ⁉️\n"
                    
                    "1- بر روی دکمه ی \"💳 تسویه حساب\" کلیک کنید.\n"

                    "2- بر روی دکمه ی کارت به کارتت کلیک کنید.\n"

                    "3- در صورتی که برای اولین بار درخواست کارت به کارت ثبت می کنید، ربات ابتدا از شما شماره کارت و نام صاحب کارت با می پرسد.\n"

                    "4- پس از ثبت شماره کارت، باید تایید کنید که می خواهید برداشت کنید.\n"

                    "5- پس از ثبت درخواست کارت به کارت، درخواست شما به بخش مالی ربات ارجاع داده می شود.\n"

                    "⚠️ هنگام ثبت درخواست واریز، ربات مبلغ 1000 تومان را از حساب شما کم کرده و درخواست شما را ثبت میکند.\n"
                    "✅ کانال ثبت واریزی ها 👇🏻\n\n\n"
                    ""
                    "➕➖➕➖➕➖➕➖➕➖\n"
                    "چگونه ووچر درخواست کنیم ⁉️"
                    "❌ درخواست ووچر به صورت  موقت امکان پذیر نمی باشد."
                ),
                buttons=Buttons.BACK_TO_HELP
            )
            del data

        case "Back-To-Help":
            
            await event.edit(
                "✅ کاربر عزیز جهت دسترسی به راهنما، لطفا بخش مورد نظر را انتخاب کنید.",
                buttons=Buttons.HELP
            )
            del data

        case "Post-Showed":

            pass



if __name__ == "__main__":

    try:

        print("Bot is onlone!")
        client.run_until_disconnected()

    except Exception as error:

        print(error)