import typing
import discord
from discord.ext import tasks
from discord import app_commands

from config import *

from sql import Database, MacroManager
_confessions = Database("data/confessions.db")
confessions_macro_manager = MacroManager("data/sql_macros.json", _confessions)

@tasks.loop(minutes=5)
async def check_to_do():
	_confessions.save()

confessions_group = app_commands.Group(
  name="confessions",
  description="Anonymous Confession Commands",
  guild_ids=[SERVER_ID]
)

confessions_database_group = app_commands.Group(
  name="database",
  description="Access and Modify Confession Database",
  guild_ids=[SERVER_ID]
)

confessions_group.add_command(confessions_database_group)

@confessions_database_group.command(name = "create-macro", description="Create a new macro")
@app_commands.checks.has_role(MOD_ROLE_ID)
@app_commands.describe(
	name = "Name of the macro, max 20 characters",
	code = "Code of the macro"
)
async def confessions_database__add_macro (interaction: discord.Interaction, name: str, code: str):
	await interaction.response.defer(ephemeral=True)
	confessions_macro_manager.create_macro(name = name, author_id = interaction.user.id, code = code)
	await interaction.followup.send("Macro successfully created!")

@confessions_database__add_macro.error
async def confessions_database__add_macro__error (interaction: discord.Interaction, error: Exception):
	if isinstance(error, app_commands.MissingRole):
		return await interaction.response.send_message("Insufficient Permissions", ephemeral=True)
	if interaction.response.is_done():
		return await interaction.followup.send("Command failed with the following message: " + str(error))
	await interaction.response.send_message("Command failed with the following message: " + str(error), ephemeral=True)

@confessions_database_group.command(name = "view-macro", description="View all macros, or get data on a specific one")
@app_commands.checks.has_role(MOD_ROLE_ID)
@app_commands.describe(name = "Get info on a specific macro")
async def confessions_database__view_macros (interaction: discord.Interaction, name: typing.Optional[str] = None):
	if name is None:
		output = "\n".join(f"`{row["name"]}` - <@{row["author_id"]}>" for row in confessions_macro_manager.get_macros())
		embed = discord.Embed(
			title="Macros: " + ("all" if name is None else name),
			description= output,
			color=int(BOT_COLOR, 16)
		).set_footer(text = f"Made by CoroboCult Mod Team", icon_url = bot.user.avatar.url) # pyright: ignore[reportOptionalMemberAccess]
		await interaction.followup.send(embed = embed)
	else:
		pass

@confessions_database__view_macros.autocomplete('name')
async def command_autocomplete_view_macros(interaction: discord.Interaction, current: str) -> typing.List[app_commands.Choice[str]]:
	return [app_commands.Choice(name = value["name"], value = value["name"])
    for value in confessions_macro_manager.get_macros() if current in value["name"]][:25]

@confessions_database__view_macros.error
async def confessions_database__view_macros__error (interaction: discord.Interaction, error: Exception):
	if isinstance(error, app_commands.MissingRole):
		return await interaction.response.send_message("Insufficient Permissions", ephemeral=True)
	if interaction.response.is_done():
		return await interaction.followup.send("Command failed with the following message: " + str(error))
	await interaction.response.send_message("Command failed with the following message: " + str(error), ephemeral=True)
