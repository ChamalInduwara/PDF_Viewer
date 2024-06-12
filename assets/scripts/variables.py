import tkinter as tk

with open('assets/data/winfo.txt') as f:
    string = f.read().splitlines()

with open('assets/data/files.txt') as f:
    list = f.read().splitlines()

with open('assets/data/settings.txt') as f:
    string_2 = f.read().splitlines()

version = open('assets/data/version.txt', 'r').read()

settings = []
files = []
for i in string_2:
    settings.append(int(i))

for i in list:
    if i == '':
        list.pop(list.index(i))
    if i == 'None':
        list.pop(list.index(i))
    if '.pdf' not in i:
        list.pop(list.index(i))

try:
    additional = []

    for i in list:
        if i not in additional:
            additional.append(i)

    list.clear()
    for i in additional:
        list.append(i)

    for i in range(12):
        files.append(list[i])
except:
    pass

theme = open('assets/data/theme.txt', 'r').read()

tab_list_name = []
tab_list_item = []

width = int(string[0])
height = int(string[1])

if width > 1300:
    width = 950

if height > 690:
    height = 500

root = tk.Tk()

x = int((root.winfo_screenwidth() / 2) - (width / 2))

current_page = 0
current_file = -1
file_path = None
file_paths = []
doc = None
full_name = None
number = 0
open = False

window = None
pdf_view = None
app = None
view = None
load_pages = None
load_files = None
list_array = []

color = '#ff0000'
draw = False
nav = None
time = 0
time_1 = 0
time_2 = 0
time_3 = 0
time_4 = 0
time_5 = 0

pages_array = []
files_array = []
last_page = None
