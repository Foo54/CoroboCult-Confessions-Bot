import discord
from corobot.config import LOG_CHANNEL_ID
import typing
import logging

logger = logging.getLogger(__name__)

class ChannelLogger:
	"""Util class for logging messages to discord channels"""

	def __init__(self, initial_channel_id: typing.Optional[int] = None):
		self.log_channel_id = initial_channel_id
		self.log_channel: typing.Optional[discord.TextChannel] = None

	def fetch_log_channel(self, bot: discord.Client):
		"""Fetch and cache the target logging channel"""
		if self.log_channel_id:
			self.log_channel = bot.get_channel(self.log_channel_id)
			return

		if self.log_channel:
			logger.info(f"Moderation logging channel set to {self.log_channel.id}")
			return

		logger.warning("Moderation logging channel could not be found or set!")

	def set_log_channel(self, channel: discord.TextChannel):
		"""Update the active logging channel"""
		self.log_channel = channel
		self.log_channel_id = channel.id

	async def channel_log_embed(self, embed: discord.Embed):
		"""Log Custom Embed into log channel"""
		if self.log_channel is None:
			logger.warning("Attempted to log embed, but no log channel is set.")
		else:
			await self.log_channel.send(embed=embed)
