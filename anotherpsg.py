from time import sleep
import PySimpleGUI as sg

def func(win, index):
    for i in range(0, 51):
        sleep(0.1)
        win.write_event_value('Update', (f'P{index}', i))

sg.theme('DarkBlue3')
layout = [
    [sg.Text('', size=(50, 1), relief='sunken', font=('Courier', 11), text_color='yellow', background_color='black',key=f'P{i}')] for i in (1, 2)] + [
    [sg.Button('Start')],
]
window = sg.Window("Title", layout)
sg.theme('DarkBlue4')

while True:

    event, values = window.read()

    if event == sg.WIN_CLOSED:
        break
    elif event == 'Start':
        window['Start'].update(disabled=True)
        window['P1'].update('')
        window['P2'].update('')
        window.perform_long_operation(lambda win=window, index=1:func(win, index), "P1 Done")
    elif event == "P1 Done":
        if sg.popup_yes_no("Step 2 ?") == 'Yes':
            window.perform_long_operation(lambda win=window, index=2:func(win, index), "P2 Done")
        else:
            window['Start'].update(disabled=False)
    elif event == "P2 Done":
        window['Start'].update(disabled=False)
    elif event == 'Update':
        key, i = values[event]
        window[key].update('¯\_( ͡° ͜ʖ ͡°)_/¯'*i)

window.close()