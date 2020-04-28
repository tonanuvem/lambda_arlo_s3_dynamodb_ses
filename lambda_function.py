# connecting - https://github.com/tchellomello/python-arlo/blob/master/pyarlo/camera.py
from pyarlo import PyArlo
from pyarlo.media import ArloMediaLibrary
from datetime import datetime
import boto3
from botocore.exceptions import ClientError
import json

SENDER = os.environ['EMAILFROM']
RECIPIENT = os.environ['EMAILTO']
login = os.environ['ARLOLOGIN']
senha = os.environ['ARLOSENHA']


def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': err.message if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
        },
    }
    
def dyndb_s3_ses_email(arlo):
	# assuming only 1 base station is available
	base = arlo.base_stations[0]
	# listing all cameras
	cameras = arlo.cameras
	print("Quantidade de cameras encontradas: " + str(len(cameras)))
	# Informações das cameras
	print("Baterias das cameras da base: " + str(base.get_cameras_battery_level()))
	print("Sinal das cameras da base: " + str(base.get_cameras_signal_strength()) + "\n")
	conectadas = []
	naoconectadas = []
	itens = []
	imagens = []
	datahora = str(datetime.now())
	for cam in cameras :
		# Salvar lista de imagens
		imagem = '/tmp/' + str(cam)[1:-1].replace(":","") + '.jpg'
		imagens.append(imagem)
		with open(imagem, 'wb') as img:
			img.write(cam.last_image)
		
		# Verificar e salvar os status somente das cameras ligadas a base
		if cam.base_station == None:
			continue
		item = {"camera": str(cam), "bateria": str(cam.battery_level), "status": cam.is_camera_connected}
		itens.append(item)
		if cam.is_camera_connected == True:
			conectadas.append( str(cam) + "\t com bateria de " + str(cam.battery_level) + " %")
		else:
			naoconectadas.append(str(cam) + "\t com bateria de " + str(cam.battery_level) + " %")

	#Salvando registros no DynamoDB
	savedyndb(datahora, itens)
	
	#Enviando email com as informações
	msgcon = "Cameras conectadas: \n"
	for i in conectadas:
		msgcon += "\t" + i + "\n"
	print(msgcon)
	msgnaocon = "\nCamera NAO conectada: \n"
	for j in naoconectadas:
		msgnaocon += "\t" + j + "\n"
	print(msgnaocon)
	textoemail = "Data e Hora: " + datahora + "\n\n" + msgcon + msgnaocon
	sendemail("Email = " + textoemail)
	
	# Salvar ultima imagem no S3
	save2s3(imagens)

def savedyndb(datahora, itens):
	try:
		dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
		table = dynamodb.Table('Registros')
		dbdata = {'RegistroID': datahora, 'Cameras': itens}
		#print('Tentando inserir DynamoDB: \n'+ json.dumps(dbdata, indent=4))
		response = table.put_item(Item=dbdata)
		print("Registro inserido no DynamoDB " + datahora + "\nJSON itens:" + json.dumps(dbdata))
		#print(json.dumps(response, indent=4))
	except Exception as e:
	    print("Erro ao inserir item no DynamoDB: " + str(e))
	    
def save2s3(imagens):
	try:
		print('Imagens a serem inseridas no S3' + str(imagens))
		# Create an S3 client
		s3 = boto3.client('s3')
		bucket_name = 'cameras-imagens'
	
		# Uploads the given file using a managed uploader, which will split up large
		# files automatically and upload parts in parallel.
		for img in imagens:
			s3.upload_file(img, bucket_name, img.replace("/tmp/",""))
	except Exception as e:
	    print("Erro ao inserir imagem no S3: " + str(e))
	    
def sendemail(textoemail):
	#CONFIGURATION_SET = "ConfigSet"
	AWS_REGION = "us-east-1"
	SUBJECT = "Cameras status"
	BODY_TEXT = (textoemail)
	CHARSET = "UTF-8"
	
	# Create a new SES resource and specify a region.
	client = boto3.client('ses',region_name=AWS_REGION)
	# Try to send the email.
	try:
	    #Provide the contents of the email.
	    response = client.send_email(
	        Destination={
	            'ToAddresses': [
	                RECIPIENT,
	            ],
	        },
	        Message={
	            'Body': {
	                'Text': {
	                    'Charset': CHARSET,
	                    'Data': BODY_TEXT,
	                },
	            },
	            'Subject': {
	                'Charset': CHARSET,
	                'Data': SUBJECT,
	            },
	        },
	        Source=SENDER,
	        # If you are not using a configuration set, comment or delete the
	        # following line
	        #ConfigurationSetName=CONFIGURATION_SET,
	    )
	# Display an error if something goes wrong.	
	except ClientError as e:
	    print(e.response['Error']['Message'])
	else:
	    print("Email enviado! Message ID:"),
	    print(response['MessageId'])
	    
def lambda_handler(event, context):
	try:
		# EXECUTION CODE
		print('Received event : ', event)
		arlo  = PyArlo(login, senha, 0)
		print("Data e Hora: " + str(datetime.now()))
		basestations = arlo.base_stations
		print("Quantidade de bases encontradas: " + str(len(basestations)))
		dyndb_s3_ses_email(arlo)
	except Exception as e:
		print ("Erro no final da função lambda_handler: " + str(e))
		#return respond(e)
	return respond(None,'Hello world from camera-arlo')
