# connecting - https://github.com/tchellomello/python-arlo/blob/master/pyarlo/camera.py
from pyarlo import PyArlo
from pyarlo.media import ArloMediaLibrary
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
 
def enviaremail(from_addr, to_addr_list, cc_addr_list,
              subject, message,
              login, password,
              smtpserver='smtp.gmail.com:587'):
	try :
	    print("Tentando enviar o email")
      server = smtplib.SMTP(smtpserver)
	    print("Server: " + str(server))
	    tls = server.starttls()
	    print("TLS: " + str(tls))
	    infologin = server.login(login,password)
	    print("Info sobre logins: " + str(infologin))
	    problems = server.sendmail(from_addr, to_addr_list, message)
	    print("Problemas: " + str(problems))
	    server.quit()
	except :
	    print("Erro ao tentar enviar o email")
      
def log_file(logs):
	try:
		with open("log_pyarlo-camera.txt","a+") as arquivo:
			arquivo.write("\n["+str(datetime.now()) + "] " + str(logs) + "\r")
			arquivo.close()
	except e:
		print("Erro ao escrever o log no arquivo")		
    
textoemail = "Data e Hora: " + str(datetime.now()) + "\n\n" + msgcon + msgnaocon
print(textoemail)

fromemail = ""
paraemail = ""
l = ""
p = ""
smtp = "email-ssl.com.br:587"
if len(naoconectadas) > 0:
	enviaremail(meuemail, paraemail, "", "ARLO CAMERA CheCK UP", textoemail, l, p, smtp)
