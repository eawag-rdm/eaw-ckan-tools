import ckanapi
from Tkinter import *
from tkinter import ttk

class Organization(object):
    
    def __init__(self, ckan, parent, col, row):
        self.ckan = ckan
        self.col = col
        self.row = row
        self.master = parent
        self.names = []
        self.ids = []
        self.selected = {'name': StringVar(),
                         'id': StringVar(),
                         'idx': IntVar()}
        self.refresh('update_dataset')

        self._mk_orga_combobox()
        
    def _select(self, idx):
        if len(self.ids) > idx and idx < len(self.ids):
               self.selected['idx'].set(idx)
               self.selected['id'].set(self.ids[idx])
               self.selected['name'].set(self.names[idx])
        else:
               self.selected['idx'].set(-1)
               self.selected['id'].set('')
               self.selected['name'].set('')
        

    def refresh(self, permission):
        orgas = self.ckan.call_action('organization_list_for_user',
                             {'permission': permission})
        self.names, self.ids = zip(*[(o['display_name'], o['id'])
                                     for o in orgas])
        self._select(0)
        
        
    def _mk_orga_combobox(self):
        
        def _callback_selected(e):
            e.widget.select_clear()
            print '_callback_selected: {}'.format(self.selected['name'].get())
            
        c = ttk.Combobox(self.master, textvariable=self.selected['name'],
                         state='readonly',values=self.names)
        c.bind('<<ComboboxSelected>>', _callback_selected)
        cl = ttk.Label(self.master, text="Organization")
        cl.grid(column=self.col, row=self.row-1)
        c.grid(column=self.col, row=self.row)
        return(c)

    
class App(object):


    def __init__(self, url, apikey, root):
        self.root = root
        self.root.title('Eawag RDP resource editor')
        self.ckan = ckanapi.RemoteCKAN(url, apikey=apikey)
        
        # main frame
        self.fr0 = self._mk_frame()
        # Organization Combobox
        self.orga_cbox = Organization(self.ckan, self.fr0, 0, 1)

    def _mk_frame(self, width=1280, height=800):
        f = ttk.Frame(self.root, width=width, height=height)
        f.grid_propagate(False)
        f.grid()
        return(f)


    def _get_packages(self, orga):
        packagelist = self.ckan.call_action('package_search',
                                    {'q':'owner_org:{}'.format(orga),
                                    'include_drafts': True,
                                    'include_private': True
                                })
        return zip(*[(p['title'], p['id']) for p in packagelist['results']])
        
#if __name__ == '__main__':
root = Tk()
app = App("http://localhost:5000", '948b0f87-d710-4cec-9979-d1ac2fd0d186', root)
# c = organization(root, 0, 1)
# url = 'http://localhost:5000'
# apikey = '948b0f87-d710-4cec-9979-d1ac2fd0d186'
# ckan = ckanapi.RemoteCKAN(url, apikey=apikey)
# o = Organization(ckan, root, 0, 1)
root.mainloop()









#print app.test
# print app.orgas_name
# print app.orgas_id

# print app._get_packages(app.orgas_id[1])

    

# def selection_clear(e):
#     e.widget.selection_clear()

# total
# total


# fr = ttk.Frame(root, width=totalwidth, height=totalheight)
# fr.grid(column=0, row=0)
# organization_value = StringVar()
# organization = ttk.Combobox(fr, textvariable=organization_value, state='readonly', height=5)

# orgas = [o['display_name'] for o in
#          get_organizations('update_dataset')]
# orgas.sort()
# organization['values'] = orgas
# organization_value.set(orgas[0])

# organization.grid(column=0, row=1)
# organization.bind("<<ComboboxSelected>>", selection_clear)
# organization.bind("<<ComboboxSelected>>", refresh_packages)


# l = ttk.Label(fr, text="LABEL")
# l.grid(column=1,row=0)
# l.bind('<1>', dummy)

# root.mainloop()


#     #host = "http://eaw-ckan-dev1.eawag.wroot.emp-eaw.ch"
#     # apikey = os.environ['CKAN_APIKEY']


# class Holla(object):

#     b = 7
    
#     def __init__(self):
#         self.a = list()
#         self.a.append("first element")

        
