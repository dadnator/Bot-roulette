import os
import discord
from discord import app_commands
from discord.ext import commands
from keep_alive import keep_alive
import random
import asyncio


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

class RejoindreView(discord.ui.View):
    opposés = {"rouge": "noir", "noir": "rouge", "pair": "impair", "impair": "pair"}

    def __init__(self, message_id, joueur1, type_pari, valeur_choisie, montant):
        super().__init__(timeout=300)
        self.message_id = message_id
        self.joueur1 = joueur1
        self.type_pari = type_pari
        self.valeur_choisie = valeur_choisie
        self.montant = montant
        self.joueur2 = None

    @discord.ui.button(label="🎯 Rejoindre le duel", style=discord.ButtonStyle.green, custom_id="rejoindre_duel")
    async def rejoindre(self, interaction: discord.Interaction, button: discord.ui.Button):
        joueur2 = interaction.user

        if joueur2.id == self.joueur1.id:
            await interaction.response.send_message("❌ Tu ne peux pas rejoindre ton propre duel.", ephemeral=True)
            return

        duel_data = duels.get(self.message_id)
        if duel_data is None:
            await interaction.response.send_message("❌ Ce duel n'existe plus ou a déjà été joué.", ephemeral=True)
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
        duel_data["joueur2"] = joueur2

        self.rejoindre.disabled = True

        self.lancer_roulette_button = discord.ui.Button(
            label="🎰 Lancer la Roulette", style=discord.ButtonStyle.success, custom_id="lancer_roulette"
        )
        self.lancer_roulette_button.callback = self.lancer_roulette
        self.add_item(self.lancer_roulette_button)

        embed = interaction.message.embeds[0]
        embed.set_field_at(
            index=1,
            name="👤 Joueur 2",
            value=f"{joueur2.mention}\nChoix : {EMOJIS[self.opposés[self.valeur_choisie]]} `{self.opposés[self.valeur_choisie].upper()}`",
            inline=True
        )
        embed.description = (
            f"{self.joueur1.mention} a choisi : {EMOJIS[self.valeur_choisie]} **{self.valeur_choisie.upper()}** ({self.type_pari})\n"
            f"Montant : **{self.montant:,} kamas** 💰\n\n"
            f"{joueur2.mention} a rejoint le duel ! Un membre du groupe `croupier` peut lancer la roulette."
        )
        embed.color = discord.Color.blue()

        await interaction.response.edit_message(embed=embed, view=self)


    async def lancer_roulette(self, interaction: discord.Interaction):
        role_croupier_found = False
        for role in interaction.user.roles:
            if role.name == "croupier":
                role_croupier_found = True
                break

        if not role_croupier_found:
            await interaction.response.send_message("❌ Seuls les membres du groupe `croupier` peuvent lancer la roulette.", ephemeral=True)
            return

        if self.joueur2 is None:
            await interaction.response.send_message("❌ Le joueur 2 n'a pas encore rejoint le duel.", ephemeral=True)
            return

        self.lancer_roulette_button.disabled = True
        await interaction.response.edit_message(view=self)

        original_message = interaction.message

        suspense_embed = discord.Embed(
            title="🎰 La roulette tourne...",
            description="On croise les doigts 🤞🏻  !",
            color=discord.Color.greyple()
        )
        suspense_embed.set_image(url="https://i.makeagif.com/media/11-22-2017/gXYMAo.gif")

        await original_message.edit(embed=suspense_embed, view=None)

        # --- Début de la section corrigée pour la boucle et les prints ---
        print("Avant la boucle de décompte.")
        for i in range(10, 0, -1): # La boucle s'exécute 10 fois (de 10 à 1 inclus)
            print(f"Décompte: {i}") # Ce print s'exécute à chaque itération
            await asyncio.sleep(1)
            suspense_embed.title = f"🎰 Tirage en cours ..." # J'ajoute le décompte ici pour un meilleur feedback
            await original_message.edit(embed=suspense_embed)
        print("Après la boucle de décompte. La boucle est terminée.") # Ce print s'exécute UNE SEULE FOIS après la boucle
        # --- Fin de la section corrigée ---


        # 3. Tirage de la roulette et détermination du gagnant
        # Modification ici: Tirage entre 1 et 36 (exclut le 0)
        numero = random.randint(1, 36)
        ROUGES = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
        NOIRS = {2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35}

        # Modification ici: Plus de "vert" pour la couleur
        couleur = "rouge" if numero in ROUGES else "noir"
        # Modification ici: Plus de "aucune" pour la parité (le 0 étant exclu)
        parite = "pair" if numero % 2 == 0 else "impair"

        valeur_joueur1 = self.valeur_choisie
        valeur_joueur2 = self.opposés[valeur_joueur1]

        if self.type_pari == "couleur":
            condition_gagnante = couleur == valeur_joueur1
        else: # type_pari == "pair"
            condition_gagnante = parite == valeur_joueur1

        gagnant = self.joueur1 if condition_gagnante else self.joueur2


         # 4. Message de résultat final
        result_embed = discord.Embed(
            title="🎲 Résultat du Duel Roulette",
            description=(
                f"🎯 **Numéro tiré** : `{numero}`\n"
                f"{'🔴 Rouge' if couleur == 'rouge' else '⚫ Noir'} — "
                f"{'🔢 Pair' if parite == 'pair' else '🔢 Impair'}"
            ),
            color=discord.Color.green() if gagnant == self.joueur1 else discord.Color.red()
        )

        result_embed.add_field(
            name="👤 Joueur 1",
            value=f"{self.joueur1.mention}\nChoix : {EMOJIS[valeur_joueur1]} `{valeur_joueur1.upper()}`",
            inline=True
        )
        result_embed.add_field(
            name="👤 Joueur 2",
            value=f"{self.joueur2.mention}\nChoix : {EMOJIS[valeur_joueur2]} `{valeur_joueur2.upper()}`",
            inline=True
        )
        # Champ avec des tirets pour créer une ligne de séparation
        # ATTENTION : La variable pour l'embed ici DOIT être `result_embed`, pas `result`
        result_embed.add_field(name=" ", value="─" * 20, inline=False) # Utilise des tirets '─' (barre horizontale légère)
        net_gain = int(self.montant * 2 * (1 - COMMISSION))
        
        result_embed.add_field(
            name="🏆 Gagnant",
            value=f"**{gagnant.mention}** remporte **{net_gain:,} kamas** 💰 (après 5% de commission)",
            inline=False
        )
        result_embed.set_footer(text="🎰 Duel terminé • Bonne chance pour le prochain !")

        await original_message.edit(embed=result_embed, view=None)

        duels.pop(self.message_id, None)

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
            title="🎰 Duel Roulette",
           description=(
    f"{self.joueur1.mention} a choisi : {EMOJIS[valeur]} **{valeur.upper()}** ({type_pari})\n"
    f"Montant misé : **{self.montant:,} kamas** 💰\n"
    f"Commission de 5% par joueur appliquée (Total gagné : **{int(self.montant * 2 * (1 - COMMISSION)):,} kamas**)"
),

            color=discord.Color.orange()
        )
        embed.add_field(name="👤 Joueur 1", value=f"{self.joueur1.mention} - {EMOJIS[valeur]} {valeur}", inline=True)
        embed.add_field(name="👤 Joueur 2", value="🕓 En attente...", inline=True)
        embed.set_footer(text=f"📋 Pari pris : {self.joueur1.display_name} - {EMOJIS[valeur]} {valeur.upper()} | Choix restant : {EMOJIS[choix_restant]} {choix_restant.upper()}")

        await interaction.response.edit_message(embed=embed, view=None)

        rejoindre_view = RejoindreView(message_id=None, joueur1=self.joueur1, type_pari=type_pari, valeur_choisie=valeur, montant=self.montant)

        message = await interaction.channel.send(embed=embed, view=rejoindre_view)

        rejoindre_view.message_id = message.id

        duels[message.id] = {
            "joueur1": self.joueur1,
            "montant": self.montant,
            "type": type_pari,
            "valeur": valeur,
            "joueur2": None
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

@bot.tree.command(name="duel", description="Lancer un duel roulette avec un montant.")
@app_commands.describe(montant="Montant misé en kamas")
async def duel(interaction: discord.Interaction, montant: int):
    # Vérifie que la commande est utilisée dans un salon texte nommé "roulette"
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
        description=f"{interaction.user.mention} veut lancer un duel pour **{montant:,} kamas** 💰",
        color=discord.Color.gold()
    )
    embed.add_field(name="Choix du pari", value="Clique sur un bouton ci-dessous : 🔴 Rouge / ⚫ Noir / 🔢 Pair / 🔢 Impair", inline=False)

    view = PariView(interaction, montant)
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)



@bot.tree.command(name="quit", description="Annule le duel en cours que tu as lancé.")
async def quit_duel(interaction: discord.Interaction):
    duel_a_annuler = None
    for message_id, duel_data in duels.items():
        if duel_data["joueur1"].id == interaction.user.id:
            duel_a_annuler = message_id
            break

    if duel_a_annuler is None:
        await interaction.response.send_message("❌ Tu n'as aucun duel en attente à annuler.", ephemeral=True)
        return

    duels.pop(duel_a_annuler)

    try:
        channel = interaction.channel
        message = await channel.fetch_message(duel_a_annuler)
        embed = message.embeds[0]
        embed.color = discord.Color.red()
        embed.title += " (Annulé)"
        embed.description = "⚠️ Ce duel a été annulé par son créateur."
        await message.edit(embed=embed, view=None)
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
