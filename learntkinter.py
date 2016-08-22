import ckanapi
from Tkinter import *
from tkinter import ttk


class App(object):

    def __init__(self, url, apikey):
        self.ckan = ckanapi.RemoteCKAN(url, apikey=apikey)
        self.orgas_name, self.orgas_id = self._get_organizations('update_dataset')

        
    def _get_organizations(self, permission):
        orgas = ckan.call_action('organization_list_for_user',
                             {'permission': permission})
        return zip(*[(o['display_name'], o['id']) for o in orgas])

    def _get_packages(self, orga):
        packagelist = ckan.call_action('package_search',
                                    {'q':'owner_org:{}'.format(orga),
                                    'include_drafts': True,
                                    'include_private': True
                                })
        return zip(*[(p['name'], p['id']) for p in packagelist['results']])
        #return zip(*[(p['name'], p['id']) for p in packagelist])

    


app = App("http://localhost:5000", '948b0f87-d710-4cec-9979-d1ac2fd0d186')

#print app.test
print app.orgas_name
print app.orgas_id

print app._get_packages(app.orgas_id[1])

    

def selection_clear(e):
    e.widget.selection_clear()

totalwidth = 1280
totalheight = 800

root = Tk()
fr = ttk.Frame(root, width=totalwidth, height=totalheight)
fr.grid(column=0, row=0)

organization_value = StringVar()
organization = ttk.Combobox(fr, textvariable=organization_value, state='readonly', height=5)

orgas = [o['display_name'] for o in
         get_organizations('update_dataset')]
orgas.sort()
organization['values'] = orgas
organization_value.set(orgas[0])

organization.grid(column=0, row=1)
organization.bind("<<ComboboxSelected>>", selection_clear)
organization.bind("<<ComboboxSelected>>", refresh_packages)

l = ttk.Label(fr, text="LABEL")
l.grid(column=1,row=0)
l.bind('<1>', dummy)

root.mainloop()


    #host = "http://eaw-ckan-dev1.eawag.wroot.emp-eaw.ch"
    # apikey = os.environ['CKAN_APIKEY']
