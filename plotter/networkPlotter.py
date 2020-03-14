import matplotlib.pyplot
import tkinter
import threading
import numpy
import math
import io
import random
from PIL import Image, ImageTk
from controllers.workflow_controller.flowVaribale import FlowVaribale as FVar
from pylab import array

external_img=[int(i) for i in list("11111111110000111111111111111111100000" \
    "11111111111111101110000001110111111111" \
    "00011100001110001111111000001100000100" \
    "00011111000000000000000000001111100000" \
    "00110100000001111111000001111110000011" \
    "11111110001111111100011111101000011111" \
    "11111000101000000011111111111100000000" \
    "00001111111111110000000000000111111111" \
    "11000000000000111111111111000000101100" \
    "01111111111000101111111000111111110001" \
    "11111111000001111110000011111110000000" \
    "10010000000111110000000000000000000011" \
    "11100000110000110000011111110001110000" \
    "11100011111111101110000011110111111111" \
    "11111100000111111111111111111000001111111111")]
size=24

external_img1=[]
[[external_img1.append(int(abs(i-size/2)>=2 and abs(j-size/2)>=2)) for j in range(size)]for i in range(size)]
import copy
class NetworkPlotter():
    _plotters={}
    def __init__(self,net_id,counters,net_metadatas,callback=lambda :0,parameters=None):

        self.callback=callback
        self.net_id=net_id
        self.counters=counters
        self.train_parameters=parameters
        self.parameters_copy={}
        self.elements={}
        self.images = {}
        self.on_selected=None
        self.selected_labels={}
        self.plot_figures={}
        self.option_vars = {}
        self.apply_list = {}
        self.lineage_status={}
        self.net_metadatas=net_metadatas
        self.real_h=0
        self.real_w=0
        self.on_hooked=False
        self.ploted=False
        self.counter_views={(c.net_id,c.name):[c] for c in self.counters}
        self.hidden_counters=set({})
        t=threading.Thread(target=self.show_window)
        t.start()


    def show_window(self):
        self.window = tkinter.Tk()
        self.window_width,self.window_height=int(self.window.winfo_screenwidth()/2.3),int(self.window.winfo_screenheight()/2.3)
        self.width,self.height=self.window_width,self.window_height-50
        self.x, self.y = self.window.winfo_screenwidth()-10-self.window_width,self.window.winfo_screenheight()-40-self.window_height
        self.window.title("CCA TrainViewer" )
        self.window.geometry(str(self.width)+"x"+str(self.height)+"+"+str(self.x)+"+"+str(self.y))

        self.layer_label=tkinter.Label(self.window,background="#aaaaaa",width=91,height=51)
        self.layer_label.pack()
        self.title_frame=tkinter.Frame(self.window)
        self.title_frame.place(x=0, y=0, width=self.width, height=50)
        sv1 = tkinter.StringVar(value="100")
        tkinter.Button(self.title_frame, font=25, text="Set",
                       command=lambda: self.set_scale(sv1.get(), "priority")).pack(side="left")




        tkinter.Scale(self.title_frame,from_=10,to=500,length=110,resolution=10,
                      orient=tkinter.HORIZONTAL,variable=sv1
                      ,command=lambda e:self.set_scale(e,"priority")).pack(side="left")
        tkinter.Label(self.title_frame,font=25,text=":size").pack(side="left")
        sv=tkinter.StringVar(value=str(self.height/self.width))
        tkinter.Button(self.title_frame,font=25,text="Set",command=lambda :self.set_scale(sv.get(),"aspectRatio")).pack(side="right")
        tkinter.Scale(self.title_frame,from_=10,to=500,length=110, resolution=3,
                      orient=tkinter.HORIZONTAL,variable=sv
                      ,command=lambda e:self.set_scale(e,"aspectRatio")).pack(side="right")
        tkinter.Label(self.title_frame,font=25,text="shape:").pack(side="right")

        title_label=tkinter.Label(self.title_frame,foreground="#ff0000",
                font=25,text="<"+self.net_metadatas["type"]+ "> - "+self.net_metadatas["name"] )
        title_label.pack()
        btn=tkinter.Button(self.title_frame,text="Refurbish",command=self.repaint)
        btn.pack()
        self.label_frame=tkinter.Frame(self.window,background="#cde")
        self.label_frame.place(x=0,y=50,width=self.width,height=self.height)

        get_img=lambda e:ImageTk.PhotoImage(Image.fromarray(array([(i/2+0.5)*235 for i in e]).reshape(24,24)))

        self.add_btn_img=get_img(external_img1)
        self.cfg_btn_img = get_img(external_img)

        self.cfg_panel = tkinter.Canvas(self.window)
        self.cfg_panel_width=250
        self.cfg_panel_open=False

        self.cfg_frame = tkinter.Frame(self.cfg_panel)
        self.cfg_frame.place(width=self.cfg_panel_width - 20, height=2000)

        vbar = tkinter.Scrollbar(self.cfg_panel, orient=tkinter.VERTICAL)
        vbar.pack(side = tkinter.RIGHT,fill = tkinter.Y)
        vbar.configure(command=self.cfg_panel.yview)
        self.cfg_panel.config(yscrollcommand=vbar.set)
        self.cfg_panel.create_window(115, 0, window=self.cfg_frame, anchor="n")

        self.add_panel = tkinter.Canvas(self.window)
        self.add_panel_width = 250
        self.add_panel_open = False

        self.add_frame = tkinter.Frame(self.add_panel)
        self.add_frame.place(width=self.add_panel_width - 20, height=2000)

        abar = tkinter.Scrollbar(self.add_panel, orient=tkinter.VERTICAL)
        abar.pack(side=tkinter.LEFT, fill=tkinter.Y)
        abar.configure(command=self.add_panel.yview)
        self.add_panel.config(yscrollcommand=abar.set)
        self.add_panel.create_window(115, 0, window=self.add_frame, anchor="n")

        #
        # hbar = tkinter.Scrollbar(self.cfg_panel, orient=tkinter.HORIZONTAL)  # 水平滚动条
        # hbar.pack(side = tkinter.BOTTOM,fill = tkinter.X)
        # hbar.configure(command=self.cfg_panel.xview)



        tkinter.Button(self.window, command=self.add_menu, image=self.add_btn_img,width=28,height=28).pack(pady=50,side="right",anchor="n")

        tkinter.Button(self.window, command=self.cfg_menu,image=self.cfg_btn_img).place(x=0,y=50,width=36,height=36)

        tkinter.Label(self.cfg_panel, text=chr(32) * 7 + "configures", background="#ccc",
                      width=int(self.cfg_panel_width/10)).pack()

        tkinter.Label(self.add_panel, text="functions", background="#ccc",
                      width=int(self.add_panel_width/10)).pack()
        self.full_menu()
        self.callback()


        self.window.bind("<Configure>",self.resize)
        self.window.mainloop()

    def full_menu(self):

        params=self.train_parameters.get_parameters()
        self.y_offset=65
        self.y_offset_1=300
        tkinter.Label(self.cfg_frame).pack()
        tkinter.Label(self.cfg_frame, text="parameters", background="#cde").pack(fill=tkinter.X)
        from system.train.trainingParameterSystem import TrainingParameterSystem



        def insert_propertys(window,dict,func,ts):
            self.parameters_copy[id(window)] = copy.copy(dict)
            self.option_vars[id(window)]={}
            self.apply_list[id(window)]=set({})
            for k,v in dict.items():

                if k in ts.keys() and type(v) in [bool,int,float,str]:
                    types = {bool: {"to": 1, "resolution": 1, "length": 60}
                        , int: {"to": ts[k], "resolution": 1, "length": 140}
                        , float: {"to": ts[k], "resolution": ts[k] / 500, "length": 220}
                        , str: None}
                    #place(y=self.y_offset,width=230,height=30)
                    tkinter.Label(window,text=k+":",background="#fff").pack(fill=tkinter.X)
                    if isinstance(v,str):
                        self.option_vars[id(window)][k] = (type(v), tkinter.StringVar(value=v))
                        label=tkinter.Label (window,text=v)
                        label.pack(fill=tkinter.X)
                        #tkinter.Entry(l, textvariable=self.option_vars[id(window)][k]).pack(fill=tkinter.X)
                        def select(e=self.apply_list[id(window)].add(k),r=k,l=label,s=[False]):
                            s[0]=not s[0]
                            if s[0]:
                                l.configure(background="#999")
                                self.on_selected=(l,self.option_vars[id(window)][r][1])
                            else:
                                l.configure(background="#eee")
                                self.on_selected=None
                        label.bind("<Button-1>",select)

                    else:
                        self.option_vars[id(window)][k]=(type(v),tkinter.DoubleVar(value=v))
                        tkinter.Scale(window,orient=tkinter.HORIZONTAL,from_=0,
                                      variable=self.option_vars[id(window)][k][-1],**types[type(v)]
                                      ,command=lambda e,r=k:self.apply_list[id(window)].add(r)).pack()
                    func()

        def add():self.y_offset += 40
        insert_propertys(self.cfg_frame,params,add,TrainingParameterSystem.settable_parameters)
        tkinter.Button(self.cfg_frame,text="Apply",command=lambda :
                        self.apply(id(self.cfg_frame),self.train_parameters.update_parameters)).pack(fill=tkinter.X,pady=3)

        tkinter.Button(self.cfg_frame,text="Reset",command=lambda :
                        self.reset(id(self.cfg_frame),self.train_parameters.update_parameters)).pack(fill=tkinter.X,pady=3)

        tkinter.Button(self.cfg_frame,text="Save").pack(fill=tkinter.X,pady=3)
        tkinter.Label(self.cfg_frame, text="operations", background="#cde").pack(fill=tkinter.X)
        #=============================add_frame===============================
        s=" "*12
        listener=tkinter.Label(self.add_frame, text=" "*1000)
        def enter_key(e):
            if self.on_selected:
                value=self.on_selected[1].get()+e.char
                if e.char=="\x08" :
                    if len(value) == 0:return
                    value=self.on_selected[1].get()[:-1]
                self.on_selected[1].set(value)
                self.on_selected[0].configure(text=self.on_selected[1].get())

        listener.focus_set()
        listener.bind('<Key>', enter_key)
        listener.pack()
        tkinter.Label(self.add_frame, text=s+"graphic", background="#cde").pack(fill=tkinter.X)
        tkinter.Label(self.add_frame, text=s+"marge", background="#fff").pack(fill=tkinter.X)
        tkinter.Button(self.add_frame, text=s+"Marge Selected", command=self.view_marge).pack(fill=tkinter.X)
        tkinter.Label(self.add_frame, text=s+"split", background="#fff").pack(fill=tkinter.X)
        tkinter.Button(self.add_frame, text=s+"Split Selected", command=self.view_split).pack(fill=tkinter.X)
        tkinter.Label(self.add_frame, text=s+"clean", background="#fff").pack(fill=tkinter.X)
        #tkinter.Scale(self.add_frame,from_=0,orient=tkinter.HORIZONTAL,variable=tkinter.DoubleVar(value=0),
                     # **{"to": 100, "resolution": 1, "length": 140}).pack()
        tkinter.Button(self.add_frame, text=s+"Clean Selected", command=self.view_clean).pack(fill=tkinter.X)
        tkinter.Label(self.add_frame, text=s+"property", background="#cde").pack(fill=tkinter.X)
        from counters.counter import Counter
        def add():self.y_offset_1+=40
        insert_propertys(self.add_frame,Counter.default,add,Counter.settable_parameters)
        update=lambda dict: [[c.metadatas.update(dict)
                       for c in self.counter_views[l]] for l in self.get_labels()]
        tkinter.Button(self.add_frame, text=s + "Apply Selected",
                       command=lambda :self.apply(id(self.add_frame),update)).pack(fill=tkinter.X)
        tkinter.Button(self.add_frame, text=s + "Reset Selected",
                       command=lambda :self.reset(id(self.add_frame),update)).pack(fill=tkinter.X)
        tkinter.Button(self.add_frame, text=s + "Save Selected").pack(fill=tkinter.X)
        tkinter.Label(self.add_frame, text=s+"creation", background="#cde").pack(fill=tkinter.X)
        tkinter.Label(self.add_frame, text=s+"plane",background="#fff").pack(fill=tkinter.X)
        tkinter.Label(self.add_frame, text=s+"3d", background="#fff").pack(fill=tkinter.X)
        tkinter.Button(self.add_frame,text=s+"New Plot", background="#cde").pack(ipady=6,padx=10,pady=20,fill=tkinter.X)
        tkinter.Button(self.add_frame,text=s+"Hidden",command=lambda :[[self.hidden_counters.add(k)
                                                                for k in self.selected_labels],self.repaint()]).pack(fill=tkinter.X)
        tkinter.Button(self.add_frame,text=s+"Detect",command=lambda :[self.hidden_counters.remove(k)
                                                                for k in self.selected_labels if k in
                                                                       self.hidden_counters]).pack(fill=tkinter.X)
        tkinter.Button(self.add_frame,text=s+"Delete").pack(fill=tkinter.X)
    def update(self):

        from system.train.trainingParameterSystem import TrainingParameterSystem
        [self.option_vars[id(self.cfg_frame)][k][1].
             set(float(v)) for k,v in self.train_parameters.get_parameters().items()
                                    if k in TrainingParameterSystem.settable_parameters]
    def reset(self,window,func):
        [v[1].set(self.parameters_copy[window][k]) for k,v in self.option_vars[window].items()]
        func(self.parameters_copy[window])
    def apply(self,window,func):
        func({v:self.option_vars[window][v][0](self.option_vars[window][v][1].get())for v in self.apply_list[window]})

        self.apply_list[window]=set([i for i in self.apply_list[window]if self.option_vars[window][i][0]==str])
        self.repaint()
        self.resize()
    def add_menu(self):
        self.add_panel_open = not self.add_panel_open
        if self.add_panel_open:
            self.label_frame.place(width=self.width - self.add_panel_width)
            self.add_panel.place(x=self.width-self.add_panel_width, y=50, width=self.add_panel_width, height=self.height)
        else:
            self.label_frame.place(width=self.width+self.add_panel_width)
            self.add_panel.place_forget()
        self.resize()
    def cfg_menu(self):
        self.cfg_panel_open=not self.cfg_panel_open
        if self.cfg_panel_open:
            self.cfg_panel.place(x=0, y=50, width=self.cfg_panel_width, height=self.height)
        else:
            self.label_frame.place(x=0)
            self.cfg_panel.place_forget()
        self.resize()
    def set_scale(self,e, str):
        for m in self.get_labels().values():
            m["plot." + str] = float(e)/100
        self.resize()
    def repaint(self):
        self.update()
        self.plot(True)
    def resize(self,event=None):
        loc=(self.window.winfo_width(),self.window.winfo_height())
        if self.ploted and (event==None or ((event.width,event.height)==loc and (self.real_w,self.real_h)!=loc)):
            main=[]
            self.real_h=self.window.winfo_height()
            self.real_w=self.window.winfo_width()
            self.height=self.window.winfo_height()-50
            self.width=self.window.winfo_width()
            self.title_frame.place(width=self.width)
            self.width-=int(self.cfg_panel_open)*self.cfg_panel_width+int(self.add_panel_open)*self.add_panel_width

            self.label_frame.place_configure(x=int(self.cfg_panel_open)*self.cfg_panel_width,
                                   width=self.width,height=self.height)
            self.cfg_panel.place_configure(width=int(self.cfg_panel_open)*self.cfg_panel_width,height=self.height)
            #self.label_frame.winfo_height() var
            self.cfg_panel.configure(scrollregion=(0,0,0,self.y_offset*2))
            self.add_panel.place_configure(x=int(self.add_panel_open)*self.window.winfo_width()-self.add_panel_width,height=self.height)
            self.add_panel.configure(scrollregion=(0, 0, 0,self.y_offset_1 * 2))
            for k in self.elements.keys():
                for c in self.counters :
                    if c.net_id == k[0] and c.name == k[1] and k not in  self.hidden_counters:
                        main.append((c, c.metadatas))
            for k,p in self.get_layout(main).items():
                if k not in self.hidden_counters:
                    self.elements[k].place_configure(**p)
    def get_layout(self,metas):
        self.total_width,self.total_height=0,0
        metas=sorted(metas,key=lambda e:e[1]["plot.priority"]**2+e[1]["plot.aspectRatio"],reverse=True)
        d=self.width/self.height
        pleces={}
        vertexs = set({})
        onused=set({})
        def add_vertex(x,y,w,h):#曼哈顿拐点
            onused.add((x, y))#define x=0,y=0,w=50,h=100
            vertexs.add((x+w,y)) #add 3 vertex at (50,0) (0,100) (50,100)
            vertexs.add((x,y+h))
            vertexs.add(((x+w),(y+h)))
            return (x,y,w,h)
        def no_crash(x,y,w,h):
            if (x + w <= self.total_width and y + h <= self.total_height):
                for k,p in pleces.items():
                    if x+w>p["x"] and x<p["x"]+p["width"] and y+h>p["y"] and y<p["y"]+p["height"]:
                        return False
                return True
        def get_place(w,h):
            if len(vertexs)==0:
                self.total_width,self.total_height=w,h
                vertexs.add((0,0))
            for x,y in sorted(vertexs,key=lambda e:e[0]+e[1]):
                if no_crash(x,y,w,h) and (x,y) not in onused:
                    return add_vertex(x,y,w,h)
        for c, meta in metas:
            size, ar = meta["plot.priority"], meta["plot.aspectRatio"]
            place = get_place(size, size * ar)
            if not place:
                if self.total_width / self.total_height > d:
                    place = add_vertex(0, self.total_height, size, size * ar)
                    self.total_height += size * ar
                else:
                    place = add_vertex(self.total_width, 0, size, size * ar)
                    self.total_width += size

            pleces[(c.net_id, c.name)] = {k:v for k,v in zip(["x","y","width","height"],place)}
        if self.total_width / self.total_height > d:
            resize=self.width/self.total_width
            offest=[0,(self.height-self.total_height*resize)/2,0,0]
        else:
            resize=self.height/self.total_height
            offest=[(self.width-self.total_width*resize)/2,0,0,0]
        return {ci:{k:v for k,v in zip(p.keys(),FVar(p.values())*resize+offest)} for ci,p in pleces.items()}

    def plot(self,repaint=False):
        if self.window:

            #self.full_menu()
            params=self.train_parameters.get_parameters()
            self.layer_label.pack_forget()
            groups={k.net_id:[]for k in self.counters }
            for k in self.counters:groups[k.net_id].append(k)
            main=[c for c in groups[self.net_id ]
                  if repaint or not self.lineage_status or len(c.get_lineage((c.net_id,c.name)))!=self.lineage_status[(c.net_id,c.name)]]
            self.lineage_status={(c.net_id,c.name):len(c.get_lineage((c.net_id,c.name))) for c in groups[self.net_id ]}
            layouts=self.get_layout([(c,c.metadatas)for c in groups[self.net_id ]
                                     if (c.net_id, c.name) not in self.hidden_counters])

            for counter in main:
                ckey = (counter.net_id, counter.name)
                if ckey not in self.hidden_counters:

                    metas=counter.metadatas
                    if ckey not in self.plot_figures.keys():
                        figure = matplotlib.pyplot.figure(figsize=(3.5,3.5*metas["plot.aspectRatio"]))
                        ax1 =figure.add_subplot(1,1,1,polar=metas["plot.polar"])
                        ax1.set_title(counter.name)
                        self.plot_figures[ckey]=(figure,ax1)
                    else:

                        figure,ax1=self.plot_figures[ckey]
                        ax1.clear()
                        ax1.set_title(counter.name)
                        figure.set_figheight(3.5*metas["plot.aspectRatio"])
                    if hasattr(ax1,metas["plot.type"]):
                        plot=getattr(ax1, metas["plot.type"])
                        for counter in self.counter_views[ckey]:
                            linedata=counter.get_lineage((counter.net_id, counter.name))

                            get_rule=lambda x:[i*params[metas["plot.rule"]] for i in range(len(x))]
                            def draw(counter,data):
                                args = [get_rule(data), data]
                                if metas["plot.type"] == "hist": args = [args[-1]]
                                plot(*args, color=counter.metadatas["plot.color"],
                                     alpha=counter.metadatas["plot.alpha"], **metas["plot.params"])
                            if len(linedata)>0 and isinstance(linedata[-1],list):
                                for i in range(len(linedata[-1])):draw(counter,numpy.array(linedata)[:,i])
                            else:
                                draw(counter,counter.get_lineage((counter.net_id, counter.name)))


                        layout=layouts[ckey]
                        buf= numpy.array(self.get_img_from_fig(figure))
                        size=(int(layout["width"]*0.95),int(layout["height"]*0.95))
                        try:
                            self.images[ckey]=ImageTk.PhotoImage(Image.fromarray(buf,"RGB").resize(size))
                            if ckey in self.elements.keys():
                                label=self.elements[ckey]
                                label.configure(image=self.images[ckey])
                            else:
                                label =tkinter.Label(self.label_frame,image=self.images[ckey],background="#ddd")
                                label.place(**layout)
                                label.bind("<Button-1>",lambda a,l=label,m=(ckey,metas),switch=[True]:self.window_configure(l,m,switch))
                                self.elements[ckey]=label

                        except:pass
                else:
                    self.elements[ckey].place_forget()

            self.ploted=True

    def view_clean(self):
        pass
    def view_split(self):
        for k in self.get_labels():
            if k in self.counter_views and len(self.counter_views[k])>1:
                l=self.counter_views.pop(k)
                for c in l:
                    if (c.net_id,c.name) in self.hidden_counters:self.hidden_counters.remove((c.net_id,c.name))
                    self.counter_views[(c.net_id,c.name)]=[c]
                self.counter_views[k]=[l[0]]
        self.repaint()
        self.resize()
    def get_labels(self):
        return {k:v for k,v in self.selected_labels.items()if k not in self.hidden_counters}
    def view_marge(self):
        kc=list(self.get_labels().keys())[0]

        for k in self.get_labels():
            if k in self.counter_views:
                if k != kc:
                    for c in self.counter_views.pop(k):
                        self.hidden_counters.add(k)
                        self.counter_views[kc].append(c)
        self.repaint()
        self.resize()
    def window_configure(self,label,kv,switch):
        if switch[0]:
            c="#f00"
            if len(self.counter_views[kv[0]])>1:c="#f0a"
            self.selected_labels[kv[0]]=kv[1]
        else:
            c="#ddd"
            self.selected_labels.pop(kv[0])
        switch[0]=not switch[0]
        label.configure(background=c)
    def get_img_from_fig(self,fig, dpi=180):
        import cv2
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=dpi)
        buf.seek(0)
        img_arr = numpy.frombuffer(buf.getvalue(), dtype=numpy.uint8)
        buf.close()
        img = cv2.imdecode(img_arr, 1)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return img
    def hide_window(self):
        self.window.withdraw()
    def close_window(self):
        self.window.quit()
    @staticmethod
    def plot_OrCreate(net_id,counters,net_metadatas,parameters):

        if net_id not in NetworkPlotter._plotters.keys():
            def p():
                NetworkPlotter._plotters[net_id].plot()
            NetworkPlotter._plotters[net_id]=NetworkPlotter(net_id,counters,net_metadatas,p,parameters)
        else:
            NetworkPlotter._plotters[net_id].plot()

if __name__ == '__main__':
    print(123)
    import CCA
    from algorithms.tools.Toolkit import *
    from pylab import array


    with CCA.Context() as context:
        import time

        counters = [context.TrainingCounterSystem.Loss_Counter("well well well_" +str(i)).set_netId(111) for i in range(9)]
        for j in range(500):


            import math
            v=random.randint(0,8)
            a=random.randint(0, 314) / 100
            square=random.randrange(1,500)/100
            mul=random.randrange(1,600)/100
            [counters[v].lineage(i,(counters[v].net_id,counters[v].name))for i in  [mul*math.sin(((a+i)/100)**square)for i in range(1,40)]]
            p=context.TrainingParameterSystem.get_OrCreate("test",context.TrainingParameterSystem.default_parameters)

            context.TrainingCounterSystem.plot(111,counters,{"type":"test","name":"t"},p)
            time.sleep(1)
