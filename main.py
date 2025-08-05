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

    suspense_embed = discord.Embed(
        title="🎰 La roulette tourne...",
        description="On croise les doigts 🤞🏻 !",
        color=discord.Color.greyple()
    )
    suspense_embed.set_image(url="https://i.makeagif.com/media/11-22-2017/gXYMAo.gif")
    
    original_message = await interaction.channel.send(embed=suspense_embed)

    for i in range(10, 0, -1):
        await asyncio.sleep(1)
        suspense_embed.title = f"🎰 Tirage en cours ..."
        await original_message.edit(embed=suspense_embed)

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

    result_embed = discord.Embed(
        title="🎲 Résultat du Duel Roulette",
        description=(
            f"🎯 **Numéro tiré** : `{numero}`\n"
            f"{'🔴 Rouge' if couleur == 'rouge' else '⚫ Noir'} — "
            f"{'🔢 Pair' if parite == 'pair' else '🔢 Impair'}"
        ),
        color=discord.Color.green() if gagnant == joueur1 else discord.Color.red()
    )

    if numero in ROULETTE_NUM_IMAGES:
        result_embed.set_thumbnail(url=ROULETTE_NUM_IMAGES[numero])

    result_embed.add_field(name="👤 Joueur 1", value=f"{joueur1.mention}\nChoix : {EMOJIS[valeur_joueur1]} `{valeur_joueur1.upper()}`", inline=True)
    result_embed.add_field(name="👤 Joueur 2", value=f"{joueur2.mention}\nChoix : {EMOJIS[valeur_joueur2]} `{valeur_joueur2.upper()}`", inline=False)
    result_embed.add_field(name=" ", value="─" * 20, inline=False)
    result_embed.add_field(name="💰 Montant misé", value=f"**{montant:,}".replace(",", " ") + " kamas** par joueur", inline=False)
    result_embed.add_field(name="🏆 Gagnant", value=f"**{gagnant.mention}** remporte **{net_gain:,}".replace(",", " ") + " kamas** 💰 (après 5% de commission)", inline=False)
    result_embed.set_footer(text="🎰 Duel terminé • Bonne chance pour le prochain !")
    
    await interaction.channel.send(embed=result_embed)

    try:
        old_message_with_buttons = await interaction.channel.fetch_message(message_id_final)
        await old_message_with_buttons.delete()
    except discord.NotFound:
        pass

    try:
        await original_message.delete()
    except discord.NotFound:
        pass

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

        self.joueur2 = joueur2
        duel_data = duels.get(self.message_id_initial)
        duel_data["joueur2"] = joueur2
        
        self.rejoindre.disabled = True
        
        if self.rejoindre_croupier_button is None:
            self.rejoindre_croupier_button = discord.ui.Button(
                label="🎲 Rejoindre en tant que Croupier", style=discord.ButtonStyle.secondary, custom_id="rejoindre_croupier", row=1
            )
            self.rejoindre_croupier_button.callback = self.rejoindre_croupier
            self.add_item(self.rejoindre_croupier_button)

        embed = interaction.message.embeds[0]
        embed.title = f"Duel entre {self.joueur1.display_name} et {self.joueur2.display_name}"
        embed.set_field_at(1, name="👤 Joueur 2", value=f"{self.joueur2.mention}", inline=True)
        embed.set_field_at(2, name="Status", value="🎲 Un croupier est attendu pour lancer le duel.", inline=False)
        embed.set_footer(text="Cliquez sur le bouton pour rejoindre en tant que croupier.")
        
        role_croupier = discord.utils.get(interaction.guild.roles, name="croupier")
        contenu_ping = ""
        if role_croupier:
            contenu_ping = f"{role_croupier.mention} — Un nouveau duel est prêt ! Un croupier est attendu."
        
        await interaction.response.edit_message(
            content=contenu_ping,
            embed=embed,
            view=self,
            allowed_mentions=discord.AllowedMentions(roles=True)
        )


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
        
        self.rejoindre_croupier_button.disabled = True
        
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
            description=(
                f"{self.joueur1.mention} a choisi : {EMOJIS[valeur]} **{valeur.upper()}** \n"
                f"Montant misé : **{self.montant:,}".replace(",", " ") + " kamas** 💰"
            ),
            color=discord.Color.orange()
        )
        embed.add_field(name="👤 Joueur 1", value=f"{self.joueur1.mention}", inline=True)
        embed.add_field(name="👤 Joueur 2", value="🕓 En attente...", inline=True)
        embed.add_field(name="Status", value="🎯 En attente d'un second joueur.", inline=False)
        embed.set_footer(text=f"📋 Pari pris : {self.joueur1.display_name} - {EMOJIS[valeur]} {valeur.upper()} | Choix restant : {EMOJIS[choix_restant]} {choix_restant.upper()}")

        rejoindre_view = RejoindreView(message_id=None, joueur1=self.joueur1, type_pari=type_pari, valeur_choisie=valeur, montant=self.montant)
        
        role_membre = discord.utils.get(interaction.guild.roles, name="membre")
        contenu_ping = ""
        if role_membre:
            contenu_ping = f"{role_membre.mention} — Un nouveau duel est prêt ! Un joueur est attendu."
        
        # Envoi d'un NOUVEAU message public
        await interaction.response.send_message(
            content=contenu_ping,
            embed=embed,
            view=rejoindre_view,
            ephemeral=False,  # C'est ici que le message devient public
            allowed_mentions=discord.AllowedMentions(roles=True)
        )

        message = await interaction.original_response()
        rejoindre_view.message_id_initial = message.id

        duels[message.id] = {
            "joueur1": self.joueur1,
            "montant": self.montant,
            "type": type_pari,
            "valeur": valeur,
            "joueur2": None,
            "croupier": None,
            "message_id_initial": message.id
        }

    @discord.ui.button(label="🔴 Rouge", style=discord.ButtonStyle.danger, custom_id="pari_rouge")
    async def rouge(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.lock_in_choice(interaction, "couleur", "rouge")

    @discord.ui.button(label="⚫ Noir", style=discord.ButtonStyle.secondary, custom_id="pari_noir")
    async def noir(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.lock_in_choice(interaction, "couleur", "noir")

    @discord.ui.button(label="🔢 Pair", style=discord.ButtonStyle.primary, custom_id="pari_pair")
    async def pair(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.lock_in_choice(interaction, "pair", "pair")

    @discord.ui.button(label="🔢 Impair", style=discord.ButtonStyle.blurple, custom_id="pari_impair")
    async def impair(self, interaction: discord.Interaction, button: discord.ui.Button):
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
        await interaction.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.button(label="◀️", style=discord.ButtonStyle.secondary)
    async def prev_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.page > 0:
            self.page -= 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.button(label="▶️", style=discord.ButtonStyle.secondary)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.page < self.max_page:
            self.page += 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.button(label="⏭️", style=discord.ButtonStyle.secondary)
    async def last_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page = self.max_page
        self.update_buttons()
        await interaction.response.edit_message(embed=self.get_embed(), view=self)

@bot.tree.command(name="statsall", description="Affiche les stats de roulette à vie")
async def statsall(interaction: discord.Interaction):
    if not isinstance(interaction.channel, discord.TextChannel) or interaction.channel.name != "roulette":
        await interaction.response.send_message("❌ Cette commande ne peut être utilisée que dans le salon #roulette.", ephemeral=True)
        return

    c.execute("""
    SELECT joueur_id,
           SUM(montant) as total_mise,
           SUM(CASE WHEN gagnant_id = joueur_id THEN montant * 2 * 0.95 ELSE 0 END) as kamas_gagnes,
           SUM(CASE WHEN gagnant_id = joueur_id THEN 1 ELSE 0 END) as victoires,
           COUNT(*) as total_paris
    FROM (
        SELECT joueur1_id as joueur_id, montant, gagnant_id FROM paris
        UNION ALL
        SELECT joueur2_id as joueur_id, montant, gagnant_id FROM paris
    )
    GROUP BY joueur_id
    """)
    data = c.fetchall()

    stats = []
    for user_id, mises, kamas_gagnes, victoires, total_paris in data:
        winrate = (victoires / total_paris * 100) if total_paris > 0 else 0.0
        stats.append((user_id, mises, kamas_gagnes, victoires, winrate, total_paris))

    stats.sort(key=lambda x: x[2], reverse=True)

    if not stats:
        await interaction.response.send_message("Aucune donnée statistique disponible.", ephemeral=True)
        return

    view = StatsView(interaction, stats)
    await interaction.response.send_message(embed=view.get_embed(), view=view, ephemeral=False)

@bot.tree.command(name="mystats", description="Affiche tes statistiques de roulette personnelles.")
async def mystats(interaction: discord.Interaction):
    user_id = interaction.user.id

    c.execute("""
    SELECT joueur_id,
           SUM(montant) as total_mise,
           SUM(CASE WHEN gagnant_id = joueur_id THEN montant * 2 * 0.95 ELSE 0 END) as kamas_gagnes,
           SUM(CASE WHEN gagnant_id = joueur_id THEN 1 ELSE 0 END) as victoires,
           COUNT(*) as total_paris
    FROM (
        SELECT joueur1_id as joueur_id, montant, gagnant_id FROM paris
        UNION ALL
        SELECT joueur2_id as joueur_id, montant, gagnant_id FROM paris
    )
    WHERE joueur_id = ?
    GROUP BY joueur_id
    """, (user_id,))
    
    stats_data = c.fetchone()

    if not stats_data:
        embed = discord.Embed(
            title="📊 Tes Statistiques Roulette",
            description="❌ Tu n'as pas encore participé à un duel. Joue ton premier duel pour voir tes stats !",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    _, mises, kamas_gagnes, victoires, total_paris = stats_data
    winrate = (victoires / total_paris * 100) if total_paris > 0 else 0.0

    embed = discord.Embed(
        title=f"📊 Statistiques de {interaction.user.display_name}",
        description="Voici un résumé de tes performances à la roulette.",
        color=discord.Color.gold()
    )

    embed.add_field(name="Total misé", value=f"**{mises:,.0f}".replace(",", " ") + " kamas**", inline=False)
    embed.add_field(name=" ", value="─" * 3, inline=False)
    embed.add_field(name="Total gagné", value=f"**{kamas_gagnes:,.0f}".replace(",", " ") + " kamas**", inline=False)
    embed.add_field(name=" ", value="─" * 20, inline=False)
    embed.add_field(name="Duels joués", value=f"**{total_paris}**", inline=True)
    embed.add_field(name=" ", value="─" * 3, inline=False)
    embed.add_field(name="Victoires", value=f"**{victoires}**", inline=True)
    embed.add_field(name=" ", value="─" * 3, inline=False)
    embed.add_field(name="Taux de victoire", value=f"**{winrate:.1f}%**", inline=False)

    embed.set_thumbnail(url=interaction.user.avatar.url if interaction.user.avatar else None)
    embed.set_footer(text="Bonne chance pour tes prochains duels !")

    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="duel", description="Lancer un duel roulette avec un montant.")
@app_commands.describe(montant="Montant misé en kamas")
async def duel(interaction: discord.Interaction, montant: int):
    if not isinstance(interaction.channel, discord.TextChannel) or interaction.channel.name != "roulette":
        await interaction.response.send_message("❌ Cette commande ne peut être utilisée que dans le salon #roulette.", ephemeral=True)
        return

    if montant <= 0:
        await interaction.response.send_message("❌ Le montant doit être supérieur à 0.", ephemeral=True)
        return

    for duel_data in duels.values():
        if duel_data["joueur1"].id == interaction.user.id or (
            "joueur2" in duel_data and duel_data["joueur2"] and duel_data["joueur2"].id == interaction.user.id
        ):
            await interaction.response.send_message(
                "❌ Tu participes déjà à un autre duel. Termine-le ou utilise `/quit` pour l'annuler.",
                ephemeral=True
            )
            return

    embed = discord.Embed(
        title="🎰 Nouveau Duel Roulette",
        description=f"Choisis ton pari pour **{montant:,}".replace(",", " ") + " kamas** 💰",
        color=discord.Color.gold()
    )
    embed.set_footer(text="Ce message n'est visible que par toi.")

    view = PariView(interaction, montant)
    # Le message initial est maintenant éphémère
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

@bot.tree.command(name="quit", description="Annule le duel en cours que tu as lancé.")
async def quit_duel(interaction: discord.Interaction):
    duel_a_annuler_id = None
    for message_id, duel_data in duels.items():
        if duel_data["joueur1"].id == interaction.user.id:
            duel_a_annuler_id = message_id
            break

    if duel_a_annuler_id is None:
        await interaction.response.send_message("❌ Tu n'as aucun duel en attente à annuler.", ephemeral=True)
        return

    duel_data = duels.pop(duel_a_annuler_id)

    try:
        message_initial = await interaction.channel.fetch_message(duel_a_annuler_id)
        embed_initial = message_initial.embeds[0]
        embed_initial.color = discord.Color.red()
        embed_initial.title += " (Annulé)"
        embed_initial.description = "⚠️ Ce duel a été annulé par son créateur."
        await message_initial.edit(embed=embed_initial, view=None)
    except Exception:
        pass

    await interaction.response.send_message("✅ Ton duel a bien été annulé.", ephemeral=True)

@bot.event
async def on_ready():
    print(f"{bot.user} est prêt !")
    try:
        await bot.tree.sync()
        print("✅ Commandes synchronisées.")
    except Exception as e:
        print(f"Erreur : {e}")

keep_alive()
bot.run(token)
