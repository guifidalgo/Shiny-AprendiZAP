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


teachers = pd.read_parquet("data/teachers_entries.parquet")
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


icon_teacher = '<img src="https://github.com/guifidalgo/Shiny-AprendiZAP/blob/master/assets/teacher_white.png?raw=true" alt="Professor" width="50" height="50">'
icon_student = '<img src="https://github.com/guifidalgo/Shiny-AprendiZAP/blob/master/assets/student_white.png?raw=true" alt="Aluno" width="50" height="50">'
icon_interaction = '<img src="https://github.com/guifidalgo/Shiny-AprendiZAP/blob/master/assets/interaction_white.png?raw=true" alt="Interação" width="50" height="50">'
icon_speedometer = '<img src="https://github.com/guifidalgo/Shiny-AprendiZAP/blob/master/assets/speedometer_white.png?raw=true" alt="Velocímetro" width="50" height="50">'
icon_stopwatch = '<img src="https://github.com/guifidalgo/Shiny-AprendiZAP/blob/master/assets/stopwatch_white.png?raw=true" alt="Cronômetro" width="50" height="50">'


app_ui = ui.page_sidebar(
    ui.sidebar(
        "Filtros",
        ui.input_switch(
            'switch_valid',
            'Apenas Usuários Válidos',
            value=False
            ),
        ui.input_slider(
            "slider_rfm_score",
            label="Score RFM",
            min=rfm_score[0],
            max=rfm_score[-1],
            value=(rfm_score[0], rfm_score[-1])
        ),
        # ui.input_selectize(
        #     'select_r_score',
        #     'Recência',
        #     choices=r_score,
        #     multiple=True,
        #     selected=r_score,  # Seleciona todas as faixas por padrão
        # ),
        # ui.input_selectize(
        #     'select_f_score',
        #     'Frequência',
        #     choices=f_score,
        #     multiple=True,
        #     selected=f_score,  # Seleciona todas as faixas por padrão
        # ),
        # ui.input_selectize(
        #     'select_m_score',
        #     'Monetização (Tempo Gasto)',
        #     choices=m_score,
        #     multiple=True,
        #     selected=m_score,  # Seleciona todas as faixas por padrão
        # ),
        ui.input_slider(
            "slider_date",
            label="Data de Cadastro:",
            min=teachers['semana_entrada'].min(),
            max=teachers['semana_entrada'].max(),
            value=(teachers['semana_entrada'].min(), teachers['semana_entrada'].max()),
            time_format="%m/%Y",
        ),
        bg="#f8f8f8"
    ),
    ui.layout_columns(
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
            ui.card_header("Cadastro de Professores"),
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
            ui.card_header("UTM Origem"),
            ui.card_body(
                ui.output_plot("plot_utm_origem")
            )
        ),
        ui.card(
            ui.card_header("Matriz RFM - Recência, Frequência e Tempo Gasto na Plataforma"),
            ui.card_body(
                ui.output_plot("plot_matriz_rfm")
            )
        ),
        col_widths=[3, 3, 3, 3, 12, 6, 6, 12]
    ),
    title="AprendiZAP - Grupo 01",
)



def server(input, output, session):
    @reactive.calc
    def teachers_filtrado():
        start_date = pd.to_datetime(input.slider_date()[0]).tz_localize(None)
        end_date = pd.to_datetime(input.slider_date()[1]).tz_localize(None)
        start_rfm = input.slider_rfm_score()[0]
        end_rfm = input.slider_rfm_score()[1]
        if input.switch_valid():
            df = teachers[teachers['usuario_valido'] == True]
        else:
            df = teachers
        return df[
            (df['semana_entrada'] >= start_date) &
            (df['semana_entrada'] <= end_date) &
            (df['RFM_Score'] >= start_rfm) &
            (df['RFM_Score'] <= end_rfm)
        ]


    @render.text
    def qtd_professores():
        return f"{teachers_filtrado().shape[0]:,d}"
    
    @render.text
    def media_score_rfm():
        df = teachers_filtrado()
        return f"{df['RFM_Score'].mean():,.2f}"

    @render.text
    def media_acessos():
        df = teachers_filtrado()
        return f"{df['Frequency'].mean():,.2f}"
    
    @render.text
    def media_duracao_acessos():
        df = teachers_filtrado()
        return f"{df['Duration'].mean():,.2f}"

    @render.plot
    def plot_cadastros():
        df = teachers_filtrado()
        semanais = df.groupby(['semana_entrada']).size().reset_index(name='cadastros_count')
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
        df = teachers_filtrado()
        heatmap = df.groupby(['R_score', 'F_score']).agg({'Duration': 'mean'}).reset_index()
        heatmap['p_cut'] = pd.qcut(heatmap['Duration'], 2, labels=("low", "high"))
        heatmap['Duration'] = heatmap['Duration'].round(1)
        plot = (
            p9.ggplot(heatmap, p9.aes(x='R_score', y='F_score', fill='Duration')) +
            p9.geom_tile(p9.aes(width=0.95, height=0.95)) +
            p9.geom_text(p9.aes(label='Duration', color='p_cut'), size=9, show_legend=False) +
            p9.scale_color_manual(['white', 'black']) +
            p9.scale_fill_cmap(cmap_name='viridis', trans="log10") +
            # p9.scale_x_discrete(limits=heatmap['R_score'].unique()[::-1]) +
            # p9.scale_y_discrete(limits=heatmap['F_score'].unique()[::-1]) +
            p9.labs(
        x="Recência",
        y="Frequência",
        fill="Tempo"
    )
)
        return plot

app = App(app_ui, server)