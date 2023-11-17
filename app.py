import streamlit as st
import pandas as pd
import plotly.express as px

# Função para carregar e limpar dados
def load_and_clean_data(filepath):
    df = pd.read_csv(filepath, skiprows=[0])
    df['Time'] = pd.to_datetime(df['Time'])
    for col in df.columns[1:]:
        df[col] = (
            df[col].replace(' µs', '', regex=True)
            .replace(' ms', '', regex=True)
            .astype(float)
            .apply(lambda x: x if x < 1000 else x * 1000)
        )
    return df

# Carregar dados
df = load_and_clean_data('data.csv')

# Streamlit widgets para seleção de servidor, período e threshold
st.title('Dashboard de Monitoramento de Servidores')
selected_server = st.selectbox('Selecione o servidor:', df.columns[1:])
selected_dates = st.date_input('Selecione o período de tempo:', [])
min_threshold, max_threshold = st.slider('Defina o threshold de tempo de resposta (µs):', 0, 10000, (100, 500))

# Filtrar dados com base na seleção
filtered_df = df[df['Time'].dt.date.between(selected_dates[0], selected_dates[1])] if selected_dates else df

# Plotar gráfico com Plotly
fig = px.line(filtered_df, x='Time', y=selected_server, title=f'Tempo de Resposta para o servidor {selected_server}')
fig.add_hline(y=max_threshold, line_dash="dot", annotation_text="Threshold Máximo", annotation_position="bottom right")
fig.add_hline(y=min_threshold, line_dash="dot", annotation_text="Threshold Mínimo", annotation_position="bottom right")
st.plotly_chart(fig, use_container_width=True)

# Download de gráficos e dados com Streamlit
st.download_button(
    label='Baixar dados como CSV',
    data=filtered_df.to_csv(index=False).encode('utf-8'),
    file_name='dados.csv',
    mime='text/csv'
)

# Verificar e exibir status com base no threshold
latest_value = filtered_df[selected_server].iloc[-1] if not filtered_df.empty else 0
status = 'OK' if latest_value < min_threshold else 'FAIL' if latest_value > max_threshold else 'WARNING'
st.write(f'Status atual: {status}')
