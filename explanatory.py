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

teachers = pd.read_parquet("data/teachers_entries.parquet")
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

entries = pd.read_parquet("data/entries.parquet")
entries['data_inicio'] = pd.to_datetime(entries['data_inicio']).dt.tz_localize(None)
entries['semana_inicio'] = entries['data_inicio'] - pd.to_timedelta(entries['data_inicio'].dt.dayofweek, unit='d')

app_ui = ui.page_sidebar(
    ui.sidebar(
        "Filtros",
        ui.input_selectize(
            "r_score",
            "R Score",
            choices=r_score,
            selected=r_score,
            multiple=True
        ),
        ui.input_selectize(
            "f_score",
            "F Score",
            choices=f_score,
            selected=f_score,
            multiple=True
        ),
        ui.input_selectize(
            "m_score",
            "M Score",
            choices=m_score,
            selected=m_score,
            multiple=True
        ),
        ui.input_slider(
            "data_interacao",
            "Data de Interação",
            min=entries['data_inicio'].min(),
            max=entries['data_inicio'].max(),
            value=(entries['data_inicio'].min(), entries['data_inicio'].max()),
            time_format="%m/%Y",
        ),
    ),
    ui.layout_columns(
        # ui.value_box(
        #     "Cadastros nos últimos 30 dias",
        #     ui.output_text("cadastros_d30"),
        #     showcase=ui.HTML(icon_teacher),
        #     theme=ui.value_box_theme("aprendizap", bg=color_map[0], fg="white")
        # ),
        ui.value_box(
            "Interações nos últimos 30 dias",
            ui.output_text("interacoes_d30"),
            showcase=ui.HTML(icon_interaction),
            theme=ui.value_box_theme("aprendizap", bg=color_map[1], fg="white")
        ),
        # ui.card(
        #     ui.card_header("Cadastros dos Professores"),
        #     ui.card_body(
        #         ui.output_data_frame("table")
        #         ),
        # ),
        ui.card(
            ui.card_header("Interações dos Professores"),
            ui.card_body(
                ui.output_plot("plot_interacoes_tempo")
            ),
        ),
        ui.card(
            ui.card_header("Interações por Professor por Estado"),
            ui.card_body("Gráfico de interações por professor por estado"),
        ),
        ui.card(
            ui.card_header("Interações por Professor por Disciplina"),
            ui.card_body("Gráfico de interações por professor por disciplina"),
        ),
        col_widths=[3, 12]
    ),
    title="AprendiZAP - Grupo 01 | Explicativo"
)

def server(input, output, session):
    @reactive.calc
    def filtered_entries():
        start_date = pd.to_datetime(input.data_interacao()[0]).tz_localize(None)
        end_date = pd.to_datetime(input.data_interacao()[1]).tz_localize(None)
        return entries[
            (entries['data_inicio'] >= start_date) &
            (entries['data_inicio'] <= end_date)
        ]
    
    @render.text
    def cadastros_d30():
        return input.r_score()

    @render.text
    def interacoes_d30():
        df = filtered_entries()
        df = df[df['data_inicio'] >= (df['data_inicio'].max() - pd.Timedelta(days=30))]
        return f"{df.shape[0]:,d}".replace(",", ".")
    
    
    @render.plot
    def plot_interacoes_tempo():
        df = filtered_entries()
        semanais = df.groupby('semana_inicio').size().reset_index(name='contagem')
        plot = (
            p9.ggplot(semanais, p9.aes(x='semana_inicio', y='contagem')) +
            p9.geom_area(fill=color_map[1], alpha=0.5) +
            p9.geom_line(color=color_map[1], size=1) +
            p9.theme_minimal()
        )
        return plot

app = App(app_ui, server)
