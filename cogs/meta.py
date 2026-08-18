import discord
from discord import app_commands
from discord.ext import commands
import typing
from corobot.config import BOT_COLOR


class MetaCog(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@app_commands.command(name="ping", description="pong")
	async def ping(self, interaction: discord.Interaction):
		await interaction.response.send_message("pong")

	@app_commands.command(name="meow", description="meow")
	async def meow(self, interaction: discord.Interaction):
		await interaction.response.send_message("meow")

	@app_commands.command(
		name="help", description="Get a list of commands or info on a single command"
	)
	@app_commands.rename(cmd="command")
	@app_commands.describe(cmd="Get info on a specific command")
	async def _help(
		self, interaction: discord.Interaction, cmd: typing.Optional[str] = None
	):
		output_lines = list()
		cmd_list = list(self.bot.tree.walk_commands(guild=interaction.guild))

		if cmd is None:
			title = "Help all" 
			output_lines.append("List of Commands\n```")
			output_lines.extend(
				f"/{command.qualified_name} - {command.description}"
					for command in cmd_list
			)
			output_lines.append("```")
		
		else:
			title = f"Help {cmd}"
			command = next(
				(command for command in cmd_list if command.qualified_name == cmd),
				None
			)

			if command is None:
				return await interaction.response.send_message(
					"Please enter a valid cmd (use /help to find them)",
					ephemeral = True
				)

			output_lines.append(
				f"`/{command.qualified_name}`\n> {command.description}"
			)

			if isinstance(command, app_commands.commands.Group):
				output_lines.append("Sub-commands:\n```")
				output_lines.extend(
					f"- {subcommand.name} > {subcommand.description}"
						for subcommand in command.commands
				)
				
			else:
				output_lines.append("Parameters:\n```")
				for parameter in command.parameters:
					if parameter.required:
						output_lines.append(
							f"- <{parameter.display_name}> > {parameter.description}"
						)
					else:
						output_lines.append(
							f"- [{parameter.display_name}] > {parameter.description}"
						)

			output_lines += "```"

		embed = discord.Embed(
			title=title,
			description="\n".join(output_lines),
			color=int(BOT_COLOR, 16),
		)
		
		embed.set_footer(
			text="Made by CoroboCult Mod Team",
			icon_url=interaction.client.user.avatar.url,
		)  # pyright: ignore[reportOptionalMemberAccess]

		await interaction.response.send_message(embed=embed)

	@_help.autocomplete("cmd")
	async def command_autocomplete(
		self, interaction: discord.Interaction, current: str
	) -> typing.List[app_commands.Choice[str]]:
		return (
			[
				app_commands.Choice(
					name=command.qualified_name, value=command.qualified_name
				)
				for command in self.bot.tree.walk_commands(guild=interaction.guild)
				if current.upper() in command.qualified_name.upper()
			][:25]
			if len(current) > 0
			else [
				app_commands.Choice(
					name=command.qualified_name, value=command.qualified_name
				)
				for command in self.bot.tree.walk_commands(guild=interaction.guild)
			][:25]
		)

async def setup(bot):
	await bot.add_cog(MetaCog(bot))
