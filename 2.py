import PySimpleGUI as sg

count    = 0
counting = False
font     = ("Courier New", 16)
big_font = ("Courier New", 40)

sg.theme("DarkBlue3")
sg.set_options(font=font)

layout = [
    [sg.Text(f"Counter:{count:0>3d}", font=big_font, key='-COUNTER-')],
    [sg.Button(button) for button in ("Start", "Stop/Pause", "Continue")],
]

window = sg.Window('Counter', layout, finalize=True)
counter = window['-COUNTER-']


while True:

    event, values = window.read(timeout=50)

    if event == sg.WINDOW_CLOSED:
        break
    elif event == "Start":
        count = 100
        counting = True
        counter.update(f"Counter:{count:0>3d}")
    elif event == "Stop/Pause":
        counting = False
    elif event == "Continue":
        counting = True
    elif event == sg.TIMEOUT_EVENT and counting:
        if count > 0:
            count -= 1
            counter.update(f"Counter:{count:0>3d}")
        else:
            counting = False

window.close()