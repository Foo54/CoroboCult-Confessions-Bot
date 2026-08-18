import discord
from discord import app_commands
from discord.ext import commands

import os

@app_commands.default_permissions(moderate_members=True)
class CogManager(
	commands.GroupCog,
	name="cog_manager",
	description="Manage Corobot Discord Cogs",
):
	def __init__(self, bot: commands.Bot):
		self.bot = bot

	async def cog_app_command_error(
		self, interaction: discord.Interaction, error
	):
		err_message = f"An error occurred: ```{error}```"
		await interaction.response.send_message(err_message, ephemeral=True)
	
	@discord.app_commands.command(name="load", description="Load a cog by filename")
	async def load_cog(self, interaction: discord.Interaction, cog_name: str):
		await self.bot.load_extension(f"cogs.{cog_name}")
		await interaction.response.send_message(f"Successfully loaded `cogs.{cog_name}`", ephemeral=True)

	@discord.app_commands.command(name="unload", description="Unload a cog by filename")
	async def unload_cog(self, interaction: discord.Interaction, cog_name: str):
		await self.bot.unload_extension(f"cogs.{cog_name}")
		await interaction.response.send_message(f"Successfully unloaded `cogs.{cog_name}`", ephemeral=True)

	@discord.app_commands.command(name="reload", description="Reload a cog by filename")
	async def reload_cog(self, interaction: discord.Interaction, cog_name: str):
		await self.bot.reload_extension(f"cogs.{cog_name}")
		await interaction.response.send_message(f"Successfully reloaded `cogs.{cog_name}`", ephemeral=True)

	@discord.app_commands.command(name="reload-all-cogs", description="Reload all cogs")
	async def reload_all_cogs(self, interaction: discord.Interaction):
		for filename in os.listdir("./cogs"):
			cog_name = filename.removesuffix(".py")
			await self.bot.reload_extension(f"cogs.{cog_name}")

		await interaction.response.send_message(f"Successfully reloaded all cogs", ephemeral=True)

async def setup(bot: commands.Bot):
	await bot.add_cog(CogManager(bot))