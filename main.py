import os
import discord
from discord import app_commands
from discord.ext import commands
import random
import asyncio
from keep_alive import keep_alive
import sqlite3
from datetime import datetime

token = os.environ['TOKEN_BOT_DISCORD']

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)

duels = {}

EMOJIS = {
    "rouge": "🔴",
    "noir": "⚫",
    "pair": "🔢",
    "impair": "🔢"
}

COMMISSION = 0.05

ROULETTE_NUM_IMAGES = {
    1: "https://i.imgur.com/zTpdyuX.png",
    2: "https://i.imgur.com/M3a3LrX.png",
    3: "https://i.imgur.com/ORf5wZr.png",
    4: "https://i.imgur.com/GhwJ3AV.png",
    5: "https://i.imgur.com/eS5hta4.png",
    6: "https://i.imgur.com/TQ1xEmt.png",
    7: "https://i.imgur.com/jb0k8Jf.png",
    8: "https://i.imgur.com/2Ws3Jzp.png",
    9: "https://i.imgur.com/VgApiC5.png",
    10: "https://i.imgur.com/1QTNeRR.png",
    11: "https://i.imgur.com/HSeRFUd.png",
    12: "https://i.imgur.com/emiOa9O.png",
    13: "https://i.imgur.com/BEs1E1l.png",
    14: "https://i.imgur.com/LcnG4dW.png",
    15: "https://i.imgur.com/9aFuLLa.png",
    16: "https://i.imgur.com/YxBBJ5Z.png",
    17: "https://i.imgur.com/kCl5lmc.png",
    18: "https://i.imgur.com/pm5uHPN.png",
    19: "https://i.imgur.com/PRvDvpz.png",
    20: "https://i.imgur.com/mtRlaDj.png",
    21: "https://i.imgur.com/M1ZPM3j.png",
    22: "https://i.imgur.com/ePok1gw.png",
    23: "https://i.imgur.com/9UASWMq.png",
    24: "https://i.imgur.com/o0pDpF5.png",
    25: "https://i.imgur.com/fT9lPuo.png",
    26: "https://i.imgur.com/27dEGiU.png",
    27: "https://i.imgur.com/lyv1KKB.png",
    28: "https://i.imgur.com/2vVVTsS.png",
    29: "https://i.imgur.com/f5iuHiu.png",
    30: "https://i.imgur.com/mnG1wnO.png",
    31: "https://i.imgur.com/HUiMBh3.png",
    32: "https://i.imgur.com/vMJJr8K.png",
    33: "https://i.imgur.com/UN3qTKl.png",
    34: "https://i.imgur.com/7wCgXNo.png",
    35: "https://i.imgur.com/qCNitVq.png",
    36: "https://i.imgur.com/xo32lYq.png"
}

conn = sqlite3.connect("roulette_stats.db")
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS paris (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    joueur1_id INTEGER NOT NULL,
    joueur2_id INTEGER NOT NULL,
    montant INTEGER NOT NULL,
    gagnant_id INTEGER NOT NULL,
    date TIMESTAMP NOT NULL
)
""")
conn.commit()

# --- Fonctions pour la roulette ---
async def lancer_la_roulette(interaction, duel_data, message_id_final):
    joueur1 = duel_data["joueur1"]
    joueur2 = duel_data["joueur2"]
    valeur_choisie = duel_data["valeur"]
    montant = duel_data["montant"]
    type_pari = duel_data["type"]
    croupier = interaction.user

    try:
        old_message_with_buttons = await interaction.channel.fetch_message(message_id_final)
        await old_message_with_buttons.delete()
    except discord.NotFound:
        pass

    suspense_embed = discord.Embed(
        title="🎰 La roulette tourne...",
        description="On croise les doigts 🤞🏻 !",
        color=discord.Color.greyple()
    )
    suspense_embed.set_image(url="https://i.makeagif.com/media/11-22-2017/gXYMAo.gif")
    
    suspense_message = await interaction.channel.send(embed=suspense_embed)

    for i in range(5, 0, -1):
        await asyncio.sleep(1)
        suspense_embed.title = f"🎰 Tirage en cours ({i})..."
        await suspense_message.edit(embed=suspense_embed)

    await asyncio.sleep(1)

    numero = random.randint(1, 36)
    ROUGES = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
    NOIRS = {2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35}

    couleur = "rouge" if numero in ROUGES else "noir"
    parite = "pair" if numero % 2 == 0 else "impair"
    opposés = {"rouge": "noir", "noir": "rouge", "pair": "impair", "impair": "pair"}

    valeur_joueur1 = valeur_choisie
    valeur_joueur2 = opposés[valeur_joueur1]

    condition_gagnante = (
        couleur == valeur_joueur1 if type_pari == "couleur" else parite == valeur_joueur1
    )

    gagnant = joueur1 if condition_gagnante else joueur2
    net_gain = int(montant * 2 * (1 - COMMISSION))

    result_embed = suspense_message.embeds[0]
    result_embed.title = "🎲 Résultat du Duel Roulette"
    result_embed.description = (
        f"🎯 **Numéro tiré** : `{numero}`\n"
        f"{'🔴 Rouge' if couleur == 'rouge' else '⚫ Noir'} — "
        f"{'🔢 Pair' if parite == 'pair' else '🔢 Impair'}"
    )
    result_embed.color = discord.Color.green() if gagnant == joueur1 else discord.Color.red()
    if numero in ROULETTE_NUM_IMAGES:
        result_embed.set_thumbnail(url=ROULETTE_NUM_IMAGES[numero])
    result_embed.set_image(url=discord.Embed.Empty)
    
    result_embed.clear_fields()
    result_embed.add_field(name="👤 Joueur 1", value=f"{joueur1.mention} - {EMOJIS[valeur_joueur1]} `{valeur_joueur1.upper()}`", inline=True)
    result_embed.add_field(name="👤 Joueur 2", value=f"{joueur2.mention} - {EMOJIS[valeur_joueur2]} `{valeur_joueur2.upper()}`", inline=True)
    result_embed.add_field(name=" ", value="─" * 20, inline=False)
    result_embed.add_field(name="💰 Montant misé", value=f"**{montant:,}".replace(",", " ") + " kamas** par joueur", inline=False)
    result_embed.add_field(name="🏆 Gagnant", value=f"**{gagnant.mention}** remporte **{net_gain:,}".replace(",", " ") + " kamas** 💰 (après 5% de commission)", inline=False)
    result_embed.set_footer(text="🎰 Duel terminé • Bonne chance pour le prochain !")
    
    await suspense_message.edit(embed=result_embed)
    
    now = datetime.utcnow()
    try:
        c.execute(
            "INSERT INTO paris (joueur1_id, joueur2_id, montant, gagnant_id, date) VALUES (?, ?, ?, ?, ?)",
            (joueur1.id, joueur2.id, montant, gagnant.id, now)
        )
        conn.commit()
    except Exception as e:
        print("❌ Erreur insertion base:", e)

    duels.pop(duel_data["message_id_initial"], None)

# --- Vues Discord ---
class RejoindreView(discord.ui.View):
    opposés = {"rouge": "noir", "noir": "rouge", "pair": "impair", "impair": "pair"}

    def __init__(self, message_id, joueur1, type_pari, valeur_choisie, montant):
        super().__init__(timeout=None)
        self.message_id_initial = message_id
        self.joueur1 = joueur1
        self.type_pari = type_pari
        self.valeur_choisie = valeur_choisie
        self.montant = montant
        self.joueur2 = None
        self.croupier = None
        
        self.rejoindre_croupier_button = None
        self.lancer_roulette_button = None

    @discord.ui.button(label="🎯 Rejoindre le duel", style=discord.ButtonStyle.green, custom_id="rejoindre_duel")
    async def rejoindre(self, interaction: discord.Interaction, button: discord.ui.Button):
        joueur2 = interaction.user
        
        if joueur2.id == self.joueur1.id:
            await interaction.response.send_message("❌ Tu ne peux pas rejoindre ton propre duel.", ephemeral=True)
            return

        for data in duels.values():
            if data["joueur1"].id == joueur2.id or (
                "joueur2" in data and data["joueur2"] and data["joueur2"].id == joueur2.id
            ):
                await interaction.response.send_message(
                    "❌ Tu participes déjà à un autre duel. Termine-le avant d’en rejoindre un autre.",
                    ephemeral=True
                )
                return
        
        await interaction.response.defer()

        self.joueur2 = joueur2
        duel_data = duels.pop(self.message_id_initial)
        duel_data["joueur2"] = joueur2
        
        embed = discord.Embed(
            title=f"Duel entre {self.joueur1.display_name} et {self.joueur2.display_name}",
            description=f"Montant misé : **{self.montant:,}".replace(",", " ") + " kamas** 💰",
            color=discord.Color.blue()
        )
        embed.add_field(name="👤 Joueur 1", value=f"{self.joueur1.mention} - {EMOJIS[self.valeur_choisie]} `{self.valeur_choisie.upper()}`", inline=True)
        embed.add_field(name="👤 Joueur 2", value=f"{self.joueur2.mention} - {EMOJIS[self.opposés[self.valeur_choisie]]} `{self.opposés[self.valeur_choisie].upper()}`", inline=True)
        embed.add_field(name="Status", value="🎲 Un croupier est attendu pour lancer le duel.", inline=False)
        embed.set_footer(text="Cliquez sur le bouton pour rejoindre en tant que croupier.")
        
        role_croupier = discord.utils.get(interaction.guild.roles, name="croupier")
        contenu_ping = ""
        if role_croupier:
            contenu_ping = f"{role_croupier.mention} — Un nouveau duel est prêt ! Un croupier est attendu."

        new_view = RejoindreView(message_id=None, joueur1=self.joueur1, type_pari=self.type_pari, valeur_choisie=self.valeur_choisie, montant=self.montant)
        new_view.joueur2 = self.joueur2
        
        rejoindre_croupier_button = discord.ui.Button(
            label="🎲 Rejoindre en tant que Croupier", style=discord.ButtonStyle.secondary, custom_id="rejoindre_croupier", row=1
        )
        rejoindre_croupier_button.callback = new_view.rejoindre_croupier
        new_view.add_item(rejoindre_croupier_button)

        try:
            old_message = await interaction.channel.fetch_message(self.message_id_initial)
            await old_message.delete()
        except discord.NotFound:
            pass 

        new_message = await interaction.channel.send(
            content=contenu_ping,
            embed=embed,
            view=new_view,
            allowed_mentions=discord.AllowedMentions(roles=True)
        )
        
        new_view.message_id_initial = new_message.id
        duels[new_message.id] = new_view
        

    async def rejoindre_croupier(self, interaction: discord.Interaction):
        role_croupier = discord.utils.get(interaction.guild.roles, name="croupier")

        if not role_croupier or role_croupier not in interaction.user.roles:
            await interaction.response.send_message("❌ Tu n'as pas le rôle de `croupier` pour rejoindre ce duel.", ephemeral=True)
            return

        if self.croupier:
            await interaction.response.send_message(f"❌ Un croupier ({self.croupier.mention}) a déjà rejoint le duel.", ephemeral=True)
            return
            
        self.croupier = interaction.user
        duel_data = duels.get(self.message_id_initial)
        duel_data["croupier"] = self.croupier

        embed = interaction.message.embeds[0]
        
        embed.set_field_at(2, name="Status", value=f"✅ Prêt à jouer ! Croupier : {self.croupier.mention}", inline=False)
        embed.set_footer(text="Le croupier peut lancer la roulette.")
        
        for item in self.children:
            if item.custom_id == "rejoindre_croupier":
                item.disabled = True
                break
        
        if self.lancer_roulette_button is None:
            self.lancer_roulette_button = discord.ui.Button(
                label="🎰 Lancer la Roulette", style=discord.ButtonStyle.success, custom_id="lancer_roulette", row=0
            )
            self.lancer_roulette_button.callback = self.lancer_roulette
            self.add_item(self.lancer_roulette_button)
        
        await interaction.response.edit_message(content="", embed=embed, view=self)


    async def lancer_roulette(self, interaction: discord.Interaction):
        duel_data = duels.get(self.message_id_initial)
        
        if not duel_data or not duel_data.get("joueur2"):
            await interaction.response.send_message("❌ Le duel n'est pas prêt. Il faut deux joueurs.", ephemeral=True)
            return
        
        if interaction.user.id != self.croupier.id:
            await interaction.response.send_message("❌ Seul le croupier peut lancer la roulette.", ephemeral=True)
            return
        
        await interaction.response.defer()

        for item in self.children:
            item.disabled = True
        await interaction.edit_original_response(view=self)
        
        await lancer_la_roulette(interaction, duel_data, interaction.message.id)

    async def on_timeout(self):
        try:
            message = await self.message.channel.fetch_message(self.message_id_initial)
            for item in self.children:
                item.disabled = True
            embed = message.embeds[0]
            embed.title += " (Annulé)"
            embed.description = "⚠️ Ce duel a expiré car personne ne l'a rejoint à temps."
            embed.color = discord.Color.red()
            await message.edit(embed=embed, view=self)
            duels.pop(self.message_id_initial, None)
        except discord.NotFound:
            pass


class PariView(discord.ui.View):
    def __init__(self, interaction, montant):
        super().__init__(timeout=180)
        self.interaction = interaction
        self.montant = montant
        self.joueur1 = interaction.user

    async def lock_in_choice(self, interaction, type_pari, valeur):
        if interaction.user.id != self.joueur1.id:
            await interaction.response.send_message("❌ Seul le joueur qui a lancé le duel peut choisir le pari.", ephemeral=True)
            return

        opposés = {"rouge": "noir", "noir": "rouge", "pair": "impair", "impair": "pair"}
        choix_restant = opposés[valeur]

        embed = discord.Embed(
            title=f"🎰 Duel Roulette en attente de joueur",
            description=f"Montant misé : **{self.montant:,}".replace(",", " ") + " kamas** 💰",
            color=discord.Color.orange()
        )
        embed.add_field(name="👤 Joueur 1", value=f"{self.joueur1.mention} - {EMOJIS[valeur]} `{valeur.upper()}`", inline=True)
        embed.add_field(name="👤 Joueur 2", value="🕓 En attente...", inline=True)
        embed.add_field(name="Status", value="🎯 En attente d'un second joueur.", inline=False)
        embed.set_footer(text=f"📋 Pari pris : {self.joueur1.display_name} - {EMOJIS[valeur]} {valeur.upper()} | Choix restant : {EMOJIS[choix_restant]} {choix_restant.upper()}")

        rejoindre_view = RejoindreView(message_id=None, joueur1=self.joueur1, type_pari=type_pari, valeur_choisie=valeur, montant=self.montant)
        
        role_membre = discord.utils.get(interaction.guild.roles, name="membre")
        contenu_ping = ""
        if role_membre:
            contenu_ping = f"{role_membre.mention} — Un nouveau duel est prêt ! Un joueur est attendu."
        
        message = await interaction.followup.send(
            content=contenu_ping,
            embed=embed,
            view=rejoindre_view,
            ephemeral=False,
            allowed_mentions=discord.AllowedMentions(roles=True)
        )
        
        rejoindre_view.message_id_initial = message.id
        duels[message.id] = rejoindre_view

    @discord.ui.button(label="🔴 Rouge", style=discord.ButtonStyle.danger, custom_id="pari_rouge")
    async def rouge(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        await self.lock_in_choice(interaction, "couleur", "rouge")

    @discord.ui.button(label="⚫ Noir", style=discord.ButtonStyle.secondary, custom_id="pari_noir")
    async def noir(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        await self.lock_in_choice(interaction, "couleur", "noir")

    @discord.ui.button(label="🔢 Pair", style=discord.ButtonStyle.primary, custom_id="pari_pair")
    async def pair(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        await self.lock_in_choice(interaction, "pair", "pair")

    @discord.ui.button(label="🔢 Impair", style=discord.ButtonStyle.blurple, custom_id="pari_impair")
    async def impair(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        await self.lock_in_choice(interaction, "pair", "impair")

class StatsView(discord.ui.View):
    def __init__(self, ctx, entries, page=0):
        super().__init__(timeout=120)
        self.ctx = ctx
        self.entries = entries
        self.page = page
        self.entries_per_page = 10
        self.max_page = (len(entries) - 1) // self.entries_per_page

        self.update_buttons()

    def update_buttons(self):
        self.first_page.disabled = self.page == 0
        self.prev_page.disabled = self.page == 0
        self.next_page.disabled = self.page == self.max_page
        self.last_page.disabled = self.page == self.max_page

    def get_embed(self):
        embed = discord.Embed(title="📊 Statistiques Roulette", color=discord.Color.gold())
        start = self.page * self.entries_per_page
        end = start + self.entries_per_page
        slice_entries = self.entries[start:end]

        if not slice_entries:
            embed.description = "Aucune donnée à afficher."
            return embed

        description = ""
        for i, (user_id, mises, kamas_gagnes, victoires, winrate, total_paris) in enumerate(slice_entries):
            rank = self.page * self.entries_per_page + i + 1
            description += (
                f"**#{rank}** <@{user_id}> — "
                f"<:emoji_2:1399792098529509546> **Misés** : **`{mises:,.0f}`".replace(",", " ") + " kamas** | "
                f"<:emoji_2:1399792098529509546> **Gagnés** : **`{kamas_gagnes:,.0f}`".replace(",", " ") + " kamas** | "
                f"**🎯Winrate** : **`{winrate:.1f}%`** (**{victoires}**/**{total_paris}**)\n"
            )
            if i < len(slice_entries) - 1:
                description += "─" * 20 + "\n"

        embed.description = description
        embed.set_footer(text=f"Page {self.page + 1}/{self.max_page + 1}")
        return embed

    @discord.ui.button(label="⏮️", style=discord.ButtonStyle.secondary)
    async def first_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page = 0
        self.update_buttons()
