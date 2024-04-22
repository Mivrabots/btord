#today we makin a economey discord bot 
import discord
from discord.ext import commands
import random
import os
#import the db for the bot 
import sqlite3
from keep_alive import keep_alive
keep_alive()

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.guilds = True
intents.members = True

token = os.environ['token']


bot = commands.Bot(command_prefix='!', intents=intents)
#bot is on/status
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    await bot.change_presence(activity=discord.Game(name="with your heart"))

#connect to the db
conn = sqlite3.connect('eco.db')
cursor = conn.cursor()
# Create a table to store user balances
cursor.execute('''CREATE TABLE IF NOT EXISTS balances ( 
                    user_id INTEGER PRIMARY KEY,
                    balance INTEGER DEFAULT 0)''')
conn.commit()

# Function to get user balance
def get_balance(user_id):
    cursor.execute('SELECT balance FROM balances WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        return 0

# Function to update user balance
def update_balance(user_id, amount):
    cursor.execute('INSERT OR REPLACE INTO balances (user_id, balance) VALUES (?, ?)', (user_id, amount))
    conn.commit()

# ping command to ckeck the bot ping as a embed 
@bot.command()
async def ping(ctx):
    embed = discord.Embed(title="Pong!", description=f"Latency: {round(bot.latency * 1000)}ms", color=discord.Color.green())
    await ctx.send(embed=embed)

# command to check the balance of a user or your slef like !bal @user or !bal as a embed
@bot.command()
async def bal(ctx, user: discord.Member = None):
    if user is None:
        user = ctx.author
    balance = get_balance(user.id)
    embed = discord.Embed(title=f"{user.display_name}'s Balance", description=f"Balance: {balance} coins", color=discord.Color.blue())  
    await ctx.send(embed=embed)

#command to give coins to a user like !give @user amount as a embed
@bot.command()
async def give(ctx, member: discord.Member, amount: int):
    if amount <= 0:
        await ctx.send("You cannot give a negative or zero amount of coins.")
        return

    author_id = ctx.author.id
    author_balance = get_balance(author_id)

    if author_balance < amount:
        await ctx.send("You don't have enough coins to do that.")
        return

    member_id = member.id
    update_balance(author_id, author_balance - amount)
    update_balance(member_id, get_balance(member_id) + amount)

    embed = discord.Embed(title="Coins Transfer Successful!", description=f"{ctx.author.name} has given {member.name} {amount} coins.", color=discord.Color.green())
    await ctx.send(embed=embed)



#command to add  coins for mods to a user like !add  @user amount as a embed 
@bot.command()
async def add(ctx, member: discord.Member, amount: int):
    if amount <= 0:
        await ctx.send("You cannot add a negative or zero amount of coins.")
        return
    
    # Check if the author is a moderator
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("You must be a moderator to use this command.")
        return

    member_id = member.id
    update_balance(member_id, get_balance(member_id) + amount)

    embed = discord.Embed(title="Coins Added!", description=f"{ctx.author.name} has added {amount} coins to {member.name}.", color=discord.Color.green())
    await ctx.send(embed=embed)

#command to gamble coins like !gamble amount as a embed
@bot.command()
async def gamble(ctx, amount: int):
    if amount <= 0:
        await ctx.send("You cannot gamble a negative or zero amount of coins.")
        return

    author_id = ctx.author.id
    author_balance = get_balance(author_id)

    if author_balance < amount:
        await ctx.send("You don't have enough coins to do that.")
        return

    # Simulate a 50/50 chance of winning or losing
    win_chance = 0.90
    if random.random() < win_chance:
        update_balance(author_id, author_balance + amount)
        embed = discord.Embed(title="Gamble Won!", description=f"{ctx.author.name} has won {amount} coins!", color=discord.Color.green())
    else:
        update_balance(author_id, author_balance - amount)
        embed = discord.Embed(title="Gamble Lost!", description=f"{ctx.author.name} has lost {amount} coins.", color=discord.Color.red())
    await ctx.send(embed=embed)

#command to rob a user like !rob @user as a embed
@bot.command()
async def rob(ctx, member: discord.Member):
    if member == ctx.author:
        await ctx.send("You cannot rob yourself.")
        return

    author_id = ctx.author.id
    author_balance = get_balance(author_id)
    member_id = member.id
    member_balance = get_balance(member_id)

    if member_balance <= 0:
        await ctx.send(f"{member.name} doesn't have any coins to rob.")
        return

    # Simulate a 50/50 chance of success
    rob_chance = 0.50
    if random.random() < rob_chance:
        stolen_amount = random.randint(1, member_balance)
        update_balance(author_id, author_balance + stolen_amount)
        update_balance(member_id, member_balance - stolen_amount)
        embed = discord.Embed(title="Robbery Successful!", description=f"{ctx.author.name} has successfully robbed {member.name} and stole {stolen_amount} coins.", color=discord.Color.green())
    else:
        fine_amount = random.randint(1, author_balance)
        update_balance(author_id, author_balance - fine_amount)
        embed = discord.Embed(title="Robbery Failed!", description=f"{ctx.author.name} failed to rob {member.name} and was fined {fine_amount} coins.", color=discord.Color.red())
    await ctx.send(embed=embed)


  #command to work like !work as a embed
@bot.command()
async def work(ctx):
    author_id = ctx.author.id
    earnings = random.randint(1, 100)
    update_balance(author_id, get_balance(author_id) + earnings)
    embed = discord.Embed(title="Work Earnings", description=f"{ctx.author.name} worked and earned {earnings} coins.", color=discord.Color.green())
    await ctx.send(embed=embed)  

#command lead to the leaderboard like !leaderboard as a embed
@bot.command()
async def leaderboard(ctx):
    cursor.execute('SELECT user_id, balance FROM balances ORDER BY balance DESC')
    results = cursor.fetchall()

    if not results:
        await ctx.send("No users found in the leaderboard.")
        return

    embed = discord.Embed(title="Leaderboard", color=discord.Color.gold())
    for index, (user_id, balance) in enumerate(results, start=1):
        user = bot.get_user(user_id)
        if user:
            embed.add_field(name=f"{index}. {user.display_name}", value=f"Balance: {balance} coins", inline=False)
        else:
            embed.add_field(name=f"{index}. Unknown User", value=f"Balance: {balance} coins", inline=False)

    await ctx.send(embed=embed)

  #command shop to buy items like !shop as a embed and it have ceo role u can buy for 100m 
@bot.command()
async def shop(ctx):
    embed = discord.Embed(title="Shop", description="Available Items:", color=discord.Color.blue())
    embed.add_field(name="1. CEO Role", value="Price: 100,000,000(!buy 1)", inline=False)
    await ctx.send(embed=embed)



#vommand to remove coins from a user like !remove @user amount as a embed
@bot.command()
async def remove(ctx, member: discord.Member, amount: int):
    if amount <= 0:
        await ctx.send("You cannot remove a negative or zero amount of coins.")
        return
    
    # Check if the author is a moderator
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("You must be a moderator to use this command.")
        return

    member_id = member.id
    update_balance(member_id, get_balance(member_id) - amount)

    embed = discord.Embed(title="Coins Removed!", description=f"{ctx.author.name} has removed {amount} coins from {member.name}.", color=discord.Color.red())
    await ctx.send(embed=embed)

#command to removeall coins from a user like !removeall @user as a embed
@bot.command()
async def removeall(ctx, member: discord.Member):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("You must be a moderator to use this command.")
        return

    member_id = member.id
    update_balance(member_id, 0)

    embed = discord.Embed(title="All Coins Removed!", description=f"All coins have been removed from {member.name}.", color=discord.Color.red())
    await ctx.send(embed=embed)

#command to gamble all as a embed
@bot.command()
async def gambleall(ctx):
    author_id = ctx.author.id
    author_balance = get_balance(author_id)

    if author_balance <= 0:
        await ctx.send("You don't have any coins to gamble.")
        return

    # Simulate a 50/50 chance of winning or losing
    win_chance = 0.50
    if random.random() < win_chance:
        update_balance(author_id, author_balance * 2)
        embed = discord.Embed(title="Gamble Won!", description=f"{ctx.author.name} has won the gamble and doubled their coins!", color=discord.Color.green())
    else:
        update_balance(author_id, 0)
        embed = discord.Embed(title="Gamble Lost!", description=f"{ctx.author.name} has lost the gamble and lost all their coins.", color=discord.Color.red())
    await ctx.send(embed=embed)

#command for the stocks shop like !shopstocks as a embed
@bot.command()
async def shopstocks(ctx):
    embed = discord.Embed(title="Stocks Shop", description="Available Stocks:", color=discord.Color.blue())
    embed.add_field(name="1. Apple", value="Price: $100,000", inline=False)
    embed.add_field(name="2. Microsoft", value="Price: $1,000,000 ", inline=False)
    embed.add_field(name="3. Tesla", value="Price: $100,000,000", inline=False)
    await ctx.send(embed=embed)

#command buy to buy items like !buy 1 as a embed  like if u do !buy 1 it will buy the CEO role and give u the role u have to put the role id in the role id place
@bot.command()
async def buy(ctx, item_number: int):
    if item_number == 1:
        role_id = 1231909308120305696  # Replace with the actual role ID
        role = ctx.guild.get_role(role_id)
        if role:
            if role not in ctx.author.roles:
                author_id = ctx.author.id
                author_balance = get_balance(author_id)
                if author_balance >= 10000000:
                    update_balance(author_id, author_balance - 10000000)
                    await ctx.author.add_roles(role)
                    embed = discord.Embed(title="Purchase Successful!", description=f"{ctx.author.name} has purchased the CEO role.", color=discord.Color.green())
                else:
                    embed = discord.Embed(title="Insufficient Balance!", description=f"{ctx.author.name}, you don't have enough coins to purchase the CEO role.", color=discord.Color.red())
            else:
                embed = discord.Embed(title="Role Already Owned!", description=f"{ctx.author.name}, you already own the CEO role.", color=discord.Color.red())
        else:
            embed = discord.Embed(title="Role Not Found!", description="The CEO role was not found.", color=discord.Color.red())
    else:
        embed = discord.Embed(title="Invalid Item Number!", description="Please choose a valid item number.", color=discord.Color.red())
    await ctx.send(embed=embed)

#command to buy stuff for users likk !buyuser @users numner as a embed
@bot.command()
async def buyuser(ctx, member: discord.Member, item_number: int):
    if item_number == 1:
        role_id = 1231909308120305696  # Replace with the actual role ID
        role = ctx.guild.get_role(role_id)
        if role:
            if role not in member.roles:
                author_id = ctx.author.id
                author_balance = get_balance(author_id)
                if author_balance >= 100000000:
                    update_balance(author_id, author_balance - 100000000)
                    await member.add_roles(role)
                    embed = discord.Embed(title="Purchase Successful!", description=f"{ctx.author.name} has purchased the CEO role for {member.name}.", color=discord.Color.green())
                else:
                    embed = discord.Embed(title="Insufficient Balance!", description=f"{ctx.author.name}, you don't have enough coins to purchase the CEO role for {member.name}.", color=discord.Color.red())
            else:
                embed = discord.Embed(title="Role Already Owned!", description=f"{member.name} already has the CEO role.", color=discord.Color.red())
        else:
            embed = discord.Embed(title="Role Not Found!", description="The CEO role was not found.", color=discord.Color.red())
    else:
        embed = discord.Embed(title="Invalid Item Number!", description="Please choose a valid item number.", color=discord.Color.red())
    await ctx.send(embed=embed)

#command to ehelp like !ehelp as a embed to show the commands 
@bot.command()
async def ehelp(ctx):
    embed = discord.Embed(title="Help", description="List of available commands:", color=discord.Color.blue())
    embed.add_field(name="!bal", value="Check your balance.", inline=False)
    embed.add_field(name="!give @user amount", value="Transfer coins to another user.", inline=False)
    embed.add_field(name="!add @user amount", value="Add coins to a user.", inline=False)
    embed.add_field(name="!gamble amount", value="Gamble coins.", inline=False)
    embed.add_field(name="!rob @user", value="Rob a user.", inline=False)
    embed.add_field(name="!work", value="Work and earn coins.", inline=False)
    embed.add_field(name="!leaderboard", value="View the leaderboard.", inline=False)
    embed.add_field(name="!shop", value="View the shop.", inline=False)
    embed.add_field(name="!remove @user amount", value="Remove coins from a user.", inline=False)
    embed.add_field(name="!removeall @user", value="Remove all coins from a user.", inline=False)
    embed.add_field(name="!gambleall", value="Gamble all coins.", inline=False)
    embed.add_field(name="!shopstocks", value="View the stocks shop.", inline=False)
    embed.add_field(name="!buy [item number]", value="Buy an item from the shop.", inline=False)
    embed.add_field(name="!buyuser @user [item number]", value="Buy an item for a user from the shop.", inline=False)
    await ctx.send(embed=embed)
                


bot.run(token)
