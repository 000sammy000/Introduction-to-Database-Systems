import psycopg2
import discord
import os


intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
client = discord.Client(intents=intents)

conn = psycopg2.connect(database="movie", user="postgres", password="***", host="oxcgrt.cwbpn6cx8ver.us-east-1.rds.amazonaws.com")
 

cur = conn.cursor()


@client.event
async def on_ready():
    print('>> Bot is online')

@client.event
async def on_message(message):
    if message.content.startswith('看影片'):
        channel = message.channel

        await channel.send('我是你的電影小幫手。查影片詳細請按1，推薦影片請按2')
        msg = await client.wait_for('message')
        if msg.content=='1':
           await channel.send('告訴我電影名字')
           msg = await client.wait_for('message')
           name=msg.content
           platform="Netflix"
           cur.execute("SELECT distinct * from title_info_n natural join title_description_n where title=%s",[name])

           row = cur.fetchone()

           if row==None:
               platform="Disney"
               cur.execute("SELECT distinct * from title_info_d natural join title_description_d where title=%s",[name])
               row = cur.fetchone()
               
           if row==None:
                await channel.send('真是個好名字，但沒有這部')
        
           else:
               await channel.send('標題: ' + str(row[0]))
               await channel.send(str(row[1]))
               await channel.send(platform)
               await channel.send('導演: ' + str(row[2]))
               await channel.send('演員: ' + str(row[3]))
               await channel.send('國家: ' + str(row[4]))
               await channel.send('上映年份: ' + str(row[5]))
               await channel.send('分級: ' + str(row[6]))
               if(str(row[1])=='Movie'):
                   await channel.send('片長: ' + str(row[7]))
               await channel.send('類型: ' + str(row[8]))
               await channel.send(str(row[9]))

           
        if msg.content=='2':
           await channel.send('要TV Show/Movie')
           msg = await client.wait_for('message')
           media=msg.content
           if media=='Movie':
               await channel.send('要多長(a.一小時內 b.兩小時內 c.三小時內 d.多長都不在乎)')
               msg = await client.wait_for('message')
               time=msg.content
           await channel.send('要哪一年')
           msg = await client.wait_for('message')
           year=msg.content
           await channel.send('要哪個平台(Netflix/Disney/都可以)')
           msg = await client.wait_for('message')
           platform=msg.content
           await channel.send('輸入分級')
           await channel.send('(電影  G:大眾級|PG:普遍級|PG-13:不適於13歲以下兒童|R:限制級)')
           await channel.send('(電視劇  TV-Y:適合所有兒童|TV-Y7：適合7歲以上兒童|TV-G：普通級，適合所有人觀看|')
           await channel.send('(        TV-14：14歲以下兒童需父母指導觀看|TV-MA：限制級成人節目，只允許17歲以上觀看)')
           msg = await client.wait_for('message')
           age=msg.content
           await channel.send('時長:'+time)
           await channel.send('年份:'+year)
           await channel.send('平台:'+platform)
           await channel.send('類型:'+media)
           await channel.send('分級:'+age)

           dur=240
           if(time=='a'):
             dur=60
               
           if(time=='b'):
             dur=120
             
           if(time=='c'):
             dur=180

           if(time=='d'):
             dur=240


           if platform=='Netflix':
               cur.execute("SELECT * from title_info_n where type=%s and rating=%s and release_year=%s and duration<=%s",[media,age,int(year),dur])

           if platform=='Disney':
               cur.execute("SELECT * from title_info_d where type=%s and rating=%s and release_year=%s and duration<=%s",[media,age,int(year),dur])

           if platform=='都可以':
               change=0
               cur.execute("""SELECT * from title_info_n as n
                            where n.type=%s and n.rating=%s and n.release_year=%s and n.duration<=%s"""
                           ,[media,age,int(year),dur,media,age,int(year),dur])

           
           i=1
           while i<=10:
             
             row = cur.fetchone()

             if row == None:
                if platform=='都可以' and change==0:
                   cur.execute("SELECT * from title_info_d where type=%s and rating=%s and release_year=%s and duration<=%s",[media,age,int(year),dur])
                   change=1
                else:
                   break

             await channel.send(str(i)+'. title: ' + str(row[0]) + '\t時長: ' + str(row[7]))
             i=i+1

           if i>=10:
             await channel.send('要看更多請按c')
           else:
             await channel.send('就這些')  
           
           while True:
            msg = await client.wait_for('message')
            if(msg.content!='c'):
                break
            else:
               i=1
               while i<=10:
                    row = cur.fetchone()
                    if row == None:
                      if platform=='都可以' and change==0:
                         cur.execute("SELECT * from title_info_d where type=%s and rating=%s and release_year=%s and duration<=%s",[media,age,int(year),dur])
                         change=1
                      else:
                          break

                    await channel.send(str(i)+'. title: ' + str(row[0]) + '\t時長: ' + str(row[7]))
                    i=i+1

               if i>=10:
                 await channel.send('要看更多請按c')
               else:
                 await channel.send('就這些')
                 break


TOKEN = "***"
client.run(TOKEN)
