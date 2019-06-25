import os
import pygame
from pygame.locals import *
import serial
import time
import mysql.connector
import binascii

pygame.init()
fenetre = pygame.display.set_mode((1366,768),pygame.FULLSCREEN|pygame.HWSURFACE)
pygame.joystick.init()
defaultFont=pygame.font.Font('/home/arcade/Téléchargements/karmatic-arcade.regular.ttf',70)
fond = pygame.image.load("Bureau/background.png").convert_alpha()
poulpe = pygame.image.load("Bureau/poulpe.png").convert_alpha()
borne = pygame.image.load("Bureau/borne.png").convert_alpha()
scanlines = pygame.image.load("Bureau/scanlines.png").convert_alpha()

def deleteExt(l):
   res = []
   for s in l:
      s=s.replace('.hi','')
      s=s.replace('.txt','')
      s=s.replace('.xml','')
      s=s.replace('.crc','')
      res.append(s)
   return res

def findPlayedGame():
   filesToCheck = list(set(deleteExt(os.listdir())))
   games=[]
   ##ajouter exception
   for name in filesToCheck:
      try:
         crcNew=str(binascii.crc32(open(name+'.hi','rb').read()))+'\n'
         crcOld=open(name+'.crc').readline()
         if  crcOld != crcNew:
            games.append(name)
            print(name+" a été lançé")
      except:
         erreur=1
   return games

def add_partie(id_jeu,id_badge):
    sql = "INSERT INTO Partie (id_jeu,id_badge) VALUES ('{0}','{1}')".format(id_jeu,id_badge)
    mycursor = mydb.cursor()
    try:
       mycursor.execute(sql)
    except:
       sqlJ="INSERT INTO Jeu (id_jeu,nom) VALUES ('{0}','{1}')".format(id_jeu,id_jeu.capitalize())
       print(sqlJ)
       mycursor.execute(sqlJ)
       mycursor.execute(sql)
    mydb.commit()
    id_partie=mycursor.lastrowid
    sqlList=list_to_sql(txt_to_list(id_jeu),id_partie)
    for sql in sqlList:
       try:
          mycursor.execute(sql)
       except:
          print("Erreur sur: "+sql)
       mydb.commit() 

def txt_to_list(id_jeu):
   os.system('java -jar hi2txt.jar -r {0}.hi > {0}.txt;'.format(id_jeu))
   try:
      txt = open(id_jeu+'.txt')
   except:
      pass
   firstLine=txt.readline().replace('\n','').split('|')
   tab = [firstLine]
   crcNew = [str(binascii.crc32(open(id_jeu+'.hi','rb').read()))]
   crcOld = open(id_jeu+'.crc').read().split('\n')
   for line in txt:
      crcLine=str(binascii.crc32(bytes(line,'UTF-8')))
      crcNew.append(crcLine)
      if not(crcLine in crcOld):
         tab.append(line.replace('\n','').split('|'))
   crcFile=open(id_jeu+'.crc','w')
   for crc in crcNew:
      crcFile.write(crc+'\n')
   crcFile.close()
   return tab


def list_to_sql(l,id_partie):
   sql = []
   for i in range(1,len(l)):
      for j in range(0,len(l[i])):
         try:
            s="INSERT INTO Score (id_partie,type,valeur) VALUES ('{0}','{1}','{2}')".format(id_partie,l[0][j],l[i][j])
            sql.append(s)
            print(s)
         except:
            s=1
   return sql

def moveHi(uid,out):
	if out:
		os.system('mv "hi" "hi_{0}"'.format(uid))
	else:
		os.system('mv "hi_{0}" "hi"'.format(uid))

def launchAttract(uid):
    os.chdir('/home/arcade/.attract/MAME/roms/mame2003/')
    oldplayer=open('/home/arcade/userlog.txt','r')
    op=oldplayer.read()
    if op != '':
       print(op)
       os.system("mv hi hi_{0}".format(str(op)))
    oldplayer.close()
    userlog=open('userlog.txt','w')
    userlog.write(uid)
    userlog.close()
    moveHi(uid,False)
    os.chdir('/home/arcade/.attract/MAME/roms/mame2003/hi')
    os.system("gnome-terminal -x attract")
    pygame.display.toggle_fullscreen()
    x=0
    while not(os.system("pgrep attract > /dev/null")):
       if x==0:
          print("Attract lancer")
       x=1
    print("Attract quitter")
    pygame.display.toggle_fullscreen()
    id_jeux=findPlayedGame()
    for id_jeu in id_jeux:
          try:
             add_partie(id_jeu,uid)
          except:
              print("BDD Down...")
    os.chdir('/home/arcade/.attract/MAME/roms/mame2003/')
    moveHi(uid,True)
    os.chdir('/home/arcade/')
    old=open('userlog.txt','w')
    old.close()
    
def stringDisplay(string,off_x,off_y):
    question = defaultFont.render(string,1, (255,255,255))
    fenetre.blit(fond,(0,0))
    fenetre.blit(question, (off_x,off_y))
    pygame.display.flip()     

def newUser(UID):
    off_x,off_y=30,30
    current=""
    ch=65
    c=0
    stringDisplay('Pseudo : '+current+chr(ch),off_x,off_y)
    wait=1
    while wait:
        joystick_count = pygame.joystick.get_count()
        for i in range(joystick_count):
           joystick = pygame.joystick.Joystick(i)
           joystick.init()

           axes = joystick.get_numaxes()
        
           for i in range( axes ):
               axis = joystick.get_axis( i )

               if axis > 0.5:
                   c+=1
                   ch=c%26+65
                   stringDisplay('Pseudo :'+current+chr(ch),off_x,off_y)
                   print('Pseudo :'+current+chr(ch))
                   time.sleep(0.3)
                   #print(axis)
               if axis < -0.5:
                   c-=1
                   ch=c%26+65
                   print('Pseudo :'+current+chr(ch))
                   stringDisplay('Pseudo :'+current+chr(ch),off_x,off_y)
                   time.sleep(0.3)
                   #print(axis)

           buttons = joystick.get_numbuttons()
           for i in range( buttons ):
               button = joystick.get_button( i )
               if button == 1 and i==0:
                   current+=chr(ch)
                   c=0
                   ch=65
                   print('Pseudo :'+current+chr(ch))
                   stringDisplay('Pseudo :'+current+chr(ch),off_x,off_y)
                   time.sleep(0.7)
                   button=0
               if button == 1 and i==1:
                   return (current+chr(ch)).capitalize()

        for event in pygame.event.get():
            if event.type == KEYDOWN and event.key == K_SPACE:
                current+=chr(ch)
                c=0
                ch=65
                print('Pseudo :'+current+chr(ch))
                stringDisplay('Pseudo :'+current+chr(ch),off_x,off_y)
            if event.type == KEYDOWN and event.key == K_DOWN:
                c-=1
                ch=c%26+65
                print('Pseudo :'+current+chr(ch))
                stringDisplay('Pseudo :'+current+chr(ch),off_x,off_y)
            if event.type == KEYDOWN and event.key == K_UP:
                c+=1
                ch=c%26+65
                stringDisplay('Pseudo :'+current+chr(ch),off_x,off_y)
                print('Pseudo :'+current+chr(ch))
            if event.type == KEYDOWN and event.key == K_RETURN:
                return (current+chr(ch)).capitalize()

def blitall(scan):
        fenetre.blit(fond, (0,0))
        fenetre.blit(borne, (0,0))
        fenetre.blit(poulpe, (0,0))
        if scan:
           fenetre.blit(scanlines, (0,0))
        pygame.display.flip()

def main(): 
    global fond
    global fenetre
    global poulpe
    global borne
    global mydb
    try:
        mydb = mysql.connector.connect(
          host="arcade.codev.resel.fr",
          user="python",
          passwd="CoDEV19arcade",
          port="32106",
          database="borne"
          )
    except:
       print('Base Déconnectée')
    try:       
       ser = serial.Serial('/dev/ttyACM0', 9600)
    except:
       print('Lecteur de Badge HS')
    

    #fenetre = pygame.display.set_mode((1300,750))

    uid="1"
    continuer = 1
    while continuer:
        blitall(True)
        try:
            uid_bytes = ser.readline()
            uid=str(uid_bytes)[3:-5]
            print(uid)
            print(len(uid))
        except:
             for event in pygame.event.get():
                if event.type == KEYDOWN and event.key == K_UP:
                     uid=("AA "*7)[:-1]
                     print(len(uid))
                if event.type == KEYDOWN and event.key == K_ESCAPE:
                     print("ESCAPE")
                     pygame.display.quit()
                     pygame.quit()
        for event in pygame.event.get():
             if event.type == KEYDOWN and event.key == K_ESCAPE:
                  print("ESCAPE")
                  pygame.display.quit()
                  pygame.quit()
        if len(uid)==20:
            try:
               print(uid)
               mycursor = mydb.cursor()
               mycursor.execute("SELECT nom FROM Joueur WHERE id_badge='{0}'".format(uid))
               myresult = []
               myresult = mycursor.fetchall()
            except:
               myresult = [('Invité',)]
               uid=("00 "*7)[:-1]
            if myresult == []:
                #Si il n'y a pas de badge avec cet id
                user=newUser(uid).capitalize() #On crée un pseudo
                sql="INSERT INTO `Joueur` (`id_badge`, `nom`) VALUES (%s, %s)"
                mycursor.execute(sql,(uid,user)) #On l'ajoute à la base
                mydb.commit()
                os.chdir('/home/arcade/.attract/MAME/roms/mame2003')
                os.system("cp -r 'hi_default' 'hi_{0}'".format(uid)) 
                Bienvenue = defaultFont.render('Bienvenue '+user+ " !",1, (255,255,255))
                blitall(False)
                fenetre.blit(Bienvenue, (0,0))
                fenetre.blit(scanlines, (0,0))
                pygame.display.flip()
                #continuer = 0
                launchAttract(uid) # On lance l'émulateur
                
                uid="0"
            else:
                user=myresult[0][0]
                Bienvenue = defaultFont.render('Bienvenue '+user+ " !",1, (255,255,255))
                fenetre.blit(Bienvenue, (0,0))
                fenetre.blit(scanlines, (0,0))
                pygame.display.flip()
                launchAttract(uid)
                
                uid="0"
                #continuer = 0
    pygame.display.quit()
    pygame.quit()
    #ser.close() 

if __name__=="__main__":
	main()   
