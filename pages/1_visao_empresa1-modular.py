#from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
from PIL import Image
import folium
from streamlit_folium import folium_static
st.set_page_config(page_title = 'Visão Empresa', layout = 'wide')
image = Image.open('OIP.jpg')
st.sidebar.image(image,width =120)
df = pd.read_csv('train.crdownload')
print(df.head())
#FUNÇÕES
#Limpeza de dados:
def clean_code(df1):
    df1 = df.copy()
    
    linhas_selecionadas = (df1['Delivery_person_Age'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    
    linhas_selecionadas = (df1['Road_traffic_density'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    linhas_selecionadas = (df1['Time_taken(min)'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    linhas_selecionadas = (df1['City'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    linhas_selecionadas = (df1['Festival'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)
    df1.shape
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format ='%d-%m-%Y')
    linhas_selecioandas = (df1['multiple_deliveries'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(float)
    df1.loc[:,'ID'] = df1.loc[:,'ID'].str.strip()
    df1.loc[:,'Festival'] = df1.loc[:,'Festival'].str.strip()
    df1.loc[:,'Road_traffic_density'] = df1.loc[:,'Road_traffic_density'].str.strip()
    df1.loc[:,'Type_of_order'] = df1.loc[:,'Type_of_order'].str.strip()
    df1.loc[:,'Type_of_vehicle'] = df1.loc[:,'Type_of_vehicle'].str.strip()
    df1.loc[:,'City'] = df1.loc[:,'City'].str.strip()
    def extract_time(text):
        try:
            return int(str(text).split('(min) ')[1])
        except (ValueError, IndexError):
            return None
    
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(extract_time)
    
    return df1

def order_metric(df1):
            
    cols = ['ID','Order_Date']
        
        # selecão de linhas
    df_aux =  df1.loc[:,cols].groupby('Order_Date').count().reset_index()          
        
    fig = px.bar(df_aux, x='Order_Date', y ='ID')
    return fig

def traffic_order_share(df1):
                
    df_aux=df1.loc[:,['ID','Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()
    df_aux=df_aux.loc[df_aux['Road_traffic_density'] !="NaN",:]
    df_aux['entregas_perc'] = df_aux['ID']/df_aux['ID'].sum()
    fig = px.pie(df_aux, values = 'entregas_perc' ,names = 'Road_traffic_density')
    return fig

def traffic_order_city(df1):
    df_aux = df1.loc[:,['ID','City','Road_traffic_density']].groupby(['City','Road_traffic_density']).count().reset_index()
    df_aux = df_aux.loc[df_aux['City']!='NaN',:]
    df_aux = df_aux.loc[df_aux['Road_traffic_density']!='NaN',:]

    fig = px.scatter(df_aux, x = 'City',y ='Road_traffic_density',size='ID',color='City')
    return fig

def order_by_week(df1):
            
    df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')
    df_aux = df1.loc[:, ['ID','week_of_year']].groupby('week_of_year').count().reset_index()
    fig = px.line(df_aux, x='week_of_year',y='ID')
    return fig

def order_share_by_week(df1):
    df_aux01 = df1.loc[:,['ID','week_of_year']].groupby('week_of_year').count().reset_index()
    df_aux02 = df1.loc[:,['Delivery_person_ID','week_of_year']].groupby('week_of_year').nunique().reset_index()
    df_aux = pd.merge(df_aux01, df_aux02, how='inner')
    df_aux['order_by_deliver'] = df_aux['ID']/df_aux['Delivery_person_ID']
    
    fig=px.line(df_aux, x ='week_of_year',y='order_by_deliver')

    return fig

def country_maps(df1):
    df_aux = df1.loc[:,['City','Road_traffic_density','Delivery_location_latitude','Delivery_location_longitude']].groupby(['City','Road_traffic_density']).median().reset_index()
    df_aux = df_aux.loc[df_aux['City'] !='NaN',:]
    df_aux = df_aux.loc[df_aux['Road_traffic_density']!='NaN',:]
#for index,location_info in df_aux.iterrows():
          #folium.Marker([location_info['Delivery_location_latitude'],location_info['Delivery_location_longitude']]).add_to(map)
    map = folium.Map()
    for index, location_info in df_aux.iterrows():
      folium.Marker([location_info['Delivery_location_latitude'],location_info[ 'Delivery_location_longitude']], popup = location_info[['City','Road_traffic_density']]).add_to(map)
    folium_static(map, width=1024, height=600)
    return None

df1 = clean_code(df)

## LAYOUT STREAMLIT
# BARRA LATERAL
##
st.header('Marketplace - Visão Cliente')
image_path='OIP.jpg'
image = Image.open(image_path)
st.sidebar.image(image, width = 120)
st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')


st.sidebar.markdown('## Selecione uma data limite')
data_slider = st.sidebar.slider('Até qual valor',value =pd.datetime(2022,4,13),min_value=pd.datetime(2022,2,11),max_value=pd.datetime(2022,4,6),format=('DD-MM-YYYY'))                    
                
st.header(data_slider)

st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect('Quais as condições do trânsito',['Low','Medium','High','Jam'],default = ['Low','Medium','High','Jam'])

st.sidebar.markdown("""---""")
st.sidebar.markdown("### Powered by Comunidade DS")

## Filtro de data
linhas_selecionadas = df1['Order_Date'] < data_slider
df1 = df1.loc[linhas_selecionadas, :]


## Filtro de trânsito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas,:]

st.dataframe(df1)
#--------------------
# layout no streamlit
#--------------------
tab1,tab2,tab3 = st.tabs(['Visão Gerencial','Visão Tática','Visão Geográfica'])
with tab1:
    with st.container():

        fig = order_metric(df1)
        st.markdown('# Order By Day')
        st.plotly_chart(fig,use_container_width=True)

        
    with st.container():
        col1,col2 = st.columns(2)
        with col1:
            fig = traffic_order_share(df1)
            st.header("Traffic Order Share")
            st.plotly_chart(fig,use_container_width=True)

                
        with col2:
            fig = traffic_order_city(df1)
            st.header("Traffic Order City")
            st.plotly_chart(fig,use_container_width=True)

            
    

            
            st.markdown('# Coluna 2')
with tab2:
    with st.container():
        
        st.markdown('# Order by week')
        fig = order_by_week(df1)
        st.plotly_chart(fig,use_container_width=True)


        
    with st.container():
        st.markdown("# Order Share by Week")
        st.plotly_chart(fig,use_container_width=True)

with tab3:
    st.markdown('# Country Maps')
    country_maps(df1)
    
    



## 3 Quantidade dos pedidos por tráfego
#df_aux = df1.loc[:,['ID','Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()
#df_aux = df_aux.loc[df_aux['Road_traffic_density']!='NaN',:]
#df_aux['entrega_perc'] = df_aux['ID']/df_aux['ID'].sum()
#px.pie(df_aux, values = 'entrega_perc',names ='Road_traffic_density')


## 4 Comparação do volume de pedidos por cidade e tipo de tráfego

#df_aux = df1.loc[:,['ID','City','Road_traffic_density']].groupby(['City','Road_traffic_density']).count().reset_index()
#df_aux = df_aux.loc[df_aux['City']!='NaN',:]
#df_aux = df_aux.loc[df_aux['Road_traffic_density']!='NaN',:]
#px.scatter(df_aux, x='City', y='Road_traffic_density',size ='ID', color='City')


## 5 Quantidade de pedidos por entregador por semana

#df_aux01 = df1.loc[:,['ID','week_of_year']].groupby('week_of_year').count().reset_index()
#df_aux02 = df1.loc[:,['Delivery_person_ID','week_of_year']].groupby('week_of_year').nunique().reset_index()
#df_aux = pd.merge(df_aux01, df_aux02, how='inner')
#df_aux['order_by_deliver'] = df_aux['ID']/df_aux['Delivery_person_ID']

#px.line(df_aux, x ='week_of_year',y='order_by_deliver')

## 6  A localização central de cada cidade por tipo de trafego

#import folium
#df_aux = df1.loc[:,['City','Road_traffic_density','Delivery_location_latitude','Delivery_location_longitude']].groupby(['City','Road_traffic_density']).median().reset_index()
#df_aux = df_aux.loc[df_aux['City'] !='NaN',:]
#df_aux = df_aux.loc[df_aux['Road_traffic_density']!='NaN',:]
#df_aux = df_aux.head()

#map = folium.Map()
#for index,location_info in df_aux.iterrows():
  #folium.Marker([location_info['Delivery_location_latitude'],location_info['Delivery_location_longitude']]).add_to(map)

#for index, location_info in df_aux.iterrows():
  #folium.Maker([location_info[0,'Delivery_location_latitude'],location_info[0, 'Delivery_location_longitude']]).add_to(map)

#columns = [
#'City',
#'Road_traffic_density',
#'Delivery_location_latitude',
#'Delivery_location_longitude'
#]
#columns_groupby = ['City', 'Road_traffic_density']
#data_plot = df1.loc[:, columns].groupby( columns_groupby ).median().reset_index()
#data_plot = data_plot[data_plot['City'] != 'NaN']
#data_plot = data_plot[data_plot['Road_traffic_density'] != 'NaN']
# Desenhar o mapa
#map_ = folium.Map( zoom_start=11 )
#for index, location_info in data_plot.iterrows():
#  folium.Marker( [location_info['Delivery_location_latitude'],
#                  location_info['Delivery_location_longitude']],
#                  popup=location_info[['City', 'Road_traffic_density']] ).add_to( map_ )
#map_

