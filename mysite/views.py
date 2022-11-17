from django.shortcuts import render, redirect
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime 
import requests
import warnings
warnings.filterwarnings("ignore")

def inicio(request):
  return render(request,"index.html","hello")

def darkorbit(request):
  #configuracion de variables y parametros
  date_text='{dt.year}/{dt.month}/{dt.day}'.format(dt = datetime.datetime.now())
  date_text_tomorrow='{dt.year}/{dt.month}/{dt.day}'.format(dt = datetime.datetime.now() + datetime.timedelta(days=1))
  ymd=date_text.split('/')
  ymd_tomorrow=date_text_tomorrow.split('/')

  def goldbooty(lista):
    has_event = False
    for i in range(len(lista)):
      if lista[i].find("Gold Booty")!=-1:
        has_event = True
    return has_event

  def upgradebonus(lista):
    has_event = False
    for i in range(len(lista)):
      if lista[i].find("Upgrade Bonus")!=-1:
        has_event = True
    return has_event

  #Extraccion y limpieza de la data
  table_MN = pd.read_html(f'https://board-en.darkorbit.com/bp-calendar/?year={ymd[0]}&month={ymd[1]}')
  df = table_MN[0]
  df.columns = df.iloc[0]
  df.drop(df.index[0]);
  df['index']= 1
  df2 = pd.melt(df, id_vars=['index'], var_name='day', value_name='value')
  df2 = df2.dropna()
  df2 = df2[df2['day']!=df2['value']]
  df2['erase']= df2['value'].apply(lambda x: 1 if len(x)>2 else 0)
  df3 = df2[df2['erase']==1]
  df3['day_no'] = df3['value'].apply(lambda x: x.split('  ')[0])
  df3['day_events'] = df3['value'].apply(lambda x: x.split('  ')[1:])
  df3['day_index'] = df3['value'].apply(lambda x: int(x.split('  ')[0]))
  df_output = df3[['day','day_no','day_index','day_events']].set_index('day_index').sort_index()

  def calculateNextGoldBBooty():  
    nextGoldBootyDay = df_output[df_output['day_events'].apply(lambda x: goldbooty(x)) == True ].day_no.astype("int").max().astype(str)
    str_date = f"{ymd[1]}-{nextGoldBootyDay}-{ymd[0]}"
    dto = datetime.datetime.strptime(str_date, '%m-%d-%Y').date()
    dtoPlusTwoWeeks= dto + datetime.timedelta(weeks=2)
    if(int(nextGoldBootyDay) == int(ymd[2])):
      return print("Hoy es dia del cofre dorado! \n a gastar esas llaves")
    elif(int(nextGoldBootyDay) < int(ymd[2])):
      diff=  (datetime.datetime.now().date()  - dto).days
      diff2=  (dtoPlusTwoWeeks - datetime.datetime.now().date()).days
      return (f"El cofre dorado ya paso hace {diff} dias y no se ha publicado informacion sobre el siguiente dia del evento \nbasado en los registros historicos lo mas probable es que sea el dia {dtoPlusTwoWeeks} y faltan {diff2} dias para esa fecha")
    else:
      diff=  (dto - datetime.datetime.now().date()).days
      return (f"El proximo cofre dorado sera el dia {dto}. Para esto faltan {diff} dias.")

  def calculateNextUpgradeBonus():  
    nextUpgradeDay = df_output[df_output['day_events'].apply(lambda x: upgradebonus(x)) == True ].day_no.astype("int").max().astype(str)
    str_date = f"{ymd[1]}-{nextUpgradeDay}-{ymd[0]}"
    dto = datetime.datetime.strptime(str_date, '%m-%d-%Y').date()
    dtoPlusTwoWeeks= dto + datetime.timedelta(weeks=2)
    if(int(nextUpgradeDay) == int(ymd[2])):
      return print("Hoy hay descuentos en mejoras! \n")
    elif(int(nextUpgradeDay) < int(ymd[2])):
      diff=  (datetime.datetime.now().date()  - dto).days
      diff2=  (dtoPlusTwoWeeks - datetime.datetime.now().date()).days
      return (f"El ultimo descuento en mejoras fue hace {diff} dias \nel siguiente sera el dia {dtoPlusTwoWeeks} y faltan {diff2} dias para esa fecha")
    else:
      diff=  (dto - datetime.datetime.now().date()).days
      return (f"El proximo descuento en mejoras sera el dia {dto}. Para esto faltan {diff} dias.")

  #Preparacion del mensaje
  event_list = df_output[df_output['day_no']==str(ymd[2])]['day_events'].iloc[0]
  event_list_tomorrow = df_output[df_output['day_no']==str(ymd_tomorrow[2])]['day_events'].iloc[0]

  day_name = df_output[df_output['day_no']==str(ymd[2])]['day'].iloc[0]

  message = f"""
  Los eventos de hoy {date_text} son los siguientes: \n
  """
  for i in range(len(event_list)):
    message+= '-\t'+event_list[i]+'\n'

  message += f"""
  Los eventos de manana {date_text_tomorrow} son los siguientes: \n
  """
  for i in range(len(event_list_tomorrow)):
    message+= '-\t'+event_list_tomorrow[i]+'\n'

  message+= f"{calculateNextGoldBBooty()} \n\n"
  message+= f"{calculateNextUpgradeBonus()} \n"
  message += f"""

  Bot creado por el Clan int1 Sir Latin Gremmy """

  message = message.replace('&',' and ')
  contexto = {'message':message }

  print(message)
  return render(request,"index.html",contexto)
