#start error logging
import tracemalloc
tracemalloc.start()

from config import TOKEN
from discord_bot import *

if __name__ == "__main__":
	bot.run(TOKEN)
