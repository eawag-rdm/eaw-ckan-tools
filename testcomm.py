from Tkinter import *
from tkinter import ttk
import ckanapi

data_name = {'A': ['A1', 'A2', 'A3', 'A4', 'A5', 'A6'],
        'B': ['B1', 'B2', 'B3', 'B4', 'B5', 'B6']}

data_id = {'A': ['AA1', 'AA2', 'AA3', 'AA4', 'AA5', 'AA6'],
        'B': ['BB1', 'BB2', 'BB3', 'BB4', 'BB5', 'BB6']}

data_name2 = {}
for i in range(1,7):
    data_name2['A'+ str(i)] = [i*'a'] * 6
    data_name2['B'+ str(i)] = [i*'b'] * 6
data_id2 = {}
for i in range(1,7):
    data_id2['A'+ str(i)] = ['id_'+i*'a'] * 6
    data_id2['B'+ str(i)] = ['id_'+i*'b'] * 6


class MyCombobox(object):

    def __init__(self, label, position, parentframe, parameter, callback):
        '''
        label (str): Label
        position (tuple): (row, column)
        parentframe (tk.Frame)
        '''
 
        self.selected = {'name': StringVar(),
                         'id': '',
                         'idx': int()}

        self.parameter = parameter
        self.callback = callback
        self.values = []
        self.c = self._mk_combobox(label, parentframe, position)

        
    def refresh(self, parameter=None):
        if parameter is not None:
            self.parameter = parameter
        self.values = [{'name': v[0], 'id': v[1]}
                       for v in zip(data_name[self.parameter],
                                    data_id[self.parameter])]
        self.c.configure(values=self._values_items('name'))
        self._refresh_select(0)
        
    def status(self):
        print "Status of {}".format(self.__class__.__name__)
        print "parameter: {}".format(self.parameter)
        print ("selected: name= {}, id= {}, idx= {}"
               .format(self.selected['name'].get(),
                       self.selected['id'],
                       self.selected['idx']))

    def get_select(self):
        return(self.selected)
        
    def _values_items(self, item):
        return [v[item] for v in self.values]

    def _mk_combobox(self, label, parent, position):
        
        def _callback_selected(e):
            e.widget.select_clear()
            self._refresh_select(e.widget.current())
            print "_callback_selected fired"
            
            
        c = ttk.Combobox(parent, textvariable=self.selected['name'],
                         state='readonly',values=self._values_items('name'))
        c.bind('<<ComboboxSelected>>', _callback_selected)
        cl = ttk.Label(parent, text=label)
        cl.grid(row=position[0] - 1, column=position[1])
        c.grid(row=position[0], column=position[1])
        return(c)

    def _refresh_select(self, idx):
        ''' Updates info about selected entity'''
        self.selected['name'].set(self.values[idx]['name'])
        self.selected['id'] = self.values[idx]['id']
        self.selected['idx'] = idx
        if self.callback is not None:
            self.callback(self.selected)

            
class Organization(MyCombobox):
    
    def refresh(self, parameter=None):
        if parameter is not None:
            self.parameter = parameter

        orgas = ckan.call_action('organization_list_for_user',
                             {'permission': 'update_dataset'})
        self.values = [{'name': o['display_name'],
                        'id': o['id']} for o in orgas]
        self.c.configure(values=self._values_items('name'))
        self._refresh_select(0)

class Package(MyCombobox):
    
    def refresh(self, parameter=None):
        if parameter is not None:
            self.parameter = parameter
        org = ckan.call_action('organization_show',
                                     {'id': self.parameter,
                                      'include_datasets': True})
        self.values = [{'name': p['name'],
                        'id': p['id']} for p in org['packages']]
        self.c.configure(values=self._values_items('name'))
        self._refresh_select(0)
        
class Resource(MyCombobox):
    
    def _mk_combobox(self, label, parent, position):
        
        # def _callback_selected(e):
        #     e.widget.select_clear()
        #     self._refresh_select(e.widget.current())
        #     print "_callback_selected fired"
            
            
        c = ttk.Treeview(parent,
                         columns=['name', 'type', 'size', 'modified'],
                         show="headings",
                         height=20,
                         padding=10,
                         selectmode='browse')
        for h in range(0,4):
            c.heading(h, text = ['Name', 'Type', 'Size', 'Modified'][h])
            #c.bind('<<ComboboxSelected>>', _callback_selected)
        c.insert('',0, None, values = ['RESNAME', 'a type',
                                           'Giigabytes', '1970-01-01'])
        cl = ttk.Label(parent, text=label)
        cl.grid(row=position[0] - 1, column=position[1], columnspan=2)
        c.grid(row=position[0], column=position[1], columnspan=2)
        return(c)

    
    def refresh(self, parameter=None):
        if parameter is not None:
            self.parameter = parameter
        print "PARAMETER: {}".format(self.parameter)
        pkg = ckan.call_action('package_show', {'id': self.parameter})
        self.values = [{'name': r['name'],
                        'id': r['id'],
                        'modified':r['last_modified'],
                        'type': r['resource_type'],
                        'size': r['size']} for r in pkg['resources']]
        for item in self.c.get_children():
            self.c.delete(item)
        for v in self.values:
            self.c.insert('', 'end', values = [v['name'], v['type'],
                                               v['size'], v['modified']])
class ResourceMeta(object):
    def __init__(self, position, parentframe, parameter):
        '''
        label (str): Label
        position (tuple): (row, column)
        parentframe (tk.Frame)
        '''
        self.parameter = parameter # resource id
        
        self.frame = self._mk_frame(parentframe, position)
        self.name_d = StringVar()
        self.name = ttk.Entry(self.frame, textvariable=self.name_d)
        self.description = Text(self.frame, wrap=WORD)
        self.citation = Text(self.frame, wrap=WORD)
        self.the_pub_d = StringVar()
        self.the_pub = ttk.Checkbutton(self.frame,
                                               text = "The Package?",
                                               variable = self.the_pub_d)
        self.restype_d = StringVar()
        self.restype = ttk.Combobox(self.frame, textvariable=self.restype_d,
                                    state='readonly')
        self.name.grid(column=0, row=1)
        self.description.grid(column=0,row=2)
        self.citation.grid(column=0,row=3)
        self.the_pub.grid(column=0,row=4)
        self.restype.grid(column=0,row=5)
                                               
    def _mk_frame(self, parent, position):
        print "Making Frame"
        frame = ttk.Frame(parent, borderwidth=5, relief='ridge')
        frame.grid(row=position[0], column=position[1], columnspan=2)
        return(frame)

def callback_orga(selected):
    package.refresh(selected['id'])

def callback_package(selected):
    ressource.refresh(selected['id'])

url = 'http://localhost:5000'
apikey = '948b0f87-d710-4cec-9979-d1ac2fd0d186'
ckan = ckanapi.RemoteCKAN(url, apikey=apikey)
root = Tk()
root.title("Eawag RDM Resource Editor")
organization = Organization('Organization', [1,0], root, None, callback_orga)
package = Package('Package', [1,1], root, None, callback_package)
ressource = Resource('Resources',[3,0], root, None, None)
resmeta = ResourceMeta([4,0], root, None)
organization.refresh()



# mc2.refresh()
