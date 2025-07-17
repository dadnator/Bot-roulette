import os
import discord
from discord.ext import commands
import random
import asyncio

TOKEN = os.environ['TOKEN_BOT_DISCORD']

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)

duels = {}
COMMISSION = 0.05

class RejoindreView(discord.ui.View):
    opposites = {"rouge": "noir", "noir": "rouge", "pair": "impair", "impair": "pair"}

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

        # Vérifier si joueur2 est déjà dans un duel
        for data in duels.values():
            if data["joueur1"].id == joueur2.id or ("joueur2" in data and data["joueur2"] and data["joueur2"].id == joueur2.id):
                await interaction.response.send_message("❌ Tu participes déjà à un autre duel. Termine-le avant d’en rejoindre un autre.", ephemeral=True)
                return

        self.joueur2 = joueur2
        duel_data["joueur2"] = joueur2
        self.rejoindre.disabled = True

        self.lancer_roulette_button = discord.ui.Button(label="🎰 Lancer la Roulette", style=discord.ButtonStyle.success, custom_id="lancer_roulette")
        self.lancer_roulette_button.callback = self.lancer_roulette
        self.add_item(self.lancer_roulette_button)

        embed = interaction.message.embeds[0]
        embed.set_field_at(1, name="👤 Joueur 2", value=f"{joueur2.mention}\nChoix : {self.opposites[self.valeur_choisie].capitalize()}", inline=True)
        embed.description = (
            f"{self.joueur1.mention} a choisi : **{self.valeur_choisie.upper()}** ({self.type_pari})\n"
            f"Montant : **{self.montant:,} kamas** 💰\n\n"
            f"{joueur2.mention} a rejoint le duel ! Un membre du groupe `croupier` peut lancer la roulette."
        )
        embed.color = discord.Color.blue()

        await interaction.response.edit_message(embed=embed, view=self)

    async def lancer_roulette(self, interaction: discord.Interaction):
        if not any(role.name == "croupier" for role in interaction.user.roles):
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
            description="On croise les doigts 🤞🏿 !",
            color=discord.Color.greyple()
        )
        suspense_embed.set_image(url="https://i.makeagif.com/media/11-22-2017/gXYMAo.gif")
        await original_message.edit(embed=suspense_embed, view=None)

        for _ in range(10):
            await asyncio.sleep(1)

        numero = random.randint(1, 36)
        rouges = {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}
        couleur = "rouge" if numero in rouges else "noir"
        parite = "pair" if numero % 2 == 0 else "impair"

        valeur_joueur1 = self.valeur_choisie
        valeur_joueur2 = self.opposites[valeur_joueur1]

        if self.type_pari == "couleur":
            gagnant = self.joueur1 if couleur == valeur_joueur1 else self.joueur2
        else:
            gagnant = self.joueur1 if parite == valeur_joueur1 else self.joueur2

        net_gain = int(self.montant * 2 * (1 - COMMISSION))

        result_embed = discord.Embed(
            title="🎲 Résultat du Duel Roulette",
            description=f"🎯 Numéro tiré : `{numero}`\n"
                        f"{'🔴 Rouge' if couleur == 'rouge' else '⚫ Noir'} — "
                        f"{'🔢 Pair' if parite == 'pair' else '🔢 Impair'}",
            color=discord.Color.green() if gagnant == self.joueur1 else discord.Color.red()
        )
        result_embed.add_field(name="👤 Joueur 1", value=f"{self.joueur1.mention}\nChoix : **{valeur_joueur1.upper()}**", inline=True)
        result_embed.add_field(name="👤 Joueur 2", value=f"{self.joueur2.mention}\nChoix : **{valeur_joueur2.upper()}**", inline=True)
        result_embed.add_field(name=" ", value="─" * 20, inline=False)
        result_embed.add_field(name="🏆 Gagnant", value=f"**{gagnant.mention}** remporte **{net_gain:,} kamas** 💰 (après 5% de commission)", inline=False)
        result_embed.set_footer(text="🎰 Duel terminé • Bonne chance pour le prochain !")

        await original_message.edit(embed=result_embed, view=None)
        duels.pop(self.message_id, None)

class PariView(discord.ui.View):
    def __init__(self, interaction, montant):
        super().__init__(timeout=180)
        self.interaction = interaction
        self.montant = montant
        self.joueur1 = interaction.user

    async def send_duel_ping(self, channel):
        role_membre = discord.utils.get(channel.guild.roles, name="membre")
        role_croupier = discord.utils.get(channel.guild.roles, name="croupier")
        mentions = ""
        if role_membre:
            mentions += f"{role_membre.mention} "
        if role_croupier:
            mentions += f"{role_croupier.mention}"
        await channel.send(mentions)

    @discord.ui.button(label="Rouge", style=discord.ButtonStyle.red, custom_id="parier_rouge")
    async def parier_rouge(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.choisir_pari(interaction, "couleur", "rouge")

    @discord.ui.button(label="Noir", style=discord.ButtonStyle.grey, custom_id="parier_noir")
    async def parier_noir(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.choisir_pari(interaction, "couleur", "noir")

    @discord.ui.button(label="Pair", style=discord.ButtonStyle.blurple, custom_id="parier_pair")
    async def parier_pair(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.choisir_pari(interaction, "parite", "pair")

    @discord.ui.button(label="Impair", style=discord.ButtonStyle.blurple, custom_id="parier_impair")
    async def parier_impair(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.choisir_pari(interaction, "parite", "impair")

    async def choisir_pari(self, interaction, type_pari, valeur):
        if interaction.user.id != self.joueur1.id:
            await interaction.response.send_message("❌ Seul le joueur qui a lancé le duel peut choisir le pari.", ephemeral=True)
            return

        # Crée l'embed du duel
        embed = discord.Embed(
            title="🎰 Duel Roulette",
            description=(
                f"{self.joueur1.mention} a choisi : **{valeur.upper()}** ({type_pari})\n"
                f"Montant : **{self.montant:,} kamas** 💰\n\n"
                f"En attente d'un adversaire..."
            ),
            color=discord.Color.orange()
        )
        embed.add_field(name="👤 Joueur 1", value=f"{self.joueur1.mention}\nChoix : **{valeur.upper()}**", inline=True)
        embed.add_field(name="👤 Joueur 2", value="En attente...", inline=True)

        message = await interaction.channel.send(embed=embed, view=RejoindreView(interaction.message.id if interaction.message else 0, self.joueur1, type_pari, valeur, self.montant))

        duels[message.id] = {
            "joueur1": self.joueur1,
            "type_pari": type_pari,
            "valeur_choisie": valeur,
            "montant": self.montant,
            "joueur2": None,
        }

        await self.send_duel_ping(interaction.channel)
        await interaction.response.edit_message(content="Duel lancé !", view=None)

@bot.command()
async def duel(ctx, montant: int):
    if montant <= 0:
        await ctx.send("Le montant doit être supérieur à 0.")
        return
    view = PariView(ctx.interaction if ctx.interaction else ctx.message, montant)
    await ctx.send(f"{ctx.author.mention}, choisissez votre pari :", view=view)

keep_alive()
bot.run(TOKEN)
