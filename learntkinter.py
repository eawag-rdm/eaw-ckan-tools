import ckanapi
from Tkinter import *
from tkinter import ttk


#host = "http://eaw-ckan-dev1.eawag.wroot.emp-eaw.ch"
host = "http://localhost:5000"
# apikey = os.environ['CKAN_APIKEY']
apikey = '948b0f87-d710-4cec-9979-d1ac2fd0d186'
ckan = ckanapi.RemoteCKAN(host, apikey=apikey)

orgas = ckan.call_action('organization_list_for_user')
orga = orgas[0]
packagelist = ckan.call_action('package_search',
                               {'q':'owner_org:{}'.format(orga['id']),
                                'include_drafts': True,
                                'include_private': True
                               })

### patch core to include private !!



pkg = ckan.call_action('package_show',{'id':'whitefish-genomics'})

totalwidth = 1280
totalheight = 800
package = StringVar()
package.set("an_example_package_name that might be quite long")

root = Tk()

fr = ttk.Frame(root, width=totalwidth, height=totalheigth)
pkg_select = ttk.Combobox(textvariable=package)
fr.grid(column=0, row=0)
pkg_select.grid(column=0, row=0, sticky=()

# fr1 = ttk.Frame(fr, width=100, height=200)
# fr1.grid(row=1, column=2)
# fr1['borderwidth'] = 3
# fr1['relief'] = 'solid'


# logo = PhotoImage(file="/home/vonwalha/buero/logos/eaw-rdm1.png")
# labstring = StringVar()
# labstring.set('Bildunterschrift')

# lab1 = ttk.Label(fr, text="A Label")
# lab1['image'] = logo
# lab1['textvariable'] = labstring
# lab1['compound'] = 'bottom'
# lab1.grid(column=4, row=3)

# but = ttk.Button(fr, text="BUTTON")
# but.grid(column=3, row=3)

# def butcmd():
#     print "Hallo"

# def checkcmd():
#     print system.get()

# but['command'] = butcmd

# system = StringVar()
# check = ttk.Checkbutton(fr1, text="Metric?",
#                         command=checkcmd, variable=system, onvalue="metric",
#                         offvalue="imperial")
# check.grid()
# check['state'] = '!disabled'

# o = StringVar()
# radio1 = ttk.Radiobutton(fr, text='Option 1', variable=o, value=1)
# radio2 = ttk.Radiobutton(fr, text='Option 2', variable=o, value=2)
# radio3 = ttk.Radiobutton(fr, text='Option 3', variable=o, value=3)
# radio1.grid(column=1, row=5)
# radio2.grid(column=2, row=5)
# radio3.grid(column=3, row=5)

# entrycontent1 = StringVar()
# entrycontent2 = StringVar()
# entry1 = ttk.Entry(fr, textvariable=entrycontent1, width=40)
# entry2 = ttk.Entry(fr, textvariable=entrycontent2, width=40)
# entry1.insert(0,"WHATEVAR!")
# entry1.grid(column=1, row=6)
# entry2.grid(column=1, row=7)


# but1 = ttk.Button(fr, text="BUTTON 1")
# but1.grid()





#fr1.grid()
