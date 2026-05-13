import discord
from discord.ext import commands, tasks
from discord import app_commands
import json
import os
import random
from datetime import datetime

# 🔥 СЮДА ТВОЙ НОВЫЙ ТОКЕН (ПОСЛЕ СБРОСА)
TOKEN = "MTUwNDA5NjI5ODMxMDE3MjcwMg.G1u9d0.BnSciJ_zM9jlg5uq5KgVFUIve1LJ90avQ52aI0"

SETTINGS_FILE = 'settings.json'

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    return {'channel_id': None, 'auto_post_enabled': False}

def save_settings(settings):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=4)

# 🔥 НОВЫЕ ШАБЛОНЫ (10 штук) + реал ссылка на TG
TEMPLATES = [
    {
        "name": "Классика",
        "text": "🔥 **M1NDS** — одежда для тех, кто мыслит иначе!\n\n🧠 Твой стиль — твои правила.\n👉 **@M1nds_Brand**\n⚡ Оформи заказ прямо сейчас!"
    },
    {
        "name": "Свежая коллекция",
        "text": "👕 **СВЕЖАЯ КОЛЛЕКЦИЯ M1NDS** уже в Telegram!\n\n🎯 Будь в тренде — будь в M1NDS.\n📲 Переходи: **@M1nds_Brand**\n💥 Успей за своим луком!"
    },
    {
        "name": "Вне шаблонов",
        "text": "🧠 **M1NDS** — стиль вне шаблонов.\n\n🚀 Одежда для смелых и свободных.\n🔥 Заходи: **@M1nds_Brand**\n💪 Будь собой. Будь в M1NDS."
    },
    {
        "name": "M1NDS ARMY",
        "text": "⚡ **ВНИМАНИЕ, M1NDS ARMY!** ⚡\n\nНовые поступления уже в канале!\n💪 Одежда для сильных духом.\n👉 **@M1nds_Brand**\n🔥 Не проморгай свой размер!"
    },
    {
        "name": "Уличный стиль",
        "text": "🛹 **STREETWEAR от M1NDS**\n\nХочешь выделяться из толпы?\nМы знаем, как.\n🚀 **@M1nds_Brand**\n💯 Качество, которое чувствуешь."
    },
    {
        "name": "Лимитка",
        "text": "⏰ **ЛИМИТИРОВАННАЯ СЕРИЯ!** ⏰\n\nM1NDS выпустил капсулу, которая разойдётся за час.\n🎯 Успей забрать своё.\n👉 **@M1nds_Brand**\n🔥 Поторопись!"
    },
    {
        "name": "Оверсайз",
        "text": "👔 **M1NDS OVERSIZE** — твой комфорт в каждой детали.\n\nСвобода движений и вайб, который цепляет.\n📲 **@M1nds_Brand**\n⚡ Забирай свой размер!"
    },
    {
        "name": "Зима/Лето",
        "text": "☀️❄️ **M1NDS на любой сезон!**\n\nХуди, футболки, свитшоты — выбирай своё.\n🧠 Будь в M1NDS — будь в кайфе.\n👉 **@M1nds_Brand**"
    },
    {
        "name": "Коллаб",
        "text": "🤝 **M1NDS COLLAB**\n\nКоллаборация с топовыми дизайнерами.\nЭксклюзив, который нельзя пропустить.\n🔥 **@M1nds_Brand**\n🚀 Только у нас!"
    },
    {
        "name": "Базовый",
        "text": "📌 **M1NDS BASICS** — база, на которой всё держится.\n\nКачественные вещи на каждый день.\n💯 Минимализм со смыслом.\n👉 **@M1nds_Brand**"
    }
]

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)
settings = load_settings()

class TemplateSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=f"{i+1}. {t['name']}", description=t['text'][:50] + "...")
            for i, t in enumerate(TEMPLATES)
        ]
        options.append(discord.SelectOption(label="📝 Свой текст", description="Напиши свою рекламу", emoji="✏️"))
        super().__init__(placeholder="Выбери шаблон для поста...", options=options, min_values=1, max_values=1)
    
    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "📝 Свой текст":
            await interaction.response.send_message("✏️ Напиши свой текст рекламы в ответ на это сообщение:", ephemeral=True)
            
            def check(m):
                return m.author == interaction.user and isinstance(m.channel, discord.DMChannel)
            
            try:
                msg = await bot.wait_for('message', timeout=60.0, check=check)
                text = msg.content
            except:
                await interaction.followup.send("⏰ Время вышло!", ephemeral=True)
                return
        else:
            idx = int(self.values[0].split('.')[0]) - 1
            text = TEMPLATES[idx]['text']
        
        channel_id = settings.get('channel_id')
        if not channel_id:
            await interaction.followup.send("❌ Сначала установи канал командой `/set_channel`", ephemeral=True)
            return
        
        channel = bot.get_channel(channel_id)
        if not channel:
            await interaction.followup.send("❌ Канал не найден!", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="🧠 **M1NDS**",
            description=text,
            color=0x000000
        )
        embed.set_footer(text=f"Пост от {interaction.user.display_name} • M1NDS Brand")
        embed.set_thumbnail(url="https://i.imgur.com/placeholder.png")
        
        await channel.send(embed=embed)
        await interaction.followup.send(f"✅ Реклама отправлена в {channel.mention}", ephemeral=True)

class TemplateView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        self.add_item(TemplateSelect())

@bot.event
async def on_ready():
    print(f'✅ Бот {bot.user} запущен!')
    print(f'📡 На серверах: {len(bot.guilds)}')
    try:
        synced = await bot.tree.sync()
        print(f'✨ Синхронизировано {len(synced)} команд')
    except Exception as e:
        print(f'Ошибка синхронизации: {e}')
    
    if settings.get('auto_post_enabled', False):
        auto_post.start()

@tasks.loop(minutes=10)
async def auto_post():
    channel_id = settings.get('channel_id')
    if not channel_id:
        return
    channel = bot.get_channel(channel_id)
    if not channel:
        return
    
    # Рандомный шаблон из всех
    template = random.choice(TEMPLATES)
    text = template['text']
    
    embed = discord.Embed(
        title="🧠 **M1NDS**",
        description=text,
        color=0x000000
    )
    embed.set_footer(text=f"Автореклама • {datetime.now().strftime('%H:%M')}")
    embed.set_thumbnail(url="https://i.imgur.com/placeholder.png")
    
    await channel.send(embed=embed)
    print(f"📨 Авто-пост '{template['name']}' отправлен в {channel.name} в {datetime.now().strftime('%H:%M:%S')}")

@auto_post.before_loop
async def before_auto_post():
    await bot.wait_until_ready()

# ============== КОМАНДЫ ==============

@bot.tree.command(name="set_channel", description="Установить канал для рекламы M1NDS")
async def set_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Только администратор!", ephemeral=True)
        return
    settings['channel_id'] = channel.id
    save_settings(settings)
    await interaction.response.send_message(f"✅ Канал установлен: {channel.mention}", ephemeral=True)

@bot.tree.command(name="post_now", description="Отправить рекламу M1NDS с выбором шаблона")
async def post_now(interaction: discord.Interaction):
    channel_id = settings.get('channel_id')
    if not channel_id:
        await interaction.response.send_message("❌ Сначала установи канал командой `/set_channel`", ephemeral=True)
        return
    
    view = TemplateView()
    await interaction.response.send_message("📋 **Выбери шаблон для рекламы M1NDS:**", view=view, ephemeral=True)

@bot.tree.command(name="templates", description="Показать все шаблоны M1NDS с номерами")
async def show_templates(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📋 **Все шаблоны M1NDS (10 шт.)**",
        description="\n\n".join([f"**{i+1}. {t['name']}**\n{t['text'][:100]}..." for i, t in enumerate(TEMPLATES)]),
        color=0x000000
    )
    embed.set_footer(text="Используй /post_template <номер> для быстрой отправки")
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="post_template", description="Отправить конкретный шаблон по номеру (1-10)")
@app_commands.describe(number="Номер шаблона от 1 до 10")
async def post_template(interaction: discord.Interaction, number: int):
    channel_id = settings.get('channel_id')
    if not channel_id:
        await interaction.response.send_message("❌ Сначала установи канал командой `/set_channel`", ephemeral=True)
        return
    
    if number < 1 or number > len(TEMPLATES):
        await interaction.response.send_message(f"❌ Введи номер от 1 до {len(TEMPLATES)}", ephemeral=True)
        return
    
    channel = bot.get_channel(channel_id)
    if not channel:
        await interaction.response.send_message("❌ Канал не найден!", ephemeral=True)
        return
    
    template = TEMPLATES[number - 1]
    embed = discord.Embed(title="🧠 **M1NDS**", description=template['text'], color=0x000000)
    embed.set_footer(text=f"Шаблон {number}: {template['name']}")
    
    await channel.send(embed=embed)
    await interaction.response.send_message(f"✅ Шаблон '{template['name']}' отправлен в {channel.mention}", ephemeral=True)

@bot.tree.command(name="start_auto", description="Запустить автопостинг каждые 10 минут")
async def start_auto(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Только администратор!", ephemeral=True)
        return
    if not settings.get('channel_id'):
        await interaction.response.send_message("❌ Сначала установи канал /set_channel", ephemeral=True)
        return
    settings['auto_post_enabled'] = True
    save_settings(settings)
    if not auto_post.is_running():
        auto_post.start()
    await interaction.response.send_message("✅ Автопостинг запущен! Каждые 10 минут 🚀", ephemeral=True)

@bot.tree.command(name="stop_auto", description="Остановить автопостинг")
async def stop_auto(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Только администратор!", ephemeral=True)
        return
    settings['auto_post_enabled'] = False
    save_settings(settings)
    if auto_post.is_running():
        auto_post.stop()
    await interaction.response.send_message("⏸️ Автопостинг остановлен", ephemeral=True)

@bot.tree.command(name="status", description="Показать статус бота")
async def show_status(interaction: discord.Interaction):
    channel_id = settings.get('channel_id')
    auto_enabled = settings.get('auto_post_enabled', False)
    channel_info = f"<#{channel_id}>" if channel_id else "❌ Не установлен"
    embed = discord.Embed(title="📊 Статус M1NDS бота", color=0x000000)
    embed.add_field(name="📢 Канал", value=channel_info, inline=False)
    embed.add_field(name="⏰ Автопостинг", value="✅ Вкл" if auto_enabled else "❌ Выкл", inline=True)
    embed.add_field(name="🕐 Интервал", value="10 минут", inline=True)
    embed.add_field(name="📝 Шаблонов", value=str(len(TEMPLATES)), inline=True)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.command()
@commands.has_permissions(administrator=True)
async def пиар(ctx):
    """Отправить рандомный шаблон"""
    channel_id = settings.get('channel_id')
    if not channel_id:
        await ctx.send("❌ Сначала установи канал командой /set_channel")
        return
    channel = bot.get_channel(channel_id)
    template = random.choice(TEMPLATES)
    embed = discord.Embed(title="🧠 **M1NDS**", description=template['text'], color=0x000000)
    await channel.send(embed=embed)
    await ctx.send(f"✅ Отправлен шаблон: {template['name']}")

@bot.command()
@commands.has_permissions(administrator=True)
async def шаблоны(ctx):
    """Показать все шаблоны"""
    msg = "**📋 ВСЕ ШАБЛОНЫ M1NDS:**\n\n"
    for i, t in enumerate(TEMPLATES, 1):
        msg += f"**{i}. {t['name']}**\n{t['text'][:80]}...\n\n"
    await ctx.send(msg[:2000])  # Discord лимит

if __name__ == "__main__":
    bot.run(TOKEN)