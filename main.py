import discord
from discord.ext import commands 
from discord.commands import slash_command
from discord import guild, permission
from discord import colour
from discord import emoji
from discord.components import SelectOption
from discord.ext import commands
from discord.ui import Button,View

#for generating and sending code through mail
from random import randint, randrange
from redmail import gmail

#importing all_student_data
from studentdata import all_student_data 
from studentdata import branch

#importing numpy for storing dictionary
import numpy as np

#mu_verify_client email id credentials
gmail.user_name='muverifybot@gmail.com'
gmail.password=''

#prefix command
client = commands.Bot(command_prefix=commands.when_mentioned_or('.'), intents = discord.Intents.all())



#all_guild_ids stores all guild_ids in which the client is present
global all_guild_ids 
all_guild_ids = []

#client goes through this at first
@client.event
async def on_ready():
    print("bot started and is running")
    for guild in client.guilds: 
        all_guild_ids.append(guild.id) #command  which helps in storing all guild ids
    print(all_guild_ids)


#setup
@client.command()
async def setup(ctx):
    #creates role named verified members
    await ctx.guild.create_role(name='verified students',color=discord.Color.blue(),)
    

    #setup message
    embed=discord.Embed(
        title="MU VERIFY Bot",
        description="Hello!!\nThank you for choosing MU VERIFY client \nPlease select which students do u want to join in your server by clicking on buttons below",
        color=discord.Color.blue() 
    )

    #creates buttons and roles
    class RoleButton(discord.ui.Button):

        def __init__(self,temp_branch):
                
                super().__init__(
                    label=branch[i-1],
                    style=discord.ButtonStyle.secondary,
                    custom_id=temp_branch
                )

        async def callback(self, interaction: discord.Interaction):
            i=0
            if(self.style==discord.ButtonStyle.primary):
                #commands to delete role
                #member = await ctx.guild.fetch_roles
                #await member.remove_roles(self.custom_id)
                #await ctx.guild.delete(self.custom_id)
                self.style=discord.ButtonStyle.secondary
                i=1
            
            
            if(self.style==discord.ButtonStyle.secondary and i==0):
                tempbranch=[self.custom_id]
                #guild_branches.setdefault(ctx.guild_id,[]).append(self.custom_id)

                #code to store branches selected by professor based on guild id
                try:
                    p=guild_branches[ctx.guild.id]
                except KeyError:
                    guild_branches[ctx.guild.id]=[]
                p=guild_branches[ctx.guild.id]
                p.extend(tempbranch)
                guild_branches[ctx.guild.id]=p
    
                #creates role with name as the branch clicked by user
                await ctx.guild.create_role(name=self.custom_id,color=discord.Color.yellow(),)

                self.style=discord.ButtonStyle.primary
                print(guild_branches)
                await interaction.response.edit_message(embed=embed,view=view)

    #store buttons in view
    view =View()
    for i in range(1, len(branch)+1):
        view.add_item(RoleButton(branch[i-1]))
        

    #print buttons and embed
    await ctx.send(embed=embed,view=view)






#verification part

#message sent to dm when a person joins server
def verify_msg(guildname):
    return "To verify yourself on {}, **please enter your student id(not email id).".format(guildname)

#sends a 6 digit otp code through mail id entered by student
def verify_code(emailid,student_id):
    x=randint(100001,999999)
    gmail.send(
            subject="Verification code",
            receivers=str(emailid),
            text="your code is"+str(x),
            html="<h3>Your Code is </h3>"+str(x))
    user_id_otp[student_id]=x


#when a member joins a guild the bot sends a dm (refer verify_msg) and it assignes user_id_guild
@client.event
async def on_member_join(member):
    await member.send(verify_msg(member.guild))
    print(member.guild.id,member.id)
    temp_guild_id=[member.guild.id]
    try:
        p=user_id_guild[member.id]
    except KeyError:
        user_id_guild[member.id]=[]
    p=user_id_guild[member.id]
    p.extend(temp_guild_id)
    user_id_guild[member.id]=p    

#when a member leaves a guild the bot removes their name from blacklist
@client.event
async def on_member_remove(member):
        for i in guild_id_blacklist_studentid[member.guild.id]:
            if (member.nick == i):
                del guild_id_blacklist_studentid[member.guild.id]    


    
@client.event
async def on_message(message):
    temp=0  #for processing commands
    temp1=0
    if(message.guild == None):
        text_entered =message.content.strip()
        text_entered=text_entered.lower()
        if (str(message.author.id) !=  "955515799559368764" ):
            try:
                x=guild_id_blacklist_studentid[user_id_guild[message.author.id][-1]]
            except KeyError:
                guild_id_blacklist_studentid[user_id_guild[message.author.id][-1]]=[""]

            for i in guild_id_blacklist_studentid[user_id_guild[message.author.id][-1]]:
                if(i==text_entered and len(text_entered)!=0):
                    await message.channel.send("student with id "+str(text_entered)+" is already present in the sever and is verified")
                    temp1=1
                    break

            if(i!=text_entered and temp1==0):
                for i in all_student_data['username']:
                    if(i==text_entered):
                        temp_student_df=all_student_data[all_student_data['username']==text_entered]
                        temp_list=temp_student_df.values.tolist()
                        for k in guild_branches[user_id_guild[message.author.id][-1]]:
                            if(k==temp_list[0][3]):         
                                user_id_temp_list[message.author.id]=temp_list
                                verify_code(temp_list[0][1],message.author.id)
                                await message.channel.send("you have recieved an OTP code to your mail id please enter the code")  
                                temp1=1
                            elif(k!=temp_list[0][3]):
                                await message.channel.send("sorry you can't join this server because you are from "+str(temp_list[0][3])+" and only these branches can join the server "+str(guild_branches[user_id_guild[message.author.id][-1]]))
                
            if(len(text_entered)==6 and message.content.isdigit()):
                if(str(text_entered)==str(user_id_otp[message.author.id])):
                    #getting member class(discord stuff)
                    curr_guild=client.get_guild(user_id_guild[message.author.id][-1])    
                    guild_id=user_id_guild[message.author.id][-1]
                    member=curr_guild.get_member(message.author.id)
                    #changes nickname  
                    await member.edit(nick=user_id_temp_list[message.author.id][0][2])
                    #getting role id for verified students role
                    role1=discord.utils.get(curr_guild.roles,name="verified students")
                    #assigns roles i.e 1. verified students 
                    await member.add_roles(role1)
                    #getting role id
                    role2=discord.utils.get(curr_guild.roles,name=user_id_temp_list[message.author.id][0][3])
                    #assigns roles i.e 2. their branch
                    await member.add_roles(role2)
                    #welcome verified message
                    await message.channel.send("Verified. Welcome to "+str(member.guild)+" server")
                    #blacklist studentid
                    tempstudentid=[user_id_temp_list[message.author.id][0][0]]
                    try:
                        p=guild_id_blacklist_studentid[guild_id]
                    except KeyError:
                        guild_id_blacklist_studentid[guild_id]=[]
                    p=guild_id_blacklist_studentid[guild_id]
                    p.extend(tempstudentid)
                    guild_id_blacklist_studentid[guild_id]=p
                    #removes his data from user_id_temp_list
                    del user_id_temp_list[message.author.id]

                if(str(text_entered)!=str(user_id_otp[message.author.id])):
                    #replying the error message
                    await message.channel.send("wrong otp entered please enter the otp again")

            temp=1
    
    if(temp==0):
        await client.process_commands(message)



#demo commands
@client.command()
async def hello(ctx):
    await ctx.send("hi i am a client")

#ping pong
@client.slash_command(name="ping",description="to see whether client is working",guild_ids=[955518657621033090])
async def add(ctx):
    await ctx.respond(f'pong Latency: {round(client.latency*1000)}ms')

#goes through this when bot starts
@client.listen()
async def on_connect():
    #dictionary with key as guild id and value as branches choosen by professors
    global guild_branches
    guild_branches=dict()

    #dictionary with key as user id of members who joined server and value as guild id 
    global user_id_guild
    user_id_guild=dict()

    #dictionary with key as user id of members and value as otp
    global user_id_otp
    user_id_otp=dict()

    #dictionary with key as user id of members and value as temp_list(helpfull for changing nickname)
    global user_id_temp_list
    user_id_temp_list=dict()

    #dictionary with key as guild id and value as id of students who are already verified which makes sure that same id isnt entered again
    global guild_id_blacklist_studentid
    guild_id_blacklist_studentid=dict()

    #loading numpy files
    guild_branches=np.load('guild_branches.npy',allow_pickle='TRUE').item()
    user_id_guild=np.load('user_id_guild.npy',allow_pickle='TRUE').item()
    user_id_otp=np.load('user_id_otp.npy',allow_pickle='TRUE').item()
    user_id_temp_list=np.load('user_id_temp_list.npy',allow_pickle='TRUE').item()
    guild_id_blacklist_studentid=np.load('guild_id_blacklist_studentid.npy',allow_pickle='TRUE').item()






#goes through this when bot stops
@client.listen()
async def on_disconnect():
    #saving dictionary as numpy file 
    np.save('guild_branches.npy',guild_branches)
    np.save('user_id_guild.npy',user_id_guild)
    np.save('user_id_otp.npy',user_id_otp)
    np.save('user_id_temp_list.npy',user_id_temp_list)
    np.save('guild_id_blacklist_studentid.npy',guild_id_blacklist_studentid)
    

client.run('')
