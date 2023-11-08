from colorama import init, Fore, Back, Style

init(convert=True)

print(Fore.WHITE)
import os,sys
from tkinter import Tk
from tkinter.filedialog import askopenfilename
os.system('title Bayfiles Uploader by J0rd1s3rr4n0')
logo = """
                                                 osN                                              
                                              Ns+//+h                                             
                                             #d+//////o                                            
                                            #o///::::://sN                                         
                                         Ny+//:::::::::/+h                                        
                                        #d+///::::::::::://o                                       
                                       #o///::::::::::::::://sN                                    
                                    Ny+//:::::::::::::::::::/+d                                   
                                   #d+///::::::::::::::::::::://o                                  
                                  s+//::::::::::::::::::::::::://yN                               
                               Nh+//:::::::::::::::::::::::::::::/+d                              
                              #do///:::::::::::::/oo/:::::::::::::://o                             
                             s+//::::::::::::/oys+oyso/:::::::::::::/+yN                          
                          #Nh+//::::::::::::oyyo+////+oyy+:::::::::::::/+d                         
                         #do///::::::::::::: Nho//////sd y/::::::::::::://s                        
                       Ny+//:::::::::::::::N    yooh    y//::::::::::::::/+hN                     
                     #Nh+///::::::::::::::::N    NhdN    y//::::::::::::::::/od                    
                     #s///::::::::::::::::::N Nds+//oy N y//::::::::::::::::://sN                  
                  #Ny+//::::::::::::::::::::N s////////sNy//:::::::::::::::::::/+hN                
                 #do///:::::::::::::::::::::N Nhs+//+sdN y//:::::::::::::::::::://o                
                #s///:::/+/:::::::::::::::::N    NyhN    y//:::::::::::::::/+/:::://yN             
             #Ny+/////+sysss+/::::::::::::::N    hoodN   y/:::::::::::::/+ssoys+/////+h            
            #do////+sys+///+oss+/:::::::::::NNhs+////+sdNy/::::::::::/+sso////+sys+////s           
           #s+////yNds+//////oyyss+:::::::::NNy+//:::/oyNy/:::::::/+osdyo//////+sNN+/////yN        
        #Nh+///::/h    yo/+sys+//+sso+::::::N  Nds++y N  y/:::::+oso+//+syo+/sdN   o//:::/+d       
       #do///::::/h     N  s////////sdso/:::N    Nd      y////osdo////////s        o//:::://s      
     Ny+//::::::/h        Nds+//+oyo+/osso/N N y+//ohN  y+oss+/+syo+//+y          o//::::::/+yN   
   #Nh+///:::::::/h           Ndhs+/:::://sh  o///::://s  ho////::/+yd             o//::::::://od  
   #o///:::::::::/h               ho//:/+sso+oys+/::/+sso+oyo+/::/sdN              o//::::::::://sN
#Ny+///::::::::://h                  ysys/:::::/sysyso/:::::+syshN                 o///::::::::://+o:
/::------------::shhhd                 y+/::::/ososyo/::::/ohN              Nhhhhh+/:-------------:\
\n               ------:                  Nds+oso/::::+syo+y                  d-------.               
               ------:                      do//::::/+y                     d-------.               
               ------:NNNNNNNNNNNNNNNNNNNNNNNN y+:/ohNNNNNNNNNNNNNNNNNNNNNNNh-------.               
                     `...........................`...........................                       
""" 
print(logo)
Tk().withdraw()

filename = askopenfilename(title="Bayfiles Upload File",filetypes=[
    ("All files","*.*"),])
try:
    os.system('title Bayfiles Uploader by J0rd1s3rr4n0 ~ [ STATUS: UPLOADING ]')
    result = os.system('curl -s -F "file=@'+filename+'" https://api.bayfiles.com/upload > a.bt ')
    os.system('title Bayfiles Uploader by J0rd1s3rr4n0 ~ [ STATUS: UPLOADED, DOWNLOADING RESOURCES...]')
    fina = "a.bt"
    char1 = '{"status":true,"data":{"file":{"url":{"full":"'
    char2 = 'FULL URL: '
    char3 = '","short":"'
    char4 = '\nSHORT URL: '
    char5 = '"},"metadata":{"'
    char6 = '\n'
    char7 = 'id":"'
    char8 = '\n[ FILE INFO ]\nID: '
    char9 = '","name":"'
    char10= '\nFILE NAME: '
    char11= '","size":{'
    char12= '\nSIZE: '
    char13= '"bytes":'
    char14= '\n BYTES: '
    char15= ',"readable":"'
    char16= '\n REDEABLE: '
    char17= '"}}}}}'
    char18= '\n'
    char19= '{"status":false,"error":{"message":"No file chosen.","type":"ERROR_FILE_NOT_PROVIDED","code":10}}'
    char20= ' [ ERROR, NO SE SELECIONO NINGUN ARCHIVO ] \n'
    filer = open(fina, "r")
    filew = open(fina+'t', "w")
    buff = filer.read()
    rbuff = buff.replace(char1, char2)
    rbuff = rbuff.replace(char3, char4)
    rbuff = rbuff.replace(char5, char6)
    rbuff = rbuff.replace(char7, char8)
    rbuff = rbuff.replace(char9, char10)
    rbuff = rbuff.replace(char11, char12)
    rbuff = rbuff.replace(char13, char14)
    rbuff = rbuff.replace(char15, char16)
    rbuff = rbuff.replace(char17, char18)
    rbuff = rbuff.replace(char19, char20)

    andale = os.system('type a.btt')
    filew.write(rbuff)
    filer.close()
    filew.close()
    nono = os.system('type '+fina+'t > '+fina)
    filen = open(fina, "r")
    buffre = filen.read()
    print(buffre)
    filen.close()
    os.remove(fina)
    os.system('title Bayfiles Uploader by J0rd1s3rr4n0 ~ [ WAITING TO CLOSE ]')
except:
    os.system('title Bayfiles Uploader by J0rd1s3rr4n0 ~ [ ERROR, WE CAN NOT UPLAOD YOUR FILE')
    print('ERROR')
try:
    os.remove(fina+'t')
except:
    a = 'a'
try:
    os.remove(fina)
except:
    a = 'a'
print('\nEN 5 MINUTOS SE CERRARA LA VENATANA')
os.system('timeout /t 500 > %TEMP%/null')
