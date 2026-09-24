# Render Free: ishga tushirish

1. ZIPni oching. Ichki loyiha papkasidagi fayllarni GitHub repozitoriysining
   ildiziga yuklang: render.yaml, backend/ va ushbu yo‘riqnoma yonma-yon tursin.
2. Tashqi PostgreSQL baza yarating (masalan, Neon). Direct connection URLni oling.
   postgres://, postgresql:// va postgresql+asyncpg:// formatlari qabul qilinadi.
   Provayderning amaldagi bepul tarif limitlarini alohida tekshiring.
3. Render → New → Blueprint → repozitoriyni tanlang.
4. So‘ralgan qiymatlar:
   - TELEGRAM_BOT_TOKEN: BotFather bergan token.
   - DATABASE_URL: PostgreSQL ulanish manzili, SSL parametrlari bilan.
   - ADMIN_TELEGRAM_IDS: o‘zingizning raqamli Telegram IDingiz, masalan [123456789].
   SESSION_SECRET va TELEGRAM_WEBHOOK_SECRET avtomatik yaratiladi.
5. Deploy tugagach https://SIZNING-SERVIS.onrender.com/health ni oching.
   Javob {"status":"ok"} bo‘lishi kerak.
6. BotFather → bot → Bot Settings → Configure Mini App:
   asosiy Mini App URLiga Render bergan HTTPS manzilni kiriting.
   Kerak bo‘lsa /setdomain orqali ham shu domenni belgilang.
   Guruhga qo‘shilish ruxsati yoqilgan bo‘lsin.
   Webhook server ishga tushganda avtomatik ro‘yxatdan o‘tadi.
7. Botning shaxsiy chatida /start → “Botni guruhga qo‘shish” →
   guruhni tanlang → admin huquqini tasdiqlang.
8. Guruhda /start → qo‘shilish tugmasi orqali ishtirokchilar kirsin.

## Tekshirish

- “Profil” tugmasi bosh menyuni ochishi kerak.
- Guruhda o‘yin borida yana /start yangi o‘yin ochmasligi kerak.
- O‘yin boshida faqat rollar soni, oxirida natijalar kelishi kerak.
- /stop faqat o‘yin egasi yoki guruh adminiga ishlaydi.
- Qayta deploydan keyin faol o‘yin checkpointdan tiklanishini tekshiring.

## Muhim cheklovlar

Render Free 15 daqiqa kiruvchi trafik bo‘lmasa uxlaydi; uyg‘onish kechikadi.
Bu tarif doimiy uzluksiz ishlashni kafolatlamaydi. Server ishlamay turgan vaqt
ham o‘yin taymeriga kiradi; tiklanganda muddati o‘tgan bosqich davom ettiriladi.
SQLite fayli Render qayta ishga tushganda yo‘qolishi mumkin; shu sabab
production faqat PostgreSQL bilan ishlaydi. Renderning bepul PostgreSQL
bazasi 30 kundan keyin tugaydi; doimiy baza rejasini alohida tanlang.

Faqat BITTA servis nusxasi va BITTA worker ishlating. O‘yin registri RAMda,
tiklash nusxasi PostgreSQLda. Bitta token bilan polling va webhookni
bir vaqtda ishga tushirmang. bot/bot.py Render uchun ishga tushirilmaydi.

Telegram xabarlari muvaffaqiyatsiz bo‘lsa 30 soniyadan keyin takror uriniladi.
Yakuniy xabar server xotirasida saqlanayotgan muddatda qayta yuboriladi;
Telegram uzilishi bilan server qayta ishga tushishi bir vaqtda bo‘lsa
yetkazishni kafolatlab bo‘lmaydi. Tokenlarni repozitoriyga joylamang.

Rasmiy manbalar:
- https://render.com/docs/free
- https://render.com/docs/blueprint-spec
- https://core.telegram.org/api/links#group-channel-bot-links
