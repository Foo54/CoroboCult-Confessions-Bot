import discord
from discord import app_commands
from discord.ext import commands

import typing
import logging

from corobot.channel_logger import ChannelLogger 
from corobot.config import MOD_ROLE_ID, LOG_CHANNEL_ID
from corobot.moderation_manager import ModerationDBManager, DB_PATH

logger = logging.getLogger(__name__)

@app_commands.default_permissions(moderate_members=True)
class ModerationCog(
	commands.GroupCog,
	ChannelLogger,
	ModerationDBManager,
	name="mod",
	description="Moderation commands",
):

	def __init__(self, bot, db_path, log_channel_id):
		self.bot = bot
		commands.Cog.__init__(self)
		ChannelLogger.__init__(self, log_channel_id)
		ModerationDBManager.__init__(self, db_path)

	@commands.Cog.listener()
	async def on_ready(self):
		self.fetch_log_channel(self.bot)

	async def cog_app_command_error(
		self,
		interaction: discord.Interaction,
		error: app_commands.AppCommandError
	):
		if isinstance(error, app_commands.errors.MissingRole):
			return await interaction.response.send_message(
				"You don't have the required role to use this command.", ephemeral=True
			)
		raise error

	@app_commands.command(name="log-here", description="Set the current log channel")
	@app_commands.checks.has_role(MOD_ROLE_ID)
	async def command_set_log_channel(self, interaction: discord.Interaction):
		"""Command to set the current log channel"""
		self.set_log_channel(interaction.channel)
		await interaction.response.send_message(
			f"Log channel updated {interaction.channel.mention}"
		)

	@app_commands.command(name="warn", description="Send user a warning")
	@app_commands.describe(target="Discord user", reason="Warning Message")
	@app_commands.checks.has_role(MOD_ROLE_ID)
	async def warn(
		self,
		interaction: discord.Interaction,
		target: discord.User,
		reason: typing.Optional[str] = None,
	):
		"""Anonymous warning command (logged)"""
		await interaction.response.defer(ephemeral=True)

		if not reason:
			return await interaction.followup.send(
				"Remember to provide a reason!", ephemeral=True
			)

		embed = discord.Embed(
			title="You have been warned!",
			description=reason,
			color=discord.Color.yellow(),
			timestamp=interaction.created_at,
		)

		embed.set_footer(
			text=f"Made by CoroboCult Mod Team",
			icon_url=interaction.client.user.avatar.url,
		)

		try:
			await target.send(embed=embed)

			await interaction.followup.send(
				f"User {target.mention} has been warned!", ephemeral=True
			)

		except:
			await interaction.followup.send(
				"Message could not be delivered!", ephemeral=True
			)

		finally:
			# log database
			self.log_mod_action(
				target_id=target.id,
				moderator_id=interaction.user.id,
				mod_action_type="WARN",
				reason=reason
			)

			# log mod channel
			embed.title = f"User: {target.display_name} has been warned!"
			embed.add_field(name="target", value=target.mention)
			embed.add_field(name="moderator", value=interaction.user.mention)
			await self.channel_log_embed(embed)


async def setup(bot):
	await bot.add_cog(ModerationCog(bot, DB_PATH, LOG_CHANNEL_ID))
