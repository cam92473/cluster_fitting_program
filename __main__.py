import numpy
import scipy.optimize as opt
import pandas as pd


class ChiSquared():
    def __init__(self):
        self.filenamevar = ""
        self.guessernamevar= ""
        self.chosenstar = "     1-cluster fit     "
        self.checkedset= 0
        self.checked2set = 0
        self.checked3set = 0
        self.checker1set = 1
        self.checker2set = 1
        self.checker3set = 1
        self.checker4set = 1
        self.sliderval1set = 0
        self.sliderval2set = 0
        self.rownumberset = ""
        self.dset = "785000"
        self.sliderstring1set = "log-log axes"
        self.sliderstring2set = "average filter wavelength"
        self.ulmethset = "Standard"
        self.model_chosen_set = "UVIT_HST"
        self.starlist1 = ["0","0.75","0.3","0.1","N/A","N/A","N/A","N/A"]
        self.starlist2 = ["-0.5",".8477","0.6","0.2","-1.5",".9477","0.8","0.1"]
        self.stardict1 = [["-2.5","0.3"],[".66",".90"],["0",".75"],["0","1"],["N/A","N/A"],["N/A","N/A"],["N/A","N/A"],["N/A","N/A"]]
        self.stardict2 = [["-2.1","-0.1"],[".66","1.01"],["0","1.4"],["0","2"],["-2.1","-0.1"],[".66","1.01"],["0","1.4"],["0","2"]]
        self.stardict3 = [["-2.1","-0.1"],[".66",".90"],["0",".75"],["0","1"],["N/A","N/A"],["N/A","N/A"],["N/A","N/A"],["N/A","N/A"]]
        self.stardict4 = [["-2.1","-0.1"],[".66","1.01"],["0","1.4"],["0","2"],["-2.1","-0.1"],[".66","1.01"],["0","1.4"],["0","2"]]
        while True:
            self.intro_gui()
            self.extract_measured_flux()
            self.extract_ul()
            self.extract_sourceids()
            self.convert_to_AB()
            self.convert_to_bandflux()
            self.prepare_for_interpolation()
            self.minimize_chisq()
            self.find_param_errors()
            self.save_output()
            self.display_all_results()


    
    def intro_gui(self):
        self.switch = False
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
        import tkinter as tk
        mwin = tk.Tk()
        mwin.geometry("1030x800+520+100")
        mwin.title("Cluster Fitting")
        mwin.config(bg='alice blue')
        mwin.resizable(0,0)

        def collectfilename():
            from tkinter import messagebox
            if user_filename.get() == "":
                tk.messagebox.showinfo('Error', 'Please enter a filename.')
                return None
            else:
                moveon = False
                if checked3.get() == 0:

                    if "," in user_rownumber.get():
                        rowlist = user_rownumber.get().split(',')
                        for elem in rowlist:
                            try:
                                rowint = int(elem)
                            except:
                                tk.messagebox.showinfo('Error', 'Please enter the number of rows with the correct syntax.')
                                return None
                            else:
                                introwlist = [int(i) for i in rowlist]
                                lowestelem = introwlist[0]
                                highestelem = introwlist[-1]
                                moveon = True

                    elif ":" in user_rownumber.get():
                        rowlist = user_rownumber.get().split(':')
                        for elem in rowlist:
                            try:
                                rowint = int(elem)
                            except:
                                tk.messagebox.showinfo('Error', 'Please enter the number of rows with the correct syntax.')
                                return None
                            else:
                                import numpy as np
                                introwlist = np.arange(int(rowlist[0]),int(rowlist[-1])+1).tolist()
                                lowestelem = introwlist[0]
                                highestelem = introwlist[-1]
                                moveon = True
                    
                    else:
                        try:
                            rowint = int(user_rownumber.get())
                        except:
                            tk.messagebox.showinfo('Error', 'Please enter the number of rows with the correct syntax.')
                            return None
                        else:
                            introwlist = [rowint]
                            lowestelem = rowint
                            highestelem = rowint
                            moveon = True
                
                elif checked3.get() == 1:
                    try:
                        import pandas as pd
                        self.inputguesses = pd.read_csv("{}".format(user_guessername.get(),delimiter=","))
                        self.guessernamevar = user_guessername.get()
                        moveon = True
                    except:
                        tk.messagebox.showinfo('Error', "Could not find input file for rows and guesses. Please place the file in the program folder and try again.")
                        return None

                if moveon == True:
                    try:
                        import pandas as pd
                        self.measuredata = pd.read_csv("{}".format(user_filename.get(),delimiter=","))
                        self.filenamevar = user_filename.get()
                    except:
                        tk.messagebox.showinfo('Error', "Could not find input file for measured fluxes. Please place the file in the program folder and try again.")
                        return None
                    else:
                        if checked3.get() == 0:
                            if highestelem > len(self.measuredata)+1 or lowestelem < 2:
                                tk.messagebox.showinfo('Error', "Rows specified are out of range.")
                                return None
                        if (checker2.get() == 1 and fluxname.get()[-4:] != ".csv") or (checker3.get() == 1 and chiname.get()[-4:] != ".csv"):
                            tk.messagebox.showinfo('Error', "The filenames specified are not allowed. Make sure to use the .csv extension.")
                            return None
                        elif checker4.get() == 1 and (imgname.get()[-4:] != ".png" and imgname.get()[-4:] != ".jpg"):
                            tk.messagebox.showinfo('Error', "The filenames specified are not allowed. Make sure to use the .png or .jpg extensions.")
                            return None
                        else:
                            try:
                                a = int(fluxname.get()[0])
                                b = int(chiname.get()[0])
                                c = int(imgname.get()[0])
                                return None
                            except:
                                try:
                                    self.switch = True
                                    if checked3.get() == 0:
                                        self.rows = [i-2 for i in introwlist]
                                        self.rownumberset = user_rownumber.get()
                                    elif checked3.get() == 1:
                                        guesssids = self.inputguesses['Source_ID'].to_list()
                                        self.measuredata = self.measuredata[self.measuredata['Source_ID'].isin(guesssids)]
                                        self.rows = list(self.measuredata.head().index)

                                    self.dispresults = checker1.get()
                                    self.fluxresults = checker2.get()
                                    self.chiparams = checker3.get()
                                    self.saveplots = checker4.get()
                                    self.plotscale = currentsliderval1.get()
                                    self.xticker = currentsliderval2.get()
                                    self.checker1set = checker1.get()
                                    self.checker2set = checker2.get()
                                    self.checker3set = checker3.get()
                                    self.checker4set = checker4.get()
                                    self.sliderval1set = currentsliderval1.get()
                                    self.sliderval1set = currentsliderval2.get()
                                    self.sliderstring1set = sliderstring1.get()
                                    self.sliderstring2set = sliderstring2.get()
                                    self.checkedset = checked.get()
                                    self.checked2set = checked2.get()
                                    self.checked3set = checked3.get()
                                    
                                    self.model_chosen = user_model_cho.get()
                                    self.model_chosen_set = user_model_cho.get()
                                    self.ulmeth = user_ulmeth.get()
                                    self.ulmethset = user_ulmeth.get()
                                    
                                    try:
                                        self.d = float(user_d.get())
                                        self.dset = user_d.get()
                                    except:
                                        tk.messagebox.showinfo('Error', "Please enter a number for d.")
                                        return None

                                    if checker2.get() == 1:
                                        self.fluxfilename = fluxname.get()
                                    if checker3.get() == 1:
                                        self.chifilename = chiname.get()
                                    if checker4.get() == 1:
                                        self.imgfilename = imgname.get()
                                    
                                    self.single_cluster = False
                                    self.double_cluster = False
                                    self.chosenstar = starno_chosen.get()
                                    if user_Zbound2lo.get() == user_agebound2lo.get() == user_Mbound2lo.get() == user_ebvbound2lo.get() == "N/A":
                                        self.single_cluster = True
                                        if checked3.get() == 0:
                                            self.Zguess1 = [user_Zguess1.get() for i in range(len(self.rows))]
                                            self.ageguess1 = [user_ageguess1.get() for i in range(len(self.rows))]
                                            self.Mguess1 = [user_Mguess1.get() for i in range(len(self.rows))]
                                            self.ebvguess1 = [user_ebvguess1.get() for i in range(len(self.rows))]
                                            self.starlist1[0]=user_Zguess1.get()
                                            self.starlist1[1]=user_ageguess1.get()
                                            self.starlist1[2]=user_Mguess1.get()
                                            self.starlist1[3]=user_ebvguess1.get()
                                        if checked3.get() == 1:
                                            self.Zguess1 = self.inputguesses['log(Z)']
                                            self.ageguess1 = self.inputguesses['log(age)/10']
                                            self.Mguess1 = self.inputguesses['log(M)/10']
                                            self.ebvguess1 = self.inputguesses['E(B-V)']

                                        self.Zbound1lo = float(user_Zbound1lo.get())
                                        self.Zbound1hi = float(user_Zbound1hi.get())
                                        self.agebound1lo = float(user_agebound1lo.get())
                                        self.agebound1hi = float(user_agebound1hi.get())
                                        self.Mbound1lo = float(user_Mbound1lo.get())
                                        self.Mbound1hi = float(user_Mbound1hi.get())
                                        self.ebvbound1lo = float(user_ebvbound1lo.get())
                                        self.ebvbound1hi = float(user_ebvbound1hi.get())
                                        if self.model_chosen == "UVIT_HST":
                                            self.stardict1[0][0] = user_Zbound1lo.get()
                                            self.stardict1[0][1] = user_Zbound1hi.get()
                                            self.stardict1[1][0] = user_agebound1lo.get()
                                            self.stardict1[1][1] = user_agebound1hi.get()
                                            self.stardict1[2][0] = user_Mbound1lo.get()
                                            self.stardict1[2][1] = user_Mbound1hi.get()
                                            self.stardict1[3][0] = user_ebvbound1lo.get()
                                            self.stardict1[3][1] = user_ebvbound1hi.get()
                                        elif self.model_chosen == "UVIT_SDSS_Spitzer":
                                            self.stardict3[0][0] = user_Zbound1lo.get()
                                            self.stardict3[0][1] = user_Zbound1hi.get()
                                            self.stardict3[1][0] = user_agebound1lo.get()
                                            self.stardict3[1][1] = user_agebound1hi.get()
                                            self.stardict3[2][0] = user_Mbound1lo.get()
                                            self.stardict3[2][1] = user_Mbound1hi.get()
                                            self.stardict3[3][0] = user_ebvbound1lo.get()
                                            self.stardict3[3][1] = user_ebvbound1hi.get()

                                    else:
                                        if checked3.get() == 0:
                                            self.Zguess1 = [user_Zguess1.get() for i in range(len(self.rows))]
                                            self.ageguess1 = [user_ageguess1.get() for i in range(len(self.rows))]
                                            self.Mguess1 = [user_Mguess1.get() for i in range(len(self.rows))]
                                            self.ebvguess1 = [user_ebvguess1.get() for i in range(len(self.rows))]
                                            self.Zguess2 = [float(user_Zguess2.get()) for i in range(len(self.rows))]
                                            self.ageguess2 = [float(user_ageguess2.get()) for i in range(len(self.rows))]
                                            self.Mguess2 = [float(user_Mguess2.get()) for i in range(len(self.rows))]
                                            self.ebvguess2 = [float(user_ebvguess2.get()) for i in range(len(self.rows))]
                                            self.starlist2[0]=user_Zguess1.get()
                                            self.starlist2[1]=user_ageguess1.get()
                                            self.starlist2[2]=user_Mguess1.get()
                                            self.starlist2[3]=user_ebvguess1.get()
                                            self.starlist2[4]=user_Zguess2.get()
                                            self.starlist2[5]=user_ageguess2.get()
                                            self.starlist2[6]=user_Mguess2.get()
                                            self.starlist2[7]=user_ebvguess2.get()
                                        elif checked3.get() == 1:
                                            self.Zguess1 = self.inputguesses['log(Z_hot)']
                                            self.ageguess1 = self.inputguesses['log(age_hot)/10']
                                            self.Mguess1 = self.inputguesses['log(M_hot)/10']
                                            self.ebvguess1 = self.inputguesses['E(B-V)_hot']
                                            self.Zguess2 = self.inputguesses['log(Z_cool)']
                                            self.ageguess2 = self.inputguesses['log(age_cool)/10']
                                            self.Mguess2 = self.inputguesses['log(M_cool)/10']
                                            self.ebvguess2 = self.inputguesses['E(B-V)_cool']

                                        self.double_cluster = True
                                        self.Zbound1lo = float(user_Zbound1lo.get())
                                        self.Zbound1hi = float(user_Zbound1hi.get())
                                        self.agebound1lo = float(user_agebound1lo.get())
                                        self.agebound1hi = float(user_agebound1hi.get())
                                        self.Mbound1lo = float(user_Mbound1lo.get())
                                        self.Mbound1hi = float(user_Mbound1hi.get())
                                        self.ebvbound1lo = float(user_ebvbound1lo.get())
                                        self.ebvbound1hi = float(user_ebvbound1hi.get())
                                        self.Zbound2lo = float(user_Zbound2lo.get())
                                        self.Zbound2hi = float(user_Zbound2hi.get())
                                        self.agebound2lo = float(user_agebound2lo.get())
                                        self.agebound2hi = float(user_agebound2hi.get())
                                        self.Mbound2lo = float(user_Mbound2lo.get())
                                        self.Mbound2hi = float(user_Mbound2hi.get())
                                        self.ebvbound2lo = float(user_ebvbound2lo.get())
                                        self.ebvbound2hi = float(user_ebvbound2hi.get())
                                        if self.model_chosen == "UVIT_HST":
                                            self.stardict2[0][0] = user_Zbound1lo.get()
                                            self.stardict2[0][1] = user_Zbound1hi.get()
                                            self.stardict2[1][0] = user_agebound1lo.get()
                                            self.stardict2[1][1] = user_agebound1hi.get()
                                            self.stardict2[2][0] = user_Mbound1lo.get()
                                            self.stardict2[2][1] = user_Mbound1hi.get()
                                            self.stardict2[3][0] = user_ebvbound1lo.get()
                                            self.stardict2[3][1] = user_ebvbound1hi.get()
                                            self.stardict2[4][0] = user_Zbound2lo.get()
                                            self.stardict2[4][1] = user_Zbound2hi.get()
                                            self.stardict2[5][0] = user_agebound2lo.get()
                                            self.stardict2[5][1] = user_agebound2hi.get()
                                            self.stardict2[6][0] = user_Mbound2lo.get()
                                            self.stardict2[6][1] = user_Mbound2hi.get()
                                            self.stardict2[7][0] = user_ebvbound2lo.get()
                                            self.stardict2[7][1] = user_ebvbound2hi.get()
                                        elif self.model_chosen == "UVIT_SDSS_Spitzer":
                                            self.stardict4[0][0] = user_Zbound1lo.get()
                                            self.stardict4[0][1] = user_Zbound1hi.get()
                                            self.stardict4[1][0] = user_agebound1lo.get()
                                            self.stardict4[1][1] = user_agebound1hi.get()
                                            self.stardict4[2][0] = user_Mbound1lo.get()
                                            self.stardict4[2][1] = user_Mbound1hi.get()
                                            self.stardict4[3][0] = user_ebvbound1lo.get()
                                            self.stardict4[3][1] = user_ebvbound1hi.get()
                                            self.stardict4[4][0] = user_Zbound2lo.get()
                                            self.stardict4[4][1] = user_Zbound2hi.get()
                                            self.stardict4[5][0] = user_agebound2lo.get()
                                            self.stardict4[5][1] = user_agebound2hi.get()
                                            self.stardict4[6][0] = user_Mbound2lo.get()
                                            self.stardict4[6][1] = user_Mbound2hi.get()
                                            self.stardict4[7][0] = user_ebvbound2lo.get()
                                            self.stardict4[7][1] = user_ebvbound2hi.get()
                                except:
                                        tk.messagebox.showinfo('Error', "One or more parameters seem to have been entered incorrectly. Please reenter the values and try again.")
                                        return None
                                else:
                                    mwin.destroy()
        
        def openrows3():
            from tkinter import messagebox
            tk.messagebox.showinfo("Help", "One of the components of the model flux is an interpolation term that performs a 2-D interpolation inside a grid whose axes are Z and log(age)/10. The term accepts a coordinate (Z, log(age)/10) and returns a flux for every filter, subsequently to be used in calcuating the model flux. One property of the data grid of fluxes is left as a choice to the user: its resolution. The program actually contains two grids which the user can choose between. The finer grid is a 13 X 19 grid, and the coarser grid is a 10 X 16 grid, whose ranges in Z and log(age)/10 are roughly the same. The coarser grid was introduced to prevent the optimizer from getting stuck (as it tends to when performing 2-cluster fits). The lower resolution of the grid seems to help remove any local dips in the fluxes, and makes the 2-D landscape more monotonic.")


        #howbutton = tk.Button(mwin,text=" ? ",font=("TimesNewRoman 10"),command = openrows3,pady=1,padx=1)
        #howbutton.place(x=180,y=402)
        user_rownumber = tk.StringVar()
        user_rownumber.set(self.rownumberset)
        enterrownumberpack = tk.Frame(mwin)
        enterrownumberpack.place(x=37,y=195)
        enterrownumber = tk.Entry(enterrownumberpack,textvariable=user_rownumber,width=12)
        enterrownumber.pack(ipady=3)
        labelwhich = tk.Label(mwin,text="Read rows", bg="alice blue")
        labelwhich.place(x=39,y=165)
        def openrows():
            from tkinter import messagebox
            tk.messagebox.showinfo("Help","  •  Use csv row labelling (which should start at row 2)\n\n  •  Specify multiple rows with commas: 2,5,6\n\n  •  Specify a selection of rows with a colon: 3:8")
        def openrows2():
            from tkinter import messagebox
            tk.messagebox.showinfo("Help","The cluster distance d appears as a constant in the model flux formula:\n\nflux_mod = M*interp(age,Z)*(10[pc]/d[pc])^2*10^(-0.4*E(B-V)*(k(λ-V)+R(V)))\n\nNote that d must be in parsecs.")
        whichbutton = tk.Button(mwin,text="?",font=("TimesNewRoman 8"),command = openrows)
        whichbutton.place(x=117,y=196)
        enterdpack = tk.Frame(mwin,bg='alice blue')
        enterdpack.place(x=167,y=195)
        user_d = tk.StringVar()
        user_d.set(self.dset)
        enterd = tk.Entry(enterdpack,textvariable=user_d,width=12)
        enterd.pack(ipady=3)
        labelwhat = tk.Label(mwin,text="d",bg="alice blue")
        labelwhat.place(x=170,y=165)
        whatbutton = tk.Button(mwin,text="?"  ,font=("TimesNewRoman 8"),command = openrows2)
        whatbutton.place(x=247,y=196)
        canvas2 = tk.Canvas(mwin,relief=tk.RIDGE,bd=2,width=330,height=380,bg='azure2')
        canvas2.place(x=310,y=150)
        canvasline = tk.Canvas(mwin,bd=3,relief=tk.GROOVE,width=680,height=1000,bg='mint cream')
        canvasline.place(x=-20,y=550)
        canvasline2 = canvasline = tk.Canvas(mwin,bd=3,relief=tk.GROOVE,width=680,height=1060,bg='lavender')
        canvasline2.place(x=660,y=150)
        user_Zguess1 = tk.DoubleVar()
        user_ageguess1 = tk.DoubleVar()
        user_Mguess1 = tk.DoubleVar()
        user_ebvguess1 = tk.DoubleVar()
        ystar1labels = 630
        ystar1entries = 660
        ycheckbutton = 580
        labelZ1 = tk.Label(mwin,text="log(Z_hot)",bg="mint cream").place(x=50,y=ystar1labels)
        entryZ1 = tk.Entry(mwin,textvariable=user_Zguess1,width=10)
        entryZ1.place(x=50,y=ystar1entries)
        labelage1 = tk.Label(mwin,text="log(age_hot)/10",bg="mint cream").place(x=155,y=ystar1labels)
        entryage1 = tk.Entry(mwin,textvariable=user_ageguess1,width=10)
        entryage1.place(x=170,y=ystar1entries)
        labelM1 = tk.Label(mwin,text="log(M_hot)/10",bg="mint cream").place(x=285,y=ystar1labels)
        entryM1 = tk.Entry(mwin,textvariable=user_Mguess1,width=10)
        entryM1.place(x=290,y=ystar1entries)
        labelebv1 = tk.Label(mwin,text="E(B-V)_hot",bg="mint cream").place(x=410,y=ystar1labels)
        entryebv1 = tk.Entry(mwin,textvariable=user_ebvguess1,width=10)
        entryebv1.place(x=410,y=ystar1entries)


        ystar2labels = 710
        ystar2entries = 740
        user_Zguess2 = tk.StringVar()
        user_ageguess2 = tk.StringVar()
        user_Mguess2 = tk.StringVar()
        user_ebvguess2 = tk.StringVar()
        labelZ2 = tk.Label(mwin,text="log(Z_cool)",bg="mint cream").place(x=50,y=ystar2labels)
        entryZ2 = tk.Entry(mwin,textvariable=user_Zguess2,width=10)
        entryZ2.place(x=50,y=ystar2entries)
        labelage2 = tk.Label(mwin,text="log(age_cool)/10",bg="mint cream").place(x=155,y=ystar2labels)
        entryage2 = tk.Entry(mwin,textvariable=user_ageguess2,width=10)
        entryage2.place(x=170,y=ystar2entries)
        labelM2 = tk.Label(mwin,text="log(M_cool)/10",bg="mint cream").place(x=285,y=ystar2labels)
        entryM2 = tk.Entry(mwin,textvariable=user_Mguess2,width=10)
        entryM2.place(x=290,y=ystar2entries)
        labelebv2 = tk.Label(mwin,text="E(B-V)_cool",bg="mint cream").place(x=410,y=ystar2labels)
        entryebv2 = tk.Entry(mwin,textvariable=user_ebvguess2,width=10)
        entryebv2.place(x=410,y=ystar2entries)
        
        starno_chosen = tk.StringVar()
        checked=tk.IntVar()
        checked.set(self.checkedset)

        def enable(howmany):
            entryZ1['state'] = tk.NORMAL
            entryage1['state'] = tk.NORMAL
            entryM1['state'] = tk.NORMAL
            entryebv1['state'] = tk.NORMAL
            if howmany == "all":
                entryZ2['state'] = tk.NORMAL
                entryage2['state'] = tk.NORMAL
                entryM2['state'] = tk.NORMAL
                entryebv2['state'] = tk.NORMAL

        def disable(howmany):
            entryZ1['state'] = tk.DISABLED
            entryage1['state'] = tk.DISABLED
            entryM1['state'] = tk.DISABLED
            entryebv1['state'] = tk.DISABLED
            if howmany == "all":
                entryZ2['state'] = tk.DISABLED
                entryage2['state'] = tk.DISABLED
                entryM2['state'] = tk.DISABLED
                entryebv2['state'] = tk.DISABLED


        def stuff_vals():
            entrylist = [entryZ1,entryage1,entryM1,entryebv1,entryZ2,entryage2,entryM2,entryebv2]
            if starno_chosen.get() == "     1-cluster fit     ":
                enable("all")
                for i,entry in enumerate(entrylist):
                    entry.delete(0,20)
                    entry.insert(0,"{}".format(self.starlist1[i]))
                disable("all")
                if checked.get() == 1:
                    enable("some")
            elif starno_chosen.get() == "     2-cluster fit     ":
                enable("all")
                for i,entry in enumerate(entrylist):
                    entry.delete(0,20)
                    entry.insert(0,"{}".format(self.starlist2[i]))
                disable("all")
                if checked.get() == 1:
                    enable("all")
        
        def openinfo():
            #info = tk.Toplevel()
            #info.geometry("900x560+600+250")
            #info.title("Info")
            #info.config(bg="white")
            #infolabel = tk.Label(info,bg="white",wraplength=800,justify=tk.LEFT,text="  This program uses chi-square minimization to find the best fit between the inputted flux data and a model flux function, whose form is specified by either 5 or 8 parameters, depending on the type of model selected (1-star or 2-star). For the single-star model, the model flux is determined at each data point in the input file (i.e. at each specified filter) by the log of the surface gravity log_g, the temperature T, the solar abundance (metallicity) Z, the stellar angular radius theta_r, and the interstellar reddening E(B-V). For the two-star model an additional three parameters are used to describe the cooler star: T_cool, theta_r_cool, and E_bv_cool, while the original five are relabeled with hot subscripts. In both models, theta_r appears as a quadratic term, while log_g, T, and Z are used to interpolate a flux value from a pre-existing data array that provides the \"filtered intrinsic model flux\" through each filter, given a point in those three coordinates. The filtered instrinsic model fluxes at each node (11-filter set) in the array were calculated beforehand using a similar array that provided the intrisic flux at each wavelength; namely, the calculations were done by integrating these intrinsic fluxes over the wavelengths of each filter (while also weighting by a model filter function). The final intrinsic filtered model flux (as a function of log_g, T, and Z, as well as the filter chosen) is a linear term in the current calculation. The final parameter, E(B-V), appears, along with a filter-dependent extinction factor k(λ-V), in a 10^(-0.4*E(B-V)(k(λ-V)-R_V)) term. (R_V is a constant, a parameter of the pre-calculated average extinction curve.)\n\n  If the model desired is single-star, one of these model calculations is done, wheras if the model is two-star, two of the calculations are done, with the cool-star calculation using the three new parameters. (The \"missing\" two are provided as constants in the program.) A chi-square minimization is performed, which in the two-star model involves finding the difference at every datapoint (filter) between the inputted data flux and the sum of the model fluxes for the hot and cool stars. The Python code used for the minimization process is Scipy's optimize.minimize (using the default method, with bounds and inital parameter guesses specified in this interface by the user). Errors for the best-fit parameters are found after the best fit is found, by varying the individual parameters about their best-fit values while fixing the others and stamping an upper error bound and a lower error bound when the chi-square value changes by 4.72 (for the single-star model) or by 9.14 (for the two-star model).")
            #infolabel.place(x=50,y=30)
            #info.mainloop()
            pass
        #helpgobutton = tk.Button(mwin,text="Info",font=("Arial",10),command = openinfo,pady=10,padx=35,bd=2)
        #helpgobutton.place(x=860,y=30)
        gobutton = tk.Button(mwin,text="Fit data",font=("Arial",10),command = collectfilename,pady=10,padx=25,bd=2)
        gobutton.place(x=865,y=70)
        checker1 = tk.IntVar()
        checker1.set(self.checker1set)
        checker2 = tk.IntVar()
        checker2.set(self.checker2set)
        checker3 = tk.IntVar()
        checker3.set(self.checker3set)
        checker4 = tk.IntVar()
        checker4.set(self.checker4set)
        sliderstring1 = tk.StringVar()
        sliderstring2 = tk.StringVar()
        currentsliderval1 = tk.IntVar()
        currentsliderval1.set(self.sliderval1set)
        currentsliderval2 = tk.IntVar()
        currentsliderval2.set(self.sliderval2set)
        fluxname = tk.StringVar()
        chiname = tk.StringVar()
        imgname = tk.StringVar()
        sliderstring1.set(self.sliderstring1set)
        sliderstring2.set(self.sliderstring2set)
        def changesliderstring1(useless):
            if currentsliderval1.get() == 1:
                sliderstring1.set(" linear axes  ")
            elif currentsliderval1.get() == 0:
                sliderstring1.set("log-log axes")
        def changesliderstring2(useless):
            if currentsliderval2.get() == 1:
                sliderstring2.set("200 nm (cleaner-looking)")
            elif currentsliderval2.get() == 0:
                sliderstring2.set("average filter wavelength")
        
        def grent1():
            if plotslider1['state'] == tk.NORMAL:
                plotslider1['state'] = tk.DISABLED
                plotslider2['state'] = tk.DISABLED
                sliderstring1.set("                     ")
                sliderstring2.set("                     ")
                sliderlabel1.config(bg="gray95")
                sliderlabel2.config(bg="gray95")
            elif plotslider1['state'] == tk.DISABLED:
                plotslider1['state'] = tk.NORMAL
                plotslider2['state'] = tk.NORMAL
                sliderlabel1.config(bg="white")
                sliderlabel2.config(bg="white")
                if currentsliderval1.get() == 1 and currentsliderval2.get() == 1:
                    sliderstring1.set(" linear axes  ")
                    sliderstring2.set("200 nm (cleaner-looking)")
                elif currentsliderval1.get() == 0 and currentsliderval2.get() == 1:
                    sliderstring1.set("log-log axes")
                    sliderstring2.set("200 nm (cleaner-looking)")
                elif currentsliderval1.get() == 1 and currentsliderval2.get() == 0:
                    sliderstring1.set(" linear axes  ")
                    sliderstring2.set("average filter wavelength")
                elif currentsliderval1.get() == 0 and currentsliderval2.get() == 0:
                    sliderstring1.set("log-log axes")
                    sliderstring2.set("average filter wavelength")

        def grent2():
            if buttentry2['state'] == tk.NORMAL:
                buttentry2.delete(0,30)
                buttentry2['state'] = tk.DISABLED
            elif buttentry2['state'] == tk.DISABLED:
                buttentry2['state'] = tk.NORMAL
                buttentry2.insert(tk.END,"flux_results.csv")
        def grent3():
            if buttentry3['state'] == tk.NORMAL:
                buttentry3.delete(0,30)
                buttentry3['state'] = tk.DISABLED
            elif buttentry3['state'] == tk.DISABLED:
                buttentry3['state'] = tk.NORMAL
                buttentry3.insert(tk.END,"chi_params.csv")
        def grent4():
            if buttentry4['state'] == tk.NORMAL:
                buttentry4.delete(0,30)
                buttentry4['state'] = tk.DISABLED
            elif buttentry4['state'] == tk.DISABLED:
                buttentry4['state'] = tk.NORMAL
                buttentry4.insert(tk.END,"plot_so_rowX.png")
                
        checkbutt1 = tk.Checkbutton(mwin,text="Display results",variable=checker1,command=grent1,bg='azure2')
        plotslider1 = tk.Scale(mwin,from_=0,to=1,orient=tk.HORIZONTAL,showvalue=0,length=65,width=25,variable=currentsliderval1, command=changesliderstring1)
        plotslider1.place(x=560,y=200)
        grayframe1= tk.Frame(mwin,bg="gray95",bd=3)
        grayframe1.place(x=350,y=200)
        sliderlabel1 = tk.Label(grayframe1,textvariable=sliderstring1,padx=5,bg='white')
        sliderlabel1.pack()
        sandwichtext = tk.Label(mwin,text="Place x-ticks every: ",bg='azure2')
        sandwichtext.place(x=352,y=238)
        plotslider2 = tk.Scale(mwin,from_=0,to=1,orient=tk.HORIZONTAL,showvalue=0,length=65,width=25,variable=currentsliderval2, command=changesliderstring2)
        plotslider2.place(x=560,y=270)
        grayframe2= tk.Frame(mwin,bg="gray95",bd=3)
        grayframe2.place(x=350,y=270)
        sliderlabel2 = tk.Label(grayframe2,textvariable=sliderstring2,padx=5,bg='white')
        sliderlabel2.pack()
        checkbutt2 = tk.Checkbutton(mwin,text="Save resulting flux data",variable=checker2,command=grent2,bg='azure2')
        checkbutt3 = tk.Checkbutton(mwin,text="Save chi^2 and minimized parameters",variable=checker3,command=grent3,bg='azure2')
        checkbutt4 = tk.Checkbutton(mwin,text="Save plot images (1 per source X)",variable=checker4,command=grent4,bg='azure2')
        buttentry2 = tk.Entry(mwin, textvariable = fluxname,width=26)
        buttentry3 = tk.Entry(mwin, textvariable = chiname,width=26)
        buttentry4 = tk.Entry(mwin,textvariable = imgname,width=26)
        if checker2.get() == 0:
            buttentry2['state'] = tk.DISABLED
        if checker3.get() == 0:
            buttentry3['state'] = tk.DISABLED
        if checker4.get() == 0:
            buttentry4['state'] = tk.DISABLED
        checkbutt1.place(x=320,y=160)
        checkbutt2.place(x=340,y=320)
        checkbutt3.place(x=340,y=390)
        checkbutt4.place(x=340,y=460)
        buttentry2.place(x=345,y=350)
        buttentry3.place(x=345,y=420)
        buttentry4.place(x=345,y=490)

        user_Zbound1lo = tk.StringVar()
        user_Zbound1hi = tk.StringVar()
        user_agebound1lo = tk.StringVar()
        user_agebound1hi = tk.StringVar()
        user_Mbound1lo = tk.StringVar()
        user_Mbound1hi = tk.StringVar()
        user_ebvbound1lo = tk.StringVar()
        user_ebvbound1hi = tk.StringVar()
        xstarbentrieslo = 685
        xstarbentrieshi = 915
        lwbound = tk.Label(mwin,text="Lower bound",font="Arial 10 underline",bg="lavender").place(x=xstarbentrieslo-7,y=280)
        upbound = tk.Label(mwin,text="Upper bound",font = "Arial 10 underline",bg="lavender").place(x=xstarbentrieshi-7,y=280)
        labelbZ1 = tk.Label(mwin,text="log(Z_hot)",bg="lavender").place(x=xstarbentrieslo+117,y=330)
        entrybZ1lo = tk.Entry(mwin,textvariable=user_Zbound1lo,width=10)
        entrybZ1lo.place(x=xstarbentrieslo,y=330)
        entrybZ1hi = tk.Entry(mwin,textvariable=user_Zbound1hi,width=10)
        entrybZ1hi.place(x=xstarbentrieshi,y=330)
        labelbage1lo = tk.Label(mwin,text="log(age_hot)/10",bg="lavender").place(x=xstarbentrieslo+102,y=390)
        entrybage1lo = tk.Entry(mwin,textvariable=user_agebound1lo,width=10)
        entrybage1lo.place(x=xstarbentrieslo,y=390)
        entrybage1hi = tk.Entry(mwin,textvariable=user_agebound1hi,width=10)
        entrybage1hi.place(x=xstarbentrieshi,y=390)
        labelbMlo = tk.Label(mwin,text="log(M_hot)/10",bg="lavender").place(x=xstarbentrieslo+108,y=450)
        entrybM1lo = tk.Entry(mwin,textvariable=user_Mbound1lo,width=10)
        entrybM1lo.place(x=xstarbentrieslo,y=450)
        entrybM1hi = tk.Entry(mwin,textvariable=user_Mbound1hi,width=10)
        entrybM1hi.place(x=xstarbentrieshi,y=450)
        labelbebv1lo = tk.Label(mwin,text="E(B-V)_hot",bg="lavender").place(x=xstarbentrieslo+115,y=510)
        entrybebv1lo = tk.Entry(mwin,textvariable=user_ebvbound1lo,width=10)
        entrybebv1lo.place(x=xstarbentrieslo,y=510)
        entrybebv1hi = tk.Entry(mwin,textvariable=user_ebvbound1hi,width=10)
        entrybebv1hi.place(x=xstarbentrieshi,y=510)

        user_Zbound2lo = tk.StringVar()
        user_Zbound2hi = tk.StringVar()
        user_agebound2lo = tk.StringVar()
        user_agebound2hi = tk.StringVar()
        user_Mbound2lo = tk.StringVar()
        user_Mbound2hi = tk.StringVar()
        user_ebvbound2lo = tk.StringVar()
        user_ebvbound2hi = tk.StringVar()
        labelbZ2lo = tk.Label(mwin,text="log(Z_cool)",bg="lavender").place(x=xstarbentrieslo+115,y=570)
        entrybZ2lo = tk.Entry(mwin,textvariable=user_Zbound2lo,width=10)
        entrybZ2lo.place(x=xstarbentrieslo,y=570)
        entrybZ2hi = tk.Entry(mwin,textvariable=user_Zbound2hi,width=10)
        entrybZ2hi.place(x=xstarbentrieshi,y=570)
        labelbage2lo = tk.Label(mwin,text="log(age_cool)/10",bg="lavender").place(x=xstarbentrieslo+100,y=630)
        entrybage2lo = tk.Entry(mwin,textvariable=user_agebound2lo,width=10)
        entrybage2lo.place(x=xstarbentrieslo,y=630)
        entrybage2hi = tk.Entry(mwin,textvariable=user_agebound2hi,width=10)
        entrybage2hi.place(x=xstarbentrieshi,y=630)
        labelbM2lo = tk.Label(mwin,text="log(M_cool)/10",bg="lavender").place(x=xstarbentrieslo+105,y=690)
        entrybM2lo = tk.Entry(mwin,textvariable=user_Mbound2lo,width=10)
        entrybM2lo.place(x=xstarbentrieslo,y=690)
        entrybM2hi = tk.Entry(mwin,textvariable=user_Mbound2hi,width=10)
        entrybM2hi.place(x=xstarbentrieshi,y=690)
        labelbebv2lo = tk.Label(mwin,text="E(B-V)_cool",bg="lavender").place(x=xstarbentrieslo+112,y=750)
        entrybebv2lo = tk.Entry(mwin,textvariable=user_ebvbound2lo,width=10)
        entrybebv2lo.place(x=xstarbentrieslo,y=750)
        entrybebv2hi = tk.Entry(mwin,textvariable=user_ebvbound2hi,width=10)
        entrybebv2hi.place(x=xstarbentrieshi,y=750)
        
        checked2=tk.IntVar()
        checked2.set(self.checked2set)

        def enable2(howmany):
            entrybZ1lo['state'] = tk.NORMAL
            entrybZ1hi['state'] = tk.NORMAL
            entrybage1lo['state'] = tk.NORMAL
            entrybage1hi['state'] = tk.NORMAL
            entrybM1lo['state'] = tk.NORMAL
            entrybM1hi['state'] = tk.NORMAL
            entrybebv1lo['state'] = tk.NORMAL
            entrybebv1hi['state'] = tk.NORMAL
            if howmany == "all":
                entrybZ2lo['state'] = tk.NORMAL
                entrybZ2hi['state'] = tk.NORMAL
                entrybage2lo['state'] = tk.NORMAL
                entrybage2hi['state'] = tk.NORMAL
                entrybM2lo['state'] = tk.NORMAL
                entrybM2hi['state'] = tk.NORMAL
                entrybebv2lo['state'] = tk.NORMAL
                entrybebv2hi['state'] = tk.NORMAL

        def disable2(howmany):
            entrybZ1lo['state'] = tk.DISABLED
            entrybZ1hi['state'] = tk.DISABLED
            entrybage1lo['state'] = tk.DISABLED
            entrybage1hi['state'] = tk.DISABLED
            entrybM1lo['state'] = tk.DISABLED
            entrybM1hi['state'] = tk.DISABLED
            entrybebv1lo['state'] = tk.DISABLED
            entrybebv1hi['state'] = tk.DISABLED
            if howmany == "all":
                entrybZ2lo['state'] = tk.DISABLED
                entrybZ2hi['state'] = tk.DISABLED
                entrybage2lo['state'] = tk.DISABLED
                entrybage2hi['state'] = tk.DISABLED
                entrybM2lo['state'] = tk.DISABLED
                entrybM2hi['state'] = tk.DISABLED
                entrybebv2lo['state'] = tk.DISABLED
                entrybebv2hi['state'] = tk.DISABLED


        def stuff_vals2():
            entrybdict = {entrybZ1lo:entrybZ1hi,entrybage1lo:entrybage1hi,entrybM1lo:entrybM1hi,entrybebv1lo:entrybebv1hi,entrybZ2lo:entrybZ2hi,entrybage2lo:entrybage2hi,entrybM2lo:entrybM2hi,entrybebv2lo:entrybebv2hi}
            if user_model_cho.get() == "UVIT_HST":
                if starno_chosen.get() == "     1-cluster fit     ":
                    enable2("all")
                    for (entryleft,entryright),(key,val) in zip(entrybdict.items(),self.stardict1):
                        entryleft.delete(0,20)
                        entryleft.insert(0,"{}".format(key))
                        entryright.delete(0,20)
                        entryright.insert(0,"{}".format(val))
                    disable2("all")
                    if checked2.get() == 1:
                        enable2("some")
                elif starno_chosen.get() == "     2-cluster fit     ":
                    enable2("all")
                    for (entryleft,entryright),(key,val) in zip(entrybdict.items(),self.stardict2):
                        entryleft.delete(0,20)
                        entryleft.insert(0,"{}".format(key))
                        entryright.delete(0,20)
                        entryright.insert(0,"{}".format(val))
                    disable2("all")
                    if checked2.get() == 1:
                        enable2("all")
            if user_model_cho.get() == "UVIT_SDSS_Spitzer":
                if starno_chosen.get() == "     1-cluster fit     ":
                    enable2("all")
                    for (entryleft,entryright),(key,val) in zip(entrybdict.items(),self.stardict3):
                        entryleft.delete(0,20)
                        entryleft.insert(0,"{}".format(key))
                        entryright.delete(0,20)
                        entryright.insert(0,"{}".format(val))
                    disable2("all")
                    if checked2.get() == 1:
                        enable2("some")
                elif starno_chosen.get() == "     2-cluster fit     ":
                    enable2("all")
                    for (entryleft,entryright),(key,val) in zip(entrybdict.items(),self.stardict4):
                        entryleft.delete(0,20)
                        entryleft.insert(0,"{}".format(key))
                        entryright.delete(0,20)
                        entryright.insert(0,"{}".format(val))
                    disable2("all")
                    if checked2.get() == 1:
                        enable2("all")

        def stuffy(useless):
            stuff_vals()
            stuff_vals2()
        
        def stuffyonly2(useless):
            stuff_vals2()


        def gray():
            if starno_chosen.get() == "     1-cluster fit     ":
                if entryZ1['state'] == tk.NORMAL:
                    disable("some")
                elif entryZ1['state'] == tk.DISABLED:
                    enable("some")
            elif starno_chosen.get() == "     2-cluster fit     ":
                if entryZ1['state'] == tk.NORMAL:
                    disable("all")
                elif entryZ1['state'] == tk.DISABLED:
                    enable("all")
        
        def gray2():
            if starno_chosen.get() == "     1-cluster fit     ":
                if entrybZ1lo['state'] == tk.NORMAL:
                    disable2("some")
                elif entrybZ1lo['state'] == tk.DISABLED:
                    enable2("some")
            elif starno_chosen.get() == "     2-cluster fit     ":
                if entrybZ1lo['state'] == tk.NORMAL:
                    disable2("all")
                elif entrybZ1lo['state'] == tk.DISABLED:
                    enable2("all")

        user_ulmeth = tk.StringVar()
        user_ulmeth.set(self.ulmethset)
        ulmethoptions = ["Standard","Limit"]
        labelulmeth = tk.Label(mwin,text="Upper limit calculation method",bg="alice blue")
        labelulmeth.place(x=37,y=280)
        ulmethmenu = tk.OptionMenu(mwin,user_ulmeth,*ulmethoptions)
        ulmethmenu.place(x=37,y=310)
        user_model_cho = tk.StringVar()
        user_model_cho.set(self.model_chosen_set)
        modelchooptions = ["UVIT_HST","UVIT_SDSS_Spitzer"]
        modelcholabel = tk.Label(mwin,text="Model data filters",bg="alice blue")
        modelcholabel.place(x=38,y=370)
        modelchomenu = tk.OptionMenu(mwin,user_model_cho,*modelchooptions,command=stuffyonly2)
        modelchomenu.place(x=32,y=400)
        starlabel = tk.Label(mwin,text="Fitting method",bg="alice blue").place(x=38,y=460)
        starno_chosen.set(self.chosenstar)
        staroptions = ["     1-cluster fit     ","     2-cluster fit     "]
        starmenu = tk.OptionMenu(mwin,starno_chosen,*staroptions,command=stuffy)
        starmenu.place(x=32,y=490)
        checkbutton = tk.Checkbutton(mwin,text="Edit default guess (parameter vector)",variable=checked,command=gray,bg="mint cream")
        checkbutton.place(x=10,y=ycheckbutton)
        checkbutton2 = tk.Checkbutton(mwin,text="Edit optimization bounds",variable=checked2,command=gray2,bg="lavender")
        checkbutton2.place(x=680,y=160)
        def disableguesses():
            if checkbutton['state'] == tk.NORMAL:
                disable('all')
                enterrownumber['state'] = tk.DISABLED
                checked.set(0)
                checkbutton['state'] = tk.DISABLED
                enterguessername['state'] = tk.NORMAL
            else:
                if checked == 1:
                    if starno_chosen.get() == "     1-cluster fit     ":
                        enable('some')
                    elif starno_chosen.get() == "     2-cluster fit     ":
                        enable('all')
                checkbutton['state'] = tk.NORMAL
                enterrownumber['state'] = tk.NORMAL
                enterguessername['state'] = tk.DISABLED

        checked3=tk.IntVar()
        checked3.set(self.checked3set)
        user_filename = tk.StringVar()
        user_filename.set(self.filenamevar)
        enterfileneame = tk.Entry(mwin,textvariable = user_filename,width=72)
        enterfileneame.place(x=224,y=34)
        user_guessername = tk.StringVar()
        user_guessername.set(self.guessernamevar)
        enterguessername = tk.Entry(mwin,textvariable = user_guessername,width=59)
        enterguessername.place(x=330,y=93)
        labeltop = tk.Label(mwin,text="Input measured flux file: ", bg='white',border=2,relief=tk.RIDGE,padx=6,pady=5)
        labeltop.place(x=35,y=29)
        labelbot = tk.Checkbutton(mwin,text="Input rows and initial guesses as a file: ", bg='white',border=2,relief=tk.RIDGE,variable=checked3,command=disableguesses)
        labelbot.place(x=35,y=89)
        grent2()
        grent2()
        grent3()
        grent3()
        grent4()
        grent4()
        disable("all")
        disable2("all")
        enterguessername['state'] = tk.DISABLED
        stuffy(3)
        mwin.mainloop()

    def extract_measured_flux(self):
        assert self.switch == True, "Program terminated"
        
        if self.model_chosen == "UVIT_HST":

            import pandas as pd
            import numpy as np
            import tkinter as tk
            
            raw_columns = ["F148W_AB","F148W_err","F169M_AB","F169M_err","F172M_AB","F172M_err","N219M_AB","N219M_err","N279N_AB","N279N_err","f275w_vega","f275w_err","f336w_vega","f336w_err","f475w_vega","f475w_err","f814w_vega","f814w_err","f110w_vega","f110w_err","f160w_vega","f160w_err"]

            self.raw_magnitudes_frame = pd.DataFrame()
            for rawname in raw_columns:
                self.raw_magnitudes_frame["{}".format(rawname)] = ""

            savebadcols = []
            for rowno in self.rows:
                curr_rowdict = {}
                for colname in raw_columns:
                    try:
                        curr_rowdict[colname] = self.measuredata.at[rowno,colname].item()
                    except:
                        curr_rowdict[colname] = -999
                        savebadcols.append(colname)
                self.raw_magnitudes_frame.loc[self.raw_magnitudes_frame.shape[0]] = curr_rowdict

            savebadcols = list(dict.fromkeys(savebadcols))
            badstr = ""
            for badcol in savebadcols:
                badstr += "{} or ".format(badcol)
            badstr = badstr[:-4]

            if len(badstr) != 0:
                import tkinter as tk
                miniwin = tk.Tk()
                miniwin.geometry("10x10+800+500")
                response = tk.messagebox.askquestion('Warning',"No entries found for {}. Do you wish to proceed?\n\n(These filters will not be fitted. If a single column is missing without its error or vice versa, you should double check the file for naming typos)".format(badstr))
                if response == "yes":
                    miniwin.destroy()
                if response == "no":
                    assert response == "yes", "Program terminated"

            for rowind,row in self.raw_magnitudes_frame.iterrows():
                for colind,colelement in enumerate(row):
                    if colelement == -999:
                        self.raw_magnitudes_frame.iat[rowind,colind] = np.nan

        elif self.model_chosen == "UVIT_SDSS_Spitzer":
            
            import pandas as pd
            import numpy as np
            import tkinter as tk
            
            raw_columns = ["F148W_AB","F148W_err","F169M_AB","F169M_err","F172M_AB","F172M_err","N219M_AB","N219M_err","N279N_AB","N279N_err","IRAC1","IRAC1_err","IRAC2","IRAC2_err","u_prime","u_prime_err","g_prime","g_prime_err","r_prime","r_prime_err","i_prime","i_prime_err","z_prime","z_prime_err"]

            self.raw_magnitudes_frame = pd.DataFrame()
            for rawname in raw_columns:
                self.raw_magnitudes_frame["{}".format(rawname)] = ""

            savebadcols = []
            for rowno in self.rows:
                curr_rowdict = {}
                for colname in raw_columns:
                    try:
                        curr_rowdict[colname] = self.measuredata.at[rowno,colname].item()
                    except:
                        curr_rowdict[colname] = -999
                        savebadcols.append(colname)
                self.raw_magnitudes_frame.loc[self.raw_magnitudes_frame.shape[0]] = curr_rowdict

            savebadcols = list(dict.fromkeys(savebadcols))
            badstr = ""
            for badcol in savebadcols:
                badstr += "{} or ".format(badcol)
            badstr = badstr[:-4]

            if len(badstr) != 0:
                import tkinter as tk
                miniwin = tk.Tk()
                miniwin.geometry("10x10+800+500")
                response = tk.messagebox.askquestion('Warning',"No entries found for {}. Do you wish to proceed?\n\n(These filters will not be fitted. If a single column is missing without its error or vice versa, you should double check the file for naming typos)".format(badstr))
                if response == "yes":
                    miniwin.destroy()
                if response == "no":
                    assert response == "yes", "Program terminated"

            for rowind,row in self.raw_magnitudes_frame.iterrows():
                for colind,colelement in enumerate(row):
                    if colelement == -999:
                        self.raw_magnitudes_frame.iat[rowind,colind] = np.nan

    def extract_ul(self):

        if self.model_chosen == "UVIT_HST":
            import pandas as pd
            import numpy as np
            import tkinter as tk

            raw_limits = ["F148W_ul","F169M_ul","F172M_ul","N219M_ul","N279N_ul","f275w_ul","f336w_ul","f475w_ul","f814w_ul","f110w_ul","f160w_ul"]
            
            self.ul_frame = pd.DataFrame()
            for rawname in raw_limits:
                self.ul_frame["{}".format(rawname)] = ""

            saverowuls = []
            savecoluls = []
            badcoluls = []
            first_time = True
            for rowno in self.rows:
                curr_rowdict = {}
                for colname in raw_limits:
                    try:
                        if self.measuredata.at[rowno,colname] == ">":
                            curr_rowdict[colname] = 1
                            savecoluls.append(colname)
                            saverowuls.append(str(rowno+2))
                        else:
                            curr_rowdict[colname] = 0
                    except:
                        curr_rowdict[colname] = np.nan
                        badcoluls.append(colname)
                self.ul_frame.loc[self.ul_frame.shape[0]] = curr_rowdict
                
                if first_time == True and len(badcoluls) > 0:
                    miniwin2 = tk.Tk()
                    miniwin2.geometry("10x10+800+500")
                    savebadcols2 = list(dict.fromkeys(badcoluls))
                    badstr2 = ""
                    for badcol2 in savebadcols2:
                        badstr2 += "{} or ".format(badcol2)
                    badstr2 = badstr2[:-4]
                    response2 = tk.messagebox.askquestion('Warning',"No upper limit columns found for {}. Do you wish to proceed?".format(badstr2))
                    if response2 == "yes":
                        miniwin2.destroy()
                        first_time = False
                    if response2 == "no":
                        assert response2 == "yes", "Program terminated"
            
            if len(savecoluls) > 0:
                miniwin = tk.Tk()
                miniwin.geometry("10x10+800+500")
                response = tk.messagebox.askquestion('Info',"Upper limits detected in columns {} in rows {}, respectively. If this sounds correct, click yes to continue.".format(", ".join(savecoluls),", ".join(saverowuls)))
                if response == "yes":
                    miniwin.destroy()
                if response == "no":
                    assert response == "yes", "Program terminated"
        
        elif self.model_chosen == "UVIT_SDSS_Spitzer":
            import pandas as pd
            import numpy as np

            raw_limits = ["F14_ul","F16_ul","F17_ul","N2_ul","N27_ul","a1_ul","a2_ul","a3_ul","a4_ul","a5_ul","a6_ul","a7_ul"]
            
            self.ul_frame = pd.DataFrame()
            for rawname in raw_limits:
                self.ul_frame["{}".format(rawname)] = ""

            for rowno in self.rows:
                curr_rowdict = {}
                for colname in raw_limits:
                  curr_rowdict[colname] = 0
                self.ul_frame.loc[self.ul_frame.shape[0]] = curr_rowdict
    
    def extract_sourceids(self):
        self.source_ids = []
        for rowno in self.rows:
            self.source_ids.append(self.measuredata['Source_ID'][rowno])
        
    def convert_to_AB(self):
        if self.model_chosen == "UVIT_HST":
            self.ab_magnitudes_frame = self.raw_magnitudes_frame
            for col in self.ab_magnitudes_frame:
                    if col == "f275w_vega":
                        self.ab_magnitudes_frame[col] = self.ab_magnitudes_frame[col].apply(lambda x: x - (-1.496))
                    elif col == "f336w_vega":
                        self.ab_magnitudes_frame[col] = self.ab_magnitudes_frame[col].apply(lambda x: x - (-1.188))
                    elif col == "f475w_vega":
                        self.ab_magnitudes_frame[col] = self.ab_magnitudes_frame[col].apply(lambda x: x - 0.091)
                    elif col == "f814w_vega":
                        self.ab_magnitudes_frame[col] = self.ab_magnitudes_frame[col].apply(lambda x: x - (-0.427))
                    elif col == "f110w_vega":
                        self.ab_magnitudes_frame[col] = self.ab_magnitudes_frame[col].apply(lambda x: x - (-0.7595))
                    elif col == "f160w_vega":
                        self.ab_magnitudes_frame[col] = self.ab_magnitudes_frame[col].apply(lambda x: x - (-1.2514))
            
            self.ab_magnitudes_frame.rename(columns={"f275w_vega" : "f275w_AB", "f336w_vega" : "f336w_AB", "f475w_vega" : "f475w_AB", "f814w_vega" : "f814w_AB", "f110w_vega" : "f110w_AB", "f160w_vega" : "f160w_AB"},inplace=True)
        
        elif self.model_chosen == "UVIT_SDSS_Spitzer":
            pass

    def convert_to_bandflux(self):

        if self.model_chosen == "UVIT_HST":

            self.filternames = ["F148W","F169M","F172M","N219M","N279N","f275w","f336w","f475w","f814w","f110w","f160w"]
            self.bandfluxes = pd.DataFrame()
            self.bandfluxerrors = pd.DataFrame()
            self.avgwvlist = [148.1,160.8,171.7,219.6,279.2,270.4,335.5,477.3,802.4,1153.4,1536.9]
            #self.avgwvlist = [150.2491,161.4697,170.856,199.1508,276.0,267.884375,336.8484,476.0,833.0,1096.7245,1522.1981]
            #self.allextinct = [5.52548923, 5.17258596, 5.0540947, 5.83766858, 3.49917568, 3.25288368, 1.95999799, 0.62151591, -1.44589933, -2.10914243, -2.51310314]
            self.allextinct = [ 5.62427152,  5.18640888,  5.04926289,  6.99406125,  3.15901211,  3.42340971, 1.97787612,  0.61008783, -1.33280758, -2.18810981, -2.52165626]

            for colind,col in enumerate(self.ab_magnitudes_frame):
                if colind%2 == 0:
                    self.ab_magnitudes_frame[col] = self.ab_magnitudes_frame[col].apply(lambda x: (10**(-0.4*(48.60+x)))*10**26)
                    self.bandfluxes["{}".format(col)] = self.ab_magnitudes_frame[col]
                elif colind%2 != 0:
                    for rowind in range(len(self.ab_magnitudes_frame[col])):
                        self.ab_magnitudes_frame.iloc[rowind,colind] = self.ab_magnitudes_frame.iloc[rowind,colind-1]*self.ab_magnitudes_frame.iloc[rowind,colind]/1.0857
                    self.bandfluxerrors["{}".format(col)] = self.ab_magnitudes_frame[col]
        
        elif self.model_chosen == "UVIT_SDSS_Spitzer":

            self.filternames = ["F148W","F169M","F172M","N219M","N279N","IRAC1","IRAC2","u_prime","g_prime","r_prime","i_prime","z_prime"]
            self.bandfluxes = pd.DataFrame()
            self.bandfluxerrors = pd.DataFrame()
            self.avgwvlist = [150.2491,161.4697,170.856,199.1508,276.0,355.1,468.6,616.6,748,893,3550,4490]
            self.allextinct = [ 5.52548923,  5.17258596,  5.0540947,   5.83766858,  3.25288368,  1.74741802, 0.68710903, -0.42704846, -1.11016491, -1.64589927, -2.89828005, -2.93432827]
            for colind,col in enumerate(self.raw_magnitudes_frame):
                if colind%2 == 0:
                    self.bandfluxes["{}".format(col)] = self.raw_magnitudes_frame[col]
                elif colind%2 != 0:
                    self.bandfluxerrors["{}".format(col)] = self.raw_magnitudes_frame[col]

        
    def prepare_for_interpolation(self):
        import pandas as pd
        import xarray as xr
        import numpy as np

        if self.model_chosen == "UVIT_HST":

            fluxdata = pd.read_csv("fluxpersolarmass2.csv")
            
            blankdata = np.zeros((13,19,11))

            row=0
            for Z in range(13):
                for age in range(19):
                    for filt in range(11):
                        blankdata[Z,age,filt] = fluxdata.iat[row,filt]
                    row += 1

            filleddata = blankdata

            zcoordlist = [-2.617,-2.36173,-2.11185,-1.86881,-1.62577,-1.37645,-1.12564,-0.87822,-0.63202,-0.38809,-0.14836,0.08353,0.303332]
            agecoordlist = [.66,.68,.70,.72,.74,.76,.78,.80,.82,.84,.86,.88,.90,.92,.94,.96,.98,1.0,1.2]
            filtercoordlist = [0,1,2,3,4,5,6,7,8,9,10]

            self.da = xr.DataArray(filleddata,coords=[("Z",zcoordlist),("Age",agecoordlist),("Filter",filtercoordlist)])

        elif self.model_chosen == "UVIT_SDSS_Spitzer":
            fluxdata = pd.read_csv("fluxpersolarmass4.csv")

            blankdata = np.zeros((10,16,12))

            row=0
            for Z in range(10):
                for age in range(16):
                    for filt in range(12):
                        blankdata[Z,age,filt] = fluxdata.iat[row,filt]
                    row += 1

            filleddata = blankdata

            zcoordlist = [-2.111850363,-1.900996997,-1.662757832,-1.435156753,-1.205380635,-0.977513852,-0.750122527,-0.524279696,-0.301029996,-0.082466585]
            agecoordlist = [0.659988307,0.68350561,0.707188201,0.730535137,0.754157924,0.777670118,0.801283722,0.824797327,0.848287358,0.87176705,0.895279244,0.918752072,0.942324587,0.965896484,0.989431606,1.013033377]
            filtercoordlist = [0,1,2,3,4,5,6,7,8,9,10,11]

            self.da = xr.DataArray(filleddata,coords=[("Z",zcoordlist),("Age",agecoordlist),("Filter",filtercoordlist)])

    def interpolate(self,Z,age,valid_filters_this_row):
        interpolist = []
        interpolated = self.da.interp(Z = Z, Age = age)
        for valid_filter in valid_filters_this_row:
            interpolist.append(interpolated.sel(Filter = valid_filter).data.item()*10**26)
        return interpolist
    
    def extinction(self,valid_filters_this_row):
        extinctlist = []
        for valid_filter in valid_filters_this_row:
            extinctlist.append(self.allextinct[valid_filter])
        return extinctlist

    def minichisqfunc_single(self,tup,valid_filters_this_row):
        Z,age,M,E_bv, = tup

        true_M = 10**(M*10)

        bestmodels = []
        interpolist = self.interpolate(Z,age,valid_filters_this_row)
        extinctolist = self.extinction(valid_filters_this_row)
        for i in range(len(valid_filters_this_row)):
            bestmodels.append(true_M*interpolist[i]*(10/self.d)**2*10**(-0.4*(E_bv*(extinctolist[i]+3.001))))

        return bestmodels

    def minichisqfunc_double(self,tup,valid_filters_this_row):
        Z1,age1,M1,E_bv1,Z2,age2,M2,E_bv2 = tup

        true_M1 = 10**(M1*10)
        true_M2 = 10**(M2*10)

        bestmodels1 = []
        interpolist1 = self.interpolate(Z1,age1,valid_filters_this_row)
        extinctolist1 =self.extinction(valid_filters_this_row)
        for i in range(len(valid_filters_this_row)):
            bestmodels1.append(true_M1*interpolist1[i]*(10/self.d)**2*10**(-0.4*(E_bv1*(extinctolist1[i]+3.001))))
        bestmodels2 = []
        interpolist2 = self.interpolate(Z2,age2,valid_filters_this_row)
        extinctolist2 = self.extinction(valid_filters_this_row)
        for i in range(len(valid_filters_this_row)):
            bestmodels2.append(true_M2*interpolist2[i]*(10/self.d)**2*10**(-0.4*(E_bv2*(extinctolist2[i]+3.001))))
        
        return bestmodels1,bestmodels2


    def chisqfunc(self,tup,valid_filters_this_row,ul_filters_this_row,curr_row):
        Z,age,M,E_bv, = tup
        print("Testing row {} with log(Z), log(age)/10, log(M)/10, E_bv: ".format(self.rows[curr_row]+2), Z,age,M,E_bv)

        true_M = 10**(M*10)

        models = []
        interpolist = self.interpolate(Z,age,valid_filters_this_row)
        extinctolist = self.extinction(valid_filters_this_row)
        for i in range(len(valid_filters_this_row)):
            models.append(true_M*interpolist[i]*(10/self.d)**2*10**(-0.4*(E_bv*(extinctolist[i]+3.001))))

        summands = []
        for i,valid_ind in enumerate(valid_filters_this_row):
            if valid_ind in ul_filters_this_row:
                if self.ulmeth == "Limit":
                    if models[i] - self.bandfluxes.iat[curr_row,valid_ind] > 0:
                        summands.append(((self.bandfluxes.iat[curr_row,valid_ind] - models[i])/self.bandfluxerrors.iat[curr_row,valid_ind])**2)
                    else:
                        pass
                elif self.ulmeth == "Standard":
                    summands.append(((self.bandfluxes.iat[curr_row,valid_ind]/3 - models[i])/(self.bandfluxes.iat[curr_row,valid_ind]/3))**2)
            else:
                summands.append(((self.bandfluxes.iat[curr_row,valid_ind] - models[i])/self.bandfluxerrors.iat[curr_row,valid_ind])**2)

        chisq = sum(summands)
        print("chisq: ",chisq,"\n")

        return chisq

    def chisqfunc2(self,tup,valid_filters_this_row,ul_filters_this_row,curr_row):
        Z1,age1,M1,E_bv1,Z2,age2,M2,E_bv2 = tup
        print("Testing row {} with log(Z1), log(age1)/10, log(M1)/10, E_bv1, log(Z2), log(age2)/10, log(M2)/10, E_bv2: ".format(self.rows[curr_row]+2), Z1, age1, M1, E_bv1, Z2, age2, M2, E_bv2)

        true_M1 = 10**(M1*10)
        true_M2 = 10**(M2*10)

        models1 = []
        interpolist1 = self.interpolate(Z1,age1,valid_filters_this_row)
        extinctolist1 =self.extinction(valid_filters_this_row)
        for i in range(len(valid_filters_this_row)):
            models1.append(true_M1*interpolist1[i]*(10/self.d)**2*10**(-0.4*(E_bv1*(extinctolist1[i]+3.001))))
        models2 = []
        interpolist2 = self.interpolate(Z2,age2,valid_filters_this_row)
        extinctolist2 = self.extinction(valid_filters_this_row)
        for i in range(len(valid_filters_this_row)):
            models2.append(true_M2*interpolist2[i]*(10/self.d)**2*10**(-0.4*(E_bv2*(extinctolist2[i]+3.001))))

        summands = []
        for i,valid_ind in enumerate(valid_filters_this_row):
            if valid_ind in ul_filters_this_row:
                if self.ulmeth == "Limit":
                    if models1[i]+models2[i] - self.bandfluxes.iat[curr_row,valid_ind] > 0:
                        summands.append(((self.bandfluxes.iat[curr_row,valid_ind] - models1[i]-models2[i])/self.bandfluxerrors.iat[curr_row,valid_ind])**2)
                    else:
                        pass
                elif self.ulmeth == "Standard":
                    summands.append(((self.bandfluxes.iat[curr_row,valid_ind]/3 -models1[i]-models2[i])/(self.bandfluxes.iat[curr_row,valid_ind]/3))**2)
            else:
                summands.append(((self.bandfluxes.iat[curr_row,valid_ind] - models1[i]-models2[i])/self.bandfluxerrors.iat[curr_row,valid_ind])**2)

        chisq = sum(summands)
        print("chisq: ",chisq,"\n")
        return chisq

    def chisqfuncerror(self,lead,leadsign,otherstup):

        if leadsign == 0:
            Z = lead
            age,M,E_bv,valid_filters_this_row,ul_filters_this_row,curr_row = otherstup[0],otherstup[1],otherstup[2],otherstup[3],otherstup[4],otherstup[5]
        elif leadsign == 1:
            age = lead
            Z,M,E_bv,valid_filters_this_row,ul_filters_this_row,curr_row = otherstup[0],otherstup[1],otherstup[2],otherstup[3],otherstup[4],otherstup[5]
        elif leadsign == 2:
            M = lead
            Z,age,E_bv,valid_filters_this_row,ul_filters_this_row,curr_row = otherstup[0],otherstup[1],otherstup[2],otherstup[3],otherstup[4],otherstup[5]
        elif leadsign == 3:
            E_bv = lead
            Z,age,M,valid_filters_this_row,ul_filters_this_row,curr_row = otherstup[0],otherstup[1],otherstup[2],otherstup[3],otherstup[4],otherstup[5]

        true_M = 10**(M*10)

        models = []
        interpolist = self.interpolate(Z,age,valid_filters_this_row)
        extinctolist = self.extinction(valid_filters_this_row)
        for i in range(len(valid_filters_this_row)):
            models.append(true_M*interpolist[i]*(10/self.d)**2*10**(-0.4*(E_bv*(extinctolist[i]+3.001))))

        summands = []
        for i,valid_ind in enumerate(valid_filters_this_row):
            if valid_ind in ul_filters_this_row:
                if self.ulmeth == "Limit":
                    if models[i] - self.bandfluxes.iat[curr_row,valid_ind] > 0:
                        summands.append(((self.bandfluxes.iat[curr_row,valid_ind] - models[i])/self.bandfluxerrors.iat[curr_row,valid_ind])**2)
                    else:
                        pass
                elif self.ulmeth == "Standard":
                    summands.append(((self.bandfluxes.iat[curr_row,valid_ind]/3 - models[i])/(self.bandfluxes.iat[curr_row,valid_ind]/3))**2)
            else:
                summands.append(((self.bandfluxes.iat[curr_row,valid_ind] - models[i])/self.bandfluxerrors.iat[curr_row,valid_ind])**2)


        chisq = sum(summands) - self.results[curr_row].fun - 4.17
        return chisq

    def chisqfunc2error(self,lead,leadsign,otherstup):

        if leadsign == 0:
            Z1 = lead
            age1,M1,E_bv1,Z2,age2,M2,E_bv2,valid_filters_this_row,ul_filters_this_row,curr_row = otherstup[0],otherstup[1],otherstup[2],otherstup[3],otherstup[4],otherstup[5],otherstup[6],otherstup[7],otherstup[8],otherstup[9]
        elif leadsign == 1:
            age1 = lead
            Z1,M1,E_bv1,Z2,age2,M2,E_bv2,valid_filters_this_row,ul_filters_this_row,curr_row = otherstup[0],otherstup[1],otherstup[2],otherstup[3],otherstup[4],otherstup[5],otherstup[6],otherstup[7],otherstup[8],otherstup[9]
        elif leadsign == 2:
            M1 = lead
            Z1,age1,E_bv1,Z2,age2,M2,E_bv2,valid_filters_this_row,ul_filters_this_row,curr_row = otherstup[0],otherstup[1],otherstup[2],otherstup[3],otherstup[4],otherstup[5],otherstup[6],otherstup[7],otherstup[8],otherstup[9]
        elif leadsign == 3:
            E_bv1 = lead
            Z1,age1,M1,Z2,age2,M2,E_bv2,valid_filters_this_row,ul_filters_this_row,curr_row = otherstup[0],otherstup[1],otherstup[2],otherstup[3],otherstup[4],otherstup[5],otherstup[6],otherstup[7],otherstup[8],otherstup[9]
        elif leadsign == 4:
            Z2 = lead
            Z1,age1,M1,E_bv1,age2,M2,E_bv2,valid_filters_this_row,ul_filters_this_row,curr_row = otherstup[0],otherstup[1],otherstup[2],otherstup[3],otherstup[4],otherstup[5],otherstup[6],otherstup[7],otherstup[8],otherstup[9]
        elif leadsign == 5:
            age2 = lead
            Z1,age1,M1,E_bv1,Z2,M2,E_bv2,valid_filters_this_row,ul_filters_this_row,curr_row = otherstup[0],otherstup[1],otherstup[2],otherstup[3],otherstup[4],otherstup[5],otherstup[6],otherstup[7],otherstup[8],otherstup[9]
        elif leadsign == 6:
            M2 = lead
            Z1,age1,M1,E_bv1,Z2,age2,E_bv2,valid_filters_this_row,ul_filters_this_row,curr_row = otherstup[0],otherstup[1],otherstup[2],otherstup[3],otherstup[4],otherstup[5],otherstup[6],otherstup[7],otherstup[8],otherstup[9]
        elif leadsign == 7:
            E_bv2 = lead
            Z1,age1,M1,E_bv1,Z2,age2,M2,valid_filters_this_row,ul_filters_this_row,curr_row = otherstup[0],otherstup[1],otherstup[2],otherstup[3],otherstup[4],otherstup[5],otherstup[6],otherstup[7],otherstup[8],otherstup[9]

        true_M1 = 10**(M1*10)
        true_M2 = 10**(M2*10)

        models1 = []
        interpolist1 = self.interpolate(Z1,age1,valid_filters_this_row)
        extinctolist1 =self.extinction(valid_filters_this_row)
        for i in range(len(valid_filters_this_row)):
            models1.append(true_M1*interpolist1[i]*(10/self.d)**2*10**(-0.4*(E_bv1*(extinctolist1[i]+3.001))))
        models2 = []
        interpolist2 = self.interpolate(Z2,age2,valid_filters_this_row)
        extinctolist2 = self.extinction(valid_filters_this_row)
        for i in range(len(valid_filters_this_row)):
            models2.append(true_M2*interpolist2[i]*(10/self.d)**2*10**(-0.4*(E_bv2*(extinctolist2[i]+3.001))))

        summands = []
        for i,valid_ind in enumerate(valid_filters_this_row):
            if valid_ind in ul_filters_this_row:
                if self.ulmeth == "Limit":
                    if models1[i]+models2[i] - self.bandfluxes.iat[curr_row,valid_ind] > 0:
                        summands.append(((self.bandfluxes.iat[curr_row,valid_ind] - models1[i]-models2[i])/self.bandfluxerrors.iat[curr_row,valid_ind])**2)
                    else:
                        pass
                elif self.ulmeth == "Standard":
                    summands.append(((self.bandfluxes.iat[curr_row,valid_ind]/3 - models1[i]-models2[i])/(self.bandfluxes.iat[curr_row,valid_ind]/3))**2)
            else:
                summands.append(((self.bandfluxes.iat[curr_row,valid_ind] - models1[i]-models2[i])/self.bandfluxerrors.iat[curr_row,valid_ind])**2)

        chisq = sum(summands) - self.results[curr_row].fun - 9.28
        return chisq

    def minimize_chisq(self):
        import numpy as np
        
        if self.single_cluster == True:
            #default guess: -1.0,0.9, 0.7, 0.1
            #bnds = ((-2.6,0.3),(.66,1.02),(0,1.4),(0,2))
            bnds = ((self.Zbound1lo,self.Zbound1hi),(self.agebound1lo,self.agebound1hi),(self.Mbound1lo,self.Mbound1hi),(self.ebvbound1lo,self.ebvbound1hi))
            self.results = []

            for curr_row in range(self.bandfluxes.shape[0]): 
                valid_filters_this_row = []
                ul_filters_this_row = []
                for valid_ind,arraytup in enumerate(zip(self.bandfluxes.loc[curr_row,:],self.ul_frame.loc[curr_row,:])):
                    if np.isnan(arraytup[0]) == False:
                        valid_filters_this_row.append(valid_ind)
                    if arraytup[1] == 1: 
                        ul_filters_this_row.append(valid_ind)
                x0 = np.array([self.Zguess1[curr_row],self.ageguess1[curr_row],self.Mguess1[curr_row],self.ebvguess1[curr_row]])
                self.results.append(opt.minimize(self.chisqfunc, x0, args=(valid_filters_this_row,ul_filters_this_row,curr_row,), bounds=bnds))
            print("results:\n",self.results)
        
        elif self.double_cluster == True:

            #default guess: -0.5, .8477, .6, .2, -1.5, .9477, .8, 0.1 
            #bnds = ((-2.6,0.3),(.66,1.02),(0,1.4),(0,2),(-2.6,0.3),(.66,1.02),(0,1.4),(0,2))
            bnds = ((self.Zbound1lo,self.Zbound1hi),(self.agebound1lo,self.agebound1hi),(self.Mbound1lo,self.Mbound1hi),(self.ebvbound1lo,self.ebvbound1hi),(self.Zbound2lo,self.Zbound2hi),(self.agebound2lo,self.agebound2hi),(self.Mbound2lo,self.Mbound2hi),(self.ebvbound2lo,self.ebvbound2hi))
            self.results = []

            for curr_row in range(self.bandfluxes.shape[0]):  
                valid_filters_this_row = []
                ul_filters_this_row = []
                for valid_ind,arraytup in enumerate(zip(self.bandfluxes.loc[curr_row,:],self.ul_frame.loc[curr_row,:])):
                    if np.isnan(arraytup[0]) == False:
                        valid_filters_this_row.append(valid_ind)
                    if arraytup[1] == 1:
                        ul_filters_this_row.append(valid_ind)
                x0 = np.array([self.Zguess1[curr_row],self.ageguess1[curr_row],self.Mguess1[curr_row],self.ebvguess1[curr_row],self.Zguess2[curr_row],self.ageguess2[curr_row],self.Mguess2[curr_row],self.ebvguess2[curr_row]])
                self.results.append(opt.minimize(self.chisqfunc2, x0, args=(valid_filters_this_row,ul_filters_this_row,curr_row,), bounds=bnds))       
            print("results:\n",self.results)


    def find_param_errors(self):
        import numpy as np

        if self.single_cluster == True:

            self.errorsallrows = []
            self.errornotes = []
            for curr_row in range(self.bandfluxes.shape[0]):  
                valid_filters_this_row = []
                ul_filters_this_row = []
                for valid_ind,arraytup in enumerate(zip(self.bandfluxes.loc[curr_row,:],self.ul_frame.loc[curr_row,:])):
                    if np.isnan(arraytup[0]) == False:
                        valid_filters_this_row.append(valid_ind)
                    if arraytup[1] == 1:
                        ul_filters_this_row.append(valid_ind)
                errorsthisrow = []
                errornotesthisrow = []
                Z,age,M,E_bv = self.results[curr_row].x[0],self.results[curr_row].x[1],self.results[curr_row].x[2],self.results[curr_row].x[3]
                ###
                otherstup = (age,M,E_bv,valid_filters_this_row,ul_filters_this_row,curr_row)
                try:
                    Zlowererror = Z - opt.root_scalar(self.chisqfuncerror, args=(0,otherstup,),method="brentq",bracket=[self.Zbound1lo,Z]).root
                    Zlowernotes = "\n"
                except:
                    Zlowererror = "N/A"
                    if self.chisqfuncerror(Z,0,otherstup,) != self.chisqfuncerror(self.Zbound1lo,0,otherstup,):
                        Zlowernotes = "cannot go low enough to\nchange chi^2 by 4.17"
                    elif self.chisqfuncerror(Z,0,otherstup,) == self.chisqfuncerror(self.Zbound1lo,0,otherstup,):
                        Zlowernotes = "sitting at lower bound\n"
                try:
                    Zuppererror = opt.root_scalar(self.chisqfuncerror, args=(0,otherstup,),method="brentq",bracket=[Z,self.Zbound1hi]).root - Z
                    Zuppernotes = "\n"
                except:
                    Zuppererror = "N/A"
                    if self.chisqfuncerror(Z,0,otherstup,) != self.chisqfuncerror(self.Zbound1hi,0,otherstup,):
                        Zuppernotes = "cannot go high enough to\nchange chi^2 by 4.17"
                    elif self.chisqfuncerror(Z,0,otherstup,) == self.chisqfuncerror(self.Zbound1hi,0,otherstup,):
                        Zuppernotes = "sitting at upper bound\n"
                errorsthisrow.append([Zlowererror,Zuppererror])
                errornotesthisrow.append([Zlowernotes,Zuppernotes])
                ###
                otherstup = (Z,M,E_bv,valid_filters_this_row,ul_filters_this_row,curr_row)              
                try:
                    agelowererror = (age - opt.root_scalar(self.chisqfuncerror, args=(1,otherstup,),method="brentq",bracket=[self.agebound1lo,age]).root)
                    agelowernotes = "\n"
                except:
                    agelowererror = "N/A"
                    if self.chisqfuncerror(age,1,otherstup,) != self.chisqfuncerror(self.agebound1lo,1,otherstup,):
                        agelowernotes = "cannot go low enough to\nchange chi^2 by 4.17"
                    elif self.chisqfuncerror(age,1,otherstup,) == self.chisqfuncerror(self.agebound1lo,1,otherstup,):
                        agelowernotes = "sitting at lower bound\n"
                try:    
                    ageuppererror = (opt.root_scalar(self.chisqfuncerror, args=(1,otherstup,),method="brentq",bracket=[age,self.agebound1hi]).root - age)
                    ageuppernotes = "\n"
                except:
                    ageuppererror = "N/A"
                    if self.chisqfuncerror(age,1,otherstup,) != self.chisqfuncerror(self.agebound1hi,1,otherstup,):
                        ageuppernotes = "cannot go high enough to\nchange chi^2 by 4.17"
                    elif self.chisqfuncerror(age,1,otherstup,) == self.chisqfuncerror(self.agebound1hi,1,otherstup,):
                        ageuppernotes = "sitting at upper bound\n"
                errorsthisrow.append([agelowererror,ageuppererror])
                errornotesthisrow.append([agelowernotes,ageuppernotes])
                ###
                otherstup = (Z,age,E_bv,valid_filters_this_row,ul_filters_this_row,curr_row)     
                try:
                    Mlowererror = M - opt.root_scalar(self.chisqfuncerror, args=(2,otherstup,),method="brentq",bracket=[self.Mbound1lo,M]).root
                    Mlowernotes = "\n"
                except:
                    Mlowererror = "N/A"
                    if self.chisqfuncerror(M,2,otherstup,) != self.chisqfuncerror(self.Mbound1lo,2,otherstup,):
                        Mlowernotes = "cannot go low enough to\nchange chi^2 by 4.17"
                    elif self.chisqfuncerror(M,2,otherstup,) == self.chisqfuncerror(self.Mbound1lo,2,otherstup,):
                        Mlowernotes = "sitting at lower bound\n"
                try:
                    Muppererror = opt.root_scalar(self.chisqfuncerror, args=(2,otherstup,),method="brentq",bracket=[M,self.Mbound1hi]).root - M
                    Muppernotes = "\n"
                except:
                    Muppererror = "N/A"
                    if self.chisqfuncerror(M,2,otherstup,) != self.chisqfuncerror(self.Mbound1hi,2,otherstup,):
                        Muppernotes = "cannot go high enough to\nchange chi^2 by 4.17"
                    elif self.chisqfuncerror(M,2,otherstup,) == self.chisqfuncerror(self.Mbound1hi,2,otherstup,):
                        Muppernotes = "sitting at upper bound\n"
                errorsthisrow.append([Mlowererror,Muppererror])
                errornotesthisrow.append([Mlowernotes,Muppernotes])
                ###
                otherstup = (Z,age,M,valid_filters_this_row,ul_filters_this_row,curr_row)                           
                try:
                    E_bvlowererror = E_bv - opt.root_scalar(self.chisqfuncerror, args=(3,otherstup,),method="brentq",bracket=[self.ebvbound1lo,E_bv]).root
                    ebvlowernotes = "\n"
                except:
                    E_bvlowererror = "N/A"
                    if self.chisqfuncerror(E_bv,3,otherstup,) != self.chisqfuncerror(self.ebvbound1lo,3,otherstup,):
                        ebvlowernotes = "cannot go low enough to\nchange chi^2 by 4.17"
                    elif self.chisqfuncerror(E_bv,3,otherstup,) == self.chisqfuncerror(self.ebvbound1lo,3,otherstup,):
                        ebvlowernotes = "sitting at lower bound\n"
                try:
                    E_bvuppererror = opt.root_scalar(self.chisqfuncerror, args=(3,otherstup,),method="brentq",bracket=[E_bv,self.ebvbound1hi]).root - E_bv
                    ebvuppernotes = "\n"
                except:
                    E_bvuppererror = "N/A"
                    if self.chisqfuncerror(E_bv,3,otherstup,) != self.chisqfuncerror(self.ebvbound1hi,3,otherstup,):
                        ebvuppernotes = "cannot go high enough to\nchange chi^2 by 4.17"
                    elif self.chisqfuncerror(E_bv,3,otherstup,) == self.chisqfuncerror(self.ebvbound1lhi,3,otherstup,):
                        ebvuppernotes = "sitting at upper bound\n"
                errorsthisrow.append([E_bvlowererror,E_bvuppererror])
                errornotesthisrow.append([ebvlowernotes,ebvuppernotes])
                ###
                self.errorsallrows.append(errorsthisrow)
                self.errornotes.append(errornotesthisrow)


        elif self.double_cluster == True:
            self.errornotes = []
            self.errorsallrows = []
            for curr_row in range(self.bandfluxes.shape[0]):  
                valid_filters_this_row = []
                ul_filters_this_row = []
                for valid_ind,arraytup in enumerate(zip(self.bandfluxes.loc[curr_row,:],self.ul_frame.loc[curr_row,:])):
                    if np.isnan(arraytup[0]) == False:
                        valid_filters_this_row.append(valid_ind)
                    if arraytup[1] == 1:
                        ul_filters_this_row.append(valid_ind)
                errorsthisrow = []
                errornotesthisrow = []
                Z1,age1,M1,E_bv1,Z2,age2,M2,E_bv2 = self.results[curr_row].x[0],self.results[curr_row].x[1],self.results[curr_row].x[2],self.results[curr_row].x[3],self.results[curr_row].x[4],self.results[curr_row].x[5],self.results[curr_row].x[6],self.results[curr_row].x[7]
                ###
                otherstup = (age1,M1,E_bv1,Z2,age2,M2,E_bv2,valid_filters_this_row,ul_filters_this_row,curr_row)
                try:
                    Z1lowererror = Z1 - opt.root_scalar(self.chisqfunc2error, args=(0,otherstup,),method="brentq",bracket=[self.Zbound1lo,Z1]).root
                    Z1lowernotes = "\n"
                except:
                    Z1lowererror = "N/A"
                    if self.chisqfunc2error(Z1,0,otherstup,) != self.chisqfunc2error(self.Zbound1lo,0,otherstup,):
                        Z1lowernotes = "cannot go low enough to\nchange chi^2 by 9.28"
                    elif self.chisqfunc2error(Z1,0,otherstup,) == self.chisqfunc2error(self.Zbound1lo,0,otherstup,):
                        Z1lowernotes = "sitting at lower bound\n"
                try:
                    Z1uppererror = opt.root_scalar(self.chisqfunc2error, args=(0,otherstup,),method="brentq",bracket=[Z1,self.Zbound1hi]).root - Z1
                    Z1uppernotes = "\n"
                except:
                    Z1uppererror = "N/A"
                    if self.chisqfunc2error(Z1,0,otherstup,) != self.chisqfunc2error(self.Zbound1hi,0,otherstup,):
                        Z1uppernotes = "cannot go high enough to\nchange chi^2 by 9.28"
                    elif self.chisqfunc2error(Z1,0,otherstup,) == self.chisqfunc2error(self.Zbound1hi,0,otherstup,):
                        Z1uppernotes = "sitting at upper bound\n"
                errorsthisrow.append([Z1lowererror,Z1uppererror])
                errornotesthisrow.append([Z1lowernotes,Z1uppernotes])
                ###
                otherstup = (Z1,M1,E_bv1,Z2,age2,M2,E_bv2,valid_filters_this_row,ul_filters_this_row,curr_row)              
                try:
                    age1lowererror = (age1 - opt.root_scalar(self.chisqfunc2error, args=(1,otherstup,),method="brentq",bracket=[self.agebound1lo,age1]).root)
                    age1lowernotes = "\n"
                except:
                    age1lowererror = "N/A"
                    if self.chisqfunc2error(age1,1,otherstup,) != self.chisqfunc2error(self.agebound1lo,1,otherstup,):
                        age1lowernotes = "cannot go low enough to\nchange chi^2 by 9.28"
                    elif self.chisqfunc2error(age1,1,otherstup,) == self.chisqfunc2error(self.agebound1lo,1,otherstup,):
                        age1lowernotes = "sitting at lower bound\n"
                try:    
                    age1uppererror = (opt.root_scalar(self.chisqfunc2error, args=(1,otherstup,),method="brentq",bracket=[age1,self.agebound1hi]).root - age1)
                    age1uppernotes = "\n"
                except:
                    age1uppererror = "N/A"
                    if self.chisqfunc2error(age1,1,otherstup,) != self.chisqfunc2error(self.agebound1hi,1,otherstup,):
                        age1uppernotes = "cannot go high enough to\nchange chi^2 by 9.28"
                    elif self.chisqfunc2error(age1,1,otherstup,) == self.chisqfunc2error(self.agebound1hi,1,otherstup,):
                        age1uppernotes = "sitting at upper bound\n"
                errorsthisrow.append([age1lowererror,age1uppererror])
                errornotesthisrow.append([age1lowernotes,age1uppernotes])
                ###
                otherstup = (Z1,age1,E_bv1,Z2,age2,M2,E_bv2,valid_filters_this_row,ul_filters_this_row,curr_row)              
                try:
                    M1lowererror = M1 - opt.root_scalar(self.chisqfunc2error, args=(2,otherstup,),method="brentq",bracket=[self.Mbound1lo,M1]).root
                    M1lowernotes = "\n"
                except:
                    M1lowererror = "N/A"
                    if self.chisqfunc2error(M1,2,otherstup,) != self.chisqfunc2error(self.Mbound1lo,2,otherstup,):
                        M1lowernotes = "cannot go low enough\nto change chi^2 by 9.28"
                    elif self.chisqfunc2error(M1,2,otherstup,) == self.chisqfunc2error(self.Mbound1lo,2,otherstup,):
                        M1lowernotes = "sitting at lower bound\n"
                try:
                    M1uppererror = opt.root_scalar(self.chisqfunc2error, args=(2,otherstup,),method="brentq",bracket=[M1,self.Mbound1hi]).root - M1
                    M1uppernotes = "\n"
                except:
                    M1uppererror = "N/A"
                    if self.chisqfunc2error(M1,2,otherstup,) != self.chisqfunc2error(self.Mbound1hi,2,otherstup,):
                        M1uppernotes = "cannot go high enough\nto change chi^2 by 9.28"
                    elif self.chisqfunc2error(M1,2,otherstup,) == self.chisqfunc2error(self.Mbound1hi,2,otherstup,):
                        M1uppernotes = "sitting at upper bound\n"
                errorsthisrow.append([M1lowererror,M1uppererror])
                errornotesthisrow.append([M1lowernotes,M1uppernotes])
                ###
                otherstup = (Z1,age1,M1,Z2,age2,M2,E_bv2,valid_filters_this_row,ul_filters_this_row,curr_row)                           
                try:
                    E_bv1lowererror = E_bv1 - opt.root_scalar(self.chisqfunc2error, args=(3,otherstup,),method="brentq",bracket=[self.ebvbound1lo,E_bv1]).root
                    ebv1lowernotes = "\n"
                except:
                    E_bv1lowererror = "N/A"
                    if self.chisqfunc2error(E_bv1,3,otherstup,) != self.chisqfunc2error(self.ebvbound1lo,3,otherstup,):
                        ebv1lowernotes = "cannot go low enough to\nchange chi^2 by 9.28"
                    elif self.chisqfunc2error(E_bv1,3,otherstup,) == self.chisqfunc2error(self.ebvbound1lo,3,otherstup,):
                        ebv1lowernotes = "sitting at lower bound\n"
                try:
                    E_bv1uppererror = opt.root_scalar(self.chisqfunc2error, args=(3,otherstup,),method="brentq",bracket=[E_bv1,self.ebvbound1hi]).root - E_bv1
                    ebv1uppernotes = "\n"
                except:
                    E_bv1uppererror = "N/A"
                    if self.chisqfunc2error(E_bv1,3,otherstup,) != self.chisqfunc2error(self.ebvbound1hi,3,otherstup,):
                        ebv1uppernotes = "cannot go high enough to\nchange chi^2 by 9.28"
                    elif self.chisqfunc2error(E_bv1,3,otherstup,) == self.chisqfunc2error(self.ebvbound1hi,3,otherstup,):
                        ebv1uppernotes = "sitting at upper bound\n"
                errorsthisrow.append([E_bv1lowererror,E_bv1uppererror])
                errornotesthisrow.append([ebv1lowernotes,ebv1uppernotes])
                ###
                otherstup = (Z1,age1,M1,E_bv1,age2,M2,E_bv2,valid_filters_this_row,ul_filters_this_row,curr_row)
                try:
                    Z2lowererror = Z2 - opt.root_scalar(self.chisqfunc2error, args=(4,otherstup,),method="brentq",bracket=[self.Zbound2lo,Z2]).root
                    Z2lowernotes = "\n"
                except:
                    Z2lowererror = "N/A"
                    if self.chisqfunc2error(Z2,4,otherstup,) != self.chisqfunc2error(self.Zbound2lo,4,otherstup,):
                        Z2lowernotes = "cannot go low enough to\nchange chi^2 by 9.28"
                    elif self.chisqfunc2error(Z2,4,otherstup,) == self.chisqfunc2error(self.Zbound2lo,4,otherstup,):
                        Z2lowernotes = "sitting at lower bound\n"
                try:
                    Z2uppererror = opt.root_scalar(self.chisqfunc2error, args=(4,otherstup,),method="brentq",bracket=[Z2,self.Zbound2hi]).root - Z2
                    Z2uppernotes = "\n"
                except:
                    Z2uppererror = "N/A"
                    if self.chisqfunc2error(Z2,4,otherstup,) != self.chisqfunc2error(self.Zbound2hi,4,otherstup,):
                        Z2uppernotes = "cannot go high enough to\nchange chi^2 by 9.28"
                    elif self.chisqfunc2error(Z2,4,otherstup,) == self.chisqfunc2error(self.Zbound2hi,4,otherstup,):
                        Z2uppernotes = "sitting at upper bound\n"
                errorsthisrow.append([Z2lowererror,Z2uppererror])
                errornotesthisrow.append([Z2lowernotes,Z2uppernotes])
                ###
                otherstup = (Z1,age1,M1,E_bv1,Z2,M2,E_bv2,valid_filters_this_row,ul_filters_this_row,curr_row)              
                try:
                    age2lowererror = (age2 - opt.root_scalar(self.chisqfunc2error, args=(5,otherstup,),method="brentq",bracket=[self.agebound2lo,age2]).root)
                    age2lowernotes = "\n"
                except:
                    age2lowererror = "N/A"
                    if self.chisqfunc2error(age2,5,otherstup,) != self.chisqfunc2error(self.agebound2lo,5,otherstup,):
                        age2lowernotes = "cannot go low enough to\nchange chi^2 by 9.28"
                    elif self.chisqfunc2error(age2,5,otherstup,) == self.chisqfunc2error(self.agebound2lo,5,otherstup,):
                        age2lowernotes = "sitting at lower bound\n"
                try:    
                    age2uppererror = (opt.root_scalar(self.chisqfunc2error, args=(5,otherstup,),method="brentq",bracket=[age2,self.agebound2hi]).root - age2)
                    age2uppernotes = "\n"
                except:
                    age2uppererror = "N/A"
                    if self.chisqfunc2error(age2,5,otherstup,) != self.chisqfunc2error(self.agebound2hi,5,otherstup,):
                        age2uppernotes = "cannot go high enough to\nchange chi^2 by 9.28"
                    elif self.chisqfunc2error(age2,5,otherstup,) == self.chisqfunc2error(self.agebound2hi,5,otherstup,):
                        age2uppernotes = "sitting at upper bound\n"
                errorsthisrow.append([age2lowererror,age2uppererror])
                errornotesthisrow.append([age2lowernotes,age2uppernotes])
                ###
                otherstup = (Z1,age1,M1,E_bv1,Z2,age2,E_bv2,valid_filters_this_row,ul_filters_this_row,curr_row)              
                try:
                    M2lowererror = M2 - opt.root_scalar(self.chisqfunc2error, args=(6,otherstup,),method="brentq",bracket=[self.Mbound2lo,M2]).root
                    M2lowernotes = "\n"
                except:
                    M2lowererror = "N/A"
                    if self.chisqfunc2error(M2,6,otherstup,) != self.chisqfunc2error(self.Mbound2lo,6,otherstup,):
                        M2lowernotes = "cannot go low enough to\nchange chi^2 by 9.28"
                    elif self.chisqfunc2error(M2,6,otherstup,) == self.chisqfunc2error(self.Mbound2lo,6,otherstup,):
                        M2lowernotes = "sitting at lower bound\n"
                try:
                    M2uppererror = opt.root_scalar(self.chisqfunc2error, args=(6,otherstup,),method="brentq",bracket=[M2,self.Mbound2hi]).root - M2
                    M2uppernotes = "\n"
                except:
                    M2uppererror = "N/A"
                    if self.chisqfunc2error(M2,6,otherstup,) != self.chisqfunc2error(self.Mbound2hi,6,otherstup,):
                        M2uppernotes = "cannot go high enough to\nchange chi^2 by 9.28"
                    elif self.chisqfunc2error(M2,6,otherstup,) == self.chisqfunc2error(self.Mbound2hi,6,otherstup,):
                        M2uppernotes = "sitting at upper bound\n"
                errorsthisrow.append([M2lowererror,M2uppererror])
                errornotesthisrow.append([M2lowernotes,M2uppernotes])
                ###
                otherstup = (Z1,age1,M1,E_bv1,Z2,age2,M2,valid_filters_this_row,ul_filters_this_row,curr_row)                           
                try:
                    E_bv2lowererror = E_bv2 - opt.root_scalar(self.chisqfunc2error, args=(7,otherstup,),method="brentq",bracket=[self.ebvbound2lo,E_bv2]).root
                    ebv2lowernotes = "\n"
                except:
                    E_bv2lowererror = "N/A"
                    if self.chisqfunc2error(E_bv2,7,otherstup,) != self.chisqfunc2error(self.ebvbound2lo,7,otherstup,):
                        ebv2lowernotes = "cannot go low enough to\nchange chi^2 by 9.28"
                    elif self.chisqfunc2error(E_bv2,7,otherstup,) == self.chisqfunc2error(self.ebvbound2lo,7,otherstup,):
                        ebv2lowernotes = "sitting at lower bound\n"
                try:
                    E_bv2uppererror = opt.root_scalar(self.chisqfunc2error, args=(7,otherstup,),method="brentq",bracket=[E_bv2,self.ebvbound2hi]).root - E_bv2
                    ebv2uppernotes = "\n"
                except:
                    E_bv2uppererror = "N/A"
                    if self.chisqfunc2error(E_bv2,7,otherstup,) != self.chisqfunc2error(self.ebvbound2hi,7,otherstup,):
                        ebv2uppernotes = "cannot go high enough to\nchange chi^2 by 9.28"
                    elif self.chisqfunc2error(E_bv2,7,otherstup,) == self.chisqfunc2error(self.ebvbound2hi,7,otherstup,):
                        ebv2uppernotes = "sitting at upper bound\n"
                errorsthisrow.append([E_bv2lowererror,E_bv2uppererror])
                errornotesthisrow.append([ebv2lowernotes,ebv2uppernotes])
                ###

                self.errorsallrows.append(errorsthisrow)
                self.errornotes.append(errornotesthisrow)
           
    def display_all_results(self):
        if self.dispresults == 1:
            if self.single_cluster == True:
                self.rsol_list = []
                for curr_row in range(self.bandfluxes.shape[0]):
                    self.display_results_single(curr_row)
            elif self.double_cluster == True:
                self.rsol_list = []
                for curr_row in range(self.bandfluxes.shape[0]): 
                    self.display_results_double(curr_row)

    def save_output(self):

        import numpy as np
        import pandas as pd
        
        if self.single_cluster == True:

            models = self.bandfluxes.copy(deep=True)
            self.truefluxerrors = self.bandfluxerrors.copy(deep=True)

            for curr_row in range(self.bandfluxes.shape[0]):
                valid_filters_this_row = []
                ul_filters_this_row = []
                for valid_ind,arraytup in enumerate(zip(self.bandfluxes.loc[curr_row,:],self.ul_frame.loc[curr_row,:])):
                    if np.isnan(arraytup[0]) == False:
                        valid_filters_this_row.append(valid_ind)
                    if arraytup[1] == 1:
                        ul_filters_this_row.append(valid_ind)

                best_tup = (self.results[curr_row].x[0],self.results[curr_row].x[1],self.results[curr_row].x[2],self.results[curr_row].x[3])
                model = self.minichisqfunc_single(best_tup,valid_filters_this_row)
                used = 0 
                for colno,col in enumerate(models.loc[curr_row,:]):
                    if np.isnan(col) == False:
                        models.iat[curr_row,colno] = model[used]
                        used += 1
                
                for colno, arraytup in enumerate(zip(self.bandfluxerrors.loc[curr_row,:],self.ul_frame.loc[curr_row,:],self.bandfluxes.loc[curr_row,:])):
                    if np.isnan(arraytup[0]) == False:
                        self.truefluxerrors.iat[curr_row,colno] = (arraytup[0])
                    if arraytup[1] == 1:
                        if self.ulmeth == "Limit":
                            self.truefluxerrors.iat[curr_row,colno] = (arraytup[0]*-3)
                        elif self.ulmeth == "Standard":
                            self.truefluxerrors.iat[curr_row,colno] = (arraytup[2]*-1/3)
            

            if self.fluxresults == 1:

                if self.model_chosen == "UVIT_HST":        
                    colnames = {"F148W_meas_flux [mJy]" : [], "F148W_err [mJy]" : [], "F148W_avg_wav [nm]" : [], "F148W_model_flux [mJy]" : [], "F169M_meas_flux [mJy]" : [], "F169M_err [mJy]" : [], "F169M_avg_wav [nm]" : [], "F169M_model_flux [mJy]" : [], "F172M_meas_flux [mJy]" : [], "F172M_err [mJy]" : [], "F172M_avg_wav [nm]" : [], "F172M_model_flux [mJy]" : [], "N219M_meas_flux [mJy]" : [], "N219M_err [mJy]" : [], "N219M_avg_wav [nm]" : [], "N219M_model_flux [mJy]" : [], "N279N_meas_flux [mJy]" : [], "N279N_err [mJy]" : [], "N279N_avg_wav [nm]" : [], "N279N_model_flux [mJy]" : [], "f275w_meas_flux [mJy]" : [], "f275w_err [mJy]" : [], "f275w_avg_wav [nm]" : [], "f275w_model_flux [mJy]" : [], "f336w_meas_flux [mJy]" : [], "f336w_err [mJy]" : [], "f336w_avg_wav [nm]" : [], "f336w_model_flux [mJy]" : [], "f475w_meas_flux [mJy]" : [], "f475w_err [mJy]" : [], "f475w_avg_wav [nm]" : [], "f475w_model_flux [mJy]" : [], "f814w_meas_flux [mJy]" : [], "f814w_err [mJy]" : [], "f814w_avg_wav [nm]" : [], "f814w_model_flux [mJy]" : [], "f110w_meas_flux [mJy]" : [], "f110w_err [mJy]" : [], "f110w_avg_wav [nm]" : [], "f110w_model_flux [mJy]" : [], "f160w_meas_flux [mJy]" : [], "f160w_err [mJy]" : [], "f160w_avg_wav [nm]" : [], "f160w_model_flux [mJy]" : []}
                elif self.model_chosen == "UVIT_SDSS_Spitzer":
                    colnames = {"F148W_meas_flux [mJy]" : [], "F148W_err [mJy]" : [], "F148W_avg_wav [nm]" : [], "F148W_model_flux [mJy]" : [], "F169M_meas_flux [mJy]" : [], "F169M_err [mJy]" : [], "F169M_avg_wav [nm]" : [], "F169M_model_flux [mJy]" : [], "F172M_meas_flux [mJy]" : [], "F172M_err [mJy]" : [], "F172M_avg_wav [nm]" : [], "F172M_model_flux [mJy]" : [], "N219M_meas_flux [mJy]" : [], "N219M_err [mJy]" : [], "N219M_avg_wav [nm]" : [], "N219M_model_flux [mJy]" : [], "N279N_meas_flux [mJy]" : [], "N279N_err [mJy]" : [], "N279N_avg_wav [nm]" : [], "N279N_model_flux [mJy]" : [], "u_prime_meas_flux [mJy]" : [], "u_prime_err [mJy]" : [], "u_prime_avg_wav [nm]" : [], "u_prime_model_flux [mJy]" : [], "g_prime_meas_flux [mJy]" : [], "g_prime_err [mJy]" : [], "g_prime_avg_wav [nm]" : [], "g_prime_model_flux [mJy]" : [], "r_prime_meas_flux [mJy]" : [], "r_prime_err [mJy]" : [], "r_prime_avg_wav [nm]" : [], "r_prime_model_flux [mJy]" : [], "i_prime_meas_flux [mJy]" : [], "i_prime_err [mJy]" : [], "i_prime_avg_wav [nm]" : [], "i_prime_model_flux [mJy]" : [], "z_prime_meas_flux [mJy]" : [], "z_prime_err [mJy]" : [], "z_prime_avg_wav [nm]" : [], "z_prime_model_flux [mJy]" : [], "IRAC1_meas_flux [mJy]" : [], "IRAC1_err [mJy]" : [], "IRAC1_avg_wav [nm]" : [], "IRAC1_model_flux [mJy]" : [], "IRAC2_meas_flux [mJy]" : [], "IRAC2_err [mJy]" : [], "IRAC2_avg_wav [nm]" : [], "IRAC2_model_flux [mJy]" : []}
                fluxresultsdf = pd.DataFrame(colnames)
                for curr_row in range(self.bandfluxes.shape[0]):
                    if self.model_chosen == "UVIT_HST": 
                        rowdict = {"F148W_meas_flux [mJy]" : self.bandfluxes.iat[curr_row,0], "F148W_err [mJy]" : self.truefluxerrors.iat[curr_row,0], "F148W_avg_wav [nm]" : self.avgwvlist[0], "F148W_model_flux [mJy]" : models.iat[curr_row,0], "F169M_meas_flux [mJy]" : self.bandfluxes.iat[curr_row,1], "F169M_err [mJy]" : self.truefluxerrors.iat[curr_row,1], "F169M_avg_wav [nm]" : self.avgwvlist[1], "F169M_model_flux [mJy]" : models.iat[curr_row,1], "F172M_meas_flux [mJy]" : self.bandfluxes.iat[curr_row,2], "F172M_err [mJy]" : self.truefluxerrors.iat[curr_row,2], "F172M_avg_wav [nm]" : self.avgwvlist[2], "F172M_model_flux [mJy]" : models.iat[curr_row,2], "N219M_meas_flux [mJy]" : self.bandfluxes.iat[curr_row,3], "N219M_err [mJy]" : self.truefluxerrors.iat[curr_row,3], "N219M_avg_wav [nm]" : self.avgwvlist[3], "N219M_model_flux [mJy]" : models.iat[curr_row,3], "N279N_meas_flux [mJy]" : self.bandfluxes.iat[curr_row,4], "N279N_err [mJy]" : self.truefluxerrors.iat[curr_row,4], "N279N_avg_wav [nm]" : self.avgwvlist[4], "N279N_model_flux [mJy]" : models.iat[curr_row,4], "f275w_meas_flux [mJy]" : self.bandfluxes.iat[curr_row,5], "f275w_err [mJy]" : self.truefluxerrors.iat[curr_row,5], "f275w_avg_wav [nm]" : self.avgwvlist[5], "f275w_model_flux [mJy]" : models.iat[curr_row,5], "f336w_meas_flux [mJy]" : self.bandfluxes.iat[curr_row,6], "f336w_err [mJy]" : self.truefluxerrors.iat[curr_row,6], "f336w_avg_wav [nm]" : self.avgwvlist[6], "f336w_model_flux [mJy]" : models.iat[curr_row,6], "f475w_meas_flux [mJy]" : self.bandfluxes.iat[curr_row,7], "f475w_err [mJy]" : self.truefluxerrors.iat[curr_row,7], "f475w_avg_wav [nm]" : self.avgwvlist[7], "f475w_model_flux [mJy]" : models.iat[curr_row,7], "f814w_meas_flux [mJy]" : self.bandfluxes.iat[curr_row,8], "f814w_err [mJy]" : self.truefluxerrors.iat[curr_row,8], "f814w_avg_wav [nm]" : self.avgwvlist[8], "f814w_model_flux [mJy]" : models.iat[curr_row,8], "f110w_meas_flux [mJy]" : self.bandfluxes.iat[curr_row,9], "f110w_err [mJy]" : self.truefluxerrors.iat[curr_row,9], "f110w_avg_wav [nm]" : self.avgwvlist[9], "f110w_model_flux [mJy]" : models.iat[curr_row,9], "f160w_meas_flux [mJy]" : self.bandfluxes.iat[curr_row,10], "f160w_err [mJy]" : self.truefluxerrors.iat[curr_row,10], "f160w_avg_wav [nm]" : self.avgwvlist[10], "f160w_model_flux [mJy]" : models.iat[curr_row,10]}
                    elif self.model_chosen == "UVIT_SDSS_Spitzer": 
                        rowdict = {"F148W_meas_flux [mJy]" : self.bandfluxes.iat[curr_row,0], "F148W_err [mJy]" : self.truefluxerrors.iat[curr_row,0], "F148W_avg_wav [nm]" : self.avgwvlist[0], "F148W_model_flux [mJy]" : models.iat[curr_row,0], "F169M_meas_flux [mJy]" : self.bandfluxes.iat[curr_row,1], "F169M_err [mJy]" : self.truefluxerrors.iat[curr_row,1], "F169M_avg_wav [nm]" : self.avgwvlist[1], "F169M_model_flux [mJy]" : models.iat[curr_row,1], "F172M_meas_flux [mJy]" : self.bandfluxes.iat[curr_row,2], "F172M_err [mJy]" : self.truefluxerrors.iat[curr_row,2], "F172M_avg_wav [nm]" : self.avgwvlist[2], "F172M_model_flux [mJy]" : models.iat[curr_row,2], "N219M_meas_flux [mJy]" : self.bandfluxes.iat[curr_row,3], "N219M_err [mJy]" : self.truefluxerrors.iat[curr_row,3], "N219M_avg_wav [nm]" : self.avgwvlist[3], "N219M_model_flux [mJy]" : models.iat[curr_row,3], "N279N_meas_flux [mJy]" : self.bandfluxes.iat[curr_row,4], "N279N_err [mJy]" : self.truefluxerrors.iat[curr_row,4], "N279N_avg_wav [nm]" : self.avgwvlist[4], "N279N_model_flux [mJy]" : models.iat[curr_row,4], "u_prime_meas_flux [mJy]" : self.bandfluxes.iat[curr_row,5], "u_prime_err [mJy]" : self.truefluxerrors.iat[curr_row,5], "u_prime_avg_wav [nm]" : self.avgwvlist[5], "u_prime_model_flux [mJy]" : models.iat[curr_row,5], "g_prime_meas_flux [mJy]" : self.bandfluxes.iat[curr_row,6], "g_prime_err [mJy]" : self.truefluxerrors.iat[curr_row,6], "g_prime_avg_wav [nm]" : self.avgwvlist[6], "g_prime_model_flux [mJy]" : models.iat[curr_row,6], "r_prime_meas_flux [mJy]" : self.bandfluxes.iat[curr_row,7], "r_prime_err [mJy]" : self.truefluxerrors.iat[curr_row,7], "r_prime_avg_wav [nm]" : self.avgwvlist[7], "r_prime_model_flux [mJy]" : models.iat[curr_row,7], "i_prime_meas_flux [mJy]" : self.bandfluxes.iat[curr_row,8], "i_prime_err [mJy]" : self.truefluxerrors.iat[curr_row,8], "i_prime_avg_wav [nm]" : self.avgwvlist[8], "i_prime_model_flux [mJy]" : models.iat[curr_row,8], "z_prime_meas_flux [mJy]" : self.bandfluxes.iat[curr_row,9], "z_prime_err [mJy]" : self.truefluxerrors.iat[curr_row,9], "z_prime_avg_wav [nm]" : self.avgwvlist[9], "z_prime_model_flux [mJy]" : models.iat[curr_row,9], "IRAC1_meas_flux [mJy]" : self.bandfluxes.iat[curr_row,10], "IRAC1_err [mJy]" : self.truefluxerrors.iat[curr_row,10], "IRAC1_avg_wav [nm]" : self.avgwvlist[10], "IRAC1_model_flux [mJy]" : models.iat[curr_row,10], "IRAC2_meas_flux [mJy]" : self.bandfluxes.iat[curr_row,11], "IRAC2_err [mJy]" : self.truefluxerrors.iat[curr_row,11], "IRAC2_avg_wav [nm]" : self.avgwvlist[11], "IRAC2_model_flux [mJy]" : models.iat[curr_row,11]}
                    fluxresultsdf =fluxresultsdf.append(rowdict,ignore_index=True)
                for curr_row in range(self.bandfluxes.shape[0]):
                    fluxresultsdf = fluxresultsdf.rename(index={curr_row:"Source at row {}".format(self.rows[curr_row]+2)})
                try:
                    fluxresultsdf.to_csv("{}".format(self.fluxfilename))
                except:
                    import tkinter as tk
                    from tkinter import messagebox
                    tk.messagebox.showerror('Error','An error occurred. This can happen if a file is open while trying to overwrite it. Please close any relevant files and try again.')  
            
            
        elif self.double_cluster == True:

            hotmodels = self.bandfluxes.copy(deep=True)
            coolmodels = self.bandfluxes.copy(deep=True)
            self.truefluxerrors = self.bandfluxerrors.copy(deep=True)

            for curr_row in range(self.bandfluxes.shape[0]):
                valid_filters_this_row = []
                ul_filters_this_row = []
                for valid_ind,arraytup in enumerate(zip(self.bandfluxes.loc[curr_row,:],self.ul_frame.loc[curr_row,:])):
                    if np.isnan(arraytup[0]) == False:
                        valid_filters_this_row.append(valid_ind)
                    if arraytup[1] == 1:
                        ul_filters_this_row.append(valid_ind)
    
                best_tup = (self.results[curr_row].x[0],self.results[curr_row].x[1],self.results[curr_row].x[2],self.results[curr_row].x[3],self.results[curr_row].x[4],self.results[curr_row].x[5],self.results[curr_row].x[6],self.results[curr_row].x[7])
                hot,cool = self.minichisqfunc_double(best_tup,valid_filters_this_row)
                usedhot = 0
                usedcool = 0
                for colno,col in enumerate(hotmodels.loc[curr_row,:]):
                    if np.isnan(col) == False:
                        hotmodels.iat[curr_row,colno] = hot[usedhot]
                        usedhot += 1
                for colno,col in enumerate(coolmodels.loc[curr_row,:]):
                    if np.isnan(col) == False:
                        coolmodels.iat[curr_row,colno] = cool[usedcool]
                        usedcool += 1

                for colno, arraytup in enumerate(zip(self.bandfluxerrors.loc[curr_row,:],self.ul_frame.loc[curr_row,:],self.bandfluxes.loc[curr_row,:])):
                    if np.isnan(arraytup[0]) == False:
                        self.truefluxerrors.iat[curr_row,colno] = (arraytup[0])
                    if arraytup[1] == 1:
                        if self.ulmeth == "Limit":
                            self.truefluxerrors.iat[curr_row,colno] = (arraytup[0]*-3)
                        elif self.ulmeth == "Standard":
                            self.truefluxerrors.iat[curr_row,colno] = (arraytup[2]*-1/3)
                
            if self.fluxresults == 1:

                if self.model_chosen == "UVIT_HST":        
                    colnames = {"F148W_meas_flux [mJy]" : [], "F148W_err [mJy]" : [], "F148W_avg_wav [nm]" : [], "F148W_hot_flux" : [], "F148W_cool_flux" : [], "F169M_meas_flux [mJy]" : [], "F169M_err [mJy]" : [], "F169M_avg_wav [nm]" : [], "F169M_hot_flux [mJy]" : [], "F169M_cool_flux [mJy]" : [], "F172M_meas_flux [mJy]" : [], "F172M_err [mJy]" : [], "F172M_avg_wav [nm]" : [], "F172M_hot_flux [mJy]" : [], "F172M_cool_flux [mJy]" : [], "N219M_meas_flux [mJy]" : [], "N219M_err [mJy]" : [], "N219M_avg_wav [nm]" : [], "N219M_hot_flux [mJy]" : [], "N219M_cool_flux [mJy]" : [], "N279N_meas_flux [mJy]" : [], "N279N_err [mJy]" : [], "N279N_avg_wav [nm]" : [], "N279N_hot_flux [mJy]" : [], "N279N_cool_flux [mJy]" : [], "f275w_meas_flux [mJy]" : [], "f275w_err [mJy]" : [], "f275w_avg_wav [nm]" : [], "f275w_hot_flux [mJy]" : [], "f275w_cool_flux [mJy]" : [], "f336w_meas_flux [mJy]" : [], "f336w_err [mJy]" : [], "f336w_avg_wav [nm]" : [], "f336w_hot_flux [mJy]" : [], "f336w_cool_flux [mJy]" : [], "f475w_meas_flux [mJy]" : [], "f475w_err [mJy]" : [], "f475w_avg_wav [nm]" : [], "f475w_hot_flux [mJy]" : [], "f475w_cool_flux [mJy]" : [], "f814w_meas_flux [mJy]" : [], "f814w_err [mJy]" : [], "f814w_avg_wav [nm]" : [], "f814w_hot_flux [mJy]" : [], "f814w_cool_flux [mJy]" : [], "f110w_meas_flux [mJy]" : [], "f110w_err [mJy]" : [], "f110w_avg_wav [nm]" : [], "f110w_hot_flux [mJy]" : [], "f110w_cool_flux [mJy]" : [], "f160w_meas_flux [mJy]" : [], "f160w_err [mJy]" : [], "f160w_avg_wav [nm]" : [], "f160w_hot_flux [mJy]" : [], "f160w_cool_flux [mJy]" : []}
                elif self.model_chosen == "UVIT_SDSS_Spitzer":
                    colnames = {"F148W_meas_flux [mJy]" : [], "F148W_err [mJy]" : [], "F148W_avg_wav [nm]" : [], "F148W_hot_flux [mJy]" : [], "F148W_cool_flux" : [], "F169M_meas_flux [mJy]" : [], "F169M_err [mJy]" : [], "F169M_avg_wav [nm]" : [], "F169M_hot_flux [mJy]" : [], "F169M_cool_flux [mJy]" : [], "F172M_meas_flux [mJy]" : [], "F172M_err [mJy]" : [], "F172M_avg_wav [nm]" : [], "F172M_hot_flux [mJy]" : [], "F172M_cool_flux [mJy]" : [], "N219M_meas_flux [mJy]" : [], "N219M_err [mJy]" : [], "N219M_avg_wav [nm]" : [], "N219M_hot_flux [mJy]" : [], "N219M_cool_flux [mJy]" : [], "N279N_meas_flux [mJy]" : [], "N279N_err [mJy]" : [], "N279N_avg_wav [nm]" : [], "N279N_hot_flux [mJy]" : [], "N279N_cool_flux [mJy]" : [], "u_prime_meas_flux [mJy]" : [], "u_prime_err [mJy]" : [], "u_prime_avg_wav [nm]" : [], "u_prime_hot_flux [mJy]" : [], "u_prime_cool_flux [mJy]" : [], "g_prime_meas_flux [mJy]" : [], "g_prime_err [mJy]" : [], "g_prime_avg_wav [nm]" : [], "g_prime_hot_flux [mJy]" : [],  "g_prime_cool_flux [mJy]" : [], "r_prime_meas_flux [mJy]" : [], "r_prime_err [mJy]" : [], "r_prime_avg_wav [nm]" : [], "r_prime_hot_flux [mJy]" : [], "r_prime_cool_flux [mJy]" : [], "i_prime_meas_flux [mJy]" : [], "i_prime_err [mJy]" : [], "i_prime_avg_wav [nm]" : [], "i_prime_hot_flux [mJy]" : [], "i_prime_cool_flux [mJy]" : [],  "z_prime_meas_flux [mJy]" : [], "z_prime_err [mJy]" : [], "z_prime_avg_wav [nm]" : [], "z_prime_hot_flux [mJy]" : [], "z_prime_cool_flux [mJy]" : [],  "IRAC1_meas_flux [mJy]" : [], "IRAC1_err [mJy]" : [], "IRAC1_avg_wav [nm]" : [], "IRAC1_hot_flux [mJy]" : [], "IRAC1_cool_flux [mJy]" : [], "IRAC2_meas_flux [mJy]" : [], "IRAC2_err [mJy]" : [], "IRAC2_avg_wav [nm]" : [], "IRAC2_hot_flux [mJy]" : [], "IRAC2_cool_flux [mJy]" : []}
                fluxresultsdf = pd.DataFrame(colnames)
                for curr_row in range(self.bandfluxes.shape[0]):
                    if self.model_chosen == "UVIT_HST": 
                        rowdict = {"F148W_meas_flux [mJy]" : self.bandfluxes.iat[curr_row,0], "F148W_err [mJy]" : self.truefluxerrors.iat[curr_row,0], "F148W_avg_wav [nm]" : self.avgwvlist[0], "F148W_hot_flux [mJy]" : hotmodels.iat[curr_row,0], "F148W_cool_flux [mJy]" : coolmodels.iat[curr_row,0], "F169M_meas_flux [mJy]" : self.bandfluxes.iat[curr_row,1], "F169M_err [mJy]" : self.truefluxerrors.iat[curr_row,1], "F169M_avg_wav [nm]" : self.avgwvlist[1], "F169M_hot_flux [mJy]" : hotmodels.iat[curr_row,1], "F169M_cool_flux [mJy]" : coolmodels.iat[curr_row,1], "F172M_meas_flux [mJy]" : self.bandfluxes.iat[curr_row,2], "F172M_err [mJy]" : self.truefluxerrors.iat[curr_row,2], "F172M_avg_wav [nm]" : self.avgwvlist[2], "F172M_hot_flux [mJy]" : hotmodels.iat[curr_row,2], "F172M_cool_flux [mJy]" : coolmodels.iat[curr_row,2], "N219M_meas_flux [mJy]" : self.bandfluxes.iat[curr_row,3], "N219M_err [mJy]" : self.truefluxerrors.iat[curr_row,3], "N219M_avg_wav [nm]" : self.avgwvlist[3], "N219M_hot_flux [mJy]" : hotmodels.iat[curr_row,3], "N219M_cool_flux [mJy]" : coolmodels.iat[curr_row,3], "N279N_meas_flux [mJy]" : self.bandfluxes.iat[curr_row,4], "N279N_err [mJy]" : self.truefluxerrors.iat[curr_row,4], "N279N_avg_wav [nm]" : self.avgwvlist[4], "N279N_hot_flux [mJy]" : hotmodels.iat[curr_row,4], "N279N_cool_flux [mJy]" : coolmodels.iat[curr_row,4], "f275w_meas_flux [mJy]" : self.bandfluxes.iat[curr_row,5], "f275w_err [mJy]" : self.truefluxerrors.iat[curr_row,5], "f275w_avg_wav [nm]" : self.avgwvlist[5], "f275w_hot_flux [mJy]" : hotmodels.iat[curr_row,5], "f275w_cool_flux [mJy]" : coolmodels.iat[curr_row,5], "f336w_meas_flux [mJy]" : self.bandfluxes.iat[curr_row,6], "f336w_err [mJy]" : self.truefluxerrors.iat[curr_row,6], "f336w_avg_wav [nm]" : self.avgwvlist[6], "f336w_hot_flux [mJy]" : hotmodels.iat[curr_row,6], "f336w_cool_flux [mJy]" : coolmodels.iat[curr_row,6], "f475w_meas_flux [mJy]" : self.bandfluxes.iat[curr_row,7], "f475w_err [mJy]" : self.truefluxerrors.iat[curr_row,7], "f475w_avg_wav [nm]" : self.avgwvlist[7], "f475w_hot_flux [mJy]" : hotmodels.iat[curr_row,7], "f475w_cool_flux [mJy]" : coolmodels.iat[curr_row,7], "f814w_meas_flux [mJy]" : self.bandfluxes.iat[curr_row,8], "f814w_err [mJy]" : self.truefluxerrors.iat[curr_row,8], "f814w_avg_wav [nm]" : self.avgwvlist[8], "f814w_hot_flux [mJy]" : hotmodels.iat[curr_row,8], "f814w_cool_flux [mJy]" : coolmodels.iat[curr_row,8], "f110w_meas_flux [mJy]" : self.bandfluxes.iat[curr_row,9], "f110w_err [mJy]" : self.truefluxerrors.iat[curr_row,9], "f110w_avg_wav [nm]" : self.avgwvlist[9], "f110w_hot_flux [mJy]" : hotmodels.iat[curr_row,9], "f110w_cool_flux [mJy]" : coolmodels.iat[curr_row,9], "f160w_meas_flux [mJy]" : self.bandfluxes.iat[curr_row,10], "f160w_err [mJy]" : self.truefluxerrors.iat[curr_row,10], "f160w_avg_wav [nm]" : self.avgwvlist[10], "f160w_hot_flux [mJy]" : hotmodels.iat[curr_row,10], "f160w_cool_flux [mJy]" : coolmodels.iat[curr_row,10]}
                    elif self.model_chosen == "UVIT_SDSS_Spitzer": 
                        rowdict = {"F148W_meas_flux [mJy]" : self.bandfluxes.iat[curr_row,0], "F148W_err [mJy]" : self.truefluxerrors.iat[curr_row,0], "F148W_avg_wav [nm]" : self.avgwvlist[0], "F148W_hot_flux [mJy]" : hotmodels.iat[curr_row,0], "F148W_cool_flux [mJy]" : coolmodels.iat[curr_row,0], "F169M_meas_flux [mJy]" : self.bandfluxes.iat[curr_row,1], "F169M_err [mJy]" : self.truefluxerrors.iat[curr_row,1], "F169M_avg_wav [nm]" : self.avgwvlist[1], "F169M_hot_flux [mJy]" : hotmodels.iat[curr_row,1], "F169M_cool_flux [mJy]" : coolmodels.iat[curr_row,1], "F172M_meas_flux [mJy]" : self.bandfluxes.iat[curr_row,2], "F172M_err [mJy]" : self.truefluxerrors.iat[curr_row,2], "F172M_avg_wav [nm]" : self.avgwvlist[2], "F172M_hot_flux [mJy]" : hotmodels.iat[curr_row,2], "F172M_cool_flux [mJy]" : coolmodels.iat[curr_row,2], "N219M_meas_flux [mJy]" : self.bandfluxes.iat[curr_row,3], "N219M_err [mJy]" : self.truefluxerrors.iat[curr_row,3], "N219M_avg_wav [nm]" : self.avgwvlist[3], "N219M_hot_flux [mJy]" : hotmodels.iat[curr_row,3], "N219M_cool_flux [mJy]" : coolmodels.iat[curr_row,3], "N279N_meas_flux [mJy]" : self.bandfluxes.iat[curr_row,4], "N279N_err [mJy]" : self.truefluxerrors.iat[curr_row,4], "N279N_avg_wav [nm]" : self.avgwvlist[4], "N279N_hot_flux [mJy]" : hotmodels.iat[curr_row,4], "N279N_cool_flux [mJy]" : coolmodels.iat[curr_row,4], "u_prime_meas_flux [mJy]" : self.bandfluxes.iat[curr_row,5], "u_prime_err [mJy]" : self.truefluxerrors.iat[curr_row,5], "u_prime_avg_wav [nm]" : self.avgwvlist[5], "u_prime_hot_flux [mJy]" : hotmodels.iat[curr_row,5], "u_prime_cool_flux [mJy]" : coolmodels.iat[curr_row,5], "g_prime_meas_flux [mJy]" : self.bandfluxes.iat[curr_row,6], "g_prime_err [mJy]" : self.truefluxerrors.iat[curr_row,6], "g_prime_avg_wav [nm]" : self.avgwvlist[6], "g_prime_hot_flux [mJy]" : hotmodels.iat[curr_row,6], "g_prime_cool_flux [mJy]" : coolmodels.iat[curr_row,6], "r_prime_meas_flux [mJy]" : self.bandfluxes.iat[curr_row,7], "r_prime_err [mJy]" : self.truefluxerrors.iat[curr_row,7], "r_prime_avg_wav [nm]" : self.avgwvlist[7], "r_prime_hot_flux [mJy]" : hotmodels.iat[curr_row,7], "r_prime_cool_flux [mJy]" : coolmodels.iat[curr_row,7], "i_prime_meas_flux [mJy]" : self.bandfluxes.iat[curr_row,8], "i_prime_err [mJy]" : self.truefluxerrors.iat[curr_row,8], "i_prime_avg_wav [nm]" : self.avgwvlist[8], "i_prime_hot_flux [mJy]" : hotmodels.iat[curr_row,8], "i_prime_cool_flux [mJy]" : coolmodels.iat[curr_row,8], "z_prime_meas_flux [mJy]" : self.bandfluxes.iat[curr_row,9], "z_prime_err [mJy]" : self.truefluxerrors.iat[curr_row,9], "z_prime_avg_wav [nm]" : self.avgwvlist[9], "z_prime_hot_flux [mJy]" : hotmodels.iat[curr_row,9], "z_prime_cool_flux [mJy]" : coolmodels.iat[curr_row,9], "IRAC1_meas_flux [mJy]" : self.bandfluxes.iat[curr_row,10], "IRAC1_err [mJy]" : self.truefluxerrors.iat[curr_row,10], "IRAC1_avg_wav [nm]" : self.avgwvlist[10], "IRAC1_hot_flux [mJy]" : hotmodels.iat[curr_row,10], "IRAC1_cool_flux [mJy]" : coolmodels.iat[curr_row,10], "IRAC2_meas_flux [mJy]" : self.bandfluxes.iat[curr_row,11], "IRAC2_err [mJy]" : self.truefluxerrors.iat[curr_row,11], "IRAC2_avg_wav [nm]" : self.avgwvlist[11], "IRAC2_hot_flux [mJy]" : hotmodels.iat[curr_row,11],  "IRAC2_cool_flux [mJy]" : coolmodels.iat[curr_row,11]}
                    fluxresultsdf =fluxresultsdf.append(rowdict,ignore_index=True)
                for curr_row in range(self.bandfluxes.shape[0]):
                    fluxresultsdf = fluxresultsdf.rename(index={curr_row:"Source at row {}".format(self.rows[curr_row]+2)})
                try:
                    fluxresultsdf.to_csv("{}".format(self.fluxfilename))
                except:
                    import tkinter as tk
                    from tkinter import messagebox
                    tk.messagebox.showerror('Error','An error occurred. This can happen if a file is open while trying to overwrite it. Please close any relevant files and try again.') 

        if self.chiparams == 1:
            
            if self.single_cluster == True:
                import math
                colnames = {'Source_ID' : [], 'minimized chi^2' : [], 'log(Z)' : [], 'log(Z)_err_lo' : [], 'log(Z)_err_hi' : [], 'log(age)/10' : [], 'log(age)/10_err_lo' : [], 'log(age)/10_err_hi' : [], 'log(M)/10' : [], 'log(M)/10_err_lo' : [], 'log(M)/10_err_hi' : [], 'E(B-V)' : [], 'E(B-V)_err_lo' : [], 'E(B-V)_err_hi' : []}
                chiparamsdf = pd.DataFrame(colnames).copy(deep=True)
                for curr_row in range(self.bandfluxes.shape[0]):
                    rowdict = {'Source_ID' : self.source_ids[curr_row], 'minimized chi^2' : self.results[curr_row].fun, 'log(Z)' : self.results[curr_row].x[0], 'log(Z)_err_lo' : self.errorsallrows[curr_row][0][0], 'log(Z)_err_hi' : self.errorsallrows[curr_row][0][1], 'log(age)/10' : self.results[curr_row].x[1], 'log(age)/10_err_lo' : self.errorsallrows[curr_row][1][0], 'log(age)/10_err_hi' : self.errorsallrows[curr_row][1][1], 'log(M)/10' : self.results[curr_row].x[2], 'log(M)/10_err_lo' : self.errorsallrows[curr_row][2][0], 'log(M)/10_err_hi' : self.errorsallrows[curr_row][2][1], 'E(B-V)' : self.results[curr_row].x[3], 'E(B-V)_err_lo' : self.errorsallrows[curr_row][3][0], 'E(B-V)_err_hi' : self.errorsallrows[curr_row][3][1]}
                    chiparamsdf = chiparamsdf.append(rowdict,ignore_index=True)
                for curr_row in range(self.bandfluxes.shape[0]):
                    chiparamsdf = chiparamsdf.rename(index={curr_row:"Source at row {}".format(self.rows[curr_row]+2)})
                try:
                    chiparamsdf.to_csv("{}".format(self.chifilename))
                except:
                    import tkinter as tk
                    from tkinter import messagebox
                    tk.messagebox.showerror('Error','An error occurred. This can happen if a file is open while trying to overwrite it. Please close any relevant files and try again.')             
            
            elif self.double_cluster == True:
                import math
                colnames = {'Source_ID' : [], 'minimized chi^2' : [], 'log(Z_hot)' : [], 'log(Z_hot)_err_lo' : [], 'log(Z_hot)_err_hi' : [], 'log(age_hot)/10' : [], 'log(age_hot)/10_err_lo' : [], 'log(age_hot)/10_err_hi' : [], 'log(M_hot)/10' : [], 'log(M_hot)/10_err_lo' : [], 'log(M_hot)/10_err_hi' : [], 'E(B-V)_hot' : [],  'E(B-V)_hot_err_lo' : [], 'E(B-V)_hot_err_hi' : [], 'log(Z_cool)' : [], 'log(Z_cool)_err_lo' : [], 'log(Z_cool)_err_hi' : [], 'log(age_cool)/10' : [], 'log(age_cool)/10_err_lo' : [], 'log(age_cool)/10_err_hi' : [], 'log(M_cool)/10' : [], 'log(M_cool)/10_err_lo' : [], 'log(M_cool)/10_err_hi' : [], 'E(B-V)_cool' : [], 'E(B-V)_cool_err_lo' : [], 'E(B-V)_cool_err_hi' : []}
                chiparamsdf = pd.DataFrame(colnames).copy(deep=True)
                for curr_row in range(self.bandfluxes.shape[0]):
                    rowdict = {'Source_ID' : self.source_ids[curr_row], 'minimized chi^2' : self.results[curr_row].fun, 'log(Z_hot)' : self.results[curr_row].x[0], 'log(Z_hot)_err_lo' : self.errorsallrows[curr_row][0][0], 'log(Z_hot)_err_hi' : self.errorsallrows[curr_row][0][1], 'log(age_hot)/10' : self.results[curr_row].x[1], 'log(age_hot)/10_err_lo' : self.errorsallrows[curr_row][1][0], 'log(age_hot)/10_err_hi' : self.errorsallrows[curr_row][1][1], 'log(M_hot)/10' : self.results[curr_row].x[2], 'log(M_hot)/10_err_lo' : self.errorsallrows[curr_row][2][0], 'log(M_hot)/10_err_hi' : self.errorsallrows[curr_row][2][1], 'E(B-V)_hot' : self.results[curr_row].x[3], 'E(B-V)_hot_err_lo' : self.errorsallrows[curr_row][3][0], 'E(B-V)_hot_err_hi' : self.errorsallrows[curr_row][3][1], 'log(Z_cool)' : self.results[curr_row].x[4], 'log(Z_cool)_err_lo' : self.errorsallrows[curr_row][4][0], 'log(Z_cool)_err_hi' : self.errorsallrows[curr_row][4][1], 'log(age_cool)/10' : self.results[curr_row].x[5], 'log(age_cool)/10_err_lo' : self.errorsallrows[curr_row][5][0], 'log(age_cool)/10_err_hi' : self.errorsallrows[curr_row][5][1], 'log(M_cool)/10' : self.results[curr_row].x[6], 'log(M_cool)/10_err_lo' : self.errorsallrows[curr_row][6][0], 'log(M_cool)/10_err_hi' : self.errorsallrows[curr_row][6][1], 'E(B-V)_cool' : self.results[curr_row].x[7], 'E(B-V)_cool_err_lo' : self.errorsallrows[curr_row][7][0], 'E(B-V)_cool_err_hi' : self.errorsallrows[curr_row][7][1]}
                    chiparamsdf = chiparamsdf.append(rowdict,ignore_index=True)
                for curr_row in range(self.bandfluxes.shape[0]):
                    chiparamsdf = chiparamsdf.rename(index={curr_row:"Source at row {}".format(self.rows[curr_row]+2)})
                try:
                    chiparamsdf.to_csv("{}".format(self.chifilename))
                except:
                    import tkinter as tk
                    from tkinter import messagebox
                    tk.messagebox.showerror('Error','An error occurred. This can happen if a file is open while trying to overwrite it. Please close any relevant files and try again.')             
    
    def display_results_single(self,curr_row):
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
        import tkinter as tk
        topw = tk.Tk()
        topw.geometry("1460x900+250+20")
        topw.title("Optimization results")
        topw.resizable(0,0)
        
        import matplotlib
        from matplotlib.figure import Figure
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        matplotlib.use('TkAgg')
        import numpy as np

        valid_filters_this_row = []
        ul_filters_this_row = []
        for valid_ind,arraytup in enumerate(zip(self.bandfluxes.loc[curr_row,:],self.ul_frame.loc[curr_row,:])):
            if np.isnan(arraytup[0]) == False:
                valid_filters_this_row.append(valid_ind)
            if arraytup[1] == 1:
                ul_filters_this_row.append(valid_ind)
        valid_notul_filters_this_row = [i for i in valid_filters_this_row if i not in ul_filters_this_row]

        valid_fluxes_this_row = []
        for valid_ind in valid_filters_this_row:
            valid_fluxes_this_row.append(self.bandfluxes.iat[curr_row,valid_ind])

        valid_notul_fluxes_this_row = []
        for valid_ind in valid_notul_filters_this_row:
            valid_notul_fluxes_this_row.append(self.bandfluxes.iat[curr_row,valid_ind])
    
        valid_ul_fluxes_this_row = []
        for valid_ind in ul_filters_this_row:
            valid_ul_fluxes_this_row.append(self.bandfluxes.iat[curr_row,valid_ind])

        valid_errors_this_row = []
        for valid_ind in valid_filters_this_row:
            valid_errors_this_row.append(self.truefluxerrors.iat[curr_row,valid_ind])

        valid_notul_errors_this_row = []
        for valid_ind in valid_notul_filters_this_row:
            valid_notul_errors_this_row.append(self.truefluxerrors.iat[curr_row,valid_ind])

        valid_ul_errors_this_row = []
        for valid_ind in ul_filters_this_row:
            valid_ul_errors_this_row.append(self.truefluxerrors.iat[curr_row,valid_ind]*-1)  

        valid_avgwv_this_row = []
        for valid_ind in valid_filters_this_row:
            valid_avgwv_this_row.append(self.avgwvlist[valid_ind])

        valid_notul_avgwv_this_row = []
        for valid_ind in valid_notul_filters_this_row:
            valid_notul_avgwv_this_row.append(self.avgwvlist[valid_ind])

        valid_ul_avgwv_this_row = []
        for valid_ind in ul_filters_this_row:
            valid_ul_avgwv_this_row.append(self.avgwvlist[valid_ind])

        valid_actualfilters_this_row = []
        for valid_ind in valid_filters_this_row:
            valid_actualfilters_this_row.append(self.filternames[valid_ind])
    

        fig = Figure(figsize=(10.5,6))
        abc = fig.add_subplot(111)
        best_tup = (self.results[curr_row].x[0],self.results[curr_row].x[1],self.results[curr_row].x[2],self.results[curr_row].x[3])
        abc.scatter(valid_avgwv_this_row,valid_fluxes_this_row,color="orange")
        abc.set_xlabel("Wavelength [nm]")
        abc.set_ylabel("Flux [mJy]")
        abc.set_title("Source at row {} (Source ID {})".format(self.rows[curr_row]+2, self.source_ids[curr_row]))
        abc.errorbar(valid_notul_avgwv_this_row,valid_notul_fluxes_this_row,yerr=valid_notul_errors_this_row,fmt="o",color="orange")
        if self.model_chosen == "UVIT_HST":
            abc.errorbar(valid_ul_avgwv_this_row,valid_ul_fluxes_this_row,yerr=valid_ul_errors_this_row,uplims=True,fmt="o",color="green")
        abc.plot(valid_avgwv_this_row,self.minichisqfunc_single(best_tup,valid_filters_this_row),color="blue")

        if self.plotscale == 1:
            if self.xticker == 1:
                abc.set_xticks([int(i) for i in np.arange(200,max(valid_avgwv_this_row),200)])
            elif self.xticker == 0:
                better_avgwv_this_row = []
                for ind, wv in enumerate(valid_avgwv_this_row[0:len(valid_avgwv_this_row)-1]):
                    if valid_avgwv_this_row[ind + 1] - valid_avgwv_this_row[ind] > 80:
                        better_avgwv_this_row.append(wv)
                abc.set_xticks(better_avgwv_this_row)

        if self.plotscale == 0:
            abc.set_xscale('log')
            abc.set_yscale('log')
            if self.xticker == 1:
                abc.set_xticks([int(i) for i in np.arange(200,max(valid_avgwv_this_row),200)])
            elif self.xticker == 0:
                better_avgwv_this_row = []
                for ind, wv in enumerate(valid_avgwv_this_row[0:len(valid_avgwv_this_row)-1]):
                    if valid_avgwv_this_row[ind + 1] - valid_avgwv_this_row[ind] > 20:
                        better_avgwv_this_row.append(wv)
                abc.set_xticks(better_avgwv_this_row)
            abc.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())

        if self.saveplots == 1:
            saveimgname = self.imgfilename.replace("X","{}".format(self.rows[curr_row]+2))
            fig.savefig('{}'.format(saveimgname), bbox_inches='tight', dpi=150)

        canvas = FigureCanvasTkAgg(fig, master=topw)
        canvas.get_tk_widget().pack(anchor=tk.E)
        canvas.draw()

        label1 = tk.Label(topw,text="Average wavelength of each filter (x):")
        label1.place(x=50,y=20)
        textbox1 = tk.Text(topw,height=6,width=30)
        for filtername,avgwv in zip(valid_actualfilters_this_row,valid_avgwv_this_row):
            textbox1.insert(tk.END,"{}      {}\n".format(filtername,avgwv))
        textbox1.place(x=50,y=50)
        label2 = tk.Label(topw,text="Bandfluxes (y, orange):")
        label2.place(x=50,y=220)
        textbox2 = tk.Text(topw,height=6,width=30)
        for filtername,bf in zip(valid_actualfilters_this_row,valid_fluxes_this_row):
            textbox2.insert(tk.END,"{}      {}\n".format(filtername,format(bf,'.8e')))
        textbox2.place(x=50,y=250)
        label3 = tk.Label(topw,text="Bandflux errors:")
        label3.place(x=50,y=420)
        textbox3 = tk.Text(topw,height=6,width=30)
        for filtername,bfe in zip(valid_actualfilters_this_row,valid_errors_this_row):
            textbox3.insert(tk.END,"{}      {}\n".format(filtername,format(bfe,'.8e')))
        textbox3.place(x=50,y=450)
        label4 = tk.Label(topw,text="Model fluxes (y, blue):")
        label4.place(x=50,y=620)
        textbox4 = tk.Text(topw,height=6,width=30)
        for filtername,mod in zip(valid_actualfilters_this_row,self.minichisqfunc_single(best_tup,valid_filters_this_row)):
            textbox4.insert(tk.END,"{}      {}\n".format(filtername,format(mod,'.8e')))
        textbox4.place(x=50,y=650)
        groove = tk.Canvas(topw,width=185,height=120,bd=4,relief=tk.RIDGE)
        groove.place(x=405,y=655)
        label5 = tk.Label(topw,text="Lowest chi^2 value")
        label5.place(x=425,y=665)
        label5a = tk.Label(topw,text="{}".format(format(self.results[curr_row].fun,'.6e')),font=("Arial",12))
        label5a.place(x=437,y=715)
        
        import math
        Z_sticker1 = format(self.results[curr_row].x[0],'.6e')
        try:
            Z_sticker2 = format(self.errorsallrows[curr_row][0][0],'.6e')
        except:
            Z_sticker2 = "       N/A       "
        try:
            Z_sticker3 = format(self.errorsallrows[curr_row][0][1],'.6e')
        except:
            Z_sticker3 = "       N/A       "
        Z_sticker4 = self.errornotes[curr_row][0][0]
        Z_sticker5 = self.errornotes[curr_row][0][1]

        age_sticker1 = format(self.results[curr_row].x[1],'.6e')
        try:
            age_sticker2 = format(self.errorsallrows[curr_row][1][0],'.6e')
        except:
            age_sticker2 = "       N/A       "
        try:
            age_sticker3 = format(self.errorsallrows[curr_row][1][1],'.6e')
        except:
            age_sticker3 = "       N/A       "
        age_sticker4 = self.errornotes[curr_row][1][0]
        age_sticker5 = self.errornotes[curr_row][1][1]    

        M_sticker1 = format(self.results[curr_row].x[2],'.6e')
        try:
            M_sticker2 = format(self.errorsallrows[curr_row][2][0],'.6')
        except:
            M_sticker2 = "       N/A       "
        try:
            M_sticker3 = format(self.errorsallrows[curr_row][2][1],'.6e')
        except:
            M_sticker3 = "       N/A       "
        M_sticker4 = self.errornotes[curr_row][2][0]
        M_sticker5 = self.errornotes[curr_row][2][1]

        ebv_sticker1 = format(self.results[curr_row].x[3],'.6e')
        try:
            ebv_sticker2 = format(self.errorsallrows[curr_row][3][0],'.6e')
        except:
            ebv_sticker2 = "       N/A       "
        try:
            ebv_sticker3 = format(self.errorsallrows[curr_row][3][1],'.6e')
        except:
            ebv_sticker3 = "       N/A       "
        ebv_sticker4 = self.errornotes[curr_row][3][0]
        ebv_sticker5 = self.errornotes[curr_row][3][1]

        colpack1 = tk.Frame(topw)
        colpack1.place(x=650,y=600)
        colpack2 = tk.Frame(topw)
        colpack2.place(x=765,y=600)
        colpack3 = tk.Frame(topw)
        colpack3.place(x=900,y=600)
        colpack4 = tk.Frame(topw)
        colpack4.place(x=1020,y=600)
        colpack5 = tk.Frame(topw)
        colpack5.place(x=1180,y=600)
        colpack6 = tk.Frame(topw)
        colpack6.place(x=1290,y=600)
        parameterhead = tk.Label(colpack1,text="Parameter",bg="azure").pack(pady=10)
        parameter1 = tk.Label(colpack1,text="log(Z)").pack(pady=10)
        parameter2 = tk.Label(colpack1,text="log(age)/10").pack(pady=10)
        parameter3 = tk.Label(colpack1,text="log(M)/10").pack(pady=10)
        parameter4 = tk.Label(colpack1,text="E(B-V)").pack(pady=10)
        besthead = tk.Label(colpack2,text="Best fit value",bg="azure").pack(pady=10)
        best1 = tk.Label(colpack2,text="{}".format(Z_sticker1)).pack(pady=10)
        best2 = tk.Label(colpack2,text="{}".format(age_sticker1)).pack(pady=10)
        best3 = tk.Label(colpack2,text="{}".format(M_sticker1)).pack(pady=10)
        best4 = tk.Label(colpack2,text="{}".format(ebv_sticker1)).pack(pady=10)
        errlohead = tk.Label(colpack3,text="Lower error",bg="azure").pack(pady=10)
        errlo1 = tk.Label(colpack3,text="{}".format(Z_sticker2)).pack(pady=10)
        errlo2 = tk.Label(colpack3,text="{}".format(age_sticker2)).pack(pady=10)
        errlo3 = tk.Label(colpack3,text="{}".format(M_sticker2)).pack(pady=10)
        errlo4 = tk.Label(colpack3,text="{}".format(ebv_sticker2)).pack(pady=10)
        noteslohead = tk.Label(colpack4,text="Lower error notes",bg="azure").pack(pady=10)
        noteslo1 = tk.Label(colpack4,text="{}".format(Z_sticker4),font="Arial, 7").pack(pady=5)
        noteslo2 = tk.Label(colpack4,text="{}".format(age_sticker4),font="Arial, 7").pack(pady=5)
        noteslo3 = tk.Label(colpack4,text="{}".format(M_sticker4),font="Arial, 7").pack(pady=5)
        noteslo4 = tk.Label(colpack4,text="{}".format(ebv_sticker4),font="Arial, 7").pack(pady=5)
        errhihead = tk.Label(colpack5,text="Upper error",bg="azure").pack(pady=10)
        errhi1 = tk.Label(colpack5,text="{}".format(Z_sticker3)).pack(pady=10)
        errhi2 = tk.Label(colpack5,text="{}".format(age_sticker3)).pack(pady=10)
        errhi3 = tk.Label(colpack5,text="{}".format(M_sticker3)).pack(pady=10)
        errhi4 = tk.Label(colpack5,text="{}".format(ebv_sticker3)).pack(pady=10)
        noteshihead = tk.Label(colpack6,text="Upper error notes",bg="azure").pack(pady=10)
        noteshi1 = tk.Label(colpack6,text="{}".format(Z_sticker5),font="Arial, 7").pack(pady=5)
        noteshi2 = tk.Label(colpack6,text="{}".format(age_sticker5),font="Arial, 7").pack(pady=5)
        noteshi3 = tk.Label(colpack6,text="{}".format(M_sticker5),font="Arial, 7").pack(pady=5)
        noteshi4 = tk.Label(colpack6,text="{}".format(ebv_sticker5),font="Arial, 7").pack(pady=5)

        def closethesource():
            topw.destroy()
        byebyebutt = tk.Button(topw, bd=3, font="Arial 10", text="Next source",command=closethesource,padx=30,pady=5)
        byebyebutt.place(x=423,y=830)
        topw.mainloop()

    def display_results_double(self,curr_row):
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
        import tkinter as tk
        topw = tk.Tk()
        topw.geometry("1460x900+250+20")
        topw.title("Optimization results")
        topw.resizable(0,0)
        
        import matplotlib
        from matplotlib.figure import Figure
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        matplotlib.use('TkAgg')
        import numpy as np

        valid_filters_this_row = []
        ul_filters_this_row = []
        for valid_ind,arraytup in enumerate(zip(self.bandfluxes.loc[curr_row,:],self.ul_frame.loc[curr_row,:])):
            if np.isnan(arraytup[0]) == False:
                valid_filters_this_row.append(valid_ind)
            if arraytup[1] == 1:
                ul_filters_this_row.append(valid_ind)
        valid_notul_filters_this_row = [i for i in valid_filters_this_row if i not in ul_filters_this_row]

        valid_fluxes_this_row = []
        for valid_ind in valid_filters_this_row:
            valid_fluxes_this_row.append(self.bandfluxes.iat[curr_row,valid_ind])

        valid_notul_fluxes_this_row = []
        for valid_ind in valid_notul_filters_this_row:
            valid_notul_fluxes_this_row.append(self.bandfluxes.iat[curr_row,valid_ind])
    
        valid_ul_fluxes_this_row = []
        for valid_ind in ul_filters_this_row:
            valid_ul_fluxes_this_row.append(self.bandfluxes.iat[curr_row,valid_ind])

        valid_errors_this_row = []
        for valid_ind in valid_filters_this_row:
            valid_errors_this_row.append(self.truefluxerrors.iat[curr_row,valid_ind])

        valid_notul_errors_this_row = []
        for valid_ind in valid_notul_filters_this_row:
            valid_notul_errors_this_row.append(self.truefluxerrors.iat[curr_row,valid_ind])

        valid_ul_errors_this_row = []
        for valid_ind in ul_filters_this_row:
            valid_ul_errors_this_row.append(self.truefluxerrors.iat[curr_row,valid_ind]*-1)  

        valid_avgwv_this_row = []
        for valid_ind in valid_filters_this_row:
            valid_avgwv_this_row.append(self.avgwvlist[valid_ind])

        valid_notul_avgwv_this_row = []
        for valid_ind in valid_notul_filters_this_row:
            valid_notul_avgwv_this_row.append(self.avgwvlist[valid_ind])

        valid_ul_avgwv_this_row = []
        for valid_ind in ul_filters_this_row:
            valid_ul_avgwv_this_row.append(self.avgwvlist[valid_ind])

        valid_actualfilters_this_row = []
        for valid_ind in valid_filters_this_row:
            valid_actualfilters_this_row.append(self.filternames[valid_ind])
    

        fig = Figure(figsize=(10.5,6))
        abc = fig.add_subplot(111)
        best_tup = (self.results[curr_row].x[0],self.results[curr_row].x[1],self.results[curr_row].x[2],self.results[curr_row].x[3],self.results[curr_row].x[4],self.results[curr_row].x[5],self.results[curr_row].x[6],self.results[curr_row].x[7])
        abc.scatter(valid_avgwv_this_row,valid_fluxes_this_row,color="orange")
        abc.set_xlabel("Wavelength [nm]")
        abc.set_ylabel("Flux [mJy]")
        abc.set_title("Source at row {} (Source ID {})".format(self.rows[curr_row]+2, self.source_ids[curr_row]))
        abc.errorbar(valid_notul_avgwv_this_row,valid_notul_fluxes_this_row,yerr=valid_notul_errors_this_row,fmt="o",color="orange")
        if self.model_chosen == "UVIT_HST":
            abc.errorbar(valid_ul_avgwv_this_row,valid_ul_fluxes_this_row,yerr=valid_ul_errors_this_row,uplims=True,fmt="o",color="green")
        hotmod = self.minichisqfunc_double(best_tup,valid_filters_this_row)[0]
        coolmod = self.minichisqfunc_double(best_tup,valid_filters_this_row)[1]
        abc.plot(valid_avgwv_this_row,hotmod,color="red")
        abc.plot(valid_avgwv_this_row,coolmod,color="blue")
        sumofmodels = [hotmod[i] + coolmod[i] for i in range(len(hotmod))]
        abc.plot(valid_avgwv_this_row,sumofmodels,color="limegreen")

        if self.plotscale == 1:
            if self.xticker == 1:
                abc.set_xticks([int(i) for i in np.arange(200,max(valid_avgwv_this_row),200)])
            elif self.xticker == 0:
                better_avgwv_this_row = []
                for ind, wv in enumerate(valid_avgwv_this_row[0:len(valid_avgwv_this_row)-1]):
                    if valid_avgwv_this_row[ind + 1] - valid_avgwv_this_row[ind] > 80:
                        better_avgwv_this_row.append(wv)
                abc.set_xticks(better_avgwv_this_row)

        if self.plotscale == 0:
            abc.set_xscale('log')
            abc.set_yscale('log')
            if self.xticker == 1:
                abc.set_xticks([int(i) for i in np.arange(200,max(valid_avgwv_this_row),200)])
            elif self.xticker == 0:
                better_avgwv_this_row = []
                for ind, wv in enumerate(valid_avgwv_this_row[0:len(valid_avgwv_this_row)-1]):
                    if valid_avgwv_this_row[ind + 1] - valid_avgwv_this_row[ind] > 20:
                        better_avgwv_this_row.append(wv)
                abc.set_xticks(better_avgwv_this_row)
            abc.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())

        if self.saveplots == 1:
            saveimgname = self.imgfilename.replace("X","{}".format(self.rows[curr_row]+2))
            fig.savefig('{}'.format(saveimgname), bbox_inches='tight', dpi=150)

        canvas = FigureCanvasTkAgg(fig, master=topw)
        canvas.get_tk_widget().pack(anchor=tk.E)
        canvas.draw()

        label1 = tk.Label(topw,text="Average wavelength of each filter (x):")
        label1.place(x=50,y=20)
        textbox1 = tk.Text(topw,height=6,width=30)
        for filtername,avgwv in zip(valid_actualfilters_this_row,valid_avgwv_this_row):
            textbox1.insert(tk.END,"{}      {}\n".format(filtername,avgwv))
        textbox1.place(x=50,y=50)
        label2 = tk.Label(topw,text="Bandfluxes (y, orange):")
        label2.place(x=50,y=195)
        textbox2 = tk.Text(topw,height=6,width=30)
        for filtername,bf in zip(valid_actualfilters_this_row,valid_fluxes_this_row):
            textbox2.insert(tk.END,"{}      {}\n".format(filtername,format(bf,'.8e')))
        textbox2.place(x=50,y=225)
        label3 = tk.Label(topw,text="Bandflux errors:")
        label3.place(x=50,y=370)
        textbox3 = tk.Text(topw,height=6,width=30)
        for filtername,bfe in zip(valid_actualfilters_this_row,valid_errors_this_row):
            textbox3.insert(tk.END,"{}      {}\n".format(filtername,format(bfe,'.8e')))
        textbox3.place(x=50,y=400)
        label4 = tk.Label(topw,text="Hot cluster model fluxes (y, red):")
        label4.place(x=50,y=545)
        textbox4 = tk.Text(topw,height=6,width=30)
        for filtername,mod in zip(valid_actualfilters_this_row,self.minichisqfunc_double(best_tup,valid_filters_this_row)[0]):
            textbox4.insert(tk.END,"{}      {}\n".format(filtername,format(mod,'.8e')))
        textbox4.place(x=50,y=575)
        label5 = tk.Label(topw,text="Cool cluster model fluxes (y, blue):")
        label5.place(x=50,y=720)
        textbox5 = tk.Text(topw,height=6,width=30)
        for filtername,mod in zip(valid_actualfilters_this_row,self.minichisqfunc_double(best_tup,valid_filters_this_row)[1]):
            textbox5.insert(tk.END,"{}      {}\n".format(filtername,format(mod,'.8e')))
        textbox5.place(x=50,y=750)
        groove = tk.Canvas(topw,width=185,height=120,bd=4,relief=tk.RIDGE)
        groove.place(x=405,y=655)
        label5 = tk.Label(topw,text="Lowest chi^2 value")
        label5.place(x=425,y=665)
        label5a = tk.Label(topw,text="{}".format(format(self.results[curr_row].fun,'.6e')),font=("Arial",12))
        label5a.place(x=437,y=715)

        import math
        Z_hot_sticker1 = format(self.results[curr_row].x[0],'.6e')
        try:
            Z_hot_sticker2 = format(self.errorsallrows[curr_row][0][0],'.6e')
        except:
            Z_hot_sticker2 = "       N/A       "
        try:
            Z_hot_sticker3 = format(self.errorsallrows[curr_row][0][1],'.6e')
        except:
            Z_hot_sticker3 = "       N/A       "
        Z_hot_sticker4 = self.errornotes[curr_row][0][0]
        Z_hot_sticker5 = self.errornotes[curr_row][0][1]

        age_hot_sticker1 = format(self.results[curr_row].x[1],'.6e')
        try:
            age_hot_sticker2 = format(self.errorsallrows[curr_row][1][0],'.6e')
        except:
            age_hot_sticker2 = "       N/A       "
        try:
            age_hot_sticker3 = format(self.errorsallrows[curr_row][1][1],'.6e')
        except:
            age_hot_sticker3 = "       N/A       "
        age_hot_sticker4 = self.errornotes[curr_row][1][0]
        age_hot_sticker5 = self.errornotes[curr_row][1][1]  

        M_hot_sticker1 = format(self.results[curr_row].x[2],'.6e')
        try:
            M_hot_sticker2 = format(self.errorsallrows[curr_row][2][0],'.6')
        except:
            M_hot_sticker2 = "       N/A       "
        try:
            M_hot_sticker3 = format(self.errorsallrows[curr_row][2][1],'.6e')
        except:
            M_hot_sticker3 = "       N/A       "
        M_hot_sticker4 = self.errornotes[curr_row][2][0]
        M_hot_sticker5 = self.errornotes[curr_row][2][1]

        ebv_hot_sticker1 = format(self.results[curr_row].x[3],'.6e')
        try:
            ebv_hot_sticker2 = format(self.errorsallrows[curr_row][3][0],'.6e')
        except:
            ebv_hot_sticker2 = "       N/A       "
        try:
            ebv_hot_sticker3 = format(self.errorsallrows[curr_row][3][1],'.6e')
        except:
            ebv_hot_sticker3 = "       N/A     "
        ebv_hot_sticker4 = self.errornotes[curr_row][3][0]
        ebv_hot_sticker5 = self.errornotes[curr_row][3][1]

        Z_cool_sticker1 = format(self.results[curr_row].x[4],'.6e')
        try:
            Z_cool_sticker2 = format(self.errorsallrows[curr_row][4][0],'.6e')
        except:
            Z_cool_sticker2 = "       N/A       "
        try:
            Z_cool_sticker3 = format(self.errorsallrows[curr_row][4][1],'.6e')
        except:
            Z_cool_sticker3 = "       N/A       "
        Z_cool_sticker4 = self.errornotes[curr_row][4][0]
        Z_cool_sticker5 = self.errornotes[curr_row][4][1]

        age_cool_sticker1 = format(self.results[curr_row].x[5],'.6e')
        try:
            age_cool_sticker2 = format(self.errorsallrows[curr_row][5][0],'.6e')
        except:
            age_cool_sticker2 = "       N/A       "
        try:
            age_cool_sticker3 = format(self.errorsallrows[curr_row][5][1],'.6e')
        except:
            age_cool_sticker3 = "       N/A       "
        age_cool_sticker4 = self.errornotes[curr_row][5][0]
        age_cool_sticker5 = self.errornotes[curr_row][5][1]

        M_cool_sticker1 = format(self.results[curr_row].x[6],'.6e')
        try:
            M_cool_sticker2 = format(self.errorsallrows[curr_row][6][0],'.6e')
        except:
            M_cool_sticker2 = "       N/A       "
        try:
            M_cool_sticker3 = format(self.errorsallrows[curr_row][6][1],'.6e')
        except:
            M_cool_sticker3 = "       N/A       "
        M_cool_sticker4 = self.errornotes[curr_row][6][0]
        M_cool_sticker5 = self.errornotes[curr_row][6][1]

        ebv_cool_sticker1 = format(self.results[curr_row].x[7],'.6e')
        try:
            ebv_cool_sticker2 = format(self.errorsallrows[curr_row][7][0],'.6e')
        except:
            ebv_cool_sticker2 = "       N/A       "
        try:
            ebv_cool_sticker3 = format(self.errorsallrows[curr_row][7][1],'.6e')
        except:
            ebv_cool_sticker3 = "       N/A       "
        ebv_cool_sticker4 = self.errornotes[curr_row][7][0]
        ebv_cool_sticker5 = self.errornotes[curr_row][7][1]

        colpack1 = tk.Frame(topw)
        colpack1.place(x=650,y=600)
        colpack2 = tk.Frame(topw)
        colpack2.place(x=790,y=600)
        colpack3 = tk.Frame(topw)
        colpack3.place(x=910,y=600)
        colpack4 = tk.Frame(topw)
        colpack4.place(x=1020,y=600)
        colpack5 = tk.Frame(topw)
        colpack5.place(x=1180,y=600)
        colpack6 = tk.Frame(topw)
        colpack6.place(x=1290,y=600)
        parameterhead = tk.Label(colpack1,text="Parameter",bg="azure").pack(pady=3)
        parameter1 = tk.Label(colpack1,text="log(Z_hot)").pack(pady=3)
        parameter2 = tk.Label(colpack1,text="log(age_hot)/10").pack(pady=3)
        parameter3 = tk.Label(colpack1,text="log(M_hot)/10").pack(pady=3)
        parameter4 = tk.Label(colpack1,text="E(B-V)_hot").pack(pady=3)
        parameter5 = tk.Label(colpack1,text="log(Z_cool)").pack(pady=3)
        parameter6 = tk.Label(colpack1,text="log(age_cool)/10").pack(pady=3)
        parameter7 = tk.Label(colpack1,text="log(M_cool)/10").pack(pady=3)
        parameter8 = tk.Label(colpack1,text="E(B-V)_cool").pack(pady=3)
        besthead = tk.Label(colpack2,text="Best fit value",bg="azure").pack(pady=3)
        best1 = tk.Label(colpack2,text="{}".format(Z_hot_sticker1)).pack(pady=3)
        best2 = tk.Label(colpack2,text="{}".format(age_hot_sticker1)).pack(pady=3)
        best3 = tk.Label(colpack2,text="{}".format(M_hot_sticker1)).pack(pady=3)
        best4 = tk.Label(colpack2,text="{}".format(ebv_hot_sticker1)).pack(pady=3)
        best5 = tk.Label(colpack2,text="{}".format(Z_cool_sticker1)).pack(pady=3)
        best6 = tk.Label(colpack2,text="{}".format(age_cool_sticker1)).pack(pady=3)
        best7 = tk.Label(colpack2,text="{}".format(M_cool_sticker1)).pack(pady=3)
        best8 = tk.Label(colpack2,text="{}".format(ebv_cool_sticker1)).pack(pady=3)
        errlohead = tk.Label(colpack3,text="Lower error",bg="azure").pack(pady=3)
        errlo1 = tk.Label(colpack3,text="{}".format(Z_hot_sticker2)).pack(pady=3)
        errlo2 = tk.Label(colpack3,text="{}".format(age_hot_sticker2)).pack(pady=3)
        errlo3 = tk.Label(colpack3,text="{}".format(M_hot_sticker2)).pack(pady=3)
        errlo4 = tk.Label(colpack3,text="{}".format(ebv_hot_sticker2)).pack(pady=3)
        errlo5 = tk.Label(colpack3,text="{}".format(Z_cool_sticker2)).pack(pady=3)
        errlo6 = tk.Label(colpack3,text="{}".format(age_cool_sticker2)).pack(pady=3)
        errlo7 = tk.Label(colpack3,text="{}".format(M_cool_sticker2)).pack(pady=3)
        errlo8 = tk.Label(colpack3,text="{}".format(ebv_cool_sticker2)).pack(pady=3)
        noteslohead = tk.Label(colpack4,text="Lower error notes",bg="azure").pack(pady=3)
        noteslo1 = tk.Label(colpack4,text="{}".format(Z_hot_sticker4),font="Arial, 6").pack()
        noteslo2 = tk.Label(colpack4,text="{}".format(age_hot_sticker4),font="Arial, 6").pack()
        noteslo3 = tk.Label(colpack4,text="{}".format(M_hot_sticker4),font="Arial, 6").pack()
        noteslo4 = tk.Label(colpack4,text="{}".format(ebv_hot_sticker4),font="Arial, 6").pack()
        noteslo5 = tk.Label(colpack4,text="{}".format(Z_cool_sticker4),font="Arial, 6").pack()
        noteslo6 = tk.Label(colpack4,text="{}".format(age_cool_sticker4),font="Arial, 6").pack()
        noteslo7 = tk.Label(colpack4,text="{}".format(M_cool_sticker4),font="Arial, 6").pack()
        noteslo8 = tk.Label(colpack4,text="{}".format(ebv_cool_sticker4),font="Arial, 6").pack()
        errhihead = tk.Label(colpack5,text="Upper error",bg="azure").pack(pady=3)
        errhi1 = tk.Label(colpack5,text="{}".format(Z_hot_sticker3)).pack(pady=3)
        errhi2 = tk.Label(colpack5,text="{}".format(age_hot_sticker3)).pack(pady=3)
        errhi3 = tk.Label(colpack5,text="{}".format(M_hot_sticker3)).pack(pady=3)
        errhi4 = tk.Label(colpack5,text="{}".format(ebv_hot_sticker3)).pack(pady=3)
        errhi5 = tk.Label(colpack5,text="{}".format(Z_cool_sticker3)).pack(pady=3)
        errhi6 = tk.Label(colpack5,text="{}".format(age_cool_sticker3)).pack(pady=3)
        errhi7 = tk.Label(colpack5,text="{}".format(M_cool_sticker3)).pack(pady=3)
        errhi8 = tk.Label(colpack5,text="{}".format(ebv_cool_sticker3)).pack(pady=3)
        noteshihead = tk.Label(colpack6,text="Upper error notes",bg="azure").pack(pady=3)
        noteshi1 = tk.Label(colpack6,text="{}".format(Z_hot_sticker5),font="Arial, 6").pack()
        noteshi2 = tk.Label(colpack6,text="{}".format(age_hot_sticker5),font="Arial, 6").pack()
        noteshi3 = tk.Label(colpack6,text="{}".format(M_hot_sticker5),font="Arial, 6").pack()
        noteshi4 = tk.Label(colpack6,text="{}".format(ebv_hot_sticker5),font="Arial, 6").pack()
        noteshi5 = tk.Label(colpack6,text="{}".format(Z_cool_sticker5),font="Arial, 6").pack()
        noteshi6 = tk.Label(colpack6,text="{}".format(age_cool_sticker5),font="Arial, 6").pack()
        noteshi7 = tk.Label(colpack6,text="{}".format(M_cool_sticker5),font="Arial, 6").pack()
        noteshi8 = tk.Label(colpack6,text="{}".format(ebv_cool_sticker5),font="Arial, 6").pack()


        def closethesource():
            topw.destroy()
        byebyebutt = tk.Button(topw, bd=3, font="Arial 10", text="Next source",command=closethesource,padx=30,pady=5)
        byebyebutt.place(x=423,y=830)
        topw.mainloop()


go = ChiSquared()