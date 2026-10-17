import discord
from discord import app_commands
import json
import os

# --- CONFIGURACIÓN DEL BOT ---
intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
TOKEN = "TU-TOKEN-AQUI"

# --- BASE DE DATOS (JSON) ---
DB_FILE = "tiers.json"

def cargar_datos():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def guardar_datos(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# --- FUNCIÓN PARA CREAR EL EMBED (Para no repetir código) ---
def crear_embed_tier(nick, datos_jugador):
    skin_url = f"https://wsrv.nl/?url=mc-heads.net/body/{nick}/right"
    
    embed = discord.Embed(
        title=f"{nick}'s Test Results 🏆",
        color=0x2b2d31
    )
    # Skin pequeña al costado (Texto)
    embed.set_thumbnail(url=skin_url)
    
    embed.add_field(name="Tester:", value=f"@{datos_jugador.get('tester', 'Desconocido')}", inline=False)
    embed.add_field(name="Region:", value=datos_jugador.get('region', 'NA'), inline=False)
    embed.add_field(name="Username:", value=nick, inline=False)
    embed.add_field(name="Modalidad:", value=datos_jugador.get('modalidad', 'SWORD'), inline=False)
    embed.add_field(name="Previous Rank:", value=datos_jugador.get('prev_rank', 'Unranked'), inline=False)
    embed.add_field(name="Rank Earned:", value=datos_jugador.get('tier', 'Sin Tier'), inline=False)
    
    embed.set_footer(text="Vandal 🏆")
    return embed

# --- EVENTOS ---
@client.event
async def on_ready():
    await tree.sync()
    print(f"Bot conectado como {client.user}")

# --- COMANDOS ---

# 1. /help
@tree.command(name="help", description="Muestra la ayuda de cómo usar el bot")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📖 Ayuda - Sistema de Tiers",
        description="Aquí tienes todos los comandos disponibles:",
        color=0x00aaff
    )
    embed.add_field(name="/set-tier", value="Establece el tier de un jugador y genera su tarjeta.", inline=False)
    embed.add_field(name="/check-tier", value="Busca y muestra el tier actual de un jugador.", inline=False)
    embed.add_field(name="/remove-tier", value="(Solo Admins) Elimina el tier de un jugador de la base de datos.", inline=False)
    embed.add_field(name="/leaderboard", value="Muestra la tabla de clasificación de los mejores jugadores.", inline=False)
    
    await interaction.response.send_message(embed=embed)

# 2. /set-tier (Modificado para guardar en JSON)
@tree.command(name="set-tier", description="Establece el tier de un jugador")
@app_commands.describe(
    nick="Nombre de usuario de Minecraft",
    tier="Rango obtenido (Ej: Low Tier 3)",
    tester="Nombre del tester que evaluó",
    region="Región del jugador (Ej: NA, EU)",
    modalidad="Modalidad jugada (Ej: SWORD, AXE)",
    prev_rank="Rango anterior (Ej: Unranked)"
)
async def set_tier(interaction: discord.Interaction, nick: str, tier: str, tester: str, region: str = "NA", modalidad: str = "SWORD", prev_rank: str = "Unranked"):
    
    # Guardar en la base de datos
    data = cargar_datos()
    data[nick] = {
        "tier": tier,
        "tester": tester,
        "region": region,
        "modalidad": modalidad,
        "prev_rank": prev_rank
    }
    guardar_datos(data)
    
    # Crear y enviar el Embed
    embed = crear_embed_tier(nick, data[nick])
    await interaction.response.send_message(embed=embed)

# 3. /check-tier
@tree.command(name="check-tier", description="Busca el tier actual de un jugador")
@app_commands.describe(nick="Nombre de usuario de Minecraft")
async def check_tier(interaction: discord.Interaction, nick: str):
    data = cargar_datos()
    
    if nick not in data:
        await interaction.response.send_message(f"❌ El jugador **{nick}** no tiene un tier registrado aún.", ephemeral=True)
        return
        
    embed = crear_embed_tier(nick, data[nick])
    await interaction.response.send_message(embed=embed)

# 4. /remove-tier (Solo Administradores)
@tree.command(name="remove-tier", description="Elimina el tier de un jugador (Solo Admins)")
@app_commands.describe(nick="Nombre de usuario de Minecraft")
@app_commands.default_permissions(administrator=True) # Esto hace que solo los Admins puedan usarlo
async def remove_tier(interaction: discord.Interaction, nick: str):
    data = cargar_datos()
    
    if nick not in data:
        await interaction.response.send_message(f"❌ El jugador **{nick}** no está en la base de datos.", ephemeral=True)
        return
        
    del data[nick]
    guardar_datos(data)
    
    await interaction.response.send_message(f"✅ Se ha eliminado correctamente el tier de **{nick}**.")

# 5. /leaderboard
@tree.command(name="leaderboard", description="Muestra la tabla de clasificación de los mejores jugadores")
async def leaderboard(interaction: discord.Interaction):
    data = cargar_datos()
    
    if not data:
        await interaction.response.send_message("📭 No hay jugadores registrados en el sistema todavía.", ephemeral=True)
        return

    # Ordenar a los jugadores alfabéticamente por su Tier
    # NOTA: Esto ordenará alfabéticamente. Si tienes tiers como "High Tier 1", "Low Tier 3", 
    # el orden podría no ser el que esperas. Para un orden perfecto, necesitarías una lista de prioridades.
    jugadores_ordenados = sorted(data.items(), key=lambda item: item[1].get('tier', 'Z'))

    descripcion = ""
    for i, (nick, info) in enumerate(jugadores_ordenados[:10], 1): # Muestra solo el Top 10
        descripcion += f"**{i}.** {nick} — `{info.get('tier', 'Sin Tier')}`\n"

    embed = discord.Embed(
        title="🏆 Leaderboard - Top 10",
        description=descripcion,
        color=0xffd700 # Color dorado
    )
    embed.set_footer(text="Vandal 🏆")
    
    await interaction.response.send_message(embed=embed)

# Iniciar el bot
client.run(TOKEN)
