import tkinter as tk
from search import Search
import webbrowser
   

def openlink(event):
    url = event.widget.cget("text")
    curl = url.split("\n")[0]
    return webbrowser.open_new(r"http://"+curl)

def main():
    s = Search()
    root = tk.Tk()
    

    root.title("Generic SearchEngine")
    #root.geometry('700x700')
    root.resizable(0,0)
    myEntryInput = tk.StringVar()
    #myScrollBar = tk.Scrollbar().grid(row = 10, column = 3 ,sticky = ("N","S"))
    

    strVar_list = []
    for i in range(20):
        strVar_list.append(tk.StringVar())


    def go():
        print(myEntryInput.get())
        for i in strVar_list:
            i.set("")

        query = myEntryInput.get()
        
        if query == "":
            strVar_list[0].set("please re-enter")
            return

        url_descrip = s.search(query)
        index = 0
        for url, des in url_descrip:
            strVar_list[index].set(url+ "\n"+ des)
            #strVar_list[index].set(url)
            labels[index].bind("<Button-1>", openlink)
            index += 1
        
     
    labels = []
    for i in range(20):
        l = tk.Label(master = root, textvariable = strVar_list[i],font = ("Arial", 12), fg = "blue", cursor = "hand2")
        l.grid(row = i+2 ,column = 3)
        labels.append(l)

    
    myEntryField = tk.Entry(master=root, text = myEntryInput).grid(row =0, column = 3, ipadx = 100)
    myButton = tk.Button(master = root,font = ("Arial",25), text="GO!", command = go).grid(row = 0, column = 4, sticky = "w")
    quitButton = tk.Button(master= root,text="Quit",command= root.destroy).grid(row=21,column=4, sticky = "e")

    root.mainloop()
    
main()

