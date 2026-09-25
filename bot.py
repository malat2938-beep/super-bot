# -*- coding: utf-8 -*-
import os, json, random, re
import yt_dlp
import requests
from PIL import Image, ImageEnhance, ImageFilter
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters
from io import BytesIO

TOKEN = os.getenv("BOT_TOKEN")
DATA_FILE = "users.json"

EIGHT_BALL = ["أكيد 100% ✅","احتمال كبير 👍","غير واضح، جرب مرة ثانية 🤔","لا أعتقد ذلك ❌","أكيد لا 🚫","الأمور بصالحك 🍀","اسأل لاحقاً ⏳"]
DECOR_TEMPLATES = ["꧁{t}꧂","『{t}』","★彡{t}彡★","_■{t}■_","◥{t}◤","『—{t}—』","•°*”˜ {t} ˜”*°•"]
FACTS = ["🧠 الدماغ البشري يحتوي على حوالي 86 مليار خلية عصبية!","🍯 العسل ما يخرب مهما مر عليه وقت!","🐙 الأخطبوط عنده 3 قلوب ودمه لونه أزرق!","🌕 يوم على كوكب الزهرة أطول من سنة كاملة بيه!","⚡ البرق أسخن من سطح الشمس بخمس مرات!"]
COMPLIMENTS = ["أنت شخص خطير وتستاهل كلشي زين ✨","ابتسامتك تغير مزاج اليوم كله 😊","عندك طاقة إيجابية تنعدي لكل من حولك 🌟"]
JOKES = ["واحد غالوله ليش زعلان؟ كال الواي فاي مقطوع من كلبي 💔📶","واحد كال لصاحبه: أنا أبرمج بلغة الحب. صاحبه كاله: زين، شكد error عطتك؟","شنو الفرق بين الطالب والمبرمج؟ الطالب يذاكر بالليلة، والمبرمج يصحح bug بالليلة! 😅"]

# ===== تخزين البيانات =====
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE,"r",encoding="utf-8") as f: return json.load(f)
        except: return {}
    return {}
def save_data(data):
    with open(DATA_FILE,"w",encoding="utf-8") as f: json.dump(data,f,ensure_ascii=False,indent=2)
def get_user(data,uid):
    uid=str(uid)
    if uid not in data: data[uid]={"points":0,"referrals":0}
    return data[uid]

# ===== القوائم =====
def main_menu():
    kb=[[InlineKeyboardButton("🎮 ألعاب",callback_data="menu_games"),InlineKeyboardButton("🛠️ أدوات",callback_data="menu_tools")],
        [InlineKeyboardButton("🔥 تسلية",callback_data="menu_fun"),InlineKeyboardButton("🎨 وسائط",callback_data="menu_media")],
        [InlineKeyboardButton("🏆 نقاطي",callback_data="menu_points")],
        [InlineKeyboardButton("📢 شارك البوت واكسب نقاط",callback_data="invite")]]
    return InlineKeyboardMarkup(kb)

def games_menu():
    kb=[[InlineKeyboardButton("🎲 نرد",callback_data="dice")],[InlineKeyboardButton("🔢 تخمين رقم",callback_data="guess_start")],
        [InlineKeyboardButton("✊ حجرة ورقة مقص",callback_data="rps_menu")],[InlineKeyboardButton("⬅️ رجوع",callback_data="main")]]
    return InlineKeyboardMarkup(kb)

def tools_menu():
    kb=[[InlineKeyboardButton("😎 زخرفة اسماء",callback_data="font")],[InlineKeyboardButton("📥 تحميل فيديو",callback_data="download")],[InlineKeyboardButton("⬅️ رجوع",callback_data="main")]]
    return InlineKeyboardMarkup(kb)

def fun_menu():
    kb=[[InlineKeyboardButton("🔮 الكرة السحرية",callback_data="eightball")],[InlineKeyboardButton("😂 نكتة",callback_data="joke")],[InlineKeyboardButton("🧠 معلومة",callback_data="fact")],[InlineKeyboardButton("💖 مدح",callback_data="compliment")],[InlineKeyboardButton("⬅️ رجوع",callback_data="main")]]
    return InlineKeyboardMarkup(kb)

def media_menu():
    kb=[[InlineKeyboardButton("🖼️ تعديل صورة (ارسل صورة)",callback_data="media_info")],[InlineKeyboardButton("⬅️ رجوع",callback_data="main")]]
    return InlineKeyboardMarkup(kb)

def rps_menu():
    kb=[[InlineKeyboardButton("✊",callback_data="rps_rock"),InlineKeyboardButton("✋",callback_data="rps_paper"),InlineKeyboardButton("✌️",callback_data="rps_scissors")],[InlineKeyboardButton("⬅️ رجوع",callback_data="menu_games")]]
    return InlineKeyboardMarkup(kb)

# ===== الأوامر =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data=load_data()
    user=get_user(data,update.effective_user.id)
    if context.args:
        try:
            ref=context.args[0]
            if ref!=str(update.effective_user.id):
                ref_user=get_user(data,ref)
                ref_user["points"]+=10
                ref_user["referrals"]+=1
                save_data(data)
        except: pass
    save_data(data)
    await update.message.reply_text(f"🔥 بوت شامل - النسخة الكاملة\n\nكلشي بمكان واحد: تسلية + أدوات + ألعاب + زخرفة نصوص + تعديل صور + تحميل فيديوهات\n\nنقاطك: {user['points']} 🏆",reply_markup=main_menu())

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q=update.callback_query
    await q.answer()
    d=q.data
    data=load_data()
    user=get_user(data,q.from_user.id)

    if d=="main": await q.message.edit_text("👑 القائمة الرئيسية:",reply_markup=main_menu())
    elif d=="menu_games": await q.message.edit_text("🎮 قسم الألعاب:",reply_markup=games_menu())
    elif d=="menu_tools": await q.message.edit_text("🛠️ قسم الأدوات:",reply_markup=tools_menu())
    elif d=="menu_fun": await q.message.edit_text("🔥 قسم التسلية:",reply_markup=fun_menu())
    elif d=="menu_media": await q.message.edit_text("🎨 قسم الوسائط - ارسل صورة وسأعدلها لك:",reply_markup=media_menu())
    elif d=="menu_points": await q.message.edit_text(f"🏆 نقاطك: {user['points']}\n👥 دعواتك: {user['referrals']}\n\nشارك رابطك:\nhttps://t.me/{context.bot.username}?start={q.from_user.id}",reply_markup=main_menu())
    elif d=="invite": await q.message.reply_text(f"📢 شارك هذا الرابط واكسب 10 نقاط لكل شخص يدخل:\nhttps://t.me/{context.bot.username}?start={q.from_user.id}")
    elif d=="dice": await q.message.reply_dice(emoji="🎲")
    elif d=="guess_start":
        context.user_data["mode"]="guess"
        context.user_data["number"]=random.randint(1,100)
        await q.message.reply_text("🔢 خمنت رقم بين 1 و 100، دز تخمينك!")
    elif d=="rps_menu": await q.message.edit_text("اختر:",reply_markup=rps_menu())
    elif d.startswith("rps_"):
        u=d.split("_")[1]
        b=random.choice(["rock","paper","scissors"])
        mp={"rock":"✊","paper":"✋","scissors":"✌️"}
        win = "تعادل!" if u==b else ("فزت! +1 نقطة 🎉" if (u=="rock" and b=="scissors") or (u=="paper" and b=="rock") or (u=="scissors" and b=="paper") else "خسرت! 😅")
        if "فزت" in win:
            user["points"]+=1
            save_data(data)
        await q.message.reply_text(f"انت: {mp[u]}\nالبوت: {mp[b]}\n{win}",reply_markup=rps_menu())
    elif d=="eightball":
        context.user_data["mode"]="eightball"
        await q.message.reply_text("🔮 اسأل سؤالك للكرة السحرية!")
    elif d=="joke": await q.message.reply_text(random.choice(JOKES))
    elif d=="fact": await q.message.reply_text(random.choice(FACTS))
    elif d=="compliment": await q.message.reply_text(random.choice(COMPLIMENTS))
    elif d=="download":
        context.user_data["mode"]="download"
        await q.message.reply_text("📥 دزلي رابط تيك توك / انستا / يوتيوب / فيسبوك")
    elif d=="font":
        context.user_data["mode"]="font"
        await q.message.reply_text("😎 دزلي اسمك ازخرفه الك")
    elif d=="media_info":
        await q.message.reply_text("🎨 دزلي صورة واني اعدلها (تحسين + فلتر)")

async def on_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text=update.message.text or ""
    mode=context.user_data.get("mode","")
    data=load_data()
    user=get_user(data,update.effective_user.id)

    if mode=="download" and ("http" in text):
        await update.message.reply_text("⏳ جاري التحميل...")
        try:
            opts={'outtmpl':'%(id)s.%(ext)s','format':'best[filesize<50M]/best','quiet':True}
            with yt_dlp.YoutubeDL(opts) as ydl:
                info=ydl.extract_info(text,download=True)
                fn=ydl.prepare_filename(info)
            await update.message.reply_video(video=open(fn,'rb'),caption="✅ تم التحميل بواسطة البوت الشامل")
            os.remove(fn)
            user["points"]+=2
            save_data(data)
        except Exception as e:
            await update.message.reply_text(f"❌ خطأ: {e}\nجرب رابط ثاني")
    elif mode=="font":
        res="\n".join([t.format(t=text) for t in DECOR_TEMPLATES])
        await update.message.reply_text(f"😎 زخرفة اسمك:\n\n{res}")
        context.user_data["mode"]=""
    elif mode=="guess":
        try:
            g=int(text)
            n=context.user_data.get("number",50)
            if g==n:
                await update.message.reply_text(f"🎉 صح! الرقم كان {n} - كسبت 5 نقاط!")
                user["points"]+=5
                save_data(data)
                context.user_data["mode"]=""
            elif g<n: await update.message.reply_text("⬆️ رقم أكبر!")
            else: await update.message.reply_text("⬇️ رقم أصغر!")
        except: await update.message.reply_text("دز رقم فقط!")
    elif mode=="eightball":
        await update.message.reply_text(f"🔮 الجواب: {random.choice(EIGHT_BALL)}")
        context.user_data["mode"]=""

    # تعديل صور
    if update.message.photo:
        try:
            file=await update.message.photo[-1].get_file()
            img_bytes=BytesIO()
            await file.download_to_memory(img_bytes)
            img=Image.open(img_bytes)
            img=ImageEnhance.Color(img).enhance(1.5)
            img=img.filter(ImageFilter.SHARPEN)
            out=BytesIO()
            out.name="edited.jpg"
            img.save(out,"JPEG")
            out.seek(0)
            await update.message.reply_photo(photo=out,caption="🎨 تم تحسين الصورة! +2 نقطة")
            user["points"]+=2
            save_data(data)
        except Exception as e:
            await update.message.reply_text(f"خطأ بالصورة: {e}")

def main():
    app=Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start",start))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND,on_message))
    app.run_polling()

if __name__=="__main__":
    main()
