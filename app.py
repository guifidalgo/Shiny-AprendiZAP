from shiny import App, ui, render, reactive
from datetime import datetime, timezone
import pandas as pd
import plotnine as p9

TIMEZONE = timezone.utc

color_map = {
    0: "#812EBB",  # Primária
    1: "#D03384",  # Secundária
    2: "#2DBE82",  # Verde esmeralda
    3: "#2CAAD6",  # Azul turquesa
    4: "#F4B93C",  # Amarelo dourado
    5: "#E85C4A",  # Vermelho coral
}

icon_teacher = '<img src="https://github.com/guifidalgo/Shiny-AprendiZAP/blob/master/assets/teacher_white.png?raw=true" alt="Professor" width="50" height="50">'
icon_student = '<img src="https://github.com/guifidalgo/Shiny-AprendiZAP/blob/master/assets/student_white.png?raw=true" alt="Aluno" width="50" height="50">'
icon_interaction = '<img src="https://github.com/guifidalgo/Shiny-AprendiZAP/blob/master/assets/interaction_white.png?raw=true" alt="Interação" width="50" height="50">'
icon_speedometer = '<img src="https://github.com/guifidalgo/Shiny-AprendiZAP/blob/master/assets/speedometer_white.png?raw=true" alt="Velocímetro" width="50" height="50">'
icon_stopwatch = '<img src="https://github.com/guifidalgo/Shiny-AprendiZAP/blob/master/assets/stopwatch_white.png?raw=true" alt="Cronômetro" width="50" height="50">'

teachers = pd.read_parquet("data-transformed/teachers_entries.parquet")
teachers = teachers[teachers['Frequency'] < 9000]
teachers['semana_entrada'] = pd.to_datetime(teachers['semana_entrada']).dt.tz_localize(None)
teachers['usuario_valido'] = teachers['selectedstages'].notna()
r_score = teachers['R_score'].unique().tolist()
r_score.sort()
f_score = teachers['F_score'].unique().tolist()
f_score.sort()
m_score = teachers['M_score'].unique().tolist()
m_score.sort()
rfm_score = teachers['RFM_Score'].unique().tolist()
rfm_score.sort()

entries = pd.read_parquet("data-transformed/entries.parquet")
entries = entries[entries['data_inicio'] >= "2022-01-03"]
entries['semana_inicio'] = pd.to_datetime(entries['data_inicio'].dt.date - pd.to_timedelta(entries['data_inicio'].dt.dayofweek, unit='d')).dt.tz_localize(None)



app_ui = ui.page_sidebar(
    ui.sidebar(
        "Filtros",
        ui.input_switch(
            'switch_valid',
            'Apenas Usuários Válidos',
            value=False
            ),
        ui.input_slider(
            "slider_date",
            label="Data de Cadastro:",
            min=teachers['semana_entrada'].min(),
            max=teachers['semana_entrada'].max(),
            value=(teachers['semana_entrada'].min(), teachers['semana_entrada'].max()),
            time_format="%m/%Y",
        ),
        ui.input_slider(
            "slider_interacoes",
            label="Data de Interação:",
            min=entries['semana_inicio'].min(),
            max=entries['semana_inicio'].max(),
            value=(entries['semana_inicio'].min(), entries['semana_inicio'].max()),
            time_format="%m/%Y",
        ),
        bg="#f8f8f8"
    ),
    ui.layout_columns(
        ui.output_ui("header_exploracao"),
        ui.value_box(
        "Cadastros",
        ui.output_text("qtd_professores"),
        "Professores",
        showcase=ui.HTML(icon_teacher),
        theme=ui.value_box_theme('aprendizap', bg=color_map[0], fg="white")
        ),
        ui.value_box(
            "Score RFM Médio",
            ui.output_text("media_score_rfm"),
            "Pontos",
            showcase=ui.HTML(icon_speedometer),
            theme=ui.value_box_theme('aprendizap3', bg=color_map[2], fg="white")
        ),
        ui.value_box(
            "Frequência Média de Acessos",
            ui.output_text("media_acessos"),
            "Acessos",
            showcase=ui.HTML(icon_interaction),
            theme=ui.value_box_theme('aprendizap2', bg=color_map[1], fg="white")
        ),
        ui.value_box(
            "Tempo Médio Gasto",
            ui.output_text("media_duracao_acessos"),
            "Minutos",
            showcase=ui.HTML(icon_stopwatch),
            theme=ui.value_box_theme('aprendizap2', bg=color_map[3], fg="white")
        ),
        ui.card(
            ui.card_header(
                ui.input_select(
                    'select_plot',
                    '',
                    choices=['Cadastro de Professores', 'RFM Score Médio', 'Frequência Média de Acessos', 'Tempo Médio Gasto'],
                )
            ),
            ui.card_body(
                ui.output_plot("plot_cadastros")
            )
        ),
        ui.card(
            ui.card_header("Professores por Estado"),
            ui.card_body(
                ui.output_plot("plot_professores_estado")
            )
        ),
        ui.card(
            ui.card_header("Professores por UTM de Origem"),
            ui.card_body(
                ui.output_plot("plot_utm_origem")
            )
        ),
        ui.output_ui("divider"),
        ui.output_ui("header_explicacao"),
        ui.card(
            ui.card_header("Matriz RFM - Recência, Frequência e Tempo Gasto na Plataforma"),
            ui.card_body(
                ui.output_plot("plot_matriz_rfm")
            )
        ),
        ui.card(
            ui.card_header("Interações Semanais de Professores"),
            ui.card_body(
                ui.output_plot("plot_interacoes")
            )
        ),
        col_widths=[12, 3, 3, 3, 3, 12, 6, 6, 12, 12, 12]
    ),
    title="AprendiZAP - Grupo 01",
)



def server(input, output, session):
    @reactive.calc
    def teachers_filtrado():
        start_date = pd.to_datetime(input.slider_date()[0]).tz_localize(None)
        end_date = pd.to_datetime(input.slider_date()[1]).tz_localize(None)
        if input.switch_valid():
            df = teachers[teachers['usuario_valido'] == True]
        else:
            df = teachers
        return df[
            (df['semana_entrada'] >= start_date) &
            (df['semana_entrada'] <= end_date)
        ]
    
    @reactive.calc
    def entries_filtrado():
        start_date = pd.to_datetime(input.slider_interacoes()[0]).tz_localize(None)
        end_date = pd.to_datetime(input.slider_interacoes()[1]).tz_localize(None)
        if input.switch_valid():
            valid_users = teachers[teachers['usuario_valido'] == True]['unique_id'].unique()
            df = entries[entries['unique_id'].isin(valid_users)]
        else:
            df = entries
        return df[
            (df['semana_inicio'] >= start_date) &
            (df['semana_inicio'] <= end_date)
        ]

    @render.ui
    def header_exploracao():
        return ui.h2("Análise Exploratória")
    
    @render.ui
    def divider():
        return ui.hr()

    @render.ui
    def header_explicacao():
        return ui.h2("Análise Explicativa")

    @render.text
    def qtd_professores():
        return f"{teachers_filtrado().shape[0]:,d}".replace(",", ".")
    
    @render.text
    def media_score_rfm():
        df = teachers_filtrado()
        return f"{df['RFM_Score'].mean():,.2f}".replace(".", ",")

    @render.text
    def media_acessos():
        df = teachers_filtrado()
        return f"{df['Frequency'].mean():,.2f}".replace(".", ",")

    @render.text
    def media_duracao_acessos():
        df = teachers_filtrado()
        return f"{df['Duration'].mean():,.2f}".replace(".", ",")

    def plot_cadastros_profs():
        df = teachers_filtrado()
        semanais = df.groupby(['semana_entrada']).size().reset_index(name='cadastros_count')
        # semanais = df.groupby(['semana_entrada']).agg({"RFM_Score": "mean"}).reset_index().rename(columns={"RFM_Score": "cadastros_count"})
        semanais['semana_entrada'] = pd.to_datetime(semanais['semana_entrada'])
        plot = (
            p9.ggplot(semanais, p9.aes(x='semana_entrada', y='cadastros_count')) +
            p9.geom_area(fill=color_map[0], alpha=0.5) +
            p9.geom_line(color=color_map[0]) +
            p9.labs(
                x='Data de Entrada (Semana)',
                y='Número de Cadastros'
            ) +
            p9.theme_minimal()
        )
        return plot
    
    def plot_rfm_score():
        df = teachers_filtrado()
        semanais = df.groupby(['semana_entrada']).agg({"RFM_Score": "mean"}).reset_index().rename(columns={"RFM_Score": "rfm_score"})
        semanais['semana_entrada'] = pd.to_datetime(semanais['semana_entrada'])
        plot = (
            p9.ggplot(semanais, p9.aes(x='semana_entrada', y='rfm_score')) +
            p9.geom_area(fill=color_map[2], alpha=0.5) +
            p9.geom_line(color=color_map[2]) +
            p9.labs(
                x='Data de Entrada (Semana)',
                y='Score RFM Médio'
            ) +
            p9.theme_minimal()
        )
        return plot
    
    def plot_frequencia():
        df = teachers_filtrado()
        semanais = df.groupby(['semana_entrada']).agg({"Frequency": "mean"}).reset_index().rename(columns={"Frequency": "frequency"})
        semanais['semana_entrada'] = pd.to_datetime(semanais['semana_entrada'])
        plot = (
            p9.ggplot(semanais, p9.aes(x='semana_entrada', y='frequency')) +
            p9.geom_area(fill=color_map[1], alpha=0.5) +
            p9.geom_line(color=color_map[1]) +
            p9.labs(
                x='Data de Entrada (Semana)',
                y='Frequência Média de Acessos'
            ) +
            p9.theme_minimal()
        )
        return plot
    
    def plot_duracao():
        df = teachers_filtrado()
        semanais = df.groupby(['semana_entrada']).agg({"Duration": "mean"}).reset_index().rename(columns={"Duration": "duration"})
        semanais['semana_entrada'] = pd.to_datetime(semanais['semana_entrada'])
        plot = (
            p9.ggplot(semanais, p9.aes(x='semana_entrada', y='duration')) +
            p9.geom_area(fill=color_map[3], alpha=0.5) +
            p9.geom_line(color=color_map[3]) +
            p9.labs(
                x='Data de Entrada (Semana)',
                y='Tempo Médio Gasto (Minutos)'
            ) +
            p9.theme_minimal()
        )
        return plot
    
    @render.plot
    def plot_cadastros():
        switch = input.select_plot()
        if switch == 'Cadastro de Professores':
            return plot_cadastros_profs()
        elif switch == 'RFM Score Médio':
            return plot_rfm_score()
        elif switch == 'Frequência Média de Acessos':
            return plot_frequencia()
        elif switch == 'Tempo Médio Gasto':
            return plot_duracao()

    
    @render.plot
    def plot_professores_estado():
        df = teachers_filtrado()
        # df['estado'] = df['estado'].fillna('Não Informado')
        estado_counts = df['estado'].value_counts().reset_index()
        estado_counts['estado'] = pd.Categorical(
            estado_counts['estado'],
            categories=estado_counts['estado'][::-1],
            ordered=True
        )
        estado_counts.columns = ['estado', 'professores_count']
        # Ordena os estados por quantidade de professores de forma decrescente
        estado_counts = estado_counts.sort_values('professores_count', ascending=False)
        plot = (
            p9.ggplot(estado_counts, p9.aes(x='estado', y='professores_count')) +
            p9.geom_bar(stat='identity', fill=color_map[0]) +
            p9.labs(
                x='',
                y='Número de Professores'
            ) +
            p9.theme_minimal() +
            p9.coord_flip()
        )
        return plot
    
    @render.plot
    def plot_utm_origem():
        df = teachers_filtrado()
        utm_counts = df['utm_origin'].value_counts().reset_index()
        utm_counts['utm_origin'] = pd.Categorical(
            utm_counts['utm_origin'],
            categories=utm_counts['utm_origin'][::-1],
            ordered=True
        )
        utm_counts.columns = ['utm_origin', 'professores_count']
        # Ordena os UTM por quantidade de professores de forma decrescente
        utm_counts = utm_counts.sort_values('professores_count', ascending=False)
        plot = (
            p9.ggplot(utm_counts, p9.aes(x='utm_origin', y='professores_count')) +
            p9.geom_bar(stat='identity', fill=color_map[0]) +
            p9.labs(
                x='',
                y='Número de Professores'
            ) +
            p9.theme_minimal() +
            p9.coord_flip()
        )
        return plot
    
    @render.plot
    def plot_matriz_rfm():
        duration_min = 0.5
        duration_max = 150
        df = teachers_filtrado()
        heatmap = df.groupby(['R_score', 'F_score']).agg({'Duration': 'mean'}).reset_index()
        heatmap['p_cut'] = pd.cut(heatmap['Duration'], bins=[0, 30, 150], labels=("low", "high"))
        heatmap['Duration'] = heatmap['Duration'].round(1)
        plot = (
            p9.ggplot(heatmap, p9.aes(x='R_score', y='F_score', fill='Duration')) +
            p9.geom_tile(p9.aes(width=0.95, height=0.95)) +
            p9.geom_text(p9.aes(label='Duration', color='p_cut'), size=9, show_legend=False) +
            p9.scale_color_manual(['white', 'black']) +
            p9.scale_fill_gradientn(colors=[color_map[1], color_map[3], color_map[2]], limits=(duration_min, duration_max), trans="log10") +
            # p9.scale_fill_cmap(cmap_name='viridis', trans="log10", limits=(duration_min, duration_max)) +
            p9.labs(
                x="Recência",
                y="Frequência",
                fill="Tempo (minutos)",
                title="Matriz RFM - Recência, Frequência e Tempo Gasto na Plataforma"
            ) +
            p9.theme_minimal() +
            p9.theme(
                panel_grid=p9.element_blank()
            )
        )
        return plot
    
    @render.plot
    def plot_interacoes():
        df = entries_filtrado()
        interacoes = df.groupby(['semana_inicio']).size().reset_index(name='interacoes_count')
        interacoes['semana_inicio'] = pd.to_datetime(interacoes['semana_inicio'])
        plot = (
            p9.ggplot(interacoes, p9.aes(x='semana_inicio', y='interacoes_count')) +
            p9.geom_area(fill=color_map[1], alpha=0.5) +
            p9.geom_line(color=color_map[1]) +
            p9.labs(
                x='Data de Início (Semana)',
                y='Número de Interações'
            ) +
            p9.theme_minimal()
        )
        return plot
    
app = App(app_ui, server)